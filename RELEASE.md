# Release Guide

This guide walks through publishing MockFactory CLI to PyPI.

## Prerequisites

### 1. Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create an account
3. Verify your email

### 2. Generate PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name it "mockfactory-cli-github-actions"
4. Scope: "Entire account" (or specific to this project after first upload)
5. Copy the token (starts with `pypi-`)

### 3. Add Token to GitHub Secrets

1. Go to https://github.com/straticus1/mockfactory-cli/settings/secrets/actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Paste your PyPI token
5. Click "Add secret"

## Publishing a Release

### Method 1: Manual PyPI Upload (First Time)

For the first release, you may want to upload manually:

```bash
# Make sure you're in the project directory
cd /Users/ryan/development/mockfactory-cli

# Build the package
python3 -m build

# Check the package
twine check dist/*

# Upload to PyPI
twine upload dist/*
# Enter your PyPI username and API token when prompted
# Username: __token__
# Password: your-pypi-token (paste the full token)
```

### Method 2: GitHub Release (Automated)

After the first manual upload and setting up the GitHub secret:

1. **Update Version**
   ```bash
   # Edit mockfactory_cli/__init__.py
   __version__ = "0.2.0"

   # Edit pyproject.toml
   version = "0.2.0"
   ```

2. **Commit and Push**
   ```bash
   git add mockfactory_cli/__init__.py pyproject.toml
   git commit -m "Bump version to 0.2.0"
   git push
   ```

3. **Create Git Tag**
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

4. **Create GitHub Release**
   ```bash
   # Using GitHub CLI
   gh release create v0.2.0 \
     --title "MockFactory CLI v0.2.0" \
     --notes "Release notes here"

   # Or go to: https://github.com/straticus1/mockfactory-cli/releases/new
   ```

5. **Automated Publishing**
   - The GitHub Action will automatically build and publish to PyPI
   - Check progress at: https://github.com/straticus1/mockfactory-cli/actions

## Verify Installation

After publishing, verify the package is available:

```bash
# Wait a few minutes for PyPI to update
pip install --upgrade mockfactory-cli

# Test it
mockfactory --version
```

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (x.0.0): Incompatible API changes
- **MINOR** version (0.x.0): New features, backwards compatible
- **PATCH** version (0.0.x): Bug fixes, backwards compatible

Examples:
- `0.1.0` → `0.1.1` - Bug fix
- `0.1.0` → `0.2.0` - New feature
- `0.9.0` → `1.0.0` - Breaking change

## Publishing Checklist

Before creating a release:

- [ ] All tests pass locally
- [ ] Version bumped in `__init__.py` and `pyproject.toml`
- [ ] CHANGELOG updated (if exists)
- [ ] README updated with new features
- [ ] All changes committed and pushed
- [ ] GitHub Actions secrets configured
- [ ] PyPI account created and verified

## First Time Setup (v0.1.0)

For the initial v0.1.0 release:

```bash
# 1. Create PyPI account and token (see above)

# 2. Upload manually first time
python3 -m build
twine upload dist/*

# 3. Create GitHub release
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
gh release create v0.1.0 --title "MockFactory CLI v0.1.0" --notes "Initial release"

# 4. Verify on PyPI
# Visit: https://pypi.org/project/mockfactory-cli/
```

## Troubleshooting

### Package Name Already Exists

If `mockfactory-cli` is taken on PyPI, you'll need to choose a different name:
1. Update `name` in `pyproject.toml`
2. Update references in README
3. Try uploading again

### Authentication Failed

- Make sure you're using `__token__` as username
- Make sure you're using the full API token (starts with `pypi-`)
- Check the token hasn't expired

### GitHub Action Failed

- Check that `PYPI_API_TOKEN` secret is set correctly
- Verify the token has write permissions
- Check the action logs for specific errors

## Support

For help, open an issue at: https://github.com/straticus1/mockfactory-cli/issues
