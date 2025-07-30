# Examples

This page provides real-world examples of using Vertagus in different project scenarios.

## Basic Python Project

### Setup

For a simple Python project with semantic versioning:

```yaml
# vertagus.yaml
scm:
  type: "git"
  tag_prefix: "v"
  version_strategy: "branch"
  target_branch: "main"
  manifest_path: "./pyproject.toml"
  manifest_type: "setuptools_pyproject"

project:
  rules:
    current: ["not_empty", "regex_mmp"]
    increment: ["any_increment"]
  
  manifests:
    - type: "setuptools_pyproject"
      path: "./pyproject.toml"
      name: "main"
```

### Workflow

```bash
# 1. Check current version
vertagus check

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Bump version automatically
vertagus bump

# 4. Create git tags
vertagus tag --push
```

## Multi-Stage Development

### Setup

For projects with development, staging, and production stages:

```yaml
# vertagus.yaml
scm:
  type: "git"
  tag_prefix: "v"
  version_strategy: "branch"
  target_branch: "main"
  manifest_path: "./pyproject.toml"
  manifest_type: "setuptools_pyproject"

project:
  rules:
    current: ["not_empty"]
    increment: ["any_increment"]
  
  stages:
    dev:
      rules:
        current: ["regex_dev_mmp"]  # e.g., 1.0.0-dev.1
    
    staging:
      aliases: ["string:staging"]
      rules:
        current: ["regex_beta_mmp"]  # e.g., 1.0.0-beta.1
    
    prod:
      aliases: ["string:stable", "string:latest", "major.minor"]
      rules:
        current: ["regex_mmp"]  # e.g., 1.0.0
  
  manifests:
    - type: "setuptools_pyproject"
      path: "./pyproject.toml"
      name: "main"
```

### Development Workflow

```bash
# Development branch
git checkout develop

# Bump development version
vertagus bump --stage dev
# Creates version like: 1.0.0-dev.1

# Create development tags
vertagus tag --stage dev
```

### Staging Workflow

```bash
# Staging branch
git checkout staging

# Bump to beta version
vertagus bump --stage staging
# Creates version like: 1.0.0-beta.1

# Create staging tags
vertagus tag --stage staging --push
# Creates: v1.0.0-beta.1, staging
```

### Production Workflow

```bash
# Production branch
git checkout main

# Bump to production version
vertagus bump --stage prod
# Creates version like: 1.0.0

# Create production tags
vertagus tag --stage prod --push
# Creates: v1.0.0, stable, latest, 1.0
```

## Monorepo with Multiple Services

### Setup

For a monorepo with multiple services that need independent versioning:

```yaml
# vertagus.yaml
scm:
  type: "git"
  tag_prefix: ""  # No prefix for monorepo
  version_strategy: "branch"
  target_branch: "main"

project:
  rules:
    current: ["not_empty"]
    increment: ["any_increment"]
  
  manifests:
    - type: "setuptools_pyproject"
      path: "./backend/pyproject.toml"
      name: "backend"
    - type: "package_json"
      path: "./frontend/package.json"
      name: "frontend"
    - type: "cargo_toml"
      path: "./worker/Cargo.toml"
      name: "worker"
```

### Service-Specific Versioning

```bash
# Bump only backend
vertagus bump --manifest backend

# Bump only frontend
vertagus bump --manifest frontend

# Check all services
vertagus status --detailed
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/version.yml
name: Version Management

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  version-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Need full history for version comparison
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Vertagus
        run: pip install vertagus
      
      - name: Validate configuration
        run: vertagus validate
      
      - name: Check version
        run: vertagus check
      
      - name: Compare with main
        run: vertagus compare --target origin/main

  auto-release:
    needs: version-check
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Vertagus
        run: pip install vertagus
      
      - name: Auto-bump version
        run: |
          vertagus bump --commit
          vertagus tag --push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Docker Integration

### Dockerfile with Version

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install Vertagus for version management
RUN pip install vertagus

WORKDIR /app
COPY . .

# Get version from Vertagus and set as label
RUN vertagus status --json > /tmp/version.json
RUN export VERSION=$(cat /tmp/version.json | python -c "import sys, json; print(json.load(sys.stdin)['version'])") && \
    echo "LABEL version=$VERSION" >> /tmp/version.label

# Install dependencies
RUN pip install -e .

CMD ["python", "-m", "myapp"]
```

### Docker Compose with Version Tags

```bash
#!/bin/bash
# build-and-tag.sh

# Get current version
VERSION=$(vertagus status --json | python -c "import sys, json; print(json.load(sys.stdin)['version'])")

# Build Docker image with version tag
docker build -t myapp:$VERSION .
docker build -t myapp:latest .

# Push to registry
docker push myapp:$VERSION
docker push myapp:latest

echo "Built and pushed myapp:$VERSION"
```

## Release Automation

### Complete Release Script

```bash
#!/bin/bash
# release.sh

set -e

STAGE=${1:-prod}

echo "Starting release process for stage: $STAGE"

# Validate current state
echo "Validating configuration..."
vertagus validate

echo "Checking current version..."
vertagus check --stage $STAGE

# Bump version
echo "Bumping version..."
NEW_VERSION=$(vertagus bump --stage $STAGE --dry-run | grep "New version" | cut -d: -f2 | tr -d ' ')

echo "Bumping to version: $NEW_VERSION"
vertagus bump --stage $STAGE

# Create commit and tags
echo "Creating git commit..."
git add .
git commit -m "chore: bump version to $NEW_VERSION"

echo "Creating git tags..."
vertagus tag --stage $STAGE

# Push changes
echo "Pushing changes and tags..."
git push origin main
git push origin --tags

echo "Release $NEW_VERSION completed successfully!"
```

## Custom Rules Example

### Advanced Validation Rules

```yaml
# vertagus.yaml with custom rules
scm:
  type: "git"
  tag_prefix: "v"
  version_strategy: "branch"
  target_branch: "main"

project:
  rules:
    current: ["not_empty", "custom_version_format"]
    increment: ["semantic_increment"]
  
  custom_rules:
    custom_version_format:
      pattern: "^\\d+\\.\\d+\\.\\d+(-[a-z]+\\d+)?$"
      description: "Version must be semver with optional pre-release"
    
    semantic_increment:
      pattern: "major|minor|patch"
      description: "Only semantic increments allowed"
  
  stages:
    dev:
      rules:
        current: ["regex_dev_mmp", "dev_branch_only"]
    
    prod:
      aliases: ["string:stable", "major.minor"]
      rules:
        current: ["regex_mmp", "no_prerelease"]
  
  manifests:
    - type: "setuptools_pyproject"
      path: "./pyproject.toml"
      name: "main"
```

These examples demonstrate various ways to integrate Vertagus into different project workflows and CI/CD pipelines. Adapt them to your specific needs and project structure.
