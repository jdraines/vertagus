import click

from vertagus.rules.comparison.loader import (
    get_rules as get_comparison_rules,
    VersionComparisonRule
)
from vertagus.rules.single_version.loader import (
    get_rules as get_single_version_rules,
    SingleVersionRule
)
from vertagus.cli.formatting import DisplayTableFormatter

@click.command('list-rules')
def list_rules_cmd():
    single_version_rules: list[type[SingleVersionRule]] = get_single_version_rules()
    comparison_rules: list[type[VersionComparisonRule]] = [
        r for r in get_comparison_rules()
        if r.name != "manifests_comparison"
    ]
    formatter = DisplayTableFormatter(max_width=240)
    header = ('Rule Name', 'Config Usage', 'Description')
    rules_rows = [header]
    for rule in comparison_rules:
        rules_rows.append((rule.name, 'increment', rule.description))
    for rule in single_version_rules:
        rules_rows.append((rule.name, 'current', rule.description))
    formatter.write_table(
        rules_rows,
        col_widths=[22, 22, 100],
        header=True
    )
    click.echo()
    click.echo(formatter.getvalue())
    click.echo()
