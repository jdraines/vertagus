import tomllib

import pytest

from vertagus.providers.manifest import toml_edit


def test_replaces_only_the_targeted_value():
    text = '[project]\nname = "pkg"\nversion = "0.1.0"  # the version\n'
    edited = toml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == '[project]\nname = "pkg"\nversion = "0.2.0"  # the version\n'


def test_preserves_comments_blank_lines_and_formatting():
    text = (
        "# A leading comment\n"
        "\n"
        "[project]  # trailing comment on a header\n"
        "# a comment about the version\n"
        "version   =    '0.1.0'\n"
        "\n"
        "classifiers = [\n"
        '    "One",  # first\n'
        '    "Two",\n'
        "]\n"
    )
    edited = toml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == text.replace("'0.1.0'", '"0.2.0"')
    assert edited.count("#") == text.count("#")


def test_preserves_crlf_line_endings():
    text = '[project]\r\nversion = "0.1.0"\r\nname = "pkg"\r\n'
    edited = toml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == '[project]\r\nversion = "0.2.0"\r\nname = "pkg"\r\n'


def test_top_level_key():
    text = 'version = "0.1.0"\n[project]\nname = "pkg"\n'
    edited = toml_edit.replace_value(text, ["version"], "0.2.0")
    assert edited == 'version = "0.2.0"\n[project]\nname = "pkg"\n'


def test_dotted_key():
    text = '# comment\nproject.version = "0.1.0"\n'
    edited = toml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == '# comment\nproject.version = "0.2.0"\n'


def test_dotted_key_inside_a_table():
    text = '[tool]\nvertagus.version = "0.1.0"\n'
    edited = toml_edit.replace_value(text, ["tool", "vertagus", "version"], "0.2.0")
    assert edited == '[tool]\nvertagus.version = "0.2.0"\n'


def test_quoted_key():
    text = '[project]\n"my.version" = "0.1.0"\n'
    edited = toml_edit.replace_value(text, ["project", "my.version"], "0.2.0")
    assert edited == '[project]\n"my.version" = "0.2.0"\n'


def test_nested_table():
    text = '[a.b]\nversion = "0.1.0"\n[a.c]\nversion = "9.9.9"\n'
    edited = toml_edit.replace_value(text, ["a", "b", "version"], "0.2.0")
    assert edited == '[a.b]\nversion = "0.2.0"\n[a.c]\nversion = "9.9.9"\n'


def test_multiline_string_value_is_replaced():
    text = '[project]\nversion = """0.1.0"""\n'
    edited = toml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == '[project]\nversion = "0.2.0"\n'


def test_a_key_inside_a_multiline_string_is_not_mistaken_for_an_assignment():
    text = '[project]\nreadme = """\n[project]\nversion = "9.9.9"\n"""\nversion = "0.1.0"\n'
    edited = toml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == text.replace('version = "0.1.0"', 'version = "0.2.0"')
    assert '"9.9.9"' in edited


def test_a_key_inside_an_inline_table_is_scoped_to_it():
    text = '[project]\nauthor = { name = "x", version = "9.9.9" }\nversion = "0.1.0"\n'
    edited = toml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == text.replace('version = "0.1.0"', 'version = "0.2.0"')


def test_array_of_tables_keys_are_not_matched():
    text = '[[project]]\nversion = "0.1.0"\n'
    assert toml_edit.replace_value(text, ["project", "version"], "0.2.0") is None


def test_missing_key_returns_none():
    text = '[project]\nname = "pkg"\n'
    assert toml_edit.replace_value(text, ["project", "version"], "0.2.0") is None


def test_duplicate_matches_return_none():
    # Not valid TOML, but the scanner must not pick one arbitrarily.
    text = '[project]\nversion = "0.1.0"\n[project]\nversion = "0.1.0"\n'
    assert toml_edit.replace_value(text, ["project", "version"], "0.2.0") is None


def test_malformed_document_returns_none():
    assert toml_edit.replace_value('[project\nversion = "0.1.0"\n', ["project", "version"], "0.2.0") is None
    assert toml_edit.replace_value('[project]\nversion "0.1.0"\n', ["project", "version"], "0.2.0") is None
    assert toml_edit.replace_value('[project]\nversion = "0.1.0\n', ["project", "version"], "0.2.0") is None


@pytest.mark.parametrize(
    "version",
    ["1.0.0", '1.0.0+build"quoted"', "1.0.0+back\\slash", "1.0.0.dev0"],
)
def test_written_values_round_trip(version):
    text = '[project]\nversion = "0.1.0"\n'
    edited = toml_edit.replace_value(text, ["project", "version"], version)
    assert tomllib.loads(edited)["project"]["version"] == version


def test_replaces_non_string_values():
    text = "[project]\nversion = 1\n"
    edited = toml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == '[project]\nversion = "0.2.0"\n'


def test_replaces_a_value_followed_by_a_comment_without_eating_it():
    text = "[project]\nversion = 1  # a number, oddly\n"
    edited = toml_edit.replace_value(text, ["project", "version"], "0.2.0")
    assert edited == '[project]\nversion = "0.2.0"  # a number, oddly\n'
