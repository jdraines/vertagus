Vertagus
========

Vertagus is a tool to enable automation around maintining versions for your source code via a source control
management tool like git. You can automate checks to compare the current code version string with version string(s)
found on a specific branch of your repo or in repo tags.

Installation
------------

To install from pip:
  
```bash
pip install vertagus
```


To install from GitHub, clone and then pip install from source:

```bash
git clone https://github.com/jdraines/vertagus.git
pip install ./vertagus
```

Assumptions
-----------

Vertagus assumes some things about your development and versioning process:

- You are using some sort of packaging or distribution tool that contains a structured text document like `yaml` or 
  `toml`, and you declare your package version in that document. Vertagus calls these documents "manifests".
- You are using a source control manager (scm) like [git](https://git-scm.com/) to manage your code's changes. (Only git is currently supported.)

What it does
------------

### Configuration

Vertagus lets you declare some things about how you'd like to maintain your versioning:

- **Version Strategy** -- there are two strategies supported, `"branch"`, and "`tag`", and you declare this as part of
  your scm configuration. The `"branch"` strategy will look at a manifest file on a particular branch to determine the
  highest previous version. The `"tag"` strategy will look through tags in a repo to determine the highest previous
  version.
- **Manifests**, which are the source of truth for your versioning. (You can declare more than one if you like, but the
  first one will be considered the authoritative version.)
- **Rules** that your versioning should follow. For example, should it match a certain regex pattern? Should it always
  be incrementally higher than the last version? Is your version required to be in multiple manifests, and you need to
  know if they are out of sync with each other? For a list of rules, you can run `vertagus list-rules`.
- **Version Aliases** whose tags can move around a bit. For example, you might use major-minor-patch semantic
  versioning, but you'd like to maintain a major-minor alias on whatever your most recent patch version is.
- **Stages** of your development process that might need different rules or aliases. This might correspond to names like
  `dev`, `staging`, or `prod`, or it could be whatever else you like, depending on how you plan to use it.
- **Tag Prefixes** in case you're developing in a repository that holds multiple packages. Or maybe you just like 
  prefixes.
- **Version bumping handler** if you'd like an automated version bumper.

You declare these in either a `vertagus.toml` or `vertagus.yaml` file next to your package in your repository. 
Here's an example of the yaml format:

```yaml
scm:
  type: git
  tag_prefix: v
  version_strategy: tag
project:
  rules:
    current:
      - not_empty
    increment:
      - any_increment
  manifests:
    - type: setuptools_pyproject
      path: ./pyproject.toml
      name: pyproject
  bumper:
    type: semver
  stages:
    dev:
      rules:
        current:
          - regex_dev_mmp
    prod:
      aliases:
        - string:latest
        - major.minor
      rules:
        current:
          - regex_mmp
```

**Version strategies**

Vertagus uses your scm as the source of truth for previous versions, so the version strategy is declared within the `scm` configuration block. Two version strategies are supported, `tag` and `branch`.

In the case of using `tag`, running `vertagus validate` will look for version tags in your source control repo
and will attempt to extract the highest version seen there for use in validation of the local version state.

In the case of using `branch`, some additional config parameters are required:

```yaml
scm:
  # other scm params
  version_strategy: branch
  target_branch: main
  manifest_path: pyproject.toml  # path relative to repo root
  manifest_type: toml
  manifest_loc: ["project", "version"]
```

For `branch`, vertagus will extract the version from the manifest on the target branch to be used as the highest previous version for use in validation of the local version state. 

Also note that when `branch` strategy is specified, the branch to be used can be overridden in the `vertagus validate` CLI command. (See below.) This allows for adding automated version checks against other branches in the case of a git-flow style merge pattern.

**Available Rules**

For a complete list of rules that can be used in the configuration, you can run `vertagus list-rules`
to see the available rules and whether they can be used as `increment` or `current` rules.

(See the [configuration](https://github.com/jdraines/vertagus/blob/main/docs/configuration.md) docs for more on the format of this file.)

### Command Line Interface

_Vertagus provides two main operations in its `vertagus` CLI:_

#### `validate`

The `validate` command looks like this:

```
vertagus validate [--stage-name STAGE_NAME --config CONFIG_FILEPATH --scm-branch SCM_BRANCH_NAME]
```

The `validate` command will check your configuration and run any rules that you have declared there. If any of the rules
are being broken by the current state of the code, then it will exit with exit code 1. Otherwise, it exits without
error.

#### `create-tag`

The `create-tag` command looks like this:

```
vertagus create-tag [--stage-name STAGE_NAME --config CONFIG_FILEPATH]
```

The `create-tag` command will check your configuration and create tags for the current version of your code as well as
for any aliases that may be declared. These tags are created locally, but then pushed to your remote.

_Additionally, Vertagus provides a number of commands for discovering the names of rules, aliases, manifets, ans scm providers:_

#### `bump`

The `bump` command looks like this:

```
vertagus bump [--stage-name STAGE_NAME --config CONFIG_FILEPATH --no-write *BUMPER_ARGS]
```

If you have configured your vertagus config to use the semver bumper, for example:

```yaml
project:
  bumper:
    type: semver
```

Then the following command would update your manifest in-place locally to bump the minor version:

```
vertagus bump minor
```

#### `list-rules`

```
vertagus list-rules
```

#### `list-aliases`

```
vertagus list-aliases
```

#### `list-manifests`

```
vertagus list-manifests
```

#### `list-scms`

```
vertagus list-scms
````

### Continuous Integration

You may have noticed that the operations described above are a little odd to run just anywhere any time. Vertagus is
best suited to be executed in CI automation. For example, you could configure your scm platform to run the `validate`
command when a pull request is created as a check that must pass in order to merge. Then, you could configure your
scm platform to run the `create-tag` command after a pull request has merged and closed.

Documentation
-------------

For more documentation, see the [docs](https://github.com/jdraines/vertagus/blob/main/docs/index.md) directory.
