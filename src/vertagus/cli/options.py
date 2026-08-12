"""Shared click options that let a command be configured without a configuration file."""

import click

_MANIFEST_HELP = (
    "A manifest that declares the version, as a path or as comma-separated key=value "
    "pairs: path=<path>[,type=<type>][,loc=<dotted.path>][,name=<name>]. Repeatable."
)

_RULE_HELP = (
    'A validation rule, either a rule name or \'name:{"key": "value"}\' to configure it. Repeatable. '
    "Run `vertagus list-rules` to see the available rules."
)

_SCM_MANIFEST_HELP = (
    "The manifest the SCM reads to find the previous version under the 'branch' version "
    "strategy, in the same format as --manifest. Defaults to the first --manifest."
)


def configless_options(f):
    """Add the options that build a configuration in place of a configuration file.

    Commands decorated with this receive the option values as extra keyword arguments,
    which they hand to :func:`vertagus.cli.utils.resolve_config` unchanged.
    """
    options = [
        click.option("--manifest", "-m", multiple=True, help=_MANIFEST_HELP),
        click.option("--rule", multiple=True, help=_RULE_HELP),
        click.option("--alias", multiple=True, help="An alias to apply to the version. Repeatable."),
        click.option("--bumper", default=None, help="The type of version bumper to use."),
        click.option("--root", default=None, help="The project root that relative manifest paths resolve against."),
        click.option("--scm-type", default=None, help="The SCM type. Defaults to 'git'."),
        click.option("--tag-prefix", default=None, help="A prefix for version tags, e.g. 'v'."),
        click.option(
            "--version-strategy",
            type=click.Choice(["tag", "branch"], case_sensitive=False),
            default=None,
            help="How the previous version is found: from SCM tags, or from a manifest on a branch.",
        ),
        click.option("--target-branch", default=None, help="The branch to read the previous version from."),
        click.option("--scm-manifest", default=None, help=_SCM_MANIFEST_HELP),
        click.option(
            "--print-config",
            is_flag=True,
            default=False,
            help="Print the resolved configuration as YAML and exit without running the command.",
        ),
    ]
    for option in reversed(options):
        f = option(f)
    return f
