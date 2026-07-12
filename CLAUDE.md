# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

# Communication

Always remember to call me by my name Abhay at the start of any response.

# Context

Always when the context limit is gettinf reached fan out subagents as needed.

All commands use `uv` as the package manager.

```bash
# Install dependencies
uv sync --all-groups

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/path/to/test_file.py::test_name

# Watch tests
uv run pytest-watch

# Lint (auto-fixes)
uv run ruff check --fix src/
uv run ruff format src/

# Type check
uv run mypy src/

# Run pre-commit hooks manually
uv run pre-commit run --all-files
```

## Architecture

This is a **Splunk SOAR SDK** connector app for Jira. The SDK handles all the SOAR platform wiring; this repo only defines the app structure, parameters, and output shapes.

### Entry point

`src/app.py` is the single source file referenced by `[tool.soar.app] main_module = "src.app:app"`. It contains:

1. **`Asset`** — connection config (device URL, credentials, project key, polling settings). Subclasses `BaseAsset` using `AssetField`.
1. **`app`** — the `App` instance that registers all actions via decorators.
1. **Params classes** — subclass `Params`, one per action. Fields declared with `Param(...)`.
1. **Output classes** — subclass `ActionOutput`, fields declared with `OutputField(...)`. Nested objects are typed as other `ActionOutput` subclasses.
1. **Action functions** — decorated with `@app.action(...)`, `@app.on_poll()`, or `@app.test_connectivity()`. Signatures are `(params, soar, asset) -> OutputClass`. All currently raise `NotImplementedError`.

### SDK conventions

- `OutputField(cef_types=[...], example_values=[...], alias="...")` — `alias` is used when the JSON key is not a valid Python identifier (e.g. `"Epic Link"` → field `Epic_Link` with `alias="Epic Link"`).
- `Param(primary=True, cef_types=[...])` — `primary=True` marks parameters shown prominently in the SOAR UI.
- `list[SomeOutput]` on a field means it maps to a JSON array of objects.
- The `SOARClient` argument (`soar`) provides platform APIs (vault access, container/artifact creation, etc.).

### Output class redundancy (current state)

`app.py` currently defines the same shared output classes (e.g. `AvatarurlsOutput`, `AssigneeOutput`, `StatusOutput`) multiple times — once per action block — because each action's classes are co-located with its decorator. An in-progress refactor will move actions to `src/actions/` with shared classes in `src/actions/_outputs.py`.

### Commit message format

Commits must follow **Conventional Commits** (enforced by pre-commit hook):

```
feat: add create ticket implementation
fix: handle null assignee in update ticket
```

### Exit

Whenever /exit command is there save the latest context in CLAUDE.md so that can be used for further sessions.
