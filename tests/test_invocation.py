import os
import shlex
from subprocess import Popen, PIPE
from yatr import __version__ as yver
from yatr.base import get_output
from syn.base_utils import chdir

DIR = os.path.abspath(os.path.dirname(__file__))
TEST2 = os.path.join(DIR, 'test2.yml')

#-------------------------------------------------------------------------------

def test_invocation():
    p = Popen(shlex.split('yatr --version'), stdout=PIPE)
    out = p.communicate()[0].decode('utf-8').strip()
    assert out == 'yatr {}'.format(yver)
    assert p.returncode == 0

    out, code = get_output('yatr -f {} bad'.format(TEST2))
    assert out == ''
    assert code == 1

    out, code = get_output('yatr -f {} good'.format(TEST2))
    assert out == ''
    assert code == 0

    # Verify example
    with chdir(os.path.join(DIR, 'example')):
        # Test --dump-path
        out, code = get_output('yatr --dump-path')
        assert out == '{}\n'.format(os.path.join(DIR, 'example/yatrfile.yml'))
        assert code == 0

        # Test nested include
        out, code = get_output('yatr -f C.yml --dump')
        assert out == 'a = baz\nb = ghi\nc = xyz\n'

        # Test included task
        out, code = get_output('yatr foo')
        assert out == 'bar\n'

        # Test default task
        out, code = get_output('yatr')
        assert out == 'bar\n'

        # Test example tasks
        out, code = get_output('yatr cwd')
        assert out == os.getcwd() + '\n'

        out, code = get_output('yatr bar')
        assert out == 'bar\nbar baz xyz\n'

        out, code = get_output('yatr bar foo')
        assert out == 'bar\nbar baz foo\n'

        out, code = get_output('yatr -v bar foo')
        assert out == 'echo bar\nbar\necho bar baz foo\nbar baz foo\n'
        
        out, code = get_output('yatr cond1')
        assert out.strip().split() == ['A.yml',
                                       'B.yml',
                                       'C.yml',
                                       'D.yml',
                                       'yatrfile.yml']

        out, code = get_output('yatr cond2')
        assert out == ''

        out, code = get_output('yatr cond3')
        assert out == ''

        out, code = get_output('yatr cond4')
        assert out == 'bar\n'

        out, code = get_output('yatr -v cond4')
        assert out == 'false\necho bar\nbar\n'

        # Test settings.silent
        out, code = get_output('yatr -f D.yml foo')
        assert out == ''
        assert code == 0

        out, code = get_output('yatr -f D.yml -s silent=false foo')
        assert out == 'bar\n'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
