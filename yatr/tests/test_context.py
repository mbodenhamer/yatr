from yatr import Context, Env
from yatr.context import Null, Bash

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

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
