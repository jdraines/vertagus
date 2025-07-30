# Vertagus

Vertagus is a tool to enable automation around maintaining versions for your source code via a source control management tool like git. You can automate checks to compare the current code version string with version string(s) found on a specific branch of your repo or in repo tags, automate bumping based on semantic commit messages, and automate creating version tags in your git repo.

## Features

- **Semver version validation** - Ensure your version strings follow semantic versioning
- **Automated version bumping** - Based on semantic commit messages or user configuration
- **Multi-stage development** - Support for different development stages (dev, staging, prod)
- **Git tag automation** - Create version tags and maintain alias tags like 'stable', 'latest'
- **Flexible configuration** - Support for TOML and YAML configuration formats
- **Multiple manifest types** - Works with various project manifest files

## Quick Start

### Installation

Install from PyPI:

```bash
pip install vertagus
```

### Basic Usage

1. Initialize your project configuration:
   ```bash
   vertagus init
   ```

2. Validate your current version:
   ```bash
   vertagus validate
   ```

3. Bump your version:
   ```bash
   vertagus bump
   ```

## Documentation Overview

- **[Getting Started](getting-started.md)** - Learn how to set up and use Vertagus
- **[Configuration](configuration.md)** - Detailed configuration options
- **[CLI Reference](cli-reference.md)** - Complete command-line interface documentation
- **[Contributing](contributing.md)** - Contribution guide

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/jdraines/vertagus/blob/main/LICENSE) file for details.
