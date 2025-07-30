# Configuration

Vertagus uses TOML or YAML for its configuration format. The configuration file should be placed in your project root and named either `vertagus.yaml`, `vertagus.yml`, or `vertagus.toml`.

!!! tip "Configuration Format"
    While both YAML and TOML are supported, we recommend using YAML for better readability and easier maintenance.

## Configuration Structure

### SCM Section

The `scm` section configures source control management settings:

```yaml
scm:
  type: "git"                    # SCM type (currently only "git" is supported)
  tag_prefix: "v"               # Prefix for version tags (e.g., "v1.0.0")
  version_strategy: "branch"    # Strategy: "branch" or "tag"
  target_branch: "main"         # Target branch for version operations
  manifest_path: "./pyproject.toml"    # Path to main manifest file
  manifest_type: "setuptools_pyproject" # Type of manifest
```

#### Supported Manifest Types

- `setuptools_pyproject` - Python projects using pyproject.toml
- `package_json` - Node.js projects using package.json
- `cargo_toml` - Rust projects using Cargo.toml

### Project Section

The `project` section defines versioning rules and stages:

```yaml
project:
  rules:
    current: ["not_empty"]           # Rules for current version validation
    increment: ["any_increment"]     # Rules for version increment validation
    manifest_comparisons: []         # Additional comparison rules
  
  stages:
    # Development stage
    dev:
      rules:
        current: ["regex_dev_mmp"]   # Allow dev versions like "1.0.0-dev.1"
    
    # Beta/staging stage
    beta:
      aliases: ["string:latest"]      # Create "latest" tag alias
      rules:
        current: ["regex_beta_mmp"]   # Allow beta versions like "1.0.0-beta.1"
    
    # Production stage
    prod:
      aliases: ["string:stable", "string:latest", "major.minor"]
      rules:
        current: ["regex_mmp"]        # Standard semver like "1.0.0"
  
  manifests:
    - type: "setuptools_pyproject"
      path: "./pyproject.toml"
      name: "pyproject"
```

## Validation Rules

### Built-in Rules

#### Current Version Rules

- `not_empty` - Version string must not be empty
- `regex_mmp` - Standard major.minor.patch format (e.g., "1.0.0")
- `regex_dev_mmp` - Development versions (e.g., "1.0.0-dev.1")
- `regex_beta_mmp` - Beta versions (e.g., "1.0.0-beta.1")

#### Increment Rules

- `any_increment` - Any version increment is allowed
- `major_increment` - Only major version increments
- `minor_increment` - Only minor version increments  
- `patch_increment` - Only patch version increments

### Custom Rules

You can define custom validation rules using regular expressions:

```yaml
project:
  rules:
    custom_rules:
      my_version_pattern:
        pattern: "^\\d+\\.\\d+\\.\\d+(-rc\\d+)?$"
        description: "Allows release candidate versions"
```

## Stage Configuration

Stages allow you to define different versioning behaviors for different environments:

### Stage Properties

- `aliases` - Git tag aliases to create/maintain
- `rules` - Validation rules specific to this stage
- `bump_strategy` - How to bump versions in this stage

### Example Multi-Stage Setup

```yaml
project:
  stages:
    # Development - allows pre-release versions
    dev:
      rules:
        current: ["regex_dev_mmp"]
      bump_strategy: "prerelease"
    
    # Staging - beta versions only
    staging:
      aliases: ["string:staging"]
      rules:
        current: ["regex_beta_mmp"]
      bump_strategy: "prerelease"
    
    # Production - stable releases only
    prod:
      aliases: ["string:stable", "string:latest", "major.minor"]
      rules:
        current: ["regex_mmp"]
      bump_strategy: "release"
```

## Alias Configuration

Aliases are additional git tags that point to specific versions:

### String Aliases
```yaml
aliases: ["string:stable", "string:latest"]
```
Creates tags like `stable` and `latest`.

### Pattern Aliases
```yaml
aliases: ["major.minor", "major"]
```
Creates tags like `1.2` (from version `1.2.3`) and `1` (from version `1.2.3`).

## Manifest Configuration

Configure multiple manifest files to keep in sync:

```yaml
project:
  manifests:
    - type: "setuptools_pyproject"
      path: "./pyproject.toml"
      name: "pyproject"
    - type: "package_json"
      path: "./frontend/package.json"
      name: "frontend"
```

## Complete Example

Here's the complete configuration from the Vertagus project itself:

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

## TOML Format

The same configuration in TOML format:

```toml
[scm]
type = "git"
tag_prefix = "v"
version_strategy = "branch"
target_branch = "main"
manifest_path = "./pyproject.toml"
manifest_type = "setuptools_pyproject"

[project.rules]
current = ["not_empty"]
increment = ["any_increment"]
manifest_comparisons = []

[project.stages.dev.rules]
current = ["regex_dev_mmp"]

[project.stages.beta]
aliases = ["string:latest"]

[project.stages.beta.rules]
current = ["regex_beta_mmp"]

[project.stages.prod]
aliases = ["string:stable", "string:latest", "major.minor"]

[project.stages.prod.rules]
current = ["regex_mmp"]

[[project.manifests]]
type = "setuptools_pyproject"
path = "./pyproject.toml"
name = "pyproject"
```
