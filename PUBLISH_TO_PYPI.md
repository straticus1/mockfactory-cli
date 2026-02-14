# Publishing MockFactory CLI to PyPI

The package is ready to publish! Here's how:

## Quick Start (First Time)

### 1. Create PyPI Account
- Go to: https://pypi.org/account/register/
- Create account and verify email

### 2. Get API Token
- Go to: https://pypi.org/manage/account/token/
- Click "Add API token"
- Name: `mockfactory-cli`
- Scope: "Entire account" (will scope to project after first upload)
- **Copy the token** (starts with `pypi-`)

### 3. Upload to PyPI

```bash
cd /Users/ryan/development/mockfactory-cli

# Upload (you'll be prompted for credentials)
twine upload dist/*

# When prompted:
# Username: __token__
# Password: <paste your PyPI token here>
```

## Verify It Worked

After uploading, check:
- PyPI page: https://pypi.org/project/mockfactory-cli/
- Test install: `pip install mockfactory-cli`

## Files Ready to Upload

- `dist/mockfactory_cli-0.1.0-py3-none-any.whl` ✓
- `dist/mockfactory_cli-0.1.0.tar.gz` ✓

Both files have been validated with `twine check` ✓

## What Happens Next

Once published, users can install with:
```bash
pip install mockfactory-cli
```

## GitHub Release

Already created! https://github.com/straticus1/mockfactory-cli/releases/tag/v0.1.0

## Troubleshooting

### "The name 'mockfactory-cli' is already taken"

If someone else claimed the name, you'll need to choose a different one:
1. Update `name` in `pyproject.toml`
2. Rebuild: `python3 -m build`
3. Try uploading again

### Alternative names to try:
- `mockfactory`
- `mockfactory-client`
- `mf-cli`
- `afterdark-mockfactory`

## Future Releases

For future versions:
1. Update version in `mockfactory_cli/__init__.py` and `pyproject.toml`
2. Rebuild: `python3 -m build`
3. Upload: `twine upload dist/*`
4. Create GitHub release: `gh release create v0.2.0`

## Need Help?

Check RELEASE.md for detailed instructions.
