# Configuration

Vertagus uses TOML or YAML for its configuration format. The configuration file should be placed in your project root and named either `vertagus.yaml`, `vertagus.yml`, or `vertagus.toml`.

!!! tip "Configuration Format"
    While both YAML and TOML are supported, we recommend using YAML for better readability and easier maintenance.

## Configuration Structure

### SCM Section

The `scm` section configures source control management settings:

```yaml
scm:
  type: "git"                   # SCM type (currently only "git" is supported)
  tag_prefix: "v"               # Prefix for version tags (e.g., "v1.0.0")
  version_strategy: "branch"    # Strategy: "branch" or "tag"
  target_branch: "main"         # Target branch for version operations
  manifest_path: "./package.json"    # Path to main manifest file
  manifest_type: "json"         # Type of manifest
  manifest_loc: "version"       # A dot-separated path indicating the location of the version within the manifest's object structure
```

#### Supported Manifest Types

- `toml`
- `yaml`
- `json`
- `setuptools_pyproject` - Python projects using pyproject.toml

### Project Section

The `project` section defines versioning rules and stages:

```yaml
project:
  rules:
    - not_empty             # Validates current version is not empty
    - regex_mmp             # Validates current version matches semver format
    - any_increment         # Validates version is greater than previous

  stages:
    # Development stage
    dev:
      rules:
        - regex_dev_mmp     # Allow dev versions like "1.0.0.dev0"

    # Beta/staging stage
    beta:
      aliases: ["string:latest"]
      rules:
        - regex_beta_mmp    # Allow beta versions like "1.0.0.b1"

    # Production stage
    prod:
      aliases: ["string:stable", "string:latest", "major.minor"]
      rules:
        - regex_mmp         # Standard semver like "1.0.0"

  manifests:
    - type: "setuptools_pyproject"
      path: "./pyproject.toml"
      name: "pyproject"
```

Rules are defined as a flat list. Vertagus automatically detects whether each rule validates a single version (e.g., format checks) or compares versions (e.g., increment checks).

## Validation Rules

### Built-in Rules

You can see which rules are pre-defined in vertagus by running the command:

```
vertagus list-rules
```

The output of this command will be a list of rules, their descriptions, and their type (`single_version` for format validation rules, `comparison` for rules that compare the current version to a previous version).

### Configurable rules

Configurable rules are rules that accept configuration values. To use a configurable rule, list it as an object with `type` and `config` fields. For example, the following combination uses a configurable rule to enforce that the major component of the version must be `1`:

```yaml
project:
  rules:
    - regex_mmp
    - type: custom_regex
      config:
        pattern: '^1.+'
```

### Manifest Comparison Rules

To ensure that version numbers across multiple manifests stay in sync, use the `manifests_comparison` rule:

```yaml
project:
  rules:
    - not_empty
    - any_increment
    - type: manifests_comparison
      config:
        manifests: [pyproject, frontend]

  manifests:
    - type: "setuptools_pyproject"
      path: "./pyproject.toml"
      name: "pyproject"
    - type: "json"
      path: "./frontend/package.json"
      name: "frontend"
```

## Stage Configuration

Stages allow you to define different versioning behaviors for different environments:

### Stage Properties

- `aliases` - Git tag aliases to create/maintain
- `rules` - Validation rules specific to this stage

### Example Multi-Stage Setup

```yaml
project:
  stages:
    # Development - allows pre-release versions
    dev:
      rules:
        - regex_dev_mmp

    # Staging - beta versions only
    staging:
      aliases: ["string:staging"]
      rules:
        - regex_beta_mmp

    # Production - stable releases only
    prod:
      aliases: ["string:stable", "string:latest", "major.minor"]
      rules:
        - regex_mmp
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
    - not_empty
    - any_increment

  stages:
    dev:
      rules:
        - regex_dev_mmp

    beta:
      aliases: ["string:latest"]
      rules:
        - regex_beta_mmp

    prod:
      aliases: ["string:stable", "string:latest", "major.minor"]
      rules:
        - regex_mmp

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

[project]
rules = ["not_empty", "any_increment"]

[project.stages.dev]
rules = ["regex_dev_mmp"]

[project.stages.beta]
aliases = ["string:latest"]
rules = ["regex_beta_mmp"]

[project.stages.prod]
aliases = ["string:stable", "string:latest", "major.minor"]
rules = ["regex_mmp"]

[[project.manifests]]
type = "setuptools_pyproject"
path = "./pyproject.toml"
name = "pyproject"
```
