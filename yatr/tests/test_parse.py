from nose.tools import assert_raises

from yatr import Document
from yatr.parse import get_delete

#-------------------------------------------------------------------------------
# Utilities

def test_get_delete():
    d1 = dict(a=1, b=2)
    d2 = {}
    get_delete(d1, d2, 'a', 3)
    assert d1 == dict(b=2)
    assert d2 == dict(a=1)

    get_delete(d1, d2, 'b', 3, 'd')
    assert d1 == {}
    assert d2 == dict(a=1, d=2)

    get_delete(d1, d2, 'c', 3)
    assert d1 == {}
    assert d2 == dict(a=1, d=2, c=3)

#-------------------------------------------------------------------------------
# Document

def test_document():
    d = Document()
    assert not d.tasks

    d = Document.from_yaml({})
    assert not d.tasks

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
