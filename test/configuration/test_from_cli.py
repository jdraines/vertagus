import os

import pytest

from vertagus.configuration import from_cli
from vertagus.errors import ConfigurationError


def opts(**kwargs):
    return from_cli.CliConfigOptions(**kwargs)


def test_any_provided():
    assert not opts().any_provided()
    assert opts(manifest=("pyproject.toml",)).any_provided()
    assert opts(rule=("not_empty",)).any_provided()
    assert opts(tag_prefix="v").any_provided()


@pytest.mark.parametrize(
    "path, expected",
    [
        ("pyproject.toml", "setuptools_pyproject"),
        ("src/pkg/pyproject.toml", "setuptools_pyproject"),
        ("version.toml", "toml"),
        ("version.yaml", "yaml"),
        ("version.yml", "yaml"),
        ("version.json", "json"),
    ],
)
def test_infer_manifest_type(path, expected):
    assert from_cli.infer_manifest_type(path) == expected


def test_infer_manifest_type_unknown():
    with pytest.raises(ConfigurationError, match="Could not determine the manifest type"):
        from_cli.infer_manifest_type("VERSION")


def test_parse_manifest_spec_bare_path():
    manifest = from_cli.parse_manifest_spec("pyproject.toml", base_dir="/proj")
    assert manifest == {
        "name": "manifest_1",
        "type": "setuptools_pyproject",
        "path": os.path.abspath(os.path.join("/proj", "pyproject.toml")),
        "loc": None,
    }


def test_parse_manifest_spec_fields():
    manifest = from_cli.parse_manifest_spec(
        "path=version.json,type=json,loc=project.version,name=api", index=2, base_dir="/proj"
    )
    assert manifest["name"] == "api"
    assert manifest["type"] == "json"
    assert manifest["loc"] == "project.version"
    assert manifest["path"] == os.path.abspath(os.path.join("/proj", "version.json"))


def test_parse_manifest_spec_defaults_name_by_index():
    assert from_cli.parse_manifest_spec("a.json", index=1)["name"] == "manifest_2"


def test_parse_manifest_spec_resolves_relative_to_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manifest = from_cli.parse_manifest_spec("sub/version.yaml")
    assert manifest["path"] == str(tmp_path / "sub" / "version.yaml")


@pytest.mark.parametrize(
    "spec, message",
    [
        ("", "the value is empty"),
        ("type=json", "no path was given"),
        ("path=a.json,bogus=1", "unknown key"),
        ("path=a.json,justtext", "expected 'key=value' pairs"),
    ],
)
def test_parse_manifest_spec_errors(spec, message):
    with pytest.raises(ConfigurationError, match=message):
        from_cli.parse_manifest_spec(spec)


def test_parse_rule_spec_bare_name():
    assert from_cli.parse_rule_spec("not_empty") == "not_empty"


def test_parse_rule_spec_with_config():
    assert from_cli.parse_rule_spec('regex:{"pattern": "^\\\\d+"}') == {
        "type": "regex",
        "config": {"pattern": "^\\d+"},
    }


@pytest.mark.parametrize(
    "spec, message",
    [
        (":{}", "no rule name was given"),
        ("regex:{not json}", "not valid JSON"),
        ("regex:[1, 2]", "must be a JSON object"),
    ],
)
def test_parse_rule_spec_errors(spec, message):
    with pytest.raises(ConfigurationError, match=message):
        from_cli.parse_rule_spec(spec)


def test_build_master_config_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = from_cli.build_master_config(opts(manifest=("pyproject.toml",), rule=("not_empty", "any_increment")))
    assert config["scm"] == {"type": "git"}
    assert config["project"]["root"] == str(tmp_path)
    assert config["project"]["rules"] == ["not_empty", "any_increment"]
    assert config["project"]["manifests"][0]["path"] == str(tmp_path / "pyproject.toml")


def test_build_master_config_full(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = from_cli.build_master_config(
        opts(
            manifest=("version.yaml",),
            rule=("not_empty",),
            alias=("string:latest",),
            bumper="semver",
            scm_type="git",
            tag_prefix="v",
            version_strategy="tag",
            target_branch="main",
            scm_manifest="path=other.yaml,type=yaml,loc=project.version",
        )
    )
    assert config["scm"] == {
        "type": "git",
        "tag_prefix": "v",
        "version_strategy": "tag",
        "target_branch": "main",
        "manifest_path": "other.yaml",
        "manifest_type": "yaml",
        "manifest_loc": "project.version",
    }
    assert config["project"]["aliases"] == ["string:latest"]
    assert config["project"]["bumper"] == {"type": "semver"}


def test_build_master_config_requires_a_manifest():
    with pytest.raises(ConfigurationError, match="No manifests were configured"):
        from_cli.build_master_config(opts(rule=("not_empty",)))


def test_build_master_config_root_option(tmp_path):
    config = from_cli.build_master_config(opts(manifest=("pyproject.toml",), root=str(tmp_path)))
    assert config["project"]["root"] == str(tmp_path)
    assert config["project"]["manifests"][0]["path"] == str(tmp_path / "pyproject.toml")


def test_branch_strategy_defaults_scm_manifest_to_first_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = from_cli.build_master_config(
        opts(manifest=("path=sub/version.yaml,loc=project.version",), version_strategy="branch", target_branch="main")
    )
    assert config["scm"]["manifest_path"] == os.path.join("sub", "version.yaml")
    assert config["scm"]["manifest_type"] == "yaml"
    assert config["scm"]["manifest_loc"] == "project.version"


def test_branch_strategy_keeps_explicit_scm_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = from_cli.build_master_config(
        opts(manifest=("version.yaml",), version_strategy="branch", scm_manifest="other.json")
    )
    assert config["scm"]["manifest_path"] == "other.json"
    assert config["scm"]["manifest_type"] == "json"


def test_tag_strategy_does_not_add_an_scm_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = from_cli.build_master_config(opts(manifest=("version.yaml",)))
    assert "manifest_path" not in config["scm"]


def test_merge_config_overrides_only_named_settings():
    base = {
        "scm": {"type": "git", "tag_prefix": "v", "target_branch": "main"},
        "project": {
            "root": "/proj",
            "rules": ["not_empty", "any_increment"],
            "manifests": [{"name": "pyproject", "type": "setuptools_pyproject", "path": "./pyproject.toml"}],
            "stages": {"dev": {"rules": ["regex_dev_mmp"]}},
        },
    }
    merged = from_cli.merge_config(base, opts(rule=("not_empty",), tag_prefix="release-"))

    assert merged["scm"]["tag_prefix"] == "release-"
    assert merged["scm"]["target_branch"] == "main"
    assert merged["project"]["rules"] == ["not_empty"]
    assert merged["project"]["manifests"] == base["project"]["manifests"]
    assert merged["project"]["stages"] == base["project"]["stages"]


def test_merge_config_does_not_mutate_the_base():
    base = {"scm": {"type": "git"}, "project": {"rules": ["not_empty"]}}
    from_cli.merge_config(base, opts(rule=("any_increment",)))
    assert base["project"]["rules"] == ["not_empty"]
