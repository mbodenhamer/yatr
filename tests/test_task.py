import os
import sys
from syn.five import PY2
from yatr import Command, Task, Env

#-------------------------------------------------------------------------------
# Task

def test_task():
    c = Command('python --version')
    t = Task(name='foo', commands=[c])

    env = Env()
    outs, errs, codes = t.run(env)

    if PY2:
        strs = errs
    else:
        strs = outs

    assert strs[0].split()[0] == 'Python'
    assert strs[0].split()[1] == sys.version.split()[0]

    t = Task.from_yaml('foo', {'command': 'pwd',
                               'if': 'true'})
    outs, errs, codes = t.run(env)
    assert outs == [os.getcwd() + '\n']
    assert errs == ['']
    assert codes == [0]

    t = Task.from_yaml('foo', {'command': 'pwd',
                               'if': 'false'})
    outs, errs, codes = t.run(env)
    assert outs == []
    assert errs == []
    assert codes == []

    t = Task.from_yaml('foo', {'command': 'pwd',
                               'ifnot': 'true'})
    outs, errs, codes = t.run(env)
    assert outs == []
    assert errs == []
    assert codes == []

    t = Task.from_yaml('foo', {'command': 'pwd',
                               'ifnot': 'false'})
    outs, errs, codes = t.run(env)
    assert outs == [os.getcwd() + '\n']
    assert errs == ['']
    assert codes == [0]

    t = Task(name='foo', commands=[Command('false'),
                                   Command('true')])
    outs, errs, codes = t.run(env)
    assert outs == ['']
    assert errs == ['']
    assert codes == [1]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
