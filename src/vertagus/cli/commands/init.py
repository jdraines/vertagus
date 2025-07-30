import click
import os
import yaml


@click.command("init")
@click.option("--dry-run", is_flag=True, help="Run the initialization wizard without making changes.")
def init_cmd(dry_run):
    vertagus_config_doc: str = _init_wizard()
    if dry_run:
        click.echo("Dry run mode: the following Vertagus configuration would be created:")
        click.echo("---")
        click.echo(vertagus_config_doc)
    else:
        write_vertagus_config(vertagus_config_doc)


def write_vertagus_config(vertagus_config_doc: str):
    if os.path.exists("vertagus.yml"):
        click.confirm("vertagus.yml already exists. Do you want to overwrite it?", abort=True)
    click.echo("Writing Vertagus configuration to vertagus.yml in the current directory.")
    with open("vertagus.yml", "w") as f:
        f.write(vertagus_config_doc)


def _init_wizard() -> str:
    click.echo("Vertagus initialization wizard:")

    version_strategy = click.prompt(
        "Select version strategy",
        type=click.Choice(["branch", "manifest"], case_sensitive=False),
        default=_default_version_strategy,
    )

    if version_strategy == "branch":
        target_branch = click.prompt("Target branch for the version strategy", default=_default_target_branch)
    else:
        target_branch = ""

    manifest_path = click.prompt("Path to the manifest file where your version is declared")
    supported_manifest_types = ["yaml", "json", "toml", "setuptools_pyproject"]
    suggested_type = None
    manifest_ext = os.path.splitext(manifest_path)[1].lstrip(".")
    if manifest_ext in supported_manifest_types:
        suggested_type = manifest_ext

    manifest_type = click.prompt(
        "Type of the manifest file",
        type=click.Choice(supported_manifest_types, case_sensitive=False),
        default=suggested_type,
    )
    if manifest_type != "setuptools_pyproject":
        version_loc = click.prompt("Location of the version in the manifest file as a dot-separated path")
    else:
        version_loc = ""

    bumper_type = click.prompt(
        "Type of the bumper to use",
        type=click.Choice(["semantic_commit", "semver"], case_sensitive=False),
        default="semantic_commit",
    )

    create_dev_prod_stages = click.confirm("Create dev and prod stages with default rules?", default=True)

    return _generate_vertagus_config(
        version_strategy=version_strategy,
        target_branch=target_branch,
        manifest_path=manifest_path,
        manifest_type=manifest_type,
        version_loc=version_loc,
        bumper_type=bumper_type,
        create_dev_prod_stages=create_dev_prod_stages,
    )


def _generate_vertagus_config(
    version_strategy: str,
    target_branch: str,
    manifest_path: str,
    manifest_type: str,
    version_loc: str,
    bumper_type: str,
    create_dev_prod_stages: bool,
) -> str:
    version_strategy_config_block = ""
    if version_strategy == "branch":
        manifest_loc_block = ""
        if version_loc:
            manifest_loc_block = f"manifest_loc: {version_loc}"
        version_strategy_config_block = _BRANCH_VERSION_STRATGEGY_CONFIG_BLOCK.format(
            target_branch=target_branch,
            manifest_path=manifest_path,
            manifest_type=manifest_type,
            manifest_loc_block=manifest_loc_block,
        )

    scm_block = _SCM_BLOCK.format(
        version_strategy=version_strategy, version_strategy_config_block=version_strategy_config_block
    )
    regex_mmp_rule = ""
    major_minor_alias = ""
    if not create_dev_prod_stages:
        regex_mmp_rule = "- regex_mmp"
        major_minor_alias = "- major.minor"

    loc_block = ""
    if version_loc:
        loc_block = f"loc: {version_loc}"

    project_block = _PROJECT_BLOCK.format(
        manifest_type=manifest_type,
        manifest_path=manifest_path,
        bumper_type=bumper_type,
        regex_mmp_rule=regex_mmp_rule,
        major_minor_alias=major_minor_alias,
        loc_block=loc_block,
    )

    stages_block = ""
    if create_dev_prod_stages:
        stages_block = _STAGES_BLOCK

    doc = scm_block + project_block + stages_block
    return yaml.dump(yaml.safe_load(doc), default_flow_style=False, sort_keys=False)


_default_version_strategy = "branch"
_default_target_branch = "main"

_SCM_BLOCK = """\
scm:
  type: git
  tag_prefix: v
  version_strategy: {version_strategy}
{version_strategy_config_block}
  
"""

_BRANCH_VERSION_STRATGEGY_CONFIG_BLOCK = """\
  target_branch: {target_branch}
  manifest_path: {manifest_path}
  manifest_type: {manifest_type}
  {manifest_loc_block}
"""

_PROJECT_BLOCK = """\
project:
  rules:
    current:
      - not_empty
      {regex_mmp_rule}
    increment:
      - any_increment
  aliases:
    - string:latest
    {major_minor_alias}

  manifests:
    - type: {manifest_type}
      path: {manifest_path}
      {loc_block}
      name: primary_manifest
  
  bumper:
    type: {bumper_type}

"""

_STAGES_BLOCK = """\
  stages:
    dev:
      rules:
        current:
          - regex_dev_mmp
    prod:
      aliases:
        - major.minor
      rules:
        current:
          - regex_mmp  
"""
