# Documentation

This directory contains the MkDocs-based documentation for Vertagus.

## Setup

1. Install documentation dependencies:
   ```bash
   pip install -e ".[docs]"
   ```

2. Serve documentation locally:
   ```bash
   mkdocs serve
   ```

3. Build documentation:
   ```bash
   mkdocs build
   ```

## Structure

- `mkdocs.yml` - Main configuration file
- `docs/` - Documentation source files
  - `index.md` - Homepage
  - `getting-started.md` - Getting started guide
  - `configuration.md` - Configuration reference
  - `cli-reference.md` - CLI command reference
  - `examples.md` - Usage examples
  - `contributing.md` - Contributing guide
  - `gen_ref_pages.py` - Script to generate API reference

## Automatic API Documentation

The API reference is automatically generated from docstrings using `mkdocstrings`. The `gen_ref_pages.py` script scans the source code and creates documentation pages for all modules.

## Deployment

Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the main branch via GitHub Actions (`.github/workflows/docs.yml`).
