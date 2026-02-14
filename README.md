# MockFactory CLI

[![PyPI version](https://badge.fury.io/py/mockfactory-cli.svg)](https://pypi.org/project/mockfactory-cli/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mockfactory-cli.svg)](https://pypi.org/project/mockfactory-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Command-line interface for [MockFactory](https://mockfactory.io) - a secure multi-language code execution sandbox.

Execute code in isolated Docker containers with comprehensive security controls, directly from your terminal.

## Features

- **Multi-Language Support**: Python, JavaScript, PHP, Perl, Go, Shell, HTML
- **Secure Execution**: All code runs in isolated containers with no network access
- **Authentication**: Login to access your account and execution history
- **Usage Tracking**: Monitor your execution limits and tier status
- **Beautiful Output**: Rich terminal formatting with syntax highlighting
- **Easy to Use**: Simple commands for quick code execution

## Installation

```bash
pip install mockfactory-cli
```

Or install from source:

```bash
git clone https://github.com/afterdarksystems/mockfactory-cli.git
cd mockfactory-cli
pip install -e .
```

## Quick Start

### Execute code inline

```bash
mockfactory run python -c "print('Hello from MockFactory!')"
```

### Execute a file

```bash
mockfactory execute script.py
```

### Auto-detect language from file extension

```bash
mockfactory execute app.js
mockfactory execute script.php
mockfactory execute program.go
```

## Commands

### Authentication

#### Sign up for a free account

```bash
mockfactory signup
```

Creates a new account with 10 free executions per day.

#### Login to your account

```bash
mockfactory login
```

#### Check authentication status

```bash
mockfactory status
```

#### Logout

```bash
mockfactory logout
```

### Code Execution

#### Run code inline

```bash
mockfactory run <language> -c "<code>"

# Examples:
mockfactory run python -c "print('Hello World')"
mockfactory run javascript -c "console.log('Hello World')"
mockfactory run php -c "echo 'Hello World';"
```

#### Run code from a file

```bash
mockfactory run <language> -f <file>

# Example:
mockfactory run python -f script.py
```

#### Execute a file (auto-detect language)

```bash
mockfactory execute <file>

# Examples:
mockfactory execute script.py      # Python
mockfactory execute app.js         # JavaScript
mockfactory execute program.go     # Go
mockfactory execute script.sh      # Shell
```

#### Set execution timeout

```bash
mockfactory run python -c "import time; time.sleep(2); print('done')" --timeout 60
```

#### Raw output mode

```bash
# Useful for piping or scripting
mockfactory run python -c "print('result')" --raw
```

### Usage & Status

#### Check your usage

```bash
mockfactory usage
```

Shows:
- Current tier (anonymous, free, pro)
- Executions used
- Remaining executions

#### View configuration

```bash
mockfactory config show
```

### Configuration

#### Set API URL

```bash
mockfactory config set api_url https://mockfactory.io
```

#### Set timeout

```bash
mockfactory config set timeout 60
```

#### Reset to defaults

```bash
mockfactory config reset
```

## Supported Languages

| Language   | Extension | Example                              |
|------------|-----------|--------------------------------------|
| Python     | `.py`     | `mockfactory execute script.py`      |
| JavaScript | `.js`     | `mockfactory execute app.js`         |
| PHP        | `.php`    | `mockfactory execute script.php`     |
| Perl       | `.pl`     | `mockfactory execute script.pl`      |
| Go         | `.go`     | `mockfactory execute program.go`     |
| Shell      | `.sh`     | `mockfactory execute script.sh`      |
| HTML       | `.html`   | `mockfactory execute page.html`      |

## Usage Tiers

| Tier           | Executions | Price     | Features                  |
|----------------|------------|-----------|---------------------------|
| Anonymous      | 5/day      | Free      | No account required       |
| Free Account   | 10/day     | Free      | Execution history         |
| Pro            | Unlimited  | $9.99/mo  | Priority support          |

Sign up for a free account:
```bash
mockfactory signup
```

Upgrade to Pro at [mockfactory.io/pricing](https://mockfactory.io/pricing)

## Examples

### Execute a Python script

```bash
mockfactory execute hello.py
```

### Run inline JavaScript

```bash
mockfactory run javascript -c "const x = [1,2,3]; console.log(x.reduce((a,b) => a+b, 0))"
```

### Execute with custom timeout

```bash
mockfactory execute long_running.py --timeout 120
```

### Check how many runs you have left

```bash
mockfactory usage
```

### Pipe output to another command

```bash
mockfactory run python -c "print('hello')" --raw | grep hello
```

### Use in shell scripts

```bash
#!/bin/bash
result=$(mockfactory run python -c "print(2+2)" --raw)
echo "The answer is: $result"
```

## Configuration Files

Configuration is stored in `~/.mockfactory/`:

- `config.json` - CLI configuration (API URL, timeout, etc.)
- `token` - Authentication token (automatically managed)

## Security

- All code executes in isolated Docker containers
- No network access for sandbox containers
- Read-only filesystem (except `/tmp`)
- Resource limits enforced (CPU, memory, time)
- Runs as unprivileged user (`nobody`)

## Troubleshooting

### Authentication errors

If you get authentication errors, try logging out and back in:

```bash
mockfactory logout
mockfactory login
```

### Connection errors

Check your API URL configuration:

```bash
mockfactory config show
```

Reset to defaults if needed:

```bash
mockfactory config reset
```

### Rate limiting

If you've exceeded your tier's execution limit:

1. Wait for the daily reset
2. Sign up for a free account (10 runs/day)
3. Upgrade to Pro (unlimited)

## Aliases

For convenience, you can use the short alias `mf`:

```bash
mf run python -c "print('shorter!')"
mf execute script.py
mf status
```

## Development

### Setup development environment

```bash
git clone https://github.com/afterdarksystems/mockfactory-cli.git
cd mockfactory-cli
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Code formatting

```bash
black .
ruff check .
```

## Links

- Website: [mockfactory.io](https://mockfactory.io)
- Documentation: [github.com/afterdarksystems/mockfactory-cli](https://github.com/afterdarksystems/mockfactory-cli)
- Issues: [github.com/afterdarksystems/mockfactory-cli/issues](https://github.com/afterdarksystems/mockfactory-cli/issues)

## License

MIT License - see LICENSE file for details

## Support

For support, contact: support@afterdarksystems.com
