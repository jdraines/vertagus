import re
from vertagus.core.rule_bases import SingleVersionRule
from vertagus.utils import regex as regex_utils


class NotEmpty(SingleVersionRule):
    name = "not_empty"

    @classmethod
    def validate_version(cls, version):
        return bool(version)
    

class RegexRuleBase(SingleVersionRule):
    pattern: str = ""

    @classmethod
    def validate_version(cls, version):
        return bool(re.match(cls.pattern, version))


# Major-Minor-Patch Regex Rules

class RegexMmp(RegexRuleBase):
    name = "regex_mmp"
    pattern = regex_utils.patterns["mmp"]


class RegexDevMmp(RegexRuleBase):
    name = "regex_dev_mmp"
    pattern = regex_utils.patterns["dev_mmp"]


class RegexBetaMmp(RegexRuleBase):
    name = "regex_beta_mmp"
    pattern = regex_utils.patterns["beta_mmp"]


class RegexRcMmp(RegexRuleBase):
    name = "regex_rc_mmp"
    pattern = regex_utils.patterns["rc_mmp"]


class RegexAlphaMmp(RegexRuleBase):
    name = "regex_alpha_mmp"
    pattern = regex_utils.patterns["alpha_mmp"]


# Major-Minor Regex Rules

class RegexMm(RegexRuleBase):
    name = "regex_mm"
    pattern = regex_utils.patterns["mm"]


class RegexDevMm(RegexRuleBase):
    name = "regex_dev_mm"
    pattern = regex_utils.patterns["dev_mm"]


class RegexBetaMm(RegexRuleBase):
    name = "regex_beta_mm"
    pattern = regex_utils.patterns["beta_mm"]


class RegexRcMm(RegexRuleBase):
    name = "regex_rc_mm"
    pattern = regex_utils.patterns["rc_mm"]


class RegexAlphaMm(RegexRuleBase):
    name = "regex_alpha_mm"
    pattern = regex_utils.patterns["alpha_mm"]

