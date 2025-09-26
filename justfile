# Run tests
[group('dev')]
test:
  uv run --extra dev test/test.sh

# Run the ruff linter
[group('dev')]
lint:
  uv run --extra dev ruff check .

# Run the ruff linter and fix issues
[group('dev')]
lint-fix:
  uv run --extra dev ruff check . --fix

# Run the ruff formatter
[group('dev')]
format:
  uv run --extra dev ruff format .

# Bump the version relying on semantic commit messages
[group('version')]
bump:
  uv run vertagus bump

# Bump the version by a specific semver level (major|minor|PATCH|tag)
[group('version')]
bump-level level="patch":
  uv run vertagus bump level={{level}}

# Serve the documentation locally
[group('docs')]
docs-serve:
  uv run --extra docs mkdocs serve

# Serve the documentation locally with a specific version
[group('docs')]
docs-serve-version version="dev":
  uv run --extra docs mike serve

# Build the documentation
[group('docs')]
docs-build:
  uv run --extra docs mkdocs build

# Deploy the documentation to GitHub Pages using Mike
[group('docs')]
docs-deploy version="dev":
  uv run git fetch origin gh-pages
  uv run --extra docs mike deploy {{version}}

# Deploy a versioned release of the documentation
[group('docs')]
docs-deploy-release version:
  uv run git fetch origin gh-pages
  uv run --extra docs mike deploy --push --update-aliases {{version}} latest
  uv run --extra docs mike set-default --push latest

# List all deployed documentation versions
[group('docs')]
docs-list:
  uv run --extra docs mike list

# Delete a documentation version
[group('docs')]
docs-delete version:
  uv run --extra docs mike delete {{version}}

# Set the default documentation version
[group('docs')]
docs-set-default version:
  uv run --extra docs mike set-default {{version}}

# Install documentation dependencies
[group('docs')]
docs-install:
  uv run --extra docs pip install -e ".[docs]"

# Initialize Mike for the first time
[group('docs')]
docs-init:
  uv run --extra docs ./scripts/mike-docs.sh init

# Mike helper script
[group('docs')]
docs-mike *args:
  uv run --extra docs ./scripts/mike-docs.sh {{args}}
