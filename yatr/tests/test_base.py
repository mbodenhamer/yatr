from nose.tools import assert_raises
from yatr.base import resolve

#-------------------------------------------------------------------------------
# Utilities

def test_resolve():
    assert resolve('abc', {}) == 'abc'
    assert_raises(KeyError, resolve, 'ab{c}', {})
    assert resolve('ab{c}', dict(c='d')) == 'abd'
    assert resolve('ab{{c}}', {}) == 'ab'
    assert resolve('ab{{c}}', dict(c='d')) == 'abd'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
