# CI/CD Guide for GFL Plugin: RAG Engine

## Overview

This plugin uses **GitHub Actions** for Continuous Integration and Continuous Deployment (CI/CD). Every code change is automatically tested, linted, and validated before merging.

## Workflows

### 1. CI Workflow (`ci.yml`)

**Trigger**: Every push or pull request to `main`/`master` branch

**Jobs**:

#### Test Job
- **Purpose**: Run the complete test suite with coverage
- **Python Versions**: 3.9, 3.10, 3.11 (matrix build)
- **Steps**:
  1. Checkout plugin repository
  2. Checkout GFL repository (dependency)
  3. Set up Python environment
  4. Install dependencies (GFL + plugin)
  5. Run pytest with coverage
  6. Upload coverage to Codecov
  7. Generate coverage HTML report
  8. Verify coverage threshold (>90%)
- **Duration**: ~3-5 minutes per Python version

#### Lint Job
- **Purpose**: Ensure code quality and style
- **Tools**:
  - **Black**: Code formatting
  - **Ruff**: Fast Python linter
  - **MyPy**: Static type checking
- **Duration**: ~1 minute

#### Security Job
- **Purpose**: Check for security vulnerabilities
- **Tools**:
  - **Bandit**: Security linter for Python
  - **Safety**: Check dependencies for known vulnerabilities
- **Duration**: ~1 minute

#### Build Job
- **Purpose**: Validate package build
- **Steps**:
  1. Build distribution packages (wheel + sdist)
  2. Validate with `twine check`
  3. Upload build artifacts
- **Duration**: ~1 minute

#### All Checks Passed
- **Purpose**: Summary job for branch protection
- **Depends on**: All previous jobs must pass
- **Use case**: Set as required check for PR merging

### 2. Release Workflow (`release.yml`)

**Trigger**: Push of version tags (e.g., `v1.0.0`)

**Steps**:
1. Build distribution packages
2. Create GitHub Release with artifacts
3. Publish to PyPI (if configured)
4. Publish to Test PyPI (alternative)

## Setup Instructions

### 1. GitHub Repository Configuration

#### Enable Actions
1. Go to repository **Settings** → **Actions** → **General**
2. Select "Allow all actions and reusable workflows"
3. Enable "Read and write permissions" for GITHUB_TOKEN

#### Branch Protection Rules
1. Go to **Settings** → **Branches**
2. Add rule for `main` branch
3. Require status checks:
   - `All Checks Passed`
   - `Test (3.9)`, `Test (3.10)`, `Test (3.11)`
   - `Code Quality Checks`
   - `Security Checks`
   - `Build and Validate Package`
4. Enable "Require branches to be up to date"
5. Enable "Require pull request reviews"

### 2. Codecov Integration (Optional)

