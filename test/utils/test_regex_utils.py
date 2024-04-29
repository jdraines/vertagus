def test_import_regex_utils():
    from vertagus.utils import regex
    assert regex.patterns is not None
