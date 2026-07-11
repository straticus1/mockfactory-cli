# CLAUDE.md

Guidance for Claude Code when working on the Python MockFactory CLI.

## Product reality

This repository contains the original Python `mockfactory`/`mf` CLI. It began as a client for remote multi-language code execution and later accumulated organization, project, cloud-resource, generator, and utility commands in a single large Click module.

It overlaps with the Go CLI in `../mockfactory-mocklib/mocklib-cli`. The intended direction is one official portable Go `mf` CLI powered by MockLib semantics, but the Python CLI must not be removed or broken until command parity, migration documentation, and a deprecation release exist.

Related repositories:

- `../mockfactory.io`: FastAPI control plane and emulation runtime.
- `../mockfactory-mocklib`: multi-language resource model, scenarios, provider APIs, and Go CLI.

## Layout

- `mockfactory_cli/cli.py`: Click commands; currently very large and mixes code execution with resource management.
- `mockfactory_cli/client.py`: HTTP transport for `/api/v1` code-execution APIs.
- `mockfactory_cli/config.py`: API URL, token, timeout, and session configuration.
- `examples/`: code-execution examples.
- `pyproject.toml`: packaging and `mockfactory`/`mf` entry points.

## Current status

- The package declares beta status, but the repository has no automated tests.
- The client defaults to `https://mockfactory.io` and appends `/api/v1`.
- Human JWTs are sent as bearer tokens.
- Resource commands may not match the current server contract; verify them end to end.
- `mockfactory_cli.egg-info/` is checked into the working tree and should not be treated as source of truth.

## Setup and checks

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/mockfactory --help
.venv/bin/pytest -q
.venv/bin/ruff check .
```

If pytest reports no tests, say so. Add tests before changing commands, configuration, authentication, or response parsing.

## CLI contract

- Human output may evolve; `--json` output must be stable and documented.
- Never print access tokens, API keys, service passwords, or secret connection strings.
- Mutations should eventually support `--idempotency-key`, `--wait`, `--no-wait`, and `--timeout`.
- Support configurable base URLs, private certificate authorities, and self-hosted installations.
- Map server error codes to actionable messages and nonzero exit codes.
- Preserve Ctrl-C cancellation and automation-safe behavior.
- Avoid embedding MockLib business semantics independently; consume shared contracts or clients.

## Migration direction

New platform-wide resource features should normally land in MockLib and the Go CLI first. Change this Python CLI only to fix current users, maintain compatibility, or implement an approved migration step. Do not declare it deprecated until the Go CLI provides verified parity.
