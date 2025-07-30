# CLI Reference

Vertagus provides a comprehensive command-line interface for version management. This page documents all available commands and their options.

## Global Options

These options are available for most commands:

- `--config, -c PATH` - Path to configuration file (default: search for vertagus.yaml/yml/toml in current directory)
- `--help` - Show help message and exit

## Commands

### `vertagus validate`

Validate the current project version against configured rules.

```bash
vertagus validate [OPTIONS]
```

**Options:**
- `--config, -c PATH` - Path to the configuration file
- `--stage-name, -s STAGE` - Name of a stage to validate against
- `--scm-branch, -b BRANCH` - Optional SCM branch to validate against (defaults to configured branch)

**Examples:**
```bash
# Validate current version
vertagus validate

# Validate against production stage rules
vertagus validate --stage-name prod

# Validate against specific branch
vertagus validate --scm-branch develop

# Use specific configuration file
vertagus validate --config ./my-config.yaml
```

**Exit codes:**
- `0` - Validation successful
- `1` - Validation failed

### `vertagus bump`

Increment the version number using configured bumpers.

```bash
vertagus bump [OPTIONS] [BUMPER_ARGS...]
```

**Options:**
- `--config, -c PATH` - Path to the configuration file
- `--stage-name, -s STAGE` - Name of a stage for stage-specific bumping
- `--no-write, -n` - If set, the version will not be written to manifest files (dry run)

**Bumper Arguments:**
Arguments passed to the bumper can be in the format `key=value` or as a single positional argument for backward compatibility:

```bash
# New key=value format
vertagus bump level=patch
vertagus bump level=minor
vertagus bump level=major
```

**Examples:**
```bash
# Use without keywords with `semantic_commit` bumper to auto-detect bump level
vertagus bump

# Bump minor version with key=value syntax
vertagus bump level=minor

# Dry run - show what would be bumped without writing
vertagus bump --no-write

# Bump with custom configuration
vertagus bump --config ./custom-config.yaml level=major
```

### `vertagus create-tag`

Create git tags based on the current version.

```bash
vertagus create-tag [OPTIONS]
```

**Options:**
- `--config, -c PATH` - Path to the configuration file (default: vertagus.toml in current directory)
- `--stage-name, -s STAGE` - Name of a stage for stage-specific tagging
- `--ref, -r REF` - An SCM ref that should be tagged (default: current commit)

**Examples:**
```bash
# Create tags for current version and commit
vertagus create-tag

# Create tags for specific stage
vertagus create-tag --stage-name prod

# Tag a specific commit
vertagus create-tag --ref abc123

# Use custom configuration
vertagus create-tag --config ./my-config.yaml
```

### `vertagus create-aliases`

Create alias tags based on configured aliases for a stage.

```bash
vertagus create-aliases [OPTIONS]
```

**Options:**
- `--config, -c PATH` - Path to the configuration file (default: vertagus.toml in current directory)
- `--stage-name, -s STAGE` - Name of a stage for stage-specific aliases
- `--ref, -r REF` - An SCM ref that should be tagged (default: current commit)

**Examples:**
```bash
# Create aliases for current version
vertagus create-aliases

# Create aliases for production stage (e.g., "stable", "latest")
vertagus create-aliases --stage-name prod

# Create aliases pointing to specific commit
vertagus create-aliases --ref v1.2.3
```

### `vertagus show-version`

Show the current version in the project's primary manifest. This is a convenience command that is often useful in CI automation, providing a single source of logic for version extraction.

**Example:**

```
$ vergatus show-version
0.4.0.dev0
```

## List Commands

These commands help you discover available components and configurations:

### `vertagus list-rules`

Display all available validation rules.

```bash
vertagus list-rules
```

Shows a table with:
- **Rule Name** - The name used in configuration
- **Config Usage** - Where to use it (`current` or `increment`)
- **Description** - What the rule validates

**Example output:**
```
Rule Name              Config Usage    Description
not_empty             current         Version string must not be empty
regex_mmp             current         Standard major.minor.patch format
any_increment         increment       Any version increment is allowed
```

### `vertagus list-bumpers`

Display all available version bumpers.

```bash
vertagus list-bumpers
```

Shows available bumper types that can be configured in your project.

### `vertagus list-aliases`

Display all available alias types.

```bash
vertagus list-aliases
```

Shows available alias generators with descriptions:
- **Alias Name** - The alias type name for configuration
- **Description** - What kind of alias it creates

### `vertagus list-manifests`

Display all supported manifest file types.

```bash
vertagus list-manifests
```

Shows supported manifest types:
- **Manifest Type** - The type name for configuration
- **Description** - What kind of manifest files are supported

### `vertagus list-scms`

Display all supported source control management systems.

```bash
vertagus list-scms
```

Shows available SCM providers (currently only `git` is supported).

## Configuration File Discovery

Vertagus automatically searches for configuration files in the current directory in this order:

1. `vertagus.toml`
2. `vertagus.yml` 
3. `vertagus.yaml`

You can override this by using the `--config` option with any command.

## Environment Variables

You can use environment variables to configure Vertagus:

- `VERTAGUS_LOG_LEVEL` - Log level (DEBUG, INFO, WARNING, ERROR) - default: INFO

## Stage-Specific Operations

Many commands support the `--stage-name` option to operate within the context of a specific stage:

```bash
# Validate using production stage rules
vertagus validate --stage-name prod

# Bump version for development stage
vertagus bump --stage-name dev

# Create production tags and aliases
vertagus create-tag --stage-name prod
vertagus create-aliases --stage-name prod
```

Running commands with this flag will load any configuration that is specific only to
that stage, as defined in your vertagus configuration file.
