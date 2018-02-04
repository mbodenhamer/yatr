import yatr.env_decorators as yed
from syn.base_utils import capture
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
# Task

def test_task():
    env = Env()
    assert 'foo' not in env.tasks

    @env.task('foo')
    def footask(env, *args, **kwargs):
        pass

    assert footask(env) == 0
    assert env.tasks['foo'].run(env) == [0]

    @env.task('bar')
    def bartask(env, *args, **kwargs):
        raise Exception('bartask exception')

    with capture() as (out, err):
        assert bartask(env) == 1
    assert out.getvalue() == ''
    assert err.getvalue() == 'bartask exception\n'

    with capture() as (out, err):
        assert env.tasks['bar'].run(env) == [1]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
