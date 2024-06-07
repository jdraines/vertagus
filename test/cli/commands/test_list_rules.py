import pytest
from click.testing import CliRunner
from vertagus.cli.commands import list_rules_cmd


@pytest.fixture
def runner():
    return CliRunner()


def test_validate_simple(runner: CliRunner):
    result = runner.invoke(list_rules_cmd, [])
    assert result.exit_code == 0

