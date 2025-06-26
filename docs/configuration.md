[index](./index.md)

Configuration
=============

Vertagus uses `toml` or `yaml` for its configuration format. 
You can see the `vertagus.yaml` file at the root of this repository 
for an example. Here's what that same file looks like in `toml` format:

```toml
[scm]
type = "git"
tag_prefix = "v"
version_strategy = "branch"
target_branch = "main"
manifest_path = "./pyproject.toml"
manifest_type = "setuptools_pyproject"

[project.rules]
current = ["not_empty"]
increment = ["any_increment"]
manifest_comparisons = []

[project.stages.dev.rules]
current = ["regex_dev_mmp"]

[project.stages.beta]
aliases = ["string:latest"]

[project.stages.beta.rules]
current = ["regex_beta_mmp"]

[project.stages.prod]
aliases = ["string:stable", "string:latest", "major.minor"]

[project.stages.prod.rules]
current = ["regex_mmp"]

[[project.manifests]]
type = "setuptools_pyproject"
path = "./pyproject.toml"
name = "pyproject"
```
