# File: jira_connector.py
#
# Copyright (c) 2016-2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#
#
import json
import os
import signal
import sys
import tempfile
import time
from datetime import datetime

import dateutil
import phantom.app as phantom
import phantom.rules as phantom_rules
import pytz
import requests
from bs4 import BeautifulSoup, UnicodeDammit
from dateutil.parser import parse
from phantom.vault import Vault
from phantom_common import paths

from jira.client import JIRA
from jira_consts import *


def timeout_handler(signum, frame):
    raise Timeout()


class Timeout(Exception):
    pass


class JiraConnector(phantom.BaseConnector):
    # actions supported by this script
    ACTION_ID_CREATE_TICKET = "create_ticket"
    ACTION_ID_LIST_PROJECTS = "list_projects"
    ACTION_ID_LIST_TICKETS = "list_tickets"
    ACTION_ID_GET_TICKET = "get_ticket"
    ACTION_ID_SET_TICKET_STATUS = "set_ticket_status"
    ACTION_ID_UPDATE_TICKET = "update_ticket"
    ACTION_ID_DELETE_TICKET = "delete_ticket"
    ACTION_ID_ADD_COMMENT = "add_comment"
    ACTION_ID_LINK_TICKETS = "link_tickets"
    ACTION_ID_ADD_WATCHER = "add_watcher"
    ACTION_ID_REMOVE_WATCHER = "remove_watcher"
    ACTION_ID_ON_POLL = "on_poll"
    ACTION_ID_GET_ATTACHMENTS = "get_attachments"
    ACTION_ID_SEARCH_USERS = "search_users"

    def __init__(self):
        # Call the BaseConnectors init first
        super().__init__()

        self._jira = None
        self._timezone = None

    def initialize(self):
        config = self.get_config()

        # Base URL
        self._base_url = config[JIRA_JSON_DEVICE_URL]
        self._host = self._base_url[self._base_url.find("//") + 2 :]
        self._timezone = config.get(JIRA_JSON_TIMEZONE, JIRA_JSON_DEFAULT_TIMEZONE)

        self._verify_cert = config.get(phantom.APP_JSON_VERIFY, False)
        self._username = config.get(phantom.APP_JSON_USERNAME)
        self._password = config[phantom.APP_JSON_PASSWORD]
        self._custom_fields_list = None
        self._custom_fields = config.get(JIRA_JSON_CUSTOM_FIELDS)

        if self._custom_fields:
            try:
                self._custom_fields_list = json.loads(self._custom_fields)
                if not isinstance(self._custom_fields_list, list):
                    return self.set_status(phantom.APP_ERROR, JIRA_CUSTOM_FIELD_NON_EMPTY_ERROR)
            except Exception as e:
                error_text = self._get_error_message_from_exception(e)
                return self.set_status(phantom.APP_ERROR, JIRA_CUSTOM_FIELD_FORMAT_ERROR.format(error_text))

        return phantom.APP_SUCCESS

    def _process_empty_response(self, response, action_result):
        """This function is used to process empty response.
        :param response: response data
        :param action_result: object of Action Result
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """

        if response.status_code == 200 or response.status_code == 204:
            return phantom.APP_SUCCESS, {}

        return (
            action_result.set_status(phantom.APP_ERROR, f"Status code: {response.status_code}. Empty response and no information in the header"),
            None,
        )

    def _process_html_response(self, response, action_result):
        """This function is used to process html response.
        :param response: response data
        :param action_result: object of Action Result
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """

        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            # Remove the script, style, footer and navigation part from the HTML message
            for element in soup(["script", "style", "footer", "nav"]):
                element.extract()
            error_text = soup.text
            split_lines = error_text.split("\n")
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = "\n".join(split_lines)
        except Exception:
            error_text = "Cannot parse error details"

        message = f"Status Code: {status_code}. Data from server:\n{error_text}\n"

        message = message.replace("{", "{{").replace("}", "}}")

        return action_result.set_status(phantom.APP_ERROR, message), None

    def _process_json_response(self, r, action_result):
        """This function is used to process json response.
        :param r: response data
        :param action_result: object of Action Result
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """

        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, f"Unable to parse JSON response. {error_text}"), None

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return phantom.APP_SUCCESS, resp_json

        message = None
        # Error handling for different type of error responses from server
        if resp_json.get("errorMessages"):
            resp_message = ", ".join(resp_json.get("errorMessages", "Error message not found"))
            message = f"Error from server. Status code: {r.status_code}. Data from server: {resp_message}"

        # You should process the error returned in the json if none of the above handling happens for error scenario
        if not message:
            resp_text = r.text.replace("{", "{{").replace("}", "}}") if r.text else "Response error text not found"
            message = f"Error from server. Status Code: {r.status_code} Data from server: {resp_text}"

        return action_result.set_status(phantom.APP_ERROR, message), None

    def _process_response(self, r, action_result):
        """This function is used to process API response.
        :param r: response data
        :param action_result: object of Action Result
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message)
        """

        # Store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": r.status_code})
            action_result.add_debug_data({"r_text": r.text})
            action_result.add_debug_data({"r_headers": r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if "json" in r.headers.get("Content-Type", ""):
            if not r.text:
                return self._process_empty_response(r, action_result)
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if "html" in r.headers.get("Content-Type", ""):
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {} Data from server: {}".format(
            r.status_code, r.text.replace("{", "{{").replace("}", "}}") if r.text else "Response error text not found"
        )

        return action_result.set_status(phantom.APP_ERROR, message), None

    def _make_rest_call(self, endpoint, action_result, method="get", params=None, data=None):
        """Function that makes the REST call to the app.
        :param endpoint: REST endpoint that needs to appended to the service address
        :param action_result: object of ActionResult class
        :param method: GET/POST/PUT/DELETE/PATCH (Default will be GET)
        :param params: request parameters
        :param data: request body
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message),
        response obtained by making an API call
        """
        resp_json = None

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            return action_result.set_status(phantom.APP_ERROR, f"Invalid method: {method}"), resp_json

        # Create headers information
        headers = dict()

        headers.update({"Content-Type": "application/json"})

        # Create a URL to connect to Jira server
        url = f"{self._base_url}/rest/api/2/{endpoint}"

        self.debug_print("Making a REST call with provided request parameters")

        try:
            if self._username:
                r = request_func(
                    url, auth=(self._username, self._password), params=params, headers=headers, data=data, timeout=JIRA_DEFAULT_TIMEOUT
                )
            else:
                self.debug_print("Updating headers with Bearer token authorization")
                headers.update({"Authorization": f"Bearer {self._password}"})
                r = request_func(url, params=params, headers=headers, data=data, timeout=JIRA_DEFAULT_TIMEOUT)
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, f"Error connecting to server. {error_text}"), resp_json

        return self._process_response(r, action_result)

    def _is_safe_path(self, basedir, path, follow_symlinks=True):
        """
        This function checks the given file path against the actual app directory
        path to combat path traversal attacks
        """
        if follow_symlinks:
            matchpath = os.path.realpath(path)
        else:
            matchpath = os.path.abspath(path)

        return basedir == os.path.commonpath((basedir, matchpath))

    def _get_error_message_from_exception(self, e):
        """
        Get appropriate error message from the exception.
        :param e: Exception object
        :return: error message
        """

        error_code = None
        error_message = ERROR_MESSAGE_UNAVAILABLE

        try:
            if hasattr(e, "args"):
                if len(e.args) > 1:
                    error_code = e.args[0]
                    error_message = e.args[1]
                elif len(e.args) == 1:
                    error_message = e.args[0]
        except Exception as e:
            self.debug_print(f"Error occurred while fetching exception information. Details: {e!s}")

        if not error_code:
            error_text = f"Error Message: {error_message}"
        else:
            error_text = f"Error Code: {error_code}. Error Message: {error_message}"

        return error_text

    def _load_state(self):
        dirpath = os.path.split(os.path.abspath(__file__))[0]
        asset_id = self.get_asset_id()
        state_file_path = f"{dirpath}/{asset_id}_state.json"

        state = {}

        try:
            with open(state_file_path) as f:
                in_json = f.read()
                state = json.loads(in_json)
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            self.debug_print(f"In _load_state: Exception: {error_text}")

        self.debug_print("Loaded state: ", state)

        return state

    def _save_state(self, state):
        self.debug_print("Saving state: ", state)

        dirpath = os.path.split(os.path.abspath(__file__))[0]
        asset_id = self.get_asset_id()
        state_file_path = f"{dirpath}/{asset_id}_state.json"

        if not state_file_path:
            self.debug_print("state_file_path is None in _save_state")
            return phantom.APP_SUCCESS

        try:
            with open(state_file_path, "w+") as f:
                f.write(json.dumps(state))
        except Exception:
            pass

        return phantom.APP_SUCCESS

    def _set_jira_error(self, result_object, message, e):
        # Newer versions of Jira API may not include the error messages in
        # e.text. Instead, these messages are included in e.response,
        # which is a Response object from requests package.
        if hasattr(e, "text") and e.text:
            error_text: str = self._extract_err_msg_from_jira_exc_text(e)
        else:
            self.debug_print("Jira error details missing in exception. Details will be fetched from HTTP Response.")
            error_text = self._extract_err_msg_from_jira_exc_response(e)

        if "Epic Name is required" in error_text:
            error_text = "{}. {}".format(
                error_text,
                'Please create a custom field for Epic Name and provide it in the fields parameter as { "customfield_Id" : "epic_name" }',
            )

        return result_object.set_status(phantom.APP_ERROR, f"{message}. Message: {error_text}")

    def _extract_err_msg_from_jira_exc_text(self, jira_exc) -> str:
        error_text = jira_exc.text
        # Try to parse the HTML content of the error in majority situations and if it fails to parse
        # the error response as HTML, then, return the raw error text to ensure that the error text
        # is not getting dropped from this point
        self.debug_print("Jira error details available in exception, parsing it with BeautifulSoup.")
        try:
            soup = BeautifulSoup(error_text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split("\n")
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = "\n".join(split_lines)
        except Exception as parsing_exception:
            try:
                error_text = f"Cannot parse error details. Unparsed error: {error_text}. Parsing exception: {parsing_exception}"
            except Exception as ex:
                error_text = (
                    f"Unable to parse the details of the error received "
                    f"in the output response. Parsing exception: "
                    f"{parsing_exception}. Formatting to str exception: "
                    f"{ex}."
                )
        return error_text

    def _extract_err_msg_from_jira_exc_response(self, jira_exc) -> str:
        try:
            response_content: dict = jira_exc.response.json()
            jira_error_messages: list[str] = response_content.get(JIRA_RESPONSE_ERROR_MESSAGES_KEY, [])
            jira_errors: dict[str, str] = response_content.get(JIRA_RESPONSE_ERRORS_KEY, {})
            all_jira_error_messages: list[str] = jira_error_messages + [
                f"{field_name}: {error_details}" for field_name, error_details in jira_errors.items()
            ]
            error_text = (
                "\n".join(all_jira_error_messages)
                if all_jira_error_messages
                else "Unable to parse the details of the error received in the output response"
            )

        except Exception as e:
            error_text = self._get_error_message_from_exception(e)

        return error_text

    def _create_jira_object(self, action_result):
        if not self._verify_cert and "REQUESTS_CA_BUNDLE" in os.environ:
            del os.environ["REQUESTS_CA_BUNDLE"]

        # create the options dictionary
        options = {"server": self._base_url, "verify": self._verify_cert}

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(JIRA_START_TIMEOUT)

        try:
            if self._username:
                self.save_progress("Creating JIRA client with HTTP Basic Authentication")
                self._jira = JIRA(options=options, basic_auth=(self._username, self._password), validate=True)
            else:
                self.save_progress("Creating JIRA client with Bearer Token Authentication")
                self._jira = JIRA(options=options, token_auth=self._password, validate=True)
        except Timeout:
            return action_result.set_status(phantom.APP_ERROR, JIRA_ERROR_API_TIMEOUT)
        except Exception as e:
            return self._set_jira_error(action_result, JIRA_ERROR_API_INITIALIZATION, e)
        finally:
            signal.alarm(0)

        return phantom.APP_SUCCESS

    def _test_connectivity(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))
        # Progress
        self.save_progress(JIRA_USING_BASE_URL.format(base_url=self._base_url))

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            self.save_progress(JIRA_ERROR_CONNECTIVITY_TEST)
            return action_result.get_status()

        try:
            self._jira.myself()
        except Exception as e:
            self._set_jira_error(action_result, JIRA_ERROR_SERVER_INFO, e)
            self.save_progress(JIRA_ERROR_CONNECTIVITY_TEST)
            return action_result.get_status()

        self.save_progress(JIRA_SUCCESS_CONNECTIVITY_TEST)
        return action_result.set_status(phantom.APP_SUCCESS, JIRA_SUCCESS_CONNECTIVITY_TEST)

    def _list_projects(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        projects = None

        # get all the projects
        try:
            projects = self._jira.projects()
        except Exception as e:
            return self._set_jira_error(action_result, JIRA_ERROR_PROJECTS_INFO, e)

        action_result.set_summary({JIRA_TOTAL_PROJECTS: 0})

        if not projects:
            return action_result.set_status(phantom.APP_SUCCESS)

        for project in projects:
            data = action_result.add_data({})
            if hasattr(project, "key"):
                data[JIRA_JSON_PROJECT_KEY] = project.key
            if hasattr(project, "id"):
                data[JIRA_JSON_PROJECT_ID] = project.id
            if hasattr(project, "name"):
                data[JIRA_JSON_PROJECT_NAME] = project.name

        action_result.set_summary({JIRA_TOTAL_PROJECTS: len(projects)})

        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_custom_fields_for_issue(self, issue_id, action_result):
        try:
            edit_meta = self._jira.editmeta(issue_id)
        except Exception as e:
            error_message = self._get_error_message_from_exception(e)
            error_text = f"Unable to get edit meta info about the issue. {error_message}"
            return action_result.set_status(phantom.APP_ERROR, error_text), None, None

        fields_meta = edit_meta.get("fields")
        if not fields_meta:
            return (
                action_result.set_status(
                    phantom.APP_ERROR, "Got an empty response to the 'editmeta' REST endpoint. This may be caused by a jira permission problem"
                ),
                None,
                None,
            )

        # create an array of custom fields
        try:
            custom_fields = [x for x in fields_meta if ("customfield" in x)]
        except Exception as e:
            error_message = self._get_error_message_from_exception(e)
            error_text = f"Unable to parse edit meta info to extract custom fields. \
                {error_message}"
            return action_result.set_status(phantom.APP_ERROR, error_text), None, None

        return phantom.APP_SUCCESS, custom_fields, fields_meta

    def _replace_custom_id_with_name(self, input_fields, custom_id_to_name, action_result):
        try:
            # get all the custom keys present in the input_fields
            custom_keys_present = set(input_fields.keys()).intersection(list(custom_id_to_name.keys()))

            for field in custom_keys_present:
                # replace them
                input_fields[custom_id_to_name[field]] = input_fields.pop(field)
        except Exception as e:
            error_message = self._get_error_message_from_exception(e)
            error_text = f"Failed to replace custom fields ID with name. {error_message}"
            return action_result.set_status(phantom.APP_ERROR, error_text), None, custom_keys_present

        return phantom.APP_SUCCESS, input_fields, custom_keys_present

    def _replace_custom_name_with_id(self, input_fields, custom_name_to_id, action_result):
        try:
            # get all the custom keys present in the input_fields
            custom_keys_present = set(input_fields.keys()).intersection(list(custom_name_to_id.keys()))

            for field in custom_keys_present:
                # replace them
                input_fields[custom_name_to_id[field]] = input_fields.pop(field)
        except Exception as e:
            error_message = self._get_error_message_from_exception(e)
            error_text = f"Failed to replace custom fields name with ID. {error_message}"
            return action_result.set_status(phantom.APP_ERROR, error_text), None

        return phantom.APP_SUCCESS, input_fields

    def _get_update_fields(self, param, issue_id, action_result, key=JIRA_JSON_UPDATE_FIELDS):
        update_fields = param.get(key, "")

        # update_fields is an optional field
        if not update_fields:
            return phantom.APP_SUCCESS, None

        # we take in as a dictionary string, first try to load it as is
        try:
            update_fields = json.loads(update_fields)
        except Exception as e:
            error_message = self._get_error_message_from_exception(e)
            error_fields_json_parse = JIRA_ERROR_FIELDS_JSON_PARSE.format(field_name=JIRA_JSON_UPDATE_FIELDS)
            error_text = f"{error_fields_json_parse} {error_message}"

            return action_result.set_status(phantom.APP_ERROR, error_text.replace("{", "(").replace("}", ")")), None

        if not isinstance(update_fields, dict):
            return action_result.set_status(phantom.APP_ERROR, "Please provide a valid JSON formatted dictionary"), None

        if not update_fields:
            return action_result.set_status(phantom.APP_ERROR, "The input dictionary seems to be empty"), None

        # make a copy of it
        update_fields_copy = dict(update_fields)

        custom_name_to_id = self._get_custom_fields_id_name_map(issue_id, action_result, id_to_name=False)

        # If the custom_fields are empty, no more processing required
        if not custom_name_to_id:
            return phantom.APP_SUCCESS, update_fields

        ret_val = True

        fields = update_fields.get("fields")

        if fields:
            status, fields = self._replace_custom_name_with_id(fields, custom_name_to_id, action_result)
            del update_fields_copy["fields"]
            ret_val &= status
            if not status:
                fields = None

        update = update_fields.get("update")
        if update:
            status, update = self._replace_custom_name_with_id(update, custom_name_to_id, action_result)
            del update_fields_copy["update"]
            ret_val &= status
            if not status:
                update = None

        # Any more keys left?
        keys = None
        if update_fields_copy:
            status, keys = self._replace_custom_name_with_id(update_fields_copy, custom_name_to_id, action_result)
            ret_val &= status
            if not status:
                keys = None

        # Create a new dictionary, because we want to replace all the keys in it
        update_fields_to_ret = {}

        if fields:
            update_fields_to_ret["fields"] = fields
        if update:
            update_fields_to_ret["update"] = update
        if keys:
            update_fields_to_ret.update(keys)

        if not ret_val:
            return action_result.get_status(), None

        return phantom.APP_SUCCESS, update_fields_to_ret

    def _set_ticket_status(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))
        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        kwargs = {}

        issue_id = param[JIRA_JSON_ID]
        param_update_fields = param.get(JIRA_JSON_UPDATE_FIELDS, "")
        time_spent = param.get(JIRA_JSON_TIMESPENT, "")

        try:
            issue = self._jira.issue(issue_id)
        except Exception as e:
            return self._set_jira_error(action_result, "Unable to find ticket info. Please make sure the issue exists", e)

        if not issue:
            return action_result.set_status(phantom.APP_ERROR, "Unable to find ticket info. Please make sure the issue exists")

        update_result = True

        if param_update_fields:
            update_result, update_fields = self._get_update_fields(param, issue_id, action_result)

            if phantom.is_fail(update_result):
                action_result_message = action_result.get_message()
                error_message = action_result_message if action_result_message else ""

                if JIRA_ERROR_FETCH_CUSTOM_FIELDS not in error_message:
                    return action_result.get_status()

            if update_fields:
                update_result = self._add_update_fields(issue, update_fields, action_result)

        if not update_result:
            error_message = "Error occurred while updating the ticket: Failed to update fields"
            return action_result.set_status(phantom.APP_ERROR, f"{error_message} Error message: {action_result.get_message()}")

        kwargs.update({"issue": issue_id})

        status_to_set = param[JIRA_JSON_STATUS]

        # get the status' that can be set
        transitions = self._jira.transitions(issue_id)

        try:
            transition_info = [x for x in transitions if x["name"] == status_to_set]
        except Exception:
            return action_result.set_status(
                phantom.APP_ERROR, "Unable to parse response from server while trying to get information about status values"
            )

        if not transition_info:
            message = JIRA_ERROR_ISSUE_VALID_TRANSITIONS
            valid_transitions = self._get_list_string(transitions)
            if valid_transitions:
                valid_transitions = ", ".join(valid_transitions)
                message = f"{message}. Valid status value(s): {valid_transitions}"
            return action_result.set_status(phantom.APP_ERROR, message)

        try:
            transition_id = transition_info[0]["id"]
        except Exception:
            return action_result.set_status(
                phantom.APP_ERROR, "Unable to parse response from server while trying to get information about status values"
            )

        kwargs.update({"transition": transition_id})

        resolution_to_set = param.get(JIRA_JSON_RESOLUTION, "")

        if resolution_to_set:
            # get the list of resolutions that we can set to
            resolutions = self._jira.resolutions()

            try:
                resolution_info = [x for x in resolutions if x.name == resolution_to_set]
            except Exception:
                return action_result.set_status(
                    phantom.APP_ERROR, "Unable to parse response from server while trying to get resolution about status values"
                )

            if not resolution_info:
                message = JIRA_ERROR_ISSUE_VALID_RESOLUTION
                valid_resolutions = self._get_list_string(resolutions)
                if valid_resolutions:
                    valid_resolutions = ", ".join(valid_resolutions)
                    message = f"{message} Valid resolution value(s): {valid_resolutions}"
                return action_result.set_status(phantom.APP_ERROR, message)

            try:
                resolution_id = resolution_info[0].id
            except Exception:
                return action_result.set_status(
                    phantom.APP_ERROR, "Unable to parse response from server while trying to get information about resolution values"
                )

            if resolution_to_set:
                kwargs.update({"fields": {"resolution": {"id": resolution_id}}})

        # So far, so good, try to now set the values
        try:
            if time_spent:
                self._jira.add_worklog(issue=issue_id, timeSpent=time_spent)

            self._jira.transition_issue(**kwargs)
        except Exception as e:
            message = "Unable to set ticket status or add worklog"
            if transition_id and resolution_to_set:
                # This period at the start is an intentional change for getting the error message in correct format
                message += ". The combination of status and resolution could be invalid"
            return self._set_jira_error(action_result, message, e)

        comment = param.get(JIRA_JSON_COMMENT, "")

        # to add comment to the issue if present
        comment_failure_message = ""
        if comment:
            ret_val = self._add_comment_for_set_status(issue_id, issue, comment, action_result)

            # The on-premise Jira gives error when we try to add comment after closing the ticket.
            # Hence, not failing it but adding the message to the action_result
            if phantom.is_fail(ret_val):
                self.debug_print(f"Error occurred while adding the comment. Error message: {action_result.get_message()}")
                comment_failure_message = JIRA_ERROR_COMMENT_SET_STATUS_FAILED

        self.save_progress("Re-querying the ticket")
        ret_val = self._set_issue_data(issue_id, action_result)

        if phantom.is_fail(ret_val):
            action_result_message = action_result.get_message()
            error_message = action_result_message if action_result_message else ""

            if JIRA_ERROR_FETCH_CUSTOM_FIELDS not in error_message:
                return action_result.get_status()

        return action_result.set_status(
            phantom.APP_SUCCESS,
            "The status is updated successfully" + (f". NOTE: {comment_failure_message}" if comment_failure_message else ""),
        )

    def _get_list_string(self, obj_list):
        # ret_string = ''
        ret_list = list()

        for item in obj_list:
            name = ""

            if hasattr(item, "raw"):
                name = item.name
            else:
                name = item.get("name")

            if name:
                # ret_string += "<li>{0}</li>".format(name)
                ret_list.append(name)

        # if (ret_string):
        # ret_string = "<ul>{0}</ul>".format(ret_string)

        # return ret_string
        return ret_list

    def _update_ticket(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        issue_id = param[JIRA_JSON_ID]

        attachment = param.get(JIRA_JSON_ATTACHMENT, "")
        param_update_fields = param.get(JIRA_JSON_UPDATE_FIELDS, "")

        if (not attachment) and (not param_update_fields):
            return action_result.set_status(phantom.APP_ERROR, JIRA_ERROR_UPDATE_NO_PARAM)

        try:
            issue = self._jira.issue(issue_id)
        except Exception as e:
            return self._set_jira_error(action_result, "Unable to find ticket info. Please make sure the issue exists", e)

        if not issue:
            return action_result.set_status(phantom.APP_ERROR, "Unable to find ticket info. Please make sure the issue exists")

        update_result = True

        if param_update_fields:
            update_result, update_fields = self._get_update_fields(param, issue_id, action_result)

            if phantom.is_fail(update_result):
                error_message = action_result.get_message()
                if not error_message:
                    error_message = ""

                if JIRA_ERROR_FETCH_CUSTOM_FIELDS not in error_message:
                    return action_result.get_status()

            if update_fields:
                update_result = self._add_update_fields(issue, update_fields, action_result)

        attach_result = True
        attachment_status = self._add_attachment(issue, attachment)

        if attachment_status:
            if action_result.get_message():
                action_result.set_status(phantom.APP_ERROR, f"{action_result.get_message()}{attachment_status}")
            else:
                action_result.set_status(phantom.APP_ERROR, attachment_status)

            attach_result = False

        self.save_progress("Re-querying the ticket")

        ret_val = phantom.APP_SUCCESS

        error_message = ""
        if attach_result and update_result:
            ret_val = self._set_issue_data(issue_id, action_result)
            error_message = action_result.get_message()

        if not error_message:
            error_message = ""

        if (not ret_val and JIRA_ERROR_FETCH_CUSTOM_FIELDS not in error_message) or not attach_result or not update_result:
            error_message = "Error occurred while updating the ticket. "
            if attachment:
                error_message += "Attachment successfully added. " if attach_result else "Failed to add attachment. "
            if param_update_fields:
                error_message += "Fields successfully updated." if update_result else "Failed to update fields."
            return action_result.set_status(phantom.APP_ERROR, f"{error_message} Error message: {action_result.get_message()}")

        return action_result.set_status(phantom.APP_SUCCESS, JIRA_SUCCESS_TICKET_UPDATED)

    def _delete_ticket(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))
        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        issue_id = param[JIRA_JSON_ID]

        try:
            issue = self._jira.issue(issue_id)
        except Exception as e:
            return self._set_jira_error(action_result, "Unable to find ticket info. Please make sure the issue exists", e)

        if not issue:
            return action_result.set_status(phantom.APP_ERROR, "Unable to find ticket info. Please make sure the issue exists")

        self.save_progress("Deleting the ticket")

        try:
            issue.delete()
        except Exception as e:
            return self._set_jira_error(action_result, "Unable to delete the ticket", e)

        return action_result.set_status(phantom.APP_SUCCESS, JIRA_SUCCESS_TICKET_DELETED)

    def _create_ticket(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        # get all the params for the issue
        project_key = param[JIRA_JSON_PROJECT_KEY]
        summary = param[JIRA_JSON_SUMMARY]
        issue_type = param[JIRA_JSON_ISSUE_TYPE]

        description = param.get(JIRA_JSON_DESCRIPTION, "")
        priority = param.get(JIRA_JSON_ISSUE_PRIORITY, "")
        attachment = param.get(JIRA_JSON_ATTACHMENT, "")

        assignee_username = param.get(JIRA_JSON_ISSUE_ASSIGNEE)

        assignee_account_id = param.get(JIRA_JSON_ISSUE_ASSIGNEE_ACCOUNT_ID)
        if assignee_username and assignee_account_id:
            return action_result.set_status(phantom.APP_ERROR, JIRA_ASSIGNEE_ERROR)

        param_fields = param.get(JIRA_JSON_FIELDS)
        fields = {}

        if param_fields:
            try:
                fields = json.loads(param_fields)
            except Exception as e:
                error_message = self._get_error_message_from_exception(e)
                error_fields_json_parse = JIRA_ERROR_FIELDS_JSON_PARSE.format(field_name=JIRA_JSON_FIELDS)
                error_text = f"{error_fields_json_parse} {error_message}"

                return action_result.set_status(phantom.APP_ERROR, error_text.replace("{", "(").replace("}", ")"))

            if "fields" in fields:
                if len(list(fields.keys())) > 1:
                    return action_result.set_status(phantom.APP_ERROR, JIRA_ERROR_INPUT_FIELDS_NOT_THE_ONLY_ONE)
                fields = fields["fields"]

        # update value in fields if not present in the json
        if project_key and ("project" not in fields):
            fields["project"] = {}
            fields["project"]["key"] = project_key

        if summary and ("summary" not in fields):
            fields["summary"] = summary

        if description and ("description" not in fields):
            fields["description"] = description

        if issue_type and ("issuetype" not in fields):
            fields["issuetype"] = {}
            fields["issuetype"]["name"] = issue_type

        if priority and ("priority" not in fields):
            fields["priority"] = {}
            fields["priority"]["name"] = priority

        self.debug_print("Creating the ticket")
        # Create JIRA ticket
        try:
            new_issue = self._jira.create_issue(fields=fields)
        except KeyError as ke:
            error_message = self._get_error_message_from_exception(ke)
            error_text = f"{JIRA_ERROR_CREATE_TICKET_FAILED}. Missing required key. {error_message}"

            return action_result.set_status(phantom.APP_ERROR, error_text)
        except Exception as e:
            return self._set_jira_error(action_result, JIRA_ERROR_CREATE_TICKET_FAILED, e)

        self.debug_print(JIRA_CREATED_TICKET)

        self.debug_print("Adding the attachment")
        attachment_status = self._add_attachment(new_issue, attachment)

        assignee_status = ""
        # now try to assign if required
        if (assignee_username is not None) or (assignee_account_id is not None):
            if assignee_username:
                self.debug_print("Assigning to user for Jira on-prem")
                try:
                    self._jira.assign_issue(new_issue, assignee_username)
                except Exception as e:
                    self.debug_print("Exception for assignee")

                    error_text = self._get_error_message_from_exception(e)
                    assignee_status = JIRA_ERROR_TICKET_ASSIGNMENT_FAILED.format(assignee_username, error_text)
            else:
                self.debug_print("Assigning to user for Jira cloud")
                endpoint = f"issue/{new_issue!s}/assignee"
                payload = {"accountId": assignee_account_id}
                try:
                    ret_val, _ = self._make_rest_call(endpoint, action_result, data=json.dumps(payload), method="put")
                except Exception as e:
                    error_text = self._get_error_message_from_exception(e)
                    assignee_status = JIRA_ERROR_TICKET_ASSIGNMENT_FAILED.format(assignee_account_id, error_text)

                if phantom.is_fail(ret_val):
                    assignee_status = JIRA_ERROR_TICKET_ASSIGNMENT_FAILED.format(assignee_account_id, action_result.get_message())

        issue_id = new_issue.key

        self.save_progress("Re-querying the ticket")

        ret_val = self._set_issue_data(issue_id, action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        status_message = JIRA_SUCCESS_TICKET_CREATED.format(id=new_issue.id, key=new_issue.key)

        result_data = action_result.get_data()[0]

        if assignee_status:
            status_message = f"{status_message} {assignee_status}"
            result_data["assign_error"] = assignee_status

        if attachment_status:
            status_message = f"{status_message} {attachment_status}"
            result_data["attach_error"] = attachment_status

        action_result.set_status(phantom.APP_SUCCESS, status_message)
        return action_result.get_status()

    def _list_tickets(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        # get all the params for the search issue
        project_key = param.get(JIRA_JSON_PROJECT_KEY)

        query = f"project={project_key}" if project_key else ""
        action_query = param.get(JIRA_JSON_QUERY, "")

        if not project_key and not action_query:
            error_text = JIRA_ERROR_LIST_TICKETS_FAILED + ". Please provide either project_key or query. Both fields cannot be empty"
            return action_result.set_status(phantom.APP_ERROR, error_text)

        start_index = param.get(JIRA_JSON_START_INDEX, DEFAULT_START_INDEX)
        start_index = self._validate_integers(action_result, start_index, "start_index action", allow_zero=True)
        if start_index is None:
            return action_result.get_status()

        limit = param.get(JIRA_JSON_MAX_RESULTS, DEFAULT_MAX_VALUE)
        limit = self._validate_integers(action_result, limit, "max_results action")

        if limit is None:
            return action_result.get_status()

        if action_query and query:
            query = f"{query} and {action_query}"
        elif action_query:
            query = action_query

        issues = self._paginator(query, action_result, start_index=start_index, limit=limit)

        if issues is None:
            return action_result.get_status()

        for issue in issues:
            issue_ar = phantom.ActionResult()

            ret_val = self._parse_issue_data(issue, issue_ar)

            if phantom.is_fail(ret_val):
                self.debug_print(f"Error occurred while parsing the issue data: {issue.key}. Error: {issue_ar.get_message()}")

            data = issue_ar.get_data()
            action_result.update_data(data)

        summary = action_result.update_summary({})
        summary[JIRA_TOTAL_ISSUES] = action_result.get_data_size()

        return action_result.set_status(phantom.APP_SUCCESS)

    def _username_paginator(self, username, action_result, start_index=0, limit=None):
        users_list = list()

        while True:
            try:
                users = self._jira.search_users(user=username, startAt=start_index, maxResults=DEFAULT_MAX_RESULTS_PER_PAGE)
            except Exception as e:
                self._set_jira_error(action_result, "Error occurred while fetching the list of users for Jira on-prem", e)
                return None

            if users is None:
                action_result.set_status(
                    phantom.APP_ERROR, "Unknown error occurred while fetching list of users using pagination for Jira on-prem"
                )
                return None

            users_list.extend(users)

            if limit and len(users_list) >= limit:
                return users_list[:limit]

            if len(users) < DEFAULT_MAX_RESULTS_PER_PAGE:
                break

            start_index = start_index + DEFAULT_MAX_RESULTS_PER_PAGE

        return users_list

    def _display_name_paginator(self, display_name, action_result, start_index=0, limit=None):
        users_list = list()
        param = dict()

        param.update(
            {
                "includeActive": True,
                "includeInactive": False,
                "maxResults": DEFAULT_MAX_RESULTS_PER_PAGE,
                "startAt": start_index,
                "query": f'displayName="{display_name}"',
            }
        )
        while True:
            try:
                ret_val, users = self._make_rest_call("user/search", action_result, params=param)
            except Exception as e:
                error_text = self._get_error_message_from_exception(e)

                action_result.set_status(
                    phantom.APP_ERROR, f"Error occurred while fetching the list of users for Jira cloud. Error: {error_text}"
                )
                return None

            if phantom.is_fail(ret_val):
                return None

            if users is None:
                action_result.set_status(
                    phantom.APP_ERROR, "Unknown error occurred while fetching list of users using pagination for Jira cloud"
                )
                return None

            users_list.extend(users)

            if limit and len(users_list) >= limit:
                return users_list[:limit]

            if len(users) < DEFAULT_MAX_RESULTS_PER_PAGE:
                break

            param.update({"startAt": start_index + DEFAULT_MAX_RESULTS_PER_PAGE})

        return users_list

    def _handle_search_users(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        # get all the params for the search issue
        username = param.get(JIRA_JSON_USERNAME)
        display_name = param.get(JIRA_JSON_DISPLAY_NAME)

        if (display_name and username) or (not display_name and not username):
            return action_result.set_status(phantom.APP_ERROR, JIRA_SEARCH_USERS_ERROR)

        start_index = 0

        limit = param.get(JIRA_JSON_MAX_RESULTS, DEFAULT_MAX_VALUE)
        limit = self._validate_integers(action_result, limit, "max_results action")
        if limit is None:
            return action_result.get_status()

        if display_name:
            users = self._display_name_paginator(display_name, action_result, start_index=start_index, limit=limit)
        else:
            users = self._username_paginator(username, action_result, start_index=start_index, limit=limit)

        if users is None:
            return action_result.get_status()

        try:
            for user in users:
                if display_name:
                    action_result.add_data(user)
                else:
                    action_result.add_data(user.raw)
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            return action_result.set_status(phantom.APP_ERROR, f"Error occurred while processing fetched response. Error: {error_text}")

        summary = action_result.update_summary({})
        summary[JIRA_TOTAL_USERS] = action_result.get_data_size()

        return action_result.set_status(phantom.APP_SUCCESS)

    def _add_comment_for_set_status(self, issue_id, issue, comment, action_result):
        """This method is used to add comment when we add comment while set status action.

        :rtype: string
        :param issue_id: Issue ID
        :param issue: Details of Issue
        :param comment: actual comment to be set
        :param action_result: action_result
        :return: status(phantom.APP_SUCCESS/phantom.APP_ERROR)
        """
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        update_body = {"update": {"comment": [{"add": {}}]}}
        comment_body = update_body["update"]["comment"][0]["add"]
        comment_body["body"] = comment

        ret_val, update_fields = self._get_update_fields({"update_fields": json.dumps(update_body)}, issue_id, action_result)

        error_message = action_result.get_message()
        if not error_message:
            error_message = ""

        if not ret_val and JIRA_ERROR_FETCH_CUSTOM_FIELDS not in error_message:
            return phantom.APP_ERROR

        if not self._add_update_fields(issue, update_fields, action_result):
            return phantom.APP_ERROR

        return action_result.set_status(phantom.APP_SUCCESS)

    def _add_comment(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        issue_id = param[JIRA_JSON_ID]

        body = param[JIRA_JSON_COMMENT]

        try:
            issue = self._jira.issue(issue_id)
        except Exception as e:
            return self._set_jira_error(action_result, "Unable to find ticket info. Please make sure the issue exists", e)

        if not issue:
            return action_result.set_status(phantom.APP_ERROR, "Unable to find ticket info. Please make sure the issue exists")

        try:
            self._jira.add_comment(issue_id, body, is_internal=param.get("internal", False))
        except Exception as e:
            return self._set_jira_error(action_result, "Failed to add the comment", e)

        return action_result.set_status(phantom.APP_SUCCESS, "Successfully added the comment")

    def _add_update_fields(self, issue, fields, action_result):
        if "fields" in fields:
            self.save_progress("Modifying the ticket using the 'fields' dictionary")
            try:
                issue.update(fields=fields["fields"])
                del fields["fields"]
            except Exception as e:
                return self._set_jira_error(action_result, JIRA_ERROR_UPDATE_FAILED, e)

        if "update" in fields:
            self.save_progress("Modifying the ticket with the 'update' dictionary")
            try:
                issue.update(update=fields["update"])
                del fields["update"]
            except Exception as e:
                return self._set_jira_error(action_result, JIRA_ERROR_UPDATE_FAILED, e)

        if fields:
            # There are still some keys present so update the issue some more
            self.save_progress("Modifying the ticket with the input dictionary")
            try:
                issue.update(fields)
            except Exception as e:
                return self._set_jira_error(action_result, JIRA_ERROR_UPDATE_FAILED, e)

        return phantom.APP_SUCCESS

    def _add_attachment(self, issue, vault_id):
        if not vault_id:
            return ""

        self.save_progress("Adding attachment to ticket")

        # Check for file in vault
        try:
            _, _, vault_meta = phantom_rules.vault_info(vault_id=vault_id)  # Vault IDs are unique
            if not vault_meta:
                self.debug_print(f"Error while fetching meta information for vault ID: {vault_id}")
                return JIRA_ERROR_FILE_NOT_IN_VAULT

        except Exception:
            return JIRA_ERROR_FILE_NOT_IN_VAULT

        file_meta = None
        try:
            for meta in vault_meta:
                if meta.get("container_id") == self.get_container_id():
                    file_meta = meta
                    break
            else:
                self.debug_print(f"Unable to find a file for the vault ID: '{vault_id}' in the container ID: '{self.get_container_id()}'")
        except Exception:
            self.debug_print(
                f"Error occurred while finding a file for the vault ID: '{vault_id}' in the container ID: '{self.get_container_id()}'"
            )
            self.debug_print("Considering the first file as the required file")
            file_meta = vault_meta[0]

        if not file_meta:
            self.debug_print(f"Unable to find a file for the vault ID: '{vault_id}' in the container ID: '{self.get_container_id()}'")
            self.debug_print("Considering the first file as the required file")
            file_meta = vault_meta[0]

        try:
            path = next(iter(vault_meta)).get("path")
            filename = file_meta["name"]

            try:
                self.debug_print("First attempt to add attachment to the given Jira ticket ID")
                with open(path, "rb") as f:
                    self._jira.add_attachment(issue=issue, attachment=f, filename=filename)
            except Exception as e:
                # Remove this block of exception handling once the PAPP-9898 bug is fixed
                self.debug_print("First attempt failed while adding attachment to the given Jira ticket ID")
                try:
                    # This failure might be happened because if we let pass the Unicode chars with filename
                    # into the add_attachment() method of Jira SDK, it throws 500 Internal Server Error
                    # and it will fail to add attachment on the Jira ticket.
                    self.debug_print("Try to remove non-ASCII Unicode chars from the filename")
                    modified_filename = filename.encode("ascii", "ignore").decode("ascii")
                    modified_filename = modified_filename.replace("\r", " ").replace("\n", " ")
                except Exception:
                    self.debug_print("Failed to remove non-ASCII Unicode chars from the filename")
                    modified_filename = filename

                # this condition will check that whether filename has Unicode chars or not, and if not it will re-thorw the same exception
                if len(modified_filename) < len(filename):
                    self.debug_print("Add prefix to filename after removing non-ASCII Unicode chars")
                    filename = f"FILENAME_ASCII_{modified_filename}"
                    with open(path, "rb") as f:
                        self._jira.add_attachment(issue=issue, attachment=f, filename=filename)
                else:
                    self.debug_print("Raise the same exception as filename doesn't have Unicode chars or unable to remove Unicode chars")
                    raise e

        except Exception as e:
            self.debug_print("Error while attaching")

            error_text = self._get_error_message_from_exception(e)
            return JIRA_ERROR_ATTACH_FAILED.format(error_text)

        return ""

    def _parse_issue_data(self, issue, action_result):
        try:
            # get the issue dict
            data = {}
            data[JIRA_JSON_NAME] = issue.key
            data[JIRA_JSON_ID] = issue.id
            issue_dict = issue.raw

            if "fields" in issue_dict:
                data["fields"] = issue_dict["fields"]

            data = action_result.add_data(data)
        except Exception:
            return action_result.set_status(phantom.APP_ERROR, "Unable to parse the response containing issue details from the server")

        try:
            data[JIRA_JSON_PRIORITY] = issue.fields.priority.name
        except Exception:
            pass

        try:
            data[JIRA_JSON_RESOLUTION] = issue.fields.resolution.name
        except Exception:
            data[JIRA_JSON_RESOLUTION] = "Unresolved"

        try:
            data[JIRA_JSON_STATUS] = issue.fields.status.name
        except Exception:
            pass

        try:
            data[JIRA_JSON_REPORTER] = issue.fields.reporter.displayName
        except Exception:
            pass

        try:
            data[JIRA_JSON_PROJECT_KEY] = issue.fields.project.key
        except Exception:
            pass

        try:
            data[JIRA_JSON_SUMMARY] = issue.fields.summary
        except Exception:
            pass

        try:
            data[JIRA_JSON_DESCRIPTION] = issue.fields.description
        except Exception:
            pass

        try:
            data[JIRA_JSON_ISSUE_TYPE] = issue.fields.issuetype.name
        except Exception:
            pass

        if not data.get("fields"):
            # No fields, so nothing more to do, we've already added the data
            return phantom.APP_SUCCESS

        custom_fields_by_name = self._fetch_fields_by_replacing_custom_fields_id_to_name(issue, action_result)

        if custom_fields_by_name is None:
            return phantom.APP_ERROR

        return phantom.APP_SUCCESS

    def _set_issue_data(self, issue_id, action_result):
        try:
            issue = self._jira.issue(issue_id)
        except Exception as e:
            return self._set_jira_error(action_result, JIRA_ERROR_GET_TICKET, e)

        return self._parse_issue_data(issue, action_result)

    def _get_ticket(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        issue_id = param[JIRA_JSON_ID]

        ret_val = self._set_issue_data(issue_id, action_result)

        error_message = ""
        if phantom.is_fail(ret_val):
            error_message = action_result.get_message()
            if not error_message:
                error_message = ""

            if JIRA_ERROR_FETCH_CUSTOM_FIELDS not in error_message:
                return action_result.get_status()
            else:
                error_message = error_message
        try:
            message = "The ticket has been retrieved successfully{}".format(
                f". Error while fetching custom fields: {error_message}" if error_message else ""
            )
        except Exception:
            message = "The ticket has been retrieved successfully"

        return action_result.set_status(phantom.APP_SUCCESS, message)

    def _get_container_id(self, issue_key):
        url = f'{self.get_phantom_base_url()}rest/container?_filter_source_data_identifier="{issue_key}"&_filter_asset={self.get_asset_id()}'

        try:
            r = requests.get(url, verify=False)  # nosemgrep
            resp_json = r.json()
        except Exception as e:
            self.debug_print("Unable to query JIRA ticket container: ", e)
            return None

        if resp_json.get("count", 0) <= 0:
            self.debug_print("No container matched")
            return None

        try:
            container_id = resp_json.get("data", [])[0]["id"]
        except Exception as e:
            self.debug_print("Container results are not proper: ", e)
            return None

        return container_id

    def _get_artifact_id(self, sdi, container_id, full_artifact=False):
        url = f'{self.get_phantom_base_url()}rest/artifact?_filter_source_data_identifier="{sdi}"&_filter_container_id={container_id}&sort=id&order=desc'

        try:
            r = requests.get(url, verify=False)  # nosemgrep
            resp_json = r.json()
        except Exception as e:
            self.debug_print("Unable to query JIRA artifact: ", e)
            return None

        if resp_json.get("count", 0) <= 0:
            self.debug_print("No artifact matched")
            return None

        try:
            if full_artifact:
                previous_artifacts_list = resp_json.get("data", [])
                return previous_artifacts_list[0]
            else:
                return resp_json.get("data", [])[0]["id"]
        except Exception as e:
            self.debug_print("Artifact results are not proper: ", e)
            return None

    def _get_custom_fields_id_name_map(self, issue_id, action_result, id_to_name=True):
        custom_fields_id_name_map = dict()

        # get custom fields info
        ret_val, custom_fields_info, fields_meta = self._get_custom_fields_for_issue(issue_id, action_result)

        # Can't replace the custom fields, but the data has been set so the user can continue
        if phantom.is_fail(ret_val):
            message = action_result.get_message()
            action_result.set_status(phantom.APP_ERROR, f"{JIRA_ERROR_FETCH_CUSTOM_FIELDS}. Error message: {message}")
            return None

        if not custom_fields_info:
            return custom_fields_id_name_map

        if id_to_name:
            return dict([(x, fields_meta[x]["name"]) for x in custom_fields_info])
        else:
            return dict([(fields_meta[x]["name"], x) for x in custom_fields_info])

    def _fetch_fields_by_replacing_custom_fields_id_to_name(self, issue, action_result):
        custom_id_to_name = self._get_custom_fields_id_name_map(issue.key, action_result)

        try:
            issue_dict = issue.raw
            fields = issue_dict.get("fields")
        except Exception:
            action_result.set_status(phantom.APP_ERROR, f"Error occurred while fetching the fields from the issue: {issue.key}")
            return None

        if not custom_id_to_name:
            return fields

        ret_val, fields, _ = self._replace_custom_id_with_name(fields, custom_id_to_name, action_result)

        if phantom.is_fail(ret_val):
            return None

        return fields

    def _build_fields_artifact(self, issue, container_id, action_result):
        artifact_json = {}

        artifact_json["container_id"] = container_id
        artifact_json["source_data_identifier"] = issue.key

        try:
            artifact_json["label"] = issue.fields.issuetype.name
        except Exception:
            artifact_json["label"] = "issue"

        artifact_cef = {}

        try:
            artifact_cef[JIRA_JSON_UPDATED_AT] = issue.fields.updated
        except Exception:
            pass

        try:
            artifact_cef[JIRA_JSON_PRIORITY] = issue.fields.priority.name
        except Exception:
            pass

        try:
            artifact_cef[JIRA_JSON_RESOLUTION] = issue.fields.resolution.name
        except Exception:
            artifact_cef[JIRA_JSON_RESOLUTION] = JIRA_JSON_UNRESOLVED

        try:
            artifact_cef[JIRA_JSON_STATUS] = issue.fields.status.name
        except Exception:
            pass

        try:
            artifact_cef[JIRA_JSON_REPORTER] = issue.fields.reporter.displayName
        except Exception:
            pass

        try:
            artifact_cef[JIRA_JSON_PROJECT_KEY] = issue.fields.project.key
        except Exception:
            pass

        try:
            artifact_cef[JIRA_JSON_SUMMARY] = issue.fields.summary
        except Exception:
            pass

        try:
            artifact_cef[JIRA_JSON_DESCRIPTION] = issue.fields.description
        except Exception:
            pass

        try:
            artifact_cef[JIRA_JSON_ISSUE_TYPE] = issue.fields.issuetype.name
        except Exception:
            pass

        if self._custom_fields_list:
            custom_fields_by_name = self._fetch_fields_by_replacing_custom_fields_id_to_name(issue, action_result)

            if custom_fields_by_name is None:
                return None

            for custom_field in self._custom_fields_list:
                try:
                    artifact_cef[custom_field] = custom_fields_by_name[custom_field]
                except Exception:
                    pass

        artifact_json["cef"] = artifact_cef

        return artifact_json

    def _download_file(self, url, local_file_path):
        self.debug_print("Downloading from: ", url)

        config = self.get_config()
        auth = (config[phantom.APP_JSON_USERNAME], config[phantom.APP_JSON_PASSWORD])

        try:
            r = requests.get(url, verify=self.get_config().get("verify_server_cert"), stream=True, auth=auth)  # nosemgrep
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            self.debug_print("Could not connect to url to download attachment: ", error_text)
            return phantom.APP_ERROR

        if not r:
            # GET failed
            self.debug_print(f"Error downloading file. Server returned with status code: {r.status_code}")
            return phantom.APP_ERROR

        bytes_downloaded = 0
        block_size = 512 * 1024

        try:
            with open(local_file_path, "wb") as file_handle:
                for chunk in r.iter_content(chunk_size=block_size):
                    if chunk:
                        bytes_downloaded += len(chunk)
                        file_handle.write(chunk)
                        file_handle.flush()
                        os.fsync(file_handle.fileno())
                        self.send_progress(f"Downloaded {bytes_downloaded} bytes")
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            self.debug_print(f"Error downloading file: {error_text}")
            return phantom.APP_ERROR

        os.chmod(local_file_path, 0o660)  # nosemgrep

        return phantom.APP_SUCCESS

    def _handle_attachment(self, attachment, container_id, artifact_list, action_result):
        try:
            if hasattr(Vault, "get_vault_tmp_dir"):
                tmp = tempfile.NamedTemporaryFile(dir=Vault.get_vault_tmp_dir(), delete=False)
            else:
                local_dir = os.path.join(paths.PHANTOM_VAULT, "tmp")
                tmp = tempfile.NamedTemporaryFile(dir=local_dir, delete=False)

            ret_val = self._download_file(attachment.content, tmp.name)

            if phantom.is_fail(ret_val):
                return phantom.APP_ERROR

            filename = attachment.filename

            success, message, vault_id = phantom_rules.vault_add(file_location=tmp.name, container=container_id, file_name=filename)

            if not success:
                self.debug_print("Error saving file to vault: ", message)
                return phantom.APP_ERROR

            artifact_json = {}

            artifact_json["name"] = f"attachment - {filename}"
            artifact_json["label"] = "attachment"
            artifact_json["container_id"] = container_id
            artifact_json["source_data_identifier"] = attachment.id

            artifact_cef = {}

            artifact_cef["size"] = attachment.size
            artifact_cef["created"] = attachment.created
            artifact_cef["filename"] = filename
            artifact_cef["mimeType"] = attachment.mimeType

            try:
                artifact_cef["author"] = attachment.author.name
                artifact_cef["author_account_id"] = None
                artifact_cef["is_on_prem"] = True
            except Exception:
                self.debug_print(
                    "Error occurred while fetching author name as server is Jira cloud. \
                    So try to fetch author display name and account ID"
                )
                artifact_cef["author_account_id"] = attachment.author.accountId
                artifact_cef["author"] = attachment.author.displayName
                artifact_cef["is_on_prem"] = False

            artifact_cef["vault_id"] = vault_id

            artifact_json["cef"] = artifact_cef

            artifact_list.append(artifact_json)
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            action_result.set_status(phantom.APP_ERROR, f"Error occurred while creation of the attachment artifact. Error message: {error_text}")
            return phantom.APP_ERROR

        return phantom.APP_SUCCESS

    def _handle_comment(self, comment, container_id, base_name, artifact_list, action_result):
        try:
            artifact_json = {}

            try:
                author = comment.author.name
                updateAuthor = comment.updateAuthor.name
                author_account_id = None
                updateAuthor_account_id = None
                is_on_prem = True
            except Exception:
                self.debug_print(
                    "Error occurred while fetching author name as server is Jira cloud. \
                    So try to fetch author display name and account ID"
                )
                author = comment.author.displayName
                updateAuthor = comment.updateAuthor.displayName
                author_account_id = comment.author.accountId
                updateAuthor_account_id = comment.updateAuthor.accountId
                is_on_prem = False

            artifact_json["name"] = f"{base_name} by {author}"
            artifact_json["label"] = "comment"
            artifact_json["container_id"] = container_id
            artifact_json["source_data_identifier"] = comment.id

            artifact_cef = {}

            artifact_cef["body"] = comment.body
            artifact_cef["created"] = comment.created
            artifact_cef["updated"] = comment.updated
            artifact_cef["is_on_prem"] = is_on_prem
            artifact_cef["author"] = author
            artifact_cef["author_account_id"] = author_account_id
            artifact_cef["updateAuthor"] = updateAuthor
            artifact_cef["updateAuthor_account_id"] = updateAuthor_account_id

            artifact_json["cef"] = artifact_cef

            artifact_list.append(artifact_json)
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            action_result.set_status(phantom.APP_ERROR, f"Error occurred while creation of the comment artifact. Error message: {error_text}")
            return phantom.APP_ERROR

        return phantom.APP_SUCCESS

    def _paginator(self, jql_query, action_result, start_index=0, limit=None, fields=False):
        issues_list = list()

        while True:
            try:
                if fields:
                    issues = self._jira.search_issues(
                        jql_str=jql_query, startAt=start_index, maxResults=DEFAULT_MAX_RESULTS_PER_PAGE, fields="updated"
                    )
                else:
                    issues = self._jira.search_issues(jql_str=jql_query, startAt=start_index, maxResults=DEFAULT_MAX_RESULTS_PER_PAGE)
            except Exception as e:
                self._set_jira_error(action_result, "Error occurred while fetching the list of tickets (issues)", e)
                return None

            if issues is None:
                action_result.set_status(phantom.APP_ERROR, "Unknown error occurred while fetching list of tickets (issues) using pagination")
                return None

            issues_list.extend(issues)
            if limit and len(issues_list) >= limit:
                return issues_list[:limit]

            if len(issues) < DEFAULT_MAX_RESULTS_PER_PAGE:
                break

            start_index = start_index + DEFAULT_MAX_RESULTS_PER_PAGE

        return issues_list

    def _handle_link_tickets(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        from_issue = param[JIRA_JSON_FROM_ID]
        to_issue = param[JIRA_JSON_TO_ID]
        link_type = param[JIRA_JSON_LINK_TYPE]

        comment_body = param.get(JIRA_JSON_COMMENT, "")

        comment_vis_type = param.get(JIRA_JSON_COMMENT_VISIBILITY_TYPE)
        comment_vis_value = param.get(JIRA_JSON_COMMENT_VISIBILITY)
        comment = None

        try:
            UnicodeDammit(link_type).unicode_markup.encode("utf-8")
        except Exception:
            return action_result.set_status(phantom.APP_ERROR, "'link_type' action parameter value failed validation. Enter a valid value")

        if comment_body:
            comment = {"body": comment_body, "visibility": {"type": comment_vis_type, "value": comment_vis_value}}

        try:
            link = self._jira.create_issue_link(link_type, from_issue, to_issue, comment)
            self.save_progress(f"Response from server:{link}")
        except Exception as e:
            return self._set_jira_error(action_result, "Failed to link the issues", e)

        action_result.add_data({"result": "success"})

        return action_result.set_status(phantom.APP_SUCCESS, "The ticket has been linked successfully")

    def _handle_add_watcher(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        issue_id = param[JIRA_JSON_ISSUE_ID]
        username = param.get(JIRA_JSON_WATCHER)
        account_id = param.get(JIRA_JSON_USER_ACCOUNT_ID)

        if (account_id and username) or (not account_id and not username):
            return action_result.set_status(phantom.APP_ERROR, JIRA_WATCHERS_ERROR)

        ret_val, watchers = self.get_watchers_list(action_result, issue_id, True if username else False)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        if (username and username in watchers) or (account_id and account_id in watchers):
            return action_result.set_status(phantom.APP_SUCCESS, f"The given user already exists in the watchers list of the issue: {issue_id}")

        user = username if username else account_id

        try:
            self._jira.add_watcher(issue_id, user)
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            error = f"Response from the server: {error_text}"
            self.save_progress(error)
            return action_result.set_status(phantom.APP_ERROR, f"Failed to add the watcher. Please check the provided parameters. {error}")

        return action_result.set_status(phantom.APP_SUCCESS, f"Successfully added the user to the watchers list of the issue ID: {issue_id}")

    def get_watchers_list(self, action_result, issue_id, flag=False):
        try:
            response = self._jira.watchers(issue_id)
        except Exception as e:
            self._set_jira_error(action_result, "Error occurred while fetching the watchers list", e)

            self.debug_print("Error occurred while fetching the watchers list")
            return action_result.get_status(), None

        watcher_list = list()
        watchers = response.raw.get("watchers", [])

        try:
            for watcher in watchers:
                if flag:
                    watcher_list.append(watcher["name"])
                else:
                    watcher_list.append(watcher["accountId"])
        except KeyError:
            return action_result.set_status(phantom.APP_ERROR, JIRA_WATCHERS_ERROR), None
        except Exception as e:
            error_message = self._get_error_message_from_exception(e)
            error_text = f"Error occurred while fetching the watchers list. {error_message}"

            self.save_progress(f"Response from the server: {error_text}")
            return action_result.set_status(phantom.APP_ERROR, error_text), None

        return phantom.APP_SUCCESS, watcher_list

    def _handle_remove_watcher(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        issue_id = param[JIRA_JSON_ISSUE_ID]
        username = param.get(JIRA_JSON_WATCHER)
        account_id = param.get(JIRA_JSON_USER_ACCOUNT_ID)

        if (account_id and username) or (not account_id and not username):
            return action_result.set_status(phantom.APP_ERROR, JIRA_WATCHERS_ERROR)

        ret_val, watchers = self.get_watchers_list(action_result, issue_id, True if username else False)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        if not watchers:
            return action_result.set_status(phantom.APP_ERROR, f"No watchers found in the issue ID: {issue_id}")

        if (username and username not in watchers) or (account_id and account_id not in watchers):
            return action_result.set_status(phantom.APP_SUCCESS, f"The given user is not found in the watchers list of the issue: {issue_id}")

        try:
            if username:
                self._jira.remove_watcher(issue_id, username)
            else:
                param = {"accountId": account_id}
                ret_val, _ = self._make_rest_call(f"issue/{issue_id}/watchers", action_result, params=param, method="delete")
                if phantom.is_fail(ret_val):
                    return action_result.get_status()
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            ERROR = f"Response from the server: {error_text}"
            self.save_progress(ERROR)
            return action_result.set_status(phantom.APP_ERROR, f"Failed to remove the watcher. Please check the provided parameters. {ERROR}")

        return action_result.set_status(phantom.APP_SUCCESS, f"Successfully removed the user from the watchers list of the issue ID: {issue_id}")

    def _write_in_file(self, action_result, attachment, full_path, container_id):
        try:
            with open(full_path, "wb") as f:
                attachment_content = attachment.get()
                f.write(attachment_content)

            success, message, vault_id = phantom_rules.vault_add(file_location=full_path, container=container_id)
            action_result.add_data({"vault_id": vault_id})

            if not success:
                error_message = message
                return action_result.set_status(
                    phantom.APP_ERROR,
                    "Error saving file to vault: {}".format(error_message if error_message else "Could not save file to vault"),
                )

        except Exception as e:
            error_message = self._get_error_message_from_exception(e)
            error_text = f"Unable to ingest attachments. {error_message}"
            return action_result.set_status(phantom.APP_ERROR, error_text)

        return phantom.APP_SUCCESS

    def _handle_get_attachments(self, param):
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        ticket_key = param["id"]
        container_id = param["container_id"]
        extension_filter = param.get("extension_filter", "")
        get_all_attachments = param.get("retrieve_all", False)

        # removing extra comma from an extension filter string
        types = [x.strip() for x in extension_filter.split(",")]
        types = list(filter(None, types))
        extension_filter = ",".join(types)

        try:
            jira_issue = self._jira.issue(ticket_key, expand="attachment")
        except Exception as e:
            return self._set_jira_error(action_result, "Please enter a valid Jira Ticket ID. Please check the provided parameters", e)

        try:
            if len(jira_issue.fields.attachment) > 0:
                ingest_file_count = 0
                temp_vault_path = Vault.get_vault_tmp_dir().rstrip("/")

                extension_list = None

                if extension_filter:
                    extension_list = extension_filter.split(",")
                    extension_list = [".{}".format(extension.lstrip(".")) for extension in extension_list]

                elif not get_all_attachments:
                    error = "Please select retrieve all or pass in a list of extensions to look for. Please check the provided parameters"
                    return action_result.set_status(phantom.APP_ERROR, error)

                for attachment in jira_issue.fields.attachment:
                    jira_filename = "".join(attachment.filename.split())

                    full_path = f"{temp_vault_path}/{jira_filename}"

                    if not self._is_safe_path(temp_vault_path, full_path):
                        return action_result.set_status(phantom.APP_ERROR, JIRA_ERROR_INVALID_FILE_PATH)

                    if extension_filter:
                        file_extension = ".{}".format(jira_filename.rsplit(".")[-1])
                        if file_extension not in extension_list:
                            continue

                    ret_val = self._write_in_file(action_result, attachment, full_path, container_id)
                    if phantom.is_fail(ret_val):
                        return action_result.get_status()
                    ingest_file_count += 1

                message = f"Successfully retrieved {ingest_file_count} attachments of {len(jira_issue.fields.attachment)} total attachments from Jira ticket- {ticket_key}"
                return action_result.set_status(phantom.APP_SUCCESS, message)

            else:
                return action_result.set_status(
                    phantom.APP_SUCCESS, "Please check the Jira Ticket ID. This issue has no attachments. Please check the provided parameters"
                )
        except Exception as e:
            error_message = self._get_error_message_from_exception(e)
            error_text = f"Unable to get attachments. {error_message}"
            return action_result.set_status(phantom.APP_ERROR, error_text)

    def _update_container(self, issue, container_id, last_time, action_result):
        update_json = {}
        update_json["data"] = issue.raw
        update_json["description"] = issue.fields.summary

        url = f"{self.get_phantom_base_url()}rest/container/{container_id}"

        try:
            r = requests.post(url, data=json.dumps(update_json), verify=False)  # nosemgrep
            resp_json = r.json()
        except Exception as e:
            error_text = self._get_error_message_from_exception(e)
            self.debug_print("Error while updating the container. ", error_text)
            action_result.set_status(
                phantom.APP_ERROR, f"Error occurred while updating the container for the issue key: {issue.key}. {error_text}"
            )
            return phantom.APP_ERROR

        if r.status_code != 200 or resp_json.get("failed"):
            self.debug_print("Error while updating the container. Error is: ", resp_json.get("failed"))
            action_result.set_status(
                phantom.APP_ERROR,
                "Error occurred while updating the container for the issue key: {}. Error message: {}".format(
                    issue.key, resp_json.get("failed")
                ),
            )
            return phantom.APP_ERROR

        artifact_list = []

        try:
            for attachment in issue.fields.attachment:
                if not self._get_artifact_id(attachment.id, container_id):
                    ret_val = self._handle_attachment(attachment, container_id, artifact_list, action_result)

                    if phantom.is_fail(ret_val):
                        self.debug_print(f"Issue key: {issue.key}. {action_result.get_message()}")
                        self.save_progress(f"Issue key: {issue.key}. {action_result.get_message()}")
                        return phantom.APP_ERROR
        except Exception:
            pass

        try:
            for comment in issue.fields.comment.comments:
                full_artifact = self._get_artifact_id(comment.id, container_id, full_artifact=True)

                if not full_artifact:
                    ret_val = self._handle_comment(
                        comment, container_id, "{}_{}".format("comment", comment.updated), artifact_list, action_result
                    )

                    if phantom.is_fail(ret_val):
                        self.debug_print(f"Issue key: {issue.key}. {action_result.get_message()}")
                        self.save_progress(f"Issue key: {issue.key}. {action_result.get_message()}")
                        return phantom.APP_ERROR

                    continue

                # Comparing current updated time of comment with the already existing comment artifact
                # 1. Fetch the current comment's updated time and convert it to UTC
                comment_current_updated_time = comment.updated
                comment_current_updated_time_jira_server_tz_specific = parse(comment_current_updated_time)
                comment_current_updated_time_utc_tz_specific = comment_current_updated_time_jira_server_tz_specific.astimezone(dateutil.tz.UTC)

                # 2. Fetch the current comment's artifact's updated time and convert it to UTC
                comment_artifact_current_updated_time = full_artifact.get("cef", {}).get("updated")

                if comment_artifact_current_updated_time:
                    comment_artifact_updated_time_jira_server_tz_specific = parse(comment_artifact_current_updated_time)
                    comment_artifact_updated_time_utc_tz_specific = comment_artifact_updated_time_jira_server_tz_specific.astimezone(
                        dateutil.tz.UTC
                    )

                # By default, we won't create the artifact for current comment
                # to avoid duplicate artifacts for comments even if the fields are updated for the ticket
                create_updated_comment_artifact_not_req = False

                if str(comment_current_updated_time_utc_tz_specific) == str(comment_artifact_updated_time_utc_tz_specific):
                    create_updated_comment_artifact_not_req = True

                if self.is_poll_now() or not comment_artifact_current_updated_time or not create_updated_comment_artifact_not_req:
                    ret_val = self._handle_comment(
                        comment, container_id, "{}_{}".format("comment", comment.updated), artifact_list, action_result
                    )

                    if phantom.is_fail(ret_val):
                        self.debug_print(f"Issue key: {issue.key}. {action_result.get_message()}")
                        self.save_progress(f"Issue key: {issue.key}. {action_result.get_message()}")
                        return phantom.APP_ERROR

        except Exception:
            pass

        artifact_json = self._build_fields_artifact(issue, container_id, action_result)

        if artifact_json is None:
            return phantom.APP_ERROR

        artifact_json["name"] = "{}_{}".format("ticket fields", issue.fields.updated)

        artifact_list.append(artifact_json)

        if artifact_list:
            ret_val, message, resp = self.save_artifacts(artifact_list)

            if not ret_val:
                self.debug_print("Error saving the artifact: ", message)
                action_result.set_status(phantom.APP_ERROR, "Error occurred while saving the artifact. Error message: {0}", message)
                return phantom.APP_ERROR

        return phantom.APP_SUCCESS

    def _save_issue(self, issue, last_time, action_result):
        container_id = self._get_container_id(issue.key)

        if container_id:
            # Ticket has already been ingested. Need to update its container.
            ret_val = self._update_container(issue, container_id, last_time, action_result)

            if phantom.is_fail(ret_val):
                return phantom.APP_ERROR

            return phantom.APP_SUCCESS

        # Build the container JSON
        container_json = {}
        container_json["name"] = issue.key
        container_json["data"] = issue.raw
        container_json["description"] = issue.fields.summary
        container_json["source_data_identifier"] = issue.key
        container_json["label"] = self.get_config().get("ingest", {}).get("container_label")

        # Save the container
        ret_val, message, container_id = self.save_container(container_json)

        if not ret_val:
            return phantom.APP_ERROR

        artifact_list = []

        # Check for and save attachments as artifacts
        try:
            for attachment in issue.fields.attachment:
                ret_val = self._handle_attachment(attachment, container_id, artifact_list, action_result)

                if phantom.is_fail(ret_val):
                    self.debug_print(f"Issue key: {issue.key}. {action_result.get_message()}")
                    self.save_progress(f"Issue key: {issue.key}. {action_result.get_message()}")
                    return phantom.APP_ERROR
        except Exception:
            pass

        # Check for and save comments as artifacts
        try:
            for comment in issue.fields.comment.comments:
                ret_val = self._handle_comment(comment, container_id, "{}_{}".format("comment", comment.updated), artifact_list, action_result)

                if phantom.is_fail(ret_val):
                    self.debug_print(f"Issue key: {issue.key}. {action_result.get_message()}")
                    self.save_progress(f"Issue key: {issue.key}. {action_result.get_message()}")
                    return phantom.APP_ERROR
        except Exception:
            pass

        # Create the main artifact of the container that will hold the ticket's fields
        artifact_json = self._build_fields_artifact(issue, container_id, action_result)

        if artifact_json is None:
            return phantom.APP_ERROR

        artifact_json["name"] = "{}_{}".format("ticket fields", issue.fields.updated)

        artifact_list.append(artifact_json)

        ret_val, message, resp = self.save_artifacts(artifact_list)

        if not ret_val:
            return phantom.APP_ERROR

        return phantom.APP_SUCCESS

    def _on_poll(self, param):
        # Add action result
        action_result = self.add_action_result(phantom.ActionResult(dict(param)))

        # Progress
        self.save_progress(JIRA_USING_BASE_URL, base_url=self._base_url)

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Create the jira object
        if phantom.is_fail(self._create_jira_object(action_result)):
            return action_result.get_status()

        # Check for load_state API, use it if it is present
        if hasattr(self, "load_state"):
            state = self.load_state()
        else:
            state = self._load_state()

        # Get config
        config = self.get_config()

        if not state:
            self.debug_print(JIRA_ERROR_STATE_FILE_CORRUPT_ERROR)
            self.save_progress(JIRA_ERROR_STATE_FILE_CORRUPT_ERROR)
            state = {"app_version": self.get_app_json().get("app_version")}
            if hasattr(self, "save_state"):
                self.save_state(state)
            else:
                self._save_state(state)
            return action_result.set_status(phantom.APP_ERROR, JIRA_ERROR_STATE_FILE_CORRUPT_ERROR)

        # Get time from last poll, save now as time for this poll
        last_time = state.get("last_time", 0)

        # This is to handle the cases if the end-user has by-mistake kept the state file status as
        # {'app_version': '<app_version>', 'last_time': ''} or {'app_version': '<app_version>', 'last_time': null} or
        # there was an issue in storing the 'last_time' key-value into the state file during the first scheduled poll run.
        # In such cases, we will continue similar to the scenario of first run of the scheduled poll.
        # We never know what the end-user can change the value of the state file to. Hence, handling such edge cases here.
        if not last_time:
            last_time = 0

        try:
            # Shifting the last_time by one minute to ensure that
            # the tickets are not missed in the On Poll due to
            # a minute's granularity of the Jira
            last_time = int(last_time)
            last_time = last_time - 60

            if last_time < 0:
                last_time = 0

            # Updating the timestamp based on the timezone mentioned
            # in the asset configuration parameters
            ts_dt = datetime.fromtimestamp(last_time)
            ts_dt_local_tzinfo = ts_dt.replace(tzinfo=dateutil.tz.tzlocal())

            timez = pytz.timezone(self._timezone)
            ts_dt_jira_ui_tzinfo = ts_dt_local_tzinfo.astimezone(timez)
            last_time_str = ts_dt_jira_ui_tzinfo.strftime(JIRA_TIME_FORMAT)

        except Exception:
            return action_result.set_status(
                phantom.APP_ERROR,
                "Error occurred while parsing the last ingested ticket's (issue's) 'updated' timestamp from the previous ingestion run",
            )

        # Build the query for the issue search
        query = ""

        try:
            project_key = config.get(JIRA_JSON_PROJECT_KEY, "")
        except Exception:
            return action_result.set_status(phantom.APP_ERROR, "Please provide a valid project key")

        if project_key:
            query = f"project={project_key}"

        action_query = config.get(JIRA_JSON_QUERY, "")

        if len(action_query) > 0:
            query = "{}{}{}".format(query, " and " if query else "", action_query)

        # If it's a poll now don't filter based on update time
        if self.is_poll_now():
            max_tickets = param.get(phantom.APP_JSON_CONTAINER_COUNT)

        # If it's the first poll, don't filter based on update time
        elif state.get("first_run", True):
            max_tickets = int(config.get("first_run_max_tickets", DEFAULT_SCHEDULED_INTERVAL_INGESTION_COUNT))
            max_tickets = self._validate_integers(action_result, max_tickets, "first_run_max_tickets config")
            if max_tickets is None:
                return action_result.get_status()

        # If it's scheduled polling add a filter for update time being greater than the last poll time
        else:
            max_tickets = int(config.get("max_tickets", DEFAULT_SCHEDULED_INTERVAL_INGESTION_COUNT))
            max_tickets = self._validate_integers(action_result, max_tickets, "max_tickets config")
            if max_tickets is None:
                return action_result.get_status()
            query = '{}{}updated>="{}"'.format(query, " and " if query else "", last_time_str)

        # Order by update time
        query = "{} order by updated asc".format(query if query else "")

        try:
            self.debug_print(f"JQL Query: {query}")
            self.save_progress(f"JQL Query: {query}")
        except Exception:
            self.debug_print("Error occurred while logging the value of JQL query, continuing the on poll execution")
            self.save_progress("Error occurred while logging the value of JQL query, continuing the on poll execution")

        # Query for issues
        issues = self._paginator(query, action_result, limit=max_tickets, fields=True)

        if issues is None:
            return action_result.get_status()

        try:
            self.save_progress(f"Total issues fetched: {len(issues)}")
            self.debug_print(f"Total issues fetched: {len(issues)}")
        except Exception:
            self.debug_print("Error occurred while logging the value of total issues fetched, continuing the on poll execution")
            self.save_progress("Error occurred while logging the value of total issues fetched, continuing the on poll execution")

        # Ingest the issues
        failed = 0
        for issue in issues:
            if not self._save_issue(self._jira.issue(issue.key), last_time, action_result):
                failed += 1

        if not self.is_poll_now() and issues:
            last_fetched_issue = self._jira.issue(issues[-1].key)
            last_time_jira_server_tz_specific = parse(last_fetched_issue.fields.updated)
            last_time_phantom_server_tz_specific = last_time_jira_server_tz_specific.astimezone(dateutil.tz.tzlocal())
            state["last_time"] = time.mktime(last_time_phantom_server_tz_specific.timetuple())

            try:
                self.debug_print(f"State File: {state!s}")
                self.debug_print(f"Last fetched Jira ticket: {issues[-1].key}")
            except Exception:
                self.debug_print(
                    "Error occurred while logging the value of state file and last fetched Jira ticket, \
                    continuing the on poll execution"
                )

        # Mark the first_run as False once the scheduled or ingestion polling
        # first run or every run has been successfully completed
        if not self.is_poll_now():
            state["first_run"] = False

        # Check for save_state API, use it if it is present
        if hasattr(self, "save_state"):
            self.save_state(state)
        else:
            self._save_state(state)

        if failed:
            return action_result.set_status(phantom.APP_ERROR, JIRA_ERROR_FAILED)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _validate_integers(self, action_result, parameter, key, allow_zero=False):
        """This function is a validation function to check if the provided input parameter value
        is a non-zero positive integer and returns the integer value of the parameter itself.
        :param action_result: Action result object
        :param parameter: input parameter
        :return: integer value of the parameter
        """

        try:
            parameter = int(parameter)

            if parameter <= 0:
                if allow_zero:
                    if parameter < 0:
                        action_result.set_status(phantom.APP_ERROR, JIRA_LIMIT_VALIDATION_ALLOW_ZERO_MESSAGE.format(parameter=key))
                        return None
                else:
                    action_result.set_status(phantom.APP_ERROR, JIRA_LIMIT_VALIDATION_MESSAGE.format(parameter=key))
                    return None
        except Exception:
            error_text = (
                JIRA_LIMIT_VALIDATION_ALLOW_ZERO_MESSAGE.format(parameter=key)
                if allow_zero
                else JIRA_LIMIT_VALIDATION_MESSAGE.format(parameter=key)
            )
            action_result.set_status(phantom.APP_ERROR, error_text)
            return None

        return parameter

    def handle_action(self, param):
        """Function that handles all the actions
        Args:
        Return:
            A status code
        """

        # Get the action that we are supposed to execute for this App Run
        action = self.get_action_identifier()
        action_execution_status = phantom.APP_SUCCESS

        self.debug_print("action_id", self.get_action_identifier())

        # Dictionary mapping each action with its corresponding actions
        action_mapping = {
            phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY: self._test_connectivity,
            self.ACTION_ID_CREATE_TICKET: self._create_ticket,
            self.ACTION_ID_LIST_PROJECTS: self._list_projects,
            self.ACTION_ID_LIST_TICKETS: self._list_tickets,
            self.ACTION_ID_GET_TICKET: self._get_ticket,
            self.ACTION_ID_UPDATE_TICKET: self._update_ticket,
            self.ACTION_ID_DELETE_TICKET: self._delete_ticket,
            self.ACTION_ID_SET_TICKET_STATUS: self._set_ticket_status,
            self.ACTION_ID_ADD_COMMENT: self._add_comment,
            self.ACTION_ID_LINK_TICKETS: self._handle_link_tickets,
            self.ACTION_ID_ADD_WATCHER: self._handle_add_watcher,
            self.ACTION_ID_REMOVE_WATCHER: self._handle_remove_watcher,
            self.ACTION_ID_ON_POLL: self._on_poll,
            self.ACTION_ID_GET_ATTACHMENTS: self._handle_get_attachments,
            self.ACTION_ID_SEARCH_USERS: self._handle_search_users,
        }

        if action in list(action_mapping.keys()):
            action_function = action_mapping[action]
            action_execution_status = action_function(param)

        return action_execution_status


if __name__ == "__main__":
    import argparse

    import pudb

    pudb.set_trace()

    argparser = argparse.ArgumentParser()

    argparser.add_argument("input_test_json", help="Input Test JSON file")
    argparser.add_argument("-u", "--username", help="username", required=False)
    argparser.add_argument("-p", "--password", help="password", required=False)
    argparser.add_argument("-v", "--verify", action="store_true", help="verify", required=False, default=False)

    args = argparser.parse_args()
    session_id = None

    username = args.username
    password = args.password
    verify = args.verify

    if username is not None and password is None:
        # User specified a username but not a password, so ask
        import getpass

        password = getpass.getpass("Password: ")

    if username and password:
        try:
            print("Accessing the Login page")
            r = requests.get(phantom.BaseConnector._get_phantom_base_url() + "login", verify=verify, timeout=JIRA_DEFAULT_TIMEOUT)
            csrftoken = r.cookies["csrftoken"]

            data = dict()
            data["username"] = username
            data["password"] = password
            data["csrfmiddlewaretoken"] = csrftoken

            headers = dict()
            headers["Cookie"] = "csrftoken=" + csrftoken
            headers["Referer"] = phantom.BaseConnector._get_phantom_base_url() + "login"

            print("Logging into Platform to get the session id")
            r2 = requests.post(
                phantom.BaseConnector._get_phantom_base_url() + "login", verify=verify, data=data, headers=headers, timeout=JIRA_DEFAULT_TIMEOUT
            )
            session_id = r2.cookies["sessionid"]
        except Exception as e:
            print("Unable to get session id from the platform. Error: " + str(e))
            sys.exit(1)

    with open(args.input_test_json) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = JiraConnector()
        connector.print_progress_message = True

        if session_id is not None:
            in_json["user_session_token"] = session_id
            connector._set_csrf_info(csrftoken, headers["Referer"])

        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)
