import os
import yatr.base as ybase

from jinja2 import UndefinedError
from nose.tools import assert_raises
from syn.base_utils import assign, capture, setitem
from yatr.base import resolve, variables, ordered_macros, get_output,\
    str_to_bool, fix_functions, args_kwargs_from_env, expand_path

#-------------------------------------------------------------------------------
# Utilities

def test_expand_path():
    assert expand_path('/foo/bar') == '/foo/bar'

    home = os.path.expanduser('~')
    assert expand_path('~/foo/bar') == '{}/foo/bar'.format(home)

    with setitem(os.environ, 'FOO_BAR', 'baz'):
        assert expand_path('~/foo/$FOO_BAR') == '{}/foo/baz'.format(home)
        assert expand_path('~/foo/${FOO_BAR}_fix.yml') == \
            '{}/foo/baz_fix.yml'.format(home)

def test_resolve():
    assert resolve('abc', {}) == 'abc'
    assert_raises(UndefinedError, resolve, 'ab{{c}}', {})
    assert resolve('ab{{c}}', {}, lenient=True) == 'ab'
    assert resolve('ab{{c}}', dict(c='d')) == 'abd'

    # No autoescape
    assert resolve('"abc" <in >& /dev/null', {}) == '"abc" <in >& /dev/null'

    # list macros
    assert resolve(['{{a}}', '{{b}}', 'c'], dict(a='d', b='e')) == ['d', 'e', 'c']

    # dict macros
    assert resolve(dict(a='{{b}}', b='1'), dict(b='2')) == dict(a='2', b='1')
    assert resolve('{{a.b}}', dict(a=dict(b='c'))) == 'c'

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

    with capture() as (out_, err):
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

def test_args_kwargs_from_env():
    assert list(args_kwargs_from_env({})) == [(), {}]
    assert list(args_kwargs_from_env(dict(_1='a',
                                          _2='b',
                                          _3='c',
                                          a='aa',
                                          b='bb'))) == \
        [('a', 'b', 'c'), dict(a='aa', b='bb')]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
