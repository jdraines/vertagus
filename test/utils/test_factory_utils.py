from vertagus.utils import factory


def test_import_object():
    obj = factory.import_object("vertagus.utils.factory.import_object")
    assert obj == factory.import_object
