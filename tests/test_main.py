import os
import sys
from nose.tools import assert_raises
from syn.base_utils import capture, assign, chdir
from yatr.main import _main, main, search_rootward
from yatr import __version__ as yver

DIR = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------------------------------------------------
# main

def test_main():
    assert_raises(RuntimeError, search_rootward, '/')

    with assign(sys, 'exit', lambda *args, **kwargs: None):
        with capture() as (out, err):
            _main('--version')
        assert out.getvalue() == 'yatr {}\n'.format(yver)

        with assign(sys, 'argv', ['', '--version']):
            with capture() as (out, err):
                main()
        assert out.getvalue() == 'yatr {}\n'.format(yver)

        with capture() as (out, err):
            _main('-f', os.path.join(DIR, 'yatrfile1.yml'), '--validate')
        assert out.getvalue() == 'Validation successful\n'

        with chdir(os.path.join(DIR, 'foo')):
            with capture() as (out, err):
                _main('--dump')
            assert out.getvalue() == 'a = abc\nb = abcdef\nc = abcdefghi\n'

            with capture() as (out, err):
                _main('print', '5')
            assert out.getvalue() == 'abcdefghi 5\n'

        # Example
        with chdir(os.path.join(DIR, 'example')):
            with capture() as (out, err):
                _main('--validate')
            assert out.getvalue() == 'Validation successful\n'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
