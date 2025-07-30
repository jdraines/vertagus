from unittest.mock import MagicMock
import pytest

from vertagus.bumpers.semantic import (
    SemanticBumper,
    SemanticCommitBumper,
    SemverBumperException
)


class TestSemanticBumper:


    def test_semantic_bumper_mmp(self):

        bumper = SemanticBumper()

        # Test major bump
        assert bumper.bump("1.0.0", "major") == "2.0.0"
        assert bumper.bump("1.2.3", "major") == "2.0.0"

        # Test minor bump
        assert bumper.bump("1.0.0", "minor") == "1.1.0"
        assert bumper.bump("1.2.3", "minor") == "1.3.0"

        # Test patch bump
        assert bumper.bump("1.0.0", "patch") == "1.0.1"
        assert bumper.bump("1.2.3", "patch") == "1.2.4"


    def test_semantic_bumper_mmp_tag(self):

        bumper = SemanticBumper("dev")

        # Test tag bump with dot separator
        assert bumper.bump("1.0.0-dev", "tag") == "1.0.0-dev1"
        assert bumper.bump("1.0.0-dev0", "tag") == "1.0.0-dev1"
        assert bumper.bump("1.2.3-dev1", "tag") == "1.2.3-dev2"

        # Test tag bump with hyphen separator
        assert bumper.bump("1.0.0-dev", "tag") == "1.0.0-dev1"
        assert bumper.bump("1.0.0-dev0", "tag") == "1.0.0-dev1"
        assert bumper.bump("1.2.3-dev1", "tag") == "1.2.3-dev2"

        # Test tag bump with no separator
        assert bumper.bump("1.0.0dev", "tag") == "1.0.0dev1"
        assert bumper.bump("1.0.0dev0", "tag") == "1.0.0dev1"
        assert bumper.bump("1.2.3dev1", "tag") == "1.2.3dev2"

        # Test non-tag bump when tag is set
        assert bumper.bump("1.2.3-dev1", "major") == "2.0.0"
        assert bumper.bump("1.2.3-dev1", "minor") == "1.3.0"
        assert bumper.bump("1.2.3-dev1", "patch") == "1.2.4"


class TestSemanticCommitBumper:

    def test__get_level_from_conventional_commits_breaking_change(self):
        bumper = SemanticCommitBumper()
        assert bumper._get_level_from_conventional_commits([
            "feat: add new feature",
            "fix: fix bug",
            "feat: new thing\nBREAKING CHANGE: change API"
        ]) == "major"

    def test__get_level_from_conventional_commits_breaking_change_lower(self):
        bumper = SemanticCommitBumper()
        assert bumper._get_level_from_conventional_commits([
            "feat: add new feature",
            "fix: fix bug",
            "feat: new thing\nbreaking change: change API"
        ]) == "minor"

    def test__get_level_from_conventional_commits_exclamation(self):
        bumper = SemanticCommitBumper()
        assert bumper._get_level_from_conventional_commits([
            "feat!: add a crazy feature",
            "fix: fix bug",
            "chore: update dependencies"
        ]) == "major"

    def test__get_level_from_conventional_commits_feat(self):
        bumper = SemanticCommitBumper()
        assert bumper._get_level_from_conventional_commits([
            "feat: add new feature",
            "fix: fix bug",
            "chore: update dependencies"
        ]) == "minor"

    def test__get_level_from_conventional_commits_fix(self):
        bumper = SemanticCommitBumper()
        assert bumper._get_level_from_conventional_commits([
            "fix: fix bug",
            "chore: update dependencies"
        ]) == "patch"

    def test__get_level_from_conventional_commits_no_conventional_commits(self):
        bumper = SemanticCommitBumper()
        assert bumper._get_level_from_conventional_commits([
            "fix bug",
            "BREAKING CHANGE: this is bad."
        ]) == "patch"


    @pytest.mark.parametrize(
        "commit_messages, expected",
        [
            (["feat: add new feature"], ("feat", None, None, "add new feature", False)),
            (["fix: fix bug"], ("fix", None, None, "fix bug", False)),
            (["chore: update dependencies"], ("chore", None, None, "update dependencies", False)),
            (["docs: update documentation"], ("docs", None, None, "update documentation", False)),
            (["style: improve formatting"], ("style", None, None, "improve formatting", False)),
            (["refactor: refactor code"], ("refactor", None, None, "refactor code", False)),
            (["test: add tests"], ("test", None, None, "add tests", False)),
            (["perf: improve performance"], ("perf", None, None, "improve performance", False)),
            (["feat!: add breaking change"], ("feat", None, "!", "add breaking change", False)),
            (["feat(scope): breaking change: add new feature"], ("feat", "scope", None, "breaking change: add new feature", False)),
            (["feat(scope): BREAKING CHANGE: add new feature"], ("feat", "scope", None, "BREAKING CHANGE: add new feature", True)),
            (["fix(scope): fix bug"], ("fix", "scope", None, "fix bug", False)),
            (["chore(scope)!: did too much on this chore"], ("chore", "scope", "!", "did too much on this chore", False)),
            (["fix method name"], None),
            (["BREAKING CHANGE! check this out"], None),
        ]
    )
    def test__extract_conventional_commits(self, commit_messages, expected):
        bumper = SemanticCommitBumper()
        result = bumper._extract_conventional_commits(commit_messages)
        if len(result) != 0:
            assert result[0] == expected
        else:
            assert expected is None

    def test_bump(self):
        bumper = SemanticCommitBumper()
        bumper.determine_bump_level = MagicMock(return_value="minor")
        
        assert bumper.bump("1.0.0", MagicMock(), level=None) == "1.1.0"
        assert bumper.bump("1.0.0", MagicMock(), level="major") == "2.0.0"
        
        with pytest.raises(SemverBumperException):
            bumper.bump("1.0.0", MagicMock(), level="patch")
        
        with pytest.raises(SemverBumperException):
            bumper.bump("1.0.0.dev0", MagicMock(), level="tag")
        