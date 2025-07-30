# Run tests
test:
  test/test.sh

# Run the ruff linter
lint:
  ruff check .

# Run the ruff linter and fix issues
lint-fix:
  ruff check . --fix

# Run the ruff formatter
format:
  ruff format .

# Bump the version relying on semantic commit messages
bump:
  vertagus bump

# Bump the version by a specific semver level (major|minor|PATCH|tag)
bump-level level="patch":
  vertagus bump level={{level}}

# Serve the documentation locally
docs-serve:
  mkdocs serve

# Serve the documentation locally with a specific version
docs-serve-version version="dev":
  mike serve

# Build the documentation
docs-build:
  mkdocs build

# Deploy the documentation to GitHub Pages using Mike
docs-deploy version="dev":
  mike deploy {{version}}

# Deploy a versioned release of the documentation
docs-deploy-release version:
  mike deploy --push --update-aliases {{version}} latest
  mike set-default --push latest

# List all deployed documentation versions
docs-list:
  mike list

# Delete a documentation version
docs-delete version:
  mike delete {{version}}

# Set the default documentation version
docs-set-default version:
  mike set-default {{version}}

# Install documentation dependencies
docs-install:
  pip install -e ".[docs]"

# Initialize Mike for the first time
docs-init:
  ./scripts/mike-docs.sh init

# Mike helper script
docs-mike *args:
  ./scripts/mike-docs.sh {{args}}
