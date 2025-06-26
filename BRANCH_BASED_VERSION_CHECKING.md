# Branch-Based Version Checking Feature

## Overview

This feature adds the ability to perform version checks against a target branch in source control, as an alternative to the existing tag-based version management strategy.

## Configuration

To enable branch-based version checking, update your `vertagus.yaml` file with the following configuration in the `scm` section:

```yaml
scm:
  type: git
  tag_prefix: v
  version_strategy: branch  # Options: "tag" (default) or "branch"
  target_branch: main       # Branch to compare versions against
```

### Configuration Options

- **`version_strategy`**: Determines the version checking strategy
  - `"tag"` (default): Use the traditional tag-based version checking
  - `"branch"`: Use the new branch-based version checking

- **`target_branch`**: The branch name to compare versions against (required when using branch strategy)
  - Example: `main`, `master`, `develop`, etc.

## How It Works

When the validation command is run with branch-based strategy:

1. The system fetches the latest changes from the remote repository
2. It extracts the version from the manifest file (e.g., `pyproject.toml`) on the target branch
3. It compares this version with the current version in the manifest file on the current branch
4. Validation passes or fails based on the configured rules (e.g., version must be incremented)

## Example Usage

1. Create or update your `vertagus.yaml` with branch-based configuration:

```yaml
scm:
  type: git
  version_strategy: branch
  target_branch: main
```

2. Run the validation command as usual:

```bash
vertagus validate
```

The validation will now compare your current branch's version against the version on the `main` branch instead of looking for the highest version tag.

## Benefits

- **Simplified Workflow**: No need to create tags for every version during development
- **Branch-Specific Validation**: Different branches can have different version progressions
- **Integration Friendly**: Works well with pull request workflows where versions are checked against the target branch

## Backward Compatibility

The feature is fully backward compatible. Existing configurations without the `version_strategy` field will continue to use the tag-based approach.