from nose.tools import assert_raises
from syn.base_utils import capture

from yatr import Context, Env, ValidationError
from yatr.context import Null, Bash, Python

#-------------------------------------------------------------------------------
# Context

def test_context():
    env = Env()
    c = Context.from_yaml('foo', {})
    assert type(c) is Null
    
    assert c.run_command('ls', env) == 'ls'

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
        assert p.run('1/0', env) == 1
    assert out.getvalue() == ''
    assert 'zero' in err.getvalue()

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
