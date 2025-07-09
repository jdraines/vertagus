from vertagus.bumpers.semantic import SemanticBumper


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
