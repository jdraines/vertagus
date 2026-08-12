# CLI Reference

Vertagus provides a comprehensive command-line interface for version management. This page documents all available commands and their options.

## Global Options

These options are available for most commands:

- `--config, -c PATH` - Path to configuration file (default: search for vertagus.yaml/yml/toml in current directory)
- `--help` - Show help message and exit

The commands that read a configuration file (`validate`, `bump`, `create-tag`, `create-aliases`,
`show-version`, `show-alias`) also accept the [configuration options](#configuration-free-usage)
below, which let you run Vertagus without a configuration file at all.

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
- Any of the [configuration options](#configuration-free-usage), e.g. `--manifest` and `--rule`

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
- Any of the [configuration options](#configuration-free-usage), e.g. `--manifest` and `--bumper`

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
- `--config, -c PATH` - Path to the configuration file
- `--stage-name, -s STAGE` - Name of a stage for stage-specific tagging
- `--ref, -r REF` - An SCM ref that should be tagged (default: current commit)
- Any of the [configuration options](#configuration-free-usage), e.g. `--manifest` and `--tag-prefix`

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
- `--config, -c PATH` - Path to the configuration file
- `--stage-name, -s STAGE` - Name of a stage for stage-specific aliases
- `--ref, -r REF` - An SCM ref that should be tagged (default: current commit)
- Any of the [configuration options](#configuration-free-usage), e.g. `--manifest` and `--alias`

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

## Configuration-Free Usage

The settings that make up a single project configuration can each be given directly on the command
line, so you can run Vertagus in a project that has no `vertagus.yaml`:

```bash
vertagus validate --manifest src/pyproject.toml --rule not_empty --rule any_increment
```

This is handy for one-off checks, for CI jobs that only need a single rule, and for trying
Vertagus out before committing to a configuration file.

**Options:**

| Option | Description |
| --- | --- |
| `--manifest, -m SPEC` | A manifest that declares the version. Repeatable. |
| `--rule SPEC` | A validation rule. Repeatable. |
| `--alias ALIAS` | An alias to apply to the version. Repeatable. |
| `--bumper TYPE` | The version bumper to use, e.g. `semver`. |
| `--root PATH` | The project root that relative manifest paths resolve against. |
| `--scm-type TYPE` | The SCM type. Defaults to `git`. |
| `--tag-prefix PREFIX` | A prefix for version tags, e.g. `v`. |
| `--version-strategy {tag,branch}` | How the previous version is found. Defaults to `tag`. |
| `--target-branch BRANCH` | The branch to read the previous version from. |
| `--scm-manifest SPEC` | The manifest the SCM reads under the `branch` strategy. |
| `--print-config` | Print the resolved configuration as YAML and exit. |

### Manifest specs

`--manifest` accepts either a bare path or a comma-separated list of `key=value` pairs, with the
keys `path`, `type`, `loc` and `name`. `--scm-manifest` takes the same form minus `name`, which an
SCM manifest has no use for:

```bash
# Bare path; the type is inferred from the file name
vertagus validate --manifest pyproject.toml

# Explicit type and version location
vertagus validate --manifest 'path=package.json,type=json,loc=version'

# Several manifests, one of them named
vertagus validate \
  --manifest pyproject.toml \
  --manifest 'path=docs/version.yaml,loc=project.version,name=docs' \
  --rule manifests_comparison
```

The manifest type is inferred from the file name when `type` is omitted: `pyproject.toml` is a
`setuptools_pyproject` manifest, and the `.toml`, `.yaml`, `.yml` and `.json` extensions map to the
manifest types of the same name. Any other file name needs an explicit `type`. Run
`vertagus list-manifests` to see the available types.

Manifest paths given on the command line are resolved against `--root`, or against the current
directory when `--root` is not given. The one exception is `--scm-manifest`, whose path is read out
of source control and so is always relative to the repository root. A value that contains an `=`
has to be written as an explicit `path=...` so that it is not mistaken for a misspelled key.

### Rule specs

`--rule` accepts either a bare rule name or a rule name and a JSON object holding its
configuration, separated by a colon:

```bash
# Bare rule names
vertagus validate -m pyproject.toml --rule not_empty --rule regex_mmp

# A configured rule
vertagus validate -m pyproject.toml --rule 'custom_regex:{"pattern": "^1\\..+"}'
```

Run `vertagus list-rules` to see the available rules.

### Version strategies

The default version strategy is `tag`, which needs no further configuration. Under the `branch`
strategy, Vertagus reads the previous version from a manifest on the target branch:

```bash
vertagus validate \
  --manifest pyproject.toml \
  --rule any_increment \
  --version-strategy branch \
  --target-branch main
```

When you do not pass `--scm-manifest`, the `branch` strategy reads the same file as your first
`--manifest`, which is the usual arrangement — including alongside `--config`, when `--manifest` is
what named the manifest and the file itself sets no SCM manifest of its own. Pass `--scm-manifest`
when the version lives in a different file on the target branch.

The derived path is expressed relative to the repository, not to `--root`, since that is how source
control addresses a file. Under `--root pkg`, a `--manifest pyproject.toml` gives the SCM
`pkg/pyproject.toml`.

### Combining options with a configuration file

The three ways of configuring a command are:

1. **No configuration options** - Vertagus discovers and reads a configuration file, exactly as it
   always has.
2. **Configuration options with no `--config`** - the options are the whole configuration. No
   configuration file is discovered in the current directory, so an ad hoc run cannot silently pick
   up settings you did not ask for.
3. **Configuration options together with `--config`** - the options override their counterparts in
   the file. This is the convenient form for CI, where a job needs one setting changed:

   ```bash
   # Validate the committed configuration, but against a release branch's tag prefix
   vertagus validate --config vertagus.yaml --tag-prefix release-
   ```

   Repeatable options replace the file's list outright rather than adding to it: passing a single
   `--rule` means that rule and no other — for the project. A stage named with `--stage-name` still
   contributes its own rules from the file on top of that.

A few settings stay file-only, because they describe more than one configuration at once or belong
to a specific provider: stages, a bumper's own options beyond its type, and the git SCM's `root` and
`remote_name`. Because stages are among them, `--stage-name` requires a configuration file;
configure a stage's rules directly with `--rule` instead when you are running without one.

### Inspecting the resolved configuration

`--print-config` prints the configuration a command would run with and exits, which is both a
debugging aid and an easy way to grow an ad hoc invocation into a real configuration file:

```bash
vertagus validate -m pyproject.toml --rule not_empty --print-config > vertagus.yaml
```

Manifest paths come back out relative to the project root, and a root that is just the directory
the file would sit in is left out, so the result is a configuration file that still works on another
machine. A manifest outside the root stays absolute, since a trail of `..` would be no clearer.

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
