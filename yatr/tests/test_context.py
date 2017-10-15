from yatr import Context
from yatr.context import Null, Bash

#-------------------------------------------------------------------------------
# Context

def test_context():
    c = Context.from_yaml('foo', {})
    assert type(c) is Null
    
    assert c.run_command('ls', None) == 'ls'

#-------------------------------------------------------------------------------
# Bash

def test_bash():
    b = Context.from_yaml('foo', dict(instanceof='bash',
                                      env=dict(a='1', 
                                               b='{{bar}}'),
                                      opts=dict(v=True, 
                                                foo='{{a}}')))
    assert type(b) is Bash

    assert b.env == dict(a='1', b='{{bar}}')
    assert b.opts == dict(v=True, foo='{{a}}')
    b.resolve_macros(dict(a='4', bar='foo'))
    assert b.env == dict(a='1', b='foo')
    assert b.opts == dict(v=True, foo='4')
    
    assert b.run_command('ls', None) == 'bash -c "ls"'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)