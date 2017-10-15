from nose.tools import assert_raises
from yatr import Command, Task, Env, ValidationError

#-------------------------------------------------------------------------------
# Command

def test_command():
    env = Env()
    c = Command('ls', context='bash')
    assert c.run_command(env) == 'bash -c "ls"'
    c.resolve_macros({})
    assert c.run_command(env) == 'bash -c "ls"'

    env = Env()
    c = Command('ls')
    assert c.run_command(env) == 'ls'

    env = Env(macros=dict(a='foo', b='bash'))
    c = Command('ls {{a}}', context='{{b}}')
    c.resolve_macros(env.macro_env())
    assert c.run_command(env) == 'bash -c "ls foo"'

#-------------------------------------------------------------------------------
# Task

def test_task():
    t = Task(name='foo', commands=[Command('{{a}}'),
                                   Command('{{b}}')])
    env = Env(macros=dict(a='ls', b='pwd'))

    t.resolve_macros(env.macro_env())
    assert t.run_commands(env) == ['ls', 'pwd']

    
    t = Task(name='foo', commands=[Command('ls')])
    assert t == Task.from_yaml('foo', 'ls')

    t = Task(name='foo', commands=[Command('ls'), Command('pwd')])
    assert t == Task.from_yaml('foo', ['ls', 'pwd'])

    t = Task(name='foo', commands=[Command('ls', context='bash')])
    assert t == Task.from_yaml('foo', dict(command='ls', context='bash'))

    assert_raises(ValidationError, Task.from_yaml, 'foo', 1)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
