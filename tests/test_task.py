import os
import sys
from yatr import Command, Task, Env
from yatr.base import read, tempfile

#-------------------------------------------------------------------------------
# Task

def test_task():
    env = Env()
    with tempfile() as f:
        c = Command('python --version > ' + f + ' 2>&1')
        t = Task(name='foo', commands=[c])
        
        codes = t.run(env)
        strs = read(f)

        assert codes == [0]
        assert strs.split()[0] == 'Python'
        assert strs.split()[1] == sys.version.split()[0]
        
        # Test conditional execution
        t = Task.from_yaml('foo', {'command': 'pwd 2>&1 > ' + f,
                                   'if': 'true'})
        codes = t.run(env)
        assert read(f) == os.getcwd() + '\n'
        assert codes == [0]

        t = Task.from_yaml('foo', {'command': 'pwd 2>&1 > ' + f,
                                   'if': 'false'})
        codes = t.run(env)
        assert codes == []

        t = Task.from_yaml('foo', {'command': 'pwd 2>&1 > ' + f,
                                   'ifnot': 'true'})
        codes = t.run(env)
        assert codes == []

        t = Task.from_yaml('foo', {'command': 'pwd 2>&1 > ' + f,
                                   'ifnot': 'false'})
        codes = t.run(env)
        assert read(f) == os.getcwd() + '\n'
        assert codes == [0]

        # Test exit_on_error
        t = Task.from_yaml('foo', ['true', 'false', 'true'])
        codes = t.run(env)
        assert codes == [0, 1]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
