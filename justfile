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

# Build the documentation
docs-build:
  mkdocs build

# Deploy the documentation to GitHub Pages
docs-deploy:
  mkdocs gh-deploy

# Install documentation dependencies
docs-install:
  pip install -e ".[docs]"
