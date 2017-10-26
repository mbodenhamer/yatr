import os
import shlex
from subprocess import Popen, PIPE
from yatr import __version__ as yver

DIR = os.path.abspath(os.path.dirname(__file__))
TEST2 = os.path.join(DIR, 'test2.yml')

#-------------------------------------------------------------------------------

def test_invocation():
    p = Popen(shlex.split('yatr --version'), stdout=PIPE)
    out = p.communicate()[0].decode('utf-8').strip()
    assert out == 'yatr {}'.format(yver)
    assert p.returncode == 0

    p = Popen(shlex.split('yatr -f {} bad'.format(TEST2)), stdout=PIPE)
    out = p.communicate()[0].decode('utf-8').strip()
    assert out == ''
    assert p.returncode == 1

    p = Popen(shlex.split('yatr -f {} good'.format(TEST2)), stdout=PIPE)
    out = p.communicate()[0].decode('utf-8').strip()
    assert out == ''
    assert p.returncode == 0

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
