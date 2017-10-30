from jinja2 import UndefinedError
from nose.tools import assert_raises
from yatr.base import resolve, variables, ordered_macros, get_output,\
    str_to_bool

#-------------------------------------------------------------------------------
# Utilities

def test_resolve():
    assert resolve('abc', {}) == 'abc'
    assert_raises(UndefinedError, resolve, 'ab{{c}}', {})
    assert resolve('ab{{c}}', {}, lenient=True) == 'ab'
    assert resolve('ab{{c}}', dict(c='d')) == 'abd'

def test_variables():
    assert variables('{{a}} {{b}}') == {'a', 'b'}

def test_ordered_macros():
    assert list(ordered_macros({})) == []

    dct = dict(a = 'b')
    assert list(ordered_macros(dct)) == [('a', 'b')]

    dct = dict(a = 'b',
               b = '{{a}}',
               c = '{{b}}')
    assert list(ordered_macros(dct)) == [('a', 'b'), 
                                         ('b', '{{a}}'),
                                         ('c', '{{b}}')]

def test_get_output():
    out, code = get_output('true')
    assert out == ''
    assert code == 0

    out, code = get_output('false')
    assert out == ''
    assert code == 1

    out, code = get_output('python -c "raise Exception(\\"Test\\")"')
    assert 'Exception' in out
    assert code == 1

def test_str_to_bool():
    assert str_to_bool(1) is True
    assert str_to_bool(True) is True
    assert str_to_bool(0) is False
    assert str_to_bool(False) is False

    assert str_to_bool(' YES   ')
    assert str_to_bool(' TrUE   ')
    assert str_to_bool(' 1   ')

    assert not str_to_bool(' NO   ')
    assert not str_to_bool(' FalSE   ')
    assert not str_to_bool(' 0   ')

    assert_raises(TypeError, str_to_bool, [])
    assert_raises(TypeError, str_to_bool, 'foo')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
