# Documentation Version Management with Mike

This project uses [Mike](https://github.com/jimporter/mike) for managing versioned documentation. Mike allows us to deploy multiple versions of our documentation and provides a version selector in the UI.

## Quick Start

### First Time Setup

1. Install documentation dependencies:
   ```bash
   just docs-install
   ```

2. Initialize Mike with the current version:
   ```bash
   just docs-init
   ```

This will:
- Deploy the current version (from `pyproject.toml`) as both the version number and `latest`
- Deploy a `dev` version for development documentation
- Set `latest` as the default version

### Daily Development

- **Serve docs locally**: `just docs-serve`
- **Serve specific version**: `just docs-serve-version dev`
- **Deploy dev version**: `just docs-deploy dev`
- **List all versions**: `just docs-list`

### Release Process

When releasing a new version:

1. **Deploy release version**:
   ```bash
   just docs-deploy-release 1.2.0
   ```
   This will deploy version `1.2.0`, alias it as `latest`, and set it as the default.

2. **Or use the helper script**:
   ```bash
   just docs-mike release 1.2.0
   ```

## Available Commands

### Justfile Commands

- `just docs-serve` - Serve documentation locally
- `just docs-serve-version VERSION` - Serve specific version locally  
- `just docs-build` - Build documentation
- `just docs-deploy VERSION` - Deploy specific version
- `just docs-deploy-release VERSION` - Deploy version as latest release
- `just docs-list` - List all deployed versions
- `just docs-delete VERSION` - Delete a version
- `just docs-set-default VERSION` - Set default version
- `just docs-install` - Install documentation dependencies
- `just docs-init` - Initialize Mike (first time setup)
- `just docs-mike COMMAND` - Use the Mike helper script

### Mike Helper Script

The `scripts/mike-docs.sh` script provides additional convenience commands:

```bash
# Initialize Mike
./scripts/mike-docs.sh init

# Deploy development docs
./scripts/mike-docs.sh deploy-dev

# Deploy a release version
./scripts/mike-docs.sh release 1.0.0

# List versions
./scripts/mike-docs.sh list

# Serve docs locally
./scripts/mike-docs.sh serve [version]

# Delete a version (with confirmation)
./scripts/mike-docs.sh delete old-version

# Set default version
./scripts/mike-docs.sh set-default 1.0.0
```

## GitHub Actions Integration

The documentation is automatically deployed via GitHub Actions using the helper script:

- **On push to `main`**: Runs `./scripts/mike-docs.sh deploy-dev` to deploy to the `dev` channel
- **On tag push** (e.g., `v1.0.0`): Runs `./scripts/mike-docs.sh release 1.0.0` to deploy as a versioned release and update `latest`
- **On pull requests**: Builds documentation for preview (uploaded as artifact)

The helper script automatically detects CI environments and includes the `--push` flag when needed.

## Version Management Strategy

- **`latest`**: Always points to the most recent stable release
- **`dev`**: Development version, updated on every push to main
- **Semantic versions** (e.g., `1.0.0`, `1.1.0`): Tagged releases
- **`main`**: Could be used for bleeding-edge development if needed

## MkDocs Configuration

The `mkdocs.yml` includes Mike-specific configuration:

```yaml
extra:
  version:
    provider: mike
    default: latest
```

This enables the version selector in the Material theme.

## Troubleshooting

### First Time Setup Issues

If you encounter issues during first-time setup:

1. Ensure you have push access to the repository
2. Make sure the `gh-pages` branch exists or can be created
3. Check that Mike is installed: `pip show mike`

### Version Not Showing

If a version doesn't appear in the selector:

1. Check if it was deployed: `just docs-list`
2. Verify the version exists in the `gh-pages` branch
3. Clear browser cache and reload

### Local Development

For local development, you can use regular MkDocs commands:

```bash
# Serve without versioning
mkdocs serve

# Build without versioning  
mkdocs build
```

But for testing the version selector, use:

```bash
# Serve with Mike (shows version selector)
mike serve
```
