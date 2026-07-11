# AGENTS.md

## Scope

These instructions apply to the Python MockFactory CLI repository.

## Before editing

- Inspect `git status`, `pyproject.toml`, `mockfactory_cli/client.py`, and the relevant Click command.
- Check the corresponding server route in `../mockfactory.io` and MockLib operation in `../mockfactory-mocklib`.
- Preserve any user modification in `mockfactory_cli/__init__.py` or other dirty files.

## Implementation rules

- Add tests before modifying behavior.
- Use Click's test runner for commands and fake HTTP transports for deterministic unit tests.
- Test exit code, stdout, stderr, JSON output, timeouts, malformed responses, and authentication failures.
- Keep transport, presentation, and command orchestration separate when extracting code from `cli.py`.
- Never store secrets in repository files or print them in diagnostics.
- Do not create another independent resource ontology; share MockLib contracts.
- Maintain Python 3.8 compatibility until package metadata intentionally changes.

## Verification

```bash
python -m pytest -q
python -m ruff check .
python -m build
python -m mockfactory_cli.cli --help
git diff --check
```

Run only commands actually supported by installed dependencies and report missing tooling accurately. Publishing to PyPI, creating releases, or changing the official `mf` ownership requires explicit authorization.
