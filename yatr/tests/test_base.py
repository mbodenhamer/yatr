from jinja2 import UndefinedError
from nose.tools import assert_raises
from syn.base_utils import assign, capture
import yatr.base as ybase
from yatr.base import resolve, variables, ordered_macros, get_output,\
    str_to_bool, fix_functions

#-------------------------------------------------------------------------------
# Utilities

def test_resolve():
    assert resolve('abc', {}) == 'abc'
    assert_raises(UndefinedError, resolve, 'ab{{c}}', {})
    assert resolve('ab{{c}}', {}, lenient=True) == 'ab'
    assert resolve('ab{{c}}', dict(c='d')) == 'abd'

    # No autoescape
    assert resolve('"abc" <in >& /dev/null', {}) == '"abc" <in >& /dev/null'

    # list macros
    assert resolve(['{{a}}', '{{b}}', 'c'], dict(a='d', b='e')) == ['d', 'e', 'c']

def test_variables():
    assert variables('{{a}} {{b}}') == {'a', 'b'}
    assert variables(['{{a}}', '{{b}}', 'c']) == {'a', 'b'}
    assert_raises(Exception, variables, '{{a|foo}}')

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

    dct = dict(a = 'b',
               b = '{{a}}',
               c = ['{{b}}', 'c'],
               d = '{{c}}')
    assert list(ordered_macros(dct)) == [('a', 'b'), 
                                         ('b', '{{a}}'),
                                         ('c', ['{{b}}', 'c']),
                                         ('d', '{{c}}')]

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

def test_fix_functions():
    from yatr import Env

    class Foo(object):
        pass
    
    def fooer():
        ret = Foo()
        ret.hex = 'foo'
        return ret

    def identity(s=None, **kwargs):
        return s

    env = Env(macros=dict(abc='def'),
              jinja_functions=dict(abc=identity))
    with capture() as (out, err):
        with assign(ybase, 'uuid4', fooer):
            out = fix_functions("{{abc('sdf')}} {{abc}} {{abc('qwe')}}", 
                                {'abc'}, env)
            assert out == "{{abc_foo('sdf')}} {{abc}} {{abc_foo('qwe')}}"
            assert resolve(out, env.macros, jenv=env.jenv) == 'sdf def qwe'

            out = fix_functions("{{abc('ghi')}}", {'abc'}, env)
            assert out == "{{abc_foo('ghi')}}"
            assert resolve(out, env.macros, jenv=env.jenv) == 'ghi'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
