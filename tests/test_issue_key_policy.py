# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONNECTOR = ROOT / "jira_connector.py"
VALIDATED_HANDLERS = {
    "_set_ticket_status",
    "_update_ticket",
    "_delete_ticket",
    "_add_comment",
    "_get_ticket",
    "_handle_link_tickets",
    "_handle_add_watcher",
    "_handle_remove_watcher",
    "_handle_get_attachments",
}


class IssueKeyPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = CONNECTOR.read_text()
        cls.tree = ast.parse(cls.source)

    def test_issue_specific_handlers_apply_shared_validation(self):
        methods = {
            node.name: ast.get_source_segment(self.source, node)
            for node in ast.walk(self.tree)
            if isinstance(node, ast.FunctionDef) and node.name in VALIDATED_HANDLERS
        }

        self.assertEqual(set(methods), VALIDATED_HANDLERS)
        for name, source in methods.items():
            with self.subTest(handler=name):
                self.assertIn("_is_valid_issue_key", source)

    def test_validator_accepts_only_issue_keys_and_numeric_ids(self):
        validator = next(node for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef) and node.name == "_is_valid_issue_key")
        module = ast.fix_missing_locations(ast.Module(body=[validator], type_ignores=[]))
        namespace = {"re": re}
        exec(compile(module, str(CONNECTOR), "exec"), namespace)
        is_valid = namespace["_is_valid_issue_key"]

        for value in ("PROJ-1", "abc_2-99", "10001"):
            with self.subTest(valid=value):
                self.assertTrue(is_valid(value))

        for value in (".", "..", "../group/member", "PROJ-1?x", "PROJ-1#x", "%2e%2e", "0", ""):
            with self.subTest(invalid=value):
                self.assertFalse(is_valid(value))


if __name__ == "__main__":
    unittest.main()
