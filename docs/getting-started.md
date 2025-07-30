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

This will walk you through a wizard to create a `vertagus.yml` configuration file in your project root with a working
project configuration that you can then modify further to meet your needs.

### 2. Configure Your Project

Edit the generated `vertagus.yaml` file to match your project structure. Here's a basic example:

```yaml
scm:
  type: "git"
  tag_prefix: "v"
  version_strategy: "branch"
  target_branch: "main"
  manifest_path: "./package.json"
  manifest_type: "json"
  manifest_loc: "version"

project:
  rules:
    current: ["not_empty"]
    increment: ["any_increment"]
    manifest_comparisons: []

  stages:
    dev:
      rules:
        current: ["regex_dev_mmp"]
    
    prod:
      aliases: ["string:stable", "string:latest", "major.minor"]
      rules:
        current: ["regex_mmp"]

  manifests:
    - type: "json"
      path: "./package.json"
      loc: "version"
      name: "package.json"
```

## Basic Usage


### Validate version

Check that the version declared in your current working codebase satisfies the rules you've configured:

```bash
vertagus validate
```

### Bump Version

To automatically bump your version, which will change the version in your manifest file:

```bash
vertagus bump
```

You can also specify the bump type:

```bash
vertagus bump level=minor
```

### Create Tags

To create git tags based on your current version:

```bash
vertagus create-tag
```

## Next Steps

- Read the [Configuration](configuration.md) guide for detailed setup options
- Explore the [CLI Reference](cli-reference.md) for all available commands
