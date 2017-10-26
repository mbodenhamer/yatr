import os
import sys
from mock import MagicMock
from nose.tools import assert_raises
from syn.base_utils import capture, assign, chdir
from yatr.main import _main, main, search_rootward
from yatr import __version__ as yver
from yatr import base as ybase

DIR = os.path.abspath(os.path.dirname(__file__))
TEST1 = os.path.join(DIR, 'test1.yml')
TEST3 = os.path.join(DIR, 'test3.yml')
URL = 'https://raw.githubusercontent.com/mbodenhamer/yatrfiles/master/yatrfiles/test/test1.yml'

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

        # Test --dump and task command-line arg passing
        with chdir(os.path.join(DIR, 'foo')):
            with capture() as (out, err):
                _main('--dump')
            assert out.getvalue() == 'a = abc\nb = abcdef\nc = abcdefghi\n'

            with capture() as (out, err):
                _main('print', '5')
            assert out.getvalue() == 'abcdefghi 5\n'

        # Test task referencing in task definition
        with capture() as (out, err):
            _main('-f', TEST3, 'a')
        assert out.getvalue() == 'abc\n'

        with capture() as (out, err):
            _main('-f', TEST3, 'b')
        assert out.getvalue() == 'abc\ndef\n'

        # Test --pull
        with assign(ybase, 'download', MagicMock()):
            ybase.resolve_url(URL)
            assert ybase.download.call_count == 0

            _main('-f', TEST1)
            assert ybase.download.call_count == 0

            _main('-f', TEST1, '--pull')
            assert ybase.download.call_count == 1

        # Verify example
        with chdir(os.path.join(DIR, 'example')):
            # Test --dump-path
            with capture() as (out, err):
                _main('--dump-path')
            assert out.getvalue() == \
                '{}\n'.format(os.path.join(DIR, 'example/yatrfile.yml'))

            # import ipdb; ipdb.set_trace()
            # _main('foo')

            with capture() as (out, err):
                _main('foo')
            assert out.getvalue() == 'bar\n'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
