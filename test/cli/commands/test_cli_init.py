import pytest
from unittest.mock import patch

import yaml
from vertagus.cli.commands import init


@pytest.mark.parametrize(
        ["version_strategy", "manifest_type", "create_dev_prod_stages", "expected_substring", "expected_not_substring"],
        [
            ("branch", "yaml", True, "stages:", None),
            ("branch", "yaml", False, None, "stages:"),
            ("branch", "yaml", False, "target_branch:", None),
            ("tag", "yaml", False, None, "target_branch:"),
            ("tag", "yaml", False, "loc:", None),
            ("tag", "setuptools_pyproject", False, None, "loc:"),
            ("branch", "setuptools_pyproject", False, None, "manifest_loc:"),
            ("branch", "toml", False, "manifest_loc:", None),
        ]
)
def test_generate_vertagus_config(
    version_strategy: str,
    manifest_type: str,
    create_dev_prod_stages: bool,
    expected_substring: str | None,
    expected_not_substring: str | None
):
    result = init._generate_vertagus_config(
        version_strategy=version_strategy,
        target_branch="main",
        manifest_path="path/to/manifest.yaml",
        manifest_type=manifest_type,
        version_loc="project.version" if manifest_type != "setuptools_pyproject" else "",
        bumper_type="semantic_commit",
        create_dev_prod_stages=create_dev_prod_stages
    )
    assert isinstance(result, str)
    if expected_substring:
        assert expected_substring in result
    if expected_not_substring:
        assert expected_not_substring not in result

    assert isinstance(yaml.load(result, Loader=yaml.SafeLoader), dict)

@pytest.mark.parametrize("inputs,expected_calls", [
    # Test branch strategy with dev/prod stages
    ({
        'version_strategy': 'branch',
        'target_branch': 'main',
        'manifest_path': 'pyproject.toml',
        'manifest_type': 'toml',
        'version_loc': 'project.version',
        'bumper_type': 'semantic_commit',
        'create_dev_prod_stages': True
    }, ['branch', 'main', 'pyproject.toml', 'toml', 'project.version', 'semantic_commit', True]),
    # Test manifest strategy without stages
    ({
        'version_strategy': 'tag', 
        'manifest_path': 'package.json',
        'manifest_type': 'json',
        'version_loc': 'version',
        'bumper_type': 'semver',
        'create_dev_prod_stages': False
    }, ['tag', '', 'package.json', 'json', 'version', 'semver', False])
])
def test_init_wizard_with_mocked_inputs(inputs, expected_calls):

    generate_config = init._generate_vertagus_config

    with patch('click.prompt') as mock_prompt, \
         patch('click.confirm') as mock_confirm, \
         patch('click.echo') as mock_echo, \
         patch('vertagus.cli.commands.init._generate_vertagus_config') as mock_generate_config:
         
        mock_generate_config.side_effect = generate_config

        # Configure mock return values
        side_effect = []
        side_effect.append(inputs['version_strategy'])
        if inputs['version_strategy'] == 'branch':
            side_effect.append(inputs['target_branch'])
        side_effect.append(inputs['manifest_path'])
        side_effect.append(inputs['manifest_type'])
        if inputs['manifest_type'] != 'setuptools_pyproject':
            side_effect.append(inputs['version_loc'])
        else:
            side_effect.append('')
        side_effect.append(inputs['bumper_type'])
        mock_prompt.side_effect = side_effect
        mock_confirm.return_value = inputs['create_dev_prod_stages']
        
        result = init._init_wizard()
        
        # Verify the result is valid YAML
        assert isinstance(result, str)
        parsed = yaml.safe_load(result)
        assert isinstance(parsed, dict)

        assert mock_generate_config.call_count == 1
        mock_generate_config.assert_called_once_with(
            version_strategy=expected_calls[0],
            target_branch=expected_calls[1],
            manifest_path=expected_calls[2],
            manifest_type=expected_calls[3],
            version_loc=expected_calls[4],
            bumper_type=expected_calls[5],
            create_dev_prod_stages=expected_calls[6]
        )
        
        
