from nose.tools import assert_raises
from syn.base_utils import assign, capture

from yatr import Context, Env, ValidationError
from yatr.context import Bash, Null, Python, PythonCallable

#-------------------------------------------------------------------------------
# Context

def test_context():
    env = Env()
    c = Context.from_yaml('foo', {})
    assert type(c) is Null
    
    assert c.run_command('ls', env) == 'ls'
    assert_raises(NotImplementedError, c.verbose, 'ls', env)

#-------------------------------------------------------------------------------
# Bash

def test_bash():
    env = Env()
    b = Context.from_yaml('foo', dict(instanceof='bash',
                                      env=dict(a='1', 
                                               b='{{bar}}'),
                                      opts=dict(v=True, 
                                                foo='{{a}}')))
    assert type(b) is Bash

    assert b.envvars == dict(a='1', b='{{bar}}')
    assert b.opts == dict(v=True, foo='{{a}}')
    envvars, opts = b.resolve_macros(Env(env=dict(a='4', bar='foo')))
    assert envvars == dict(a='1', b='foo')
    assert opts == dict(v=True, foo='4')
    
    assert b.run_command('ls', env) == 'bash -c "ls"'

#-------------------------------------------------------------------------------
# Python

def test_python():
    env = Env()
    p = Context.from_yaml('foo', dict(instanceof='python'))
    assert type(p) is Python

    assert p.run_command('1/1', env) == '1/1'
    assert p.run('1/1', env) == 0

    with capture() as (out, err):
        assert p.run('1/1', env, verbose=True, preview=True) is None
    assert out.getvalue() == 'Python eval: 1/1\n'

    with capture() as (out, err):
        assert p.run('1/1', env, verbose=True) == 0
    assert out.getvalue() == 'Python eval: 1/1\n'

    with capture() as (out, err):
        assert p.run('1/0', env) == 1
    assert out.getvalue() == ''
    assert 'zero' in err.getvalue()

#-------------------------------------------------------------------------------
# PythonCallable

def test_pythoncallable():
    env = Env()
    p = Context.from_yaml('foo', dict(instanceof='python_callable'))
    assert type(p) is PythonCallable

    def foo(env, *args, **kwargs):
        return 0

    with capture() as (out, err):
        assert p.run(foo, env, verbose=True) == 0
    assert out.getvalue() == 'foo()\n'

    with assign(env, 'env', dict(a=1, b=2)):
        with capture() as (out, err):
            assert p.run(foo, env, verbose=True, preview=True) is None
        assert out.getvalue() == 'foo(a=1, b=2)\n'

        env.env['_1'] = 'a'
        env.env['_2'] = 'b'

        with capture() as (out, err):
            assert p.run(foo, env, verbose=True, preview=True) is None
        assert out.getvalue() == 'foo(a, b, a=1, b=2)\n'

        del env.env['a']
        del env.env['b']

        with capture() as (out, err):
            assert p.run(foo, env, verbose=True, preview=True) is None
        assert out.getvalue() == 'foo(a, b)\n'

#-------------------------------------------------------------------------------
# SSH

def test_ssh():
    env = Env()
    assert_raises(ValidationError, Context.from_yaml,
                  'foo', dict(instanceof='ssh'))
                                      
    s = Context.from_yaml('foo', dict(instanceof='ssh',
                                      opts=dict(user='foo',
                                                hostname='bar')))
    assert s.run_command('ls', env) == 'ssh foo@bar "ls"'

    env.contexts['foo'] = s
    sb = Context.from_yaml('bar', dict(instanceof='bash',
                                       inside='foo'))
    assert sb.run_command('ls', env) == 'ssh foo@bar "bash -c \"ls\""'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
