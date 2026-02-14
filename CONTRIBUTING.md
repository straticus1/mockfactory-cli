# Contributing to MockFactory CLI

Thank you for your interest in contributing to MockFactory CLI!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/straticus1/mockfactory-cli.git
cd mockfactory-cli
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

4. Verify installation:
```bash
mockfactory --version
```

## Running Tests

```bash
pytest
```

## Code Style

We use `black` for code formatting and `ruff` for linting:

```bash
# Format code
black .

# Check linting
ruff check .
```

## Making Changes

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes

3. Test your changes:
```bash
pytest
black .
ruff check .
```

4. Commit your changes:
```bash
git add .
git commit -m "Add: your feature description"
```

5. Push and create a pull request:
```bash
git push origin feature/your-feature-name
```

## Project Structure

```
mockfactory-cli/
├── mockfactory_cli/
│   ├── __init__.py       # Package version
│   ├── cli.py            # Main CLI commands
│   ├── client.py         # API client
│   └── config.py         # Configuration management
├── examples/             # Example scripts
├── pyproject.toml        # Package configuration
└── README.md            # Documentation
```

## Adding New Commands

To add a new command to the CLI:

1. Open `mockfactory_cli/cli.py`
2. Add your command using the `@cli.command()` decorator
3. Update the README.md with usage examples
4. Test the command locally

Example:
```python
@cli.command()
@click.argument("name")
def greet(name: str):
    """Greet someone."""
    console.print(f"Hello, {name}!")
```

## Adding New API Methods

To add a new API method:

1. Open `mockfactory_cli/client.py`
2. Add your method to the `MockFactoryClient` class
3. Use the `_request` helper method for API calls
4. Add appropriate error handling

Example:
```python
def get_something(self) -> Dict[str, Any]:
    """Get something from the API."""
    return self._request("GET", "/api/v1/something")
```

## Release Process

1. Update version in `mockfactory_cli/__init__.py`
2. Update version in `pyproject.toml`
3. Update CHANGELOG.md (if exists)
4. Create a git tag:
```bash
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

5. Build and publish to PyPI:
```bash
pip install build twine
python -m build
twine upload dist/*
```

## Questions?

Open an issue or contact: support@afterdarksystems.com
