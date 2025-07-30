# Contributing

We welcome contributions to Vertagus! This guide will help you get started with contributing to the project.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- just for automation commands (See: https://github.com/casey/just)

### Setting up the Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/your-username/vertagus.git
   cd vertagus
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev,docs]"
   ```

4. **Verify the installation:**
   ```bash
   vertagus --help
   pytest
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the project conventions

3. **Run tests:**
   ```bash
   just test
   ```

4. **Run quality checks:**
   ```bash
   just lint-fix
   just format
   ```

5. **Test documentation locally:**
   ```bash
   just docs-serve
   ```

6. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Commit Message Convention

We follow the [Conventional Commits](https://conventionalcommits.org/) specification:

- `feat:` - New features (minor bump)
- `fix:` - Bug fixes (patch bump)
- `docs:` - Documentation changes (patch bump)
- `style:` - Code style changes (formatting, etc.) (patch bump)
- `refactor:` - Code refactoring (patch bump)
- `test:` - Adding or updating tests (patch bump)
- `chore:` - Maintenance tasks (patch bump)

Examples:
```
feat: add support for Cargo.toml manifests 
fix: resolve version comparison edge case
docs: update configuration examples
test: add tests for semantic bumper
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vertagus

# Run specific test file
pytest test/test_operations.py

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `test/` directory
- Follow the existing test structure and naming conventions
- Use descriptive test names that explain what is being tested
- Include both positive and negative test cases
- Mock external dependencies (git, file system) when appropriate

Example test structure:
```python
def test_version_bump_increments_patch_version():
    """Test that bump operation correctly increments patch version."""
    # Arrange
    initial_version = "1.0.0"
    
    # Act
    result = bump_version(initial_version, "patch")
    
    # Assert
    assert result == "1.0.1"
```

## Documentation

### Building Documentation

The documentation is built using MkDocs with the Material theme:

```bash
# Install docs dependencies
just docs-install

# Serve documentation locally
just docs-serve

# Build documentation
just docs build
```

### Documentation Guidelines

- Write clear, concise documentation
- Include code examples where appropriate
- Update relevant documentation when adding features
- Use proper Markdown formatting
- Test documentation examples to ensure they work

## Code Style

### Python Code Style

- Generally follow PEP 8 guidelines
- Use type hints ubiquitously, but maintain compatibility with Python 3.9
- Keep line length under 120 characters
- Use meaningful variable and function names
- Limit docstrings; prefer readable tests

### Code Formatting Tools

We primarily use ruff for linting and formatting.

## Contributing Guidelines

### Before Submitting a Pull Request

1. **Check existing issues** - It's best if your contribution addresses an existing issue or clearly describes a new problem/feature
2. **Run the full test suite** - Ensure all tests pass
3. **Update documentation** - Add or update relevant documentation
4. **Write/update tests** - Include tests for new functionality
5. **Follow commit conventions** - Use conventional commit messages

### Pull Request Process

1. **Create a pull request** with a clear title and description
2. **Reference related issues** using keywords like "Closes #123"
3. **Provide context** - Explain why the change is needed
4. **Include testing information** - Describe how you tested the changes
5. **Be responsive** - Address feedback and questions promptly

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Related Issue
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (describe)

## Testing
- [ ] Tests pass locally
- [ ] Added/updated tests for changes
- [ ] Manual testing performed

## Documentation
- [ ] Updated relevant documentation
- [ ] Added docstrings for new functions
```

Thank you for contributing to Vertagus! Your contributions help make version management easier for everyone.
