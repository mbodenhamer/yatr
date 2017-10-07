from subprocess import Popen, PIPE
from yatr import __version__ as yver

#-------------------------------------------------------------------------------

def test_invocation():
    p = Popen('yatr', stdout=PIPE)
    out = p.communicate()[0].decode('utf-8').strip()
    assert out == 'yatr {}'.format(yver)
    assert p.returncode == 0

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
