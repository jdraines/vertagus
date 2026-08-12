import click

from vertagus.cli.formatting import DisplayTableFormatter
from vertagus.rules.registry import get_all_rules, get_rule_category


@click.command("list-rules")
def list_rules_cmd():
    all_rules = get_all_rules()
    formatter = DisplayTableFormatter(max_width=240)
    header = ("Rule Name", "Type", "Description")
    rules_rows = [header]
    for rule_cls in all_rules.values():
        description = rule_cls.description if isinstance(rule_cls.description, str) else rule_cls().description
        rules_rows.append((rule_cls.name, get_rule_category(rule_cls), description))
    formatter.write_table(rules_rows, col_widths=[22, 22, 100], header=True)
    click.echo()
    click.echo(formatter.getvalue())
    click.echo()
