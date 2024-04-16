class Rule:
    name: str = "base"


class ComparisonRule(Rule):

    @classmethod
    def compare(cls, value1, value2):
        raise NotImplementedError('Method compare must be implemented in subclass')
    


class ValidationRule(Rule):

    @classmethod
    def validate(cls, value):
        raise NotImplementedError('Method validate must be implemented in subclass')