#### Sign Up
1. Go to [codecov.io](https://about.codecov.io/)
2. Sign in with GitHub
3. Add your repository

#### Configure Token
1. Copy the Codecov token from repository settings
2. Go to GitHub repository **Settings** → **Secrets and variables** → **Actions**
3. Create new secret: `CODECOV_TOKEN`
4. Paste the token value

#### Benefits
- Visual coverage reports
- PR comments with coverage changes
- Coverage trend graphs
- Badge for README

### 3. PyPI Publishing (Optional)

#### Create PyPI API Token
1. Go to [pypi.org](https://pypi.org/) and sign in
2. Go to **Account settings** → **API tokens**
3. Create token with scope "Entire account"

#### Configure Secrets
1. Go to GitHub **Settings** → **Secrets and variables** → **Actions**
2. Create secret: `PYPI_TOKEN`
3. Paste the API token

#### Test PyPI (Recommended First)
1. Create token at [test.pypi.org](https://test.pypi.org/)
2. Create secret: `TEST_PYPI_TOKEN`
3. Test release before publishing to production

## Running CI Locally

### Run Tests Locally

```bash
# Full test suite
pytest

# With coverage
pytest --cov=gfl_plugin_rag_engine --cov-report=html

# Using the test runner script
bash run_tests.sh --coverage
```

### Run Linting Locally

```bash
# Black formatting
black gfl_plugin_rag_engine/ tests/

# Ruff linting
ruff check gfl_plugin_rag_engine/ tests/

# MyPy type checking
mypy gfl_plugin_rag_engine/ --ignore-missing-imports
```

### Run Security Checks Locally

```bash
# Bandit security linting
bandit -r gfl_plugin_rag_engine/

# Safety dependency check
safety check
```

### Build Package Locally

```bash
# Install build tools
pip install build twine

# Build
python -m build

# Check
twine check dist/*
```

## CI/CD Best Practices

### 1. Always Test Before Pushing

```bash
# Pre-push checklist
pytest                          # Run tests
black --check .                 # Check formatting
ruff check .                    # Lint code
bandit -r gfl_plugin_rag_engine/ # Security check
```

### 2. Use Meaningful Commit Messages

```bash
# Good
git commit -m "feat: Add support for batch hypothesis validation"
git commit -m "fix: Handle empty PubMed results gracefully"
git commit -m "test: Add coverage for edge cases in confidence scoring"

# Bad
git commit -m "fixed stuff"
git commit -m "updates"
```

### 3. Keep Pull Requests Focused

- One feature/fix per PR
- Include tests for new features
- Update documentation if needed
- Ensure all CI checks pass

### 4. Review CI Failures

When CI fails:
1. Click on the failed job
2. Expand the failed step
3. Read the error message
4. Reproduce locally
5. Fix and push again

## Monitoring and Maintenance

### Check CI Status

- **Repository**: Actions tab shows all workflow runs
- **Pull Request**: Checks section shows status
- **Branch**: Branch protection shows required checks

### Coverage Trends

- View on Codecov dashboard
- Track coverage over time
- Identify untested code paths

### Build Artifacts

- Download from Actions tab
- Test artifacts: Coverage reports
- Build artifacts: Distribution packages

## Troubleshooting

### CI Fails But Tests Pass Locally

**Possible causes**:
- Different Python version
- Missing dependencies in CI
- Environment-specific issues

**Solution**:
```bash
# Test with specific Python version
python3.9 -m pytest
python3.10 -m pytest
python3.11 -m pytest
```

### Coverage Upload Fails

**Cause**: Missing `CODECOV_TOKEN`

**Solution**: Add token to repository secrets (see Setup Instructions)

### Build Fails on PyPI Publishing

**Causes**:
- Version already exists on PyPI
- Missing or invalid `PYPI_TOKEN`
- Package name conflict

**Solution**:
- Bump version in `pyproject.toml`
- Check token configuration
- Use Test PyPI first

### Linting Fails with Style Issues

**Solution**:
```bash
# Auto-fix formatting
black gfl_plugin_rag_engine/ tests/

# Auto-fix some ruff issues
ruff check --fix gfl_plugin_rag_engine/ tests/
```

## Performance Optimization

### Cache Dependencies

The CI workflow already caches pip dependencies:
```yaml
- uses: actions/setup-python@v5
  with:
    cache: 'pip'
```

### Parallel Jobs

Tests run in parallel across Python versions:
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```

### Artifact Retention

Artifacts are kept for 90 days by default. Adjust if needed:
```yaml
- uses: actions/upload-artifact@v4
  with:
    retention-days: 30
```

## Security Considerations

### Secrets Management

- Never commit tokens or passwords
- Use GitHub Secrets for sensitive data
- Rotate tokens periodically

### Dependency Security

- `safety` checks for known vulnerabilities
- Dependabot alerts for security updates
- Regular dependency updates

### Code Security

- `bandit` scans for security issues
- Follow security best practices
- Review security advisories

## Release Process

### Creating a Release

1. **Update Version**
   ```bash
   # Edit pyproject.toml
   version = "1.1.0"
   ```

2. **Commit and Tag**
   ```bash
   git commit -m "chore: Bump version to 1.1.0"
   git tag v1.1.0
   git push origin main
   git push origin v1.1.0
   ```

3. **GitHub Release**
   - Automatically created by workflow
   - Includes build artifacts
   - Shows release notes

4. **PyPI Release**
   - Automatically published (if configured)
   - Available via `pip install gfl-plugin-rag-engine`

## Metrics and KPIs

### CI/CD Metrics to Track

- **Build Success Rate**: % of successful builds
- **Average Build Time**: Time to complete CI
- **Test Coverage**: % of code covered by tests
- **Time to Merge**: Time from PR creation to merge
- **Deployment Frequency**: How often releases happen

### Current Status

- ✅ **42 Tests**: Comprehensive coverage
- ✅ **~98% Coverage**: High code coverage
- ✅ **~2s Test Duration**: Fast feedback
- ✅ **3 Python Versions**: Broad compatibility
- ✅ **4 CI Jobs**: Multi-faceted validation

---

**Last Updated**: October 2025
**CI/CD Version**: 1.0.0
**Maintained by**: GeneForge Development Team
