import yatr.env_decorators as yed
from nose.tools import assert_raises
from yatr import Env

#-------------------------------------------------------------------------------
# EnvDecorator

def test_envdecorator():
    env = Env()
    dec = yed.EnvDecorator(env, 'foo')
    assert_raises(NotImplementedError, dec, None)

#-------------------------------------------------------------------------------
# JinjaFilter

def test_jinjafilter():
    env = Env()
    assert 'foo' not in env.jinja_filters

    @env.jinja_filter('foo')
    def foofilt(value, **kwargs):
        return '{}_foo'.format(value)

    assert foofilt('bar') == 'bar_foo'
    assert env.jinja_filters['foo'] is foofilt

#-------------------------------------------------------------------------------
# JinjaFunction

def test_jinjafunction():
    env = Env()
    assert 'foo' not in env.jinja_functions

    @env.jinja_function('foo')
    def foofunc(value, **kwargs):
        return '{}_foo'.format(value)

    assert foofunc('bar') == 'bar_foo'
    assert env.jinja_functions['foo'] is foofunc

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
