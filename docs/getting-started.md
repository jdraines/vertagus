# Getting Started

This guide will help you get up and running with Vertagus quickly.

## Prerequisites

- Python 3.9 or higher
- Git repository for your project
- A project manifest file (e.g., `pyproject.toml`, `package.json`, etc.)

## Installation

### From PyPI

```bash
pip install vertagus
```

### From Source

```bash
git clone https://github.com/jdraines/vertagus.git
cd vertagus
pip install -e .
```

### Development Installation

If you want to contribute to Vertagus or need the development dependencies:

```bash
pip install -e ".[dev,docs]"
```

## Initial Setup

### 1. Initialize Configuration

Navigate to your project directory and run:

```bash
vertagus init
```

This will create a `vertagus.yaml` configuration file in your project root with sensible defaults.

### 2. Configure Your Project

Edit the generated `vertagus.yaml` file to match your project structure. Here's a basic example:

```yaml
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
    manifest_comparisons: []

  stages:
    dev:
      rules:
        current: ["regex_dev_mmp"]
    
    beta:
      aliases: ["string:latest"]
      rules:
        current: ["regex_beta_mmp"]
    
    prod:
      aliases: ["string:stable", "string:latest", "major.minor"]
      rules:
        current: ["regex_mmp"]

  manifests:
    - type: "setuptools_pyproject"
      path: "./pyproject.toml"
      name: "pyproject"
```

## Basic Usage

### Check Current Version

To check if your current version is valid:

```bash
vertagus check
```

### Compare Versions

To compare your current version with what's in your SCM:

```bash
vertagus compare
```

### Bump Version

To automatically bump your version:

```bash
vertagus bump
```

You can also specify the bump type:

```bash
vertagus bump --type patch
vertagus bump --type minor
vertagus bump --type major
```

### Create Tags

To create git tags based on your current version:

```bash
vertagus tag
```

## Common Workflows

### Development Workflow

1. Make your changes
2. Commit with semantic commit messages (e.g., `feat: add new feature`)
3. Run `vertagus bump` to automatically increment version
4. Run `vertagus tag` to create git tags
5. Push changes and tags

### Release Workflow

1. Ensure you're on the target branch (usually `main`)
2. Run `vertagus check` to validate current state
3. Run `vertagus bump --stage prod` for production release
4. Run `vertagus tag` to create release tags
5. Push changes and tags

## Next Steps

- Read the [Configuration](configuration.md) guide for detailed setup options
- Check out [Examples](examples.md) for real-world usage scenarios
- Explore the [CLI Reference](cli-reference.md) for all available commands
- Review the [API Reference](reference/) if you need to integrate Vertagus programmatically
