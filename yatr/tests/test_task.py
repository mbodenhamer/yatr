from jinja2 import UndefinedError
from nose.tools import assert_raises
from yatr import Command, Task, Env, For, ValidationError

#-------------------------------------------------------------------------------
# For

def test_for():
    f = For.from_yaml('x in y')
    assert f.var == 'x'
    assert f.in_ == 'y'
    
    env = Env(env=dict(x='abc', y='def'))
    assert_raises(ValidationError, f.resolve_macros, env)

    env = Env(env=dict(x='abc', y=['d', 'e']))
    assert list(f.resolve_macros(env)) == [['x'], [['d', 'e']]]
    assert list(f.loop(env)) == [Env(env=dict(x='d', y=['d', 'e'])),
                                 Env(env=dict(x='e', y=['d', 'e']))]

    assert_raises(ValidationError, For.from_yaml, '-x in y')
    assert_raises(ValidationError, For.from_yaml, {'var': ['x'], 
                                                   'in': ['x', 'y']})

    f = For.from_yaml({'var': ['x', 'y'], 'in': ['A', 'B']})
    env = Env(env=dict(A=['a', 'b'], B=['c', 'd']))
    assert list(f.resolve_macros(env)) == [['x', 'y'], [['a', 'b'],
                                                        ['c', 'd']]]
    assert list(f.loop(env)) == [Env(env=dict(x='a', y='c', A=['a', 'b'],
                                              B=['c','d'])),
                                 Env(env=dict(x='a', y='d', A=['a', 'b'],
                                              B=['c','d'])),
                                 Env(env=dict(x='b', y='c', A=['a', 'b'],
                                              B=['c','d'])),
                                 Env(env=dict(x='b', y='d', A=['a', 'b'],
                                              B=['c','d']))]

    f = For.from_yaml({'var': ['x', 'y'], 'in': ['A', [1, 2]]})
    env = Env(env=dict(A=['a', 'b']))
    assert list(f.resolve_macros(env)) == [['x', 'y'], [['a', 'b'],
                                                        [1, 2]]]
    assert list(f.loop(env)) == [Env(env=dict(x='a', y=1, A=['a', 'b'])),
                                 Env(env=dict(x='a', y=2, A=['a', 'b'])),
                                 Env(env=dict(x='b', y=1, A=['a', 'b'])),
                                 Env(env=dict(x='b', y=2, A=['a', 'b']))]

    assert_raises(TypeError, For.from_yaml, {})
    assert_raises(ValidationError, For.from_yaml, {'var': ['x', 'y'], 
                                                   'in': ['A', 'B'],
                                                   'bar': 2})

#-------------------------------------------------------------------------------
# Command

def test_command():
    env = Env()
    c = Command('ls', context='bash')
    assert c.run_command(env) == 'bash -c "ls"'

    env = Env()
    c = Command('ls')
    assert c.run_command(env) == 'ls'

    env = Env(macros=dict(a='foo', b='bash'))
    env.resolve_macros()
    c = Command('ls {{a}}', context='{{b}}')
    assert c.run_command(env) == 'bash -c "ls foo"'
    assert c.command == 'ls {{a}}'

#-------------------------------------------------------------------------------
# Task

def test_task():
    t = Task(commands=[Command('{{a}}'),
                       Command('{{b}}')])

    env = Env()
    assert_raises(UndefinedError, t.run_commands, env)

    env = Env(macros=dict(a='ls', b='pwd'))
    env.resolve_macros()
    assert t.run_commands(env) == ['ls', 'pwd']

    
    t = Task(commands=[Command('ls')])
    assert t == Task.from_yaml('foo', 'ls')

    t = Task(commands=[Command('ls'), Command('pwd')])
    assert t == Task.from_yaml('foo', ['ls', 'pwd'])

    t = Task(commands=[Command('ls', context='bash')])
    assert t == Task.from_yaml('foo', dict(command='ls', context='bash'))

    assert_raises(ValidationError, Task.from_yaml, 'foo', 1)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
