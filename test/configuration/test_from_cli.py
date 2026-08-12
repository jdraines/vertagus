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
    assert config["scm"]["manifest_path"] == "sub/version.yaml"
    assert config["scm"]["manifest_type"] == "yaml"
    assert config["scm"]["manifest_loc"] == "project.version"


def test_branch_strategy_scm_manifest_is_relative_to_the_repository_not_the_project_root(tmp_path, monkeypatch):
    """The scm reads its manifest with `git show <ref>:<path>`, which resolves against the
    repository — the scm's root — while --root moves only the project."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pkg").mkdir()

    config = from_cli.build_master_config(
        opts(
            manifest=("pyproject.toml",),
            root="pkg",
            version_strategy="branch",
            target_branch="main",
        )
    )

    assert config["project"]["root"] == str(tmp_path / "pkg")
    assert config["scm"]["manifest_path"] == "pkg/pyproject.toml"


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


def test_merge_config_defaults_the_scm_manifest_like_a_configless_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = {"scm": {"type": "git", "target_branch": "main"}, "project": {"root": str(tmp_path)}}

    merged = from_cli.merge_config(base, opts(manifest=("version.yaml",), version_strategy="branch"))

    assert merged["scm"]["manifest_path"] == "version.yaml"
    assert merged["scm"]["manifest_type"] == "yaml"


def test_merge_config_keeps_the_files_scm_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    base = {
        "scm": {"type": "git", "version_strategy": "branch", "manifest_path": "from_file.yaml", "manifest_type": "yaml"},
        "project": {"root": str(tmp_path)},
    }

    merged = from_cli.merge_config(base, opts(manifest=("version.yaml",)))

    assert merged["scm"]["manifest_path"] == "from_file.yaml"


@pytest.mark.parametrize("flag, kwargs", [("--bumper", {"bumper": ""}), ("--target-branch", {"target_branch": ""})])
def test_empty_scalar_options_are_rejected(flag, kwargs):
    with pytest.raises(ConfigurationError, match=f"Invalid {flag}: the value is empty"):
        from_cli.build_config_overlay(opts(**kwargs))


def test_an_empty_tag_prefix_is_a_real_setting():
    """`--tag-prefix ''` is how a run says "no tag prefix", so it has to count as configuration."""
    assert opts(tag_prefix="").any_provided()
    assert from_cli.build_config_overlay(opts(tag_prefix=""))["scm"]["tag_prefix"] == ""

    merged = from_cli.merge_config({"scm": {"type": "git", "tag_prefix": "v"}, "project": {}}, opts(tag_prefix=""))
    assert merged["scm"]["tag_prefix"] == ""


def test_a_path_containing_an_equals_sign_can_be_written_as_a_spec(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manifest = from_cli.parse_manifest_spec("path=ver=1/version.yaml")
    assert manifest["path"] == str(tmp_path / "ver=1" / "version.yaml")


def test_a_misspelled_key_is_not_silently_read_as_a_path():
    """`pth=version.yaml` would otherwise infer a type from the extension and go looking
    for a file of that name, rather than saying the key is wrong."""
    with pytest.raises(ConfigurationError, match="must open with one of path, type, loc, name"):
        from_cli.parse_manifest_spec("pth=version.yaml")


def test_spec_keys_given_without_a_value_fall_back_to_their_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    manifest = from_cli.parse_manifest_spec("path=version.yaml,loc=,name=")
    assert manifest["loc"] is None
    assert manifest["name"] == "manifest_1"


def test_scm_manifest_rejects_a_name():
    with pytest.raises(ConfigurationError, match="unknown key 'name'"):
        from_cli._parse_scm_manifest_spec("path=version.yaml,name=x")
