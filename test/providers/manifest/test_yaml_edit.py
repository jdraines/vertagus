import yaml

import pytest

from vertagus.providers.manifest import yaml_edit


def test_replaces_only_the_targeted_value():
    text = "project:\n  name: pkg\n  version: 0.1.0  # the version\n"
    edited = yaml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == "project:\n  name: pkg\n  version: '0.2.0'  # the version\n"


def test_preserves_comments_blank_lines_and_formatting():
    text = (
        "# A leading comment\n"
        "\n"
        "project:  # the project\n"
        "  # a comment about the version\n"
        "  version:    '0.1.0'\n"
        "\n"
        "  deps:\n"
        "    - click  # the CLI framework\n"
    )
    edited = yaml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == text.replace("'0.1.0'", "'0.2.0'")
    assert edited.count("#") == text.count("#")


def test_preserves_crlf_line_endings():
    text = "project:\r\n  version: 0.1.0\r\n  name: pkg\r\n"
    edited = yaml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == "project:\r\n  version: '0.2.0'\r\n  name: pkg\r\n"


def test_top_level_key():
    text = "version: 0.1.0\nname: pkg\n"
    edited = yaml_edit.replace_value(text, ["version"], "0.2.0")
    assert edited == "version: '0.2.0'\nname: pkg\n"


def test_deeply_nested_key():
    text = "a:\n  b:\n    version: 0.1.0\n  c:\n    version: 9.9.9\n"
    edited = yaml_edit.replace_value(text, ["a", "b", "version"], "0.2.0")
    assert edited == "a:\n  b:\n    version: '0.2.0'\n  c:\n    version: 9.9.9\n"


def test_quoting_style_is_preserved():
    assert yaml_edit.replace_value('version: "0.1.0"\n', ["version"], "0.2.0") == 'version: "0.2.0"\n'
    assert yaml_edit.replace_value("version: '0.1.0'\n", ["version"], "0.2.0") == "version: '0.2.0'\n"


def test_a_plain_value_is_quoted_so_its_type_cannot_change():
    edited = yaml_edit.replace_value("version: 0.1.0\n", ["version"], "1.0")
    assert edited == "version: '1.0'\n"
    assert yaml.safe_load(edited)["version"] == "1.0"


def test_quoted_key():
    text = 'project:\n  "my.version": 0.1.0\n'
    edited = yaml_edit.replace_value(text, ["project", "my.version"], "0.2.0")
    assert edited == 'project:\n  "my.version": \'0.2.0\'\n'


def test_a_hash_inside_a_quoted_value_is_not_treated_as_a_comment():
    text = "version: '0.1.0#1'  # real comment\n"
    edited = yaml_edit.replace_value(text, ["version"], "0.2.0")
    assert edited == "version: '0.2.0'  # real comment\n"


def test_keys_inside_a_sequence_are_not_matched():
    text = "manifests:\n  - name: a\n    version: 0.1.0\n"
    assert yaml_edit.replace_value(text, ["manifests", "version"], "0.2.0") is None


def test_a_sequence_elsewhere_does_not_block_the_edit():
    text = "manifests:\n  - name: a\n    version: 9.9.9\nproject:\n  version: 0.1.0\n"
    edited = yaml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == text.replace("version: 0.1.0", "version: '0.2.0'")


def test_a_key_inside_a_block_scalar_is_not_mistaken_for_an_assignment():
    text = "readme: |\n  project:\n  version: 9.9.9\nversion: 0.1.0\n"
    edited = yaml_edit.replace_value(text, ["version"], "0.2.0")
    assert edited == text.replace("version: 0.1.0", "version: '0.2.0'")
    assert "9.9.9" in edited


def test_missing_key_returns_none():
    assert yaml_edit.replace_value("project:\n  name: pkg\n", ["project", "version"], "0.2.0") is None


def test_duplicate_matches_return_none():
    text = "project:\n  version: 0.1.0\nproject:\n  version: 0.1.0\n"
    assert yaml_edit.replace_value(text, ["project", "version"], "0.2.0") is None


@pytest.mark.parametrize(
    "text",
    [
        "project: {version: 0.1.0}\n",  # flow mapping
        "project: &anchor\n  version: 0.1.0\n",  # anchor
        "project:\n\tversion: 0.1.0\n",  # tab indentation
        "project:\n  version: 0.1.0\n---\nproject:\n  version: 0.2.0\n",  # multiple documents
        "just a scalar\n",  # not a mapping
    ],
)
def test_unmodelled_yaml_returns_none(text):
    assert yaml_edit.replace_value(text, ["project", "version"], "0.3.0") is None


@pytest.mark.parametrize("version", ["1.0.0", "1.0.0+it's", '1.0.0+say"what"', "1.0.0.dev0"])
def test_written_values_round_trip(version):
    for original in ("version: 0.1.0\n", "version: '0.1.0'\n", 'version: "0.1.0"\n'):
        edited = yaml_edit.replace_value(original, ["version"], version)
        assert yaml.safe_load(edited)["version"] == version


def test_a_version_containing_a_newline_is_refused():
    assert yaml_edit.replace_value("version: 0.1.0\n", ["version"], "0.2.0\nname: evil") is None
