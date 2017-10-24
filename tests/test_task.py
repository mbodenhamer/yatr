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

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
