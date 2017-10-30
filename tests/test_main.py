import os
import sys
from jinja2 import UndefinedError
from mock import MagicMock
from nose.tools import assert_raises
from syn.base_utils import capture, assign, chdir
from yatr.main import _main, main, search_rootward
from yatr import __version__ as yver
from yatr import base as ybase
from yatr.base import read, tempdir, ValidationError

DIR = os.path.abspath(os.path.dirname(__file__))
TEST1 = os.path.join(DIR, 'test1.yml')
TEST3 = os.path.join(DIR, 'test3.yml')
TEST4 = os.path.join(DIR, 'test4.yml')
OUT = os.path.join(DIR, 'output')
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

        try:
            # Test --dump and task command-line arg passing
            with chdir(os.path.join(DIR, 'foo')):
                with capture() as (out, err):
                    _main('--dump')
                assert out.getvalue() == 'a = abc\nb = abcdef\nc = abcdefghi\n'

                _main('print', '5')
                assert read(OUT) == 'abcdefghi 5\n'

            # Test task referencing in task definition
            _main('-f', TEST3, 'a')
            assert read(OUT) == 'abc\n'

            _main('-f', TEST3, 'b')
            assert read(OUT) == 'abc\ndef\n'
        finally:
            os.remove(OUT)

        # Test --pull
        ybase.resolve_url(URL)
        with assign(ybase, 'download', MagicMock()):
            ybase.resolve_url(URL)
            assert ybase.download.call_count == 0

            _main('-f', TEST1)
            assert ybase.download.call_count == 0

            _main('-f', TEST1, '--pull')
            assert ybase.download.call_count == 1

            with tempdir() as d:
                assert_raises(ValidationError, _main, '-f', TEST1, '--cache-dir', d)
            assert ybase.download.call_count == 2

        # Test --validate
        with capture() as (out, err):
            _main('-f', TEST4)
        assert out.getvalue() == ''
        assert err.getvalue() == ''
        assert_raises(UndefinedError, _main, '-f', TEST4, '--validate')

        # Verify example
        with chdir(os.path.join(DIR, 'example')):
            # Test --dump-path
            with capture() as (out, err):
                _main('--dump-path')
            assert out.getvalue() == \
                '{}\n'.format(os.path.join(DIR, 'example/yatrfile.yml'))
            
            # Test -p
            with capture() as (out, err):
                _main('-p', 'bar', 'foo')
            assert out.getvalue() == 'echo bar\necho bar baz foo\n'

            with capture() as (out, err):
                _main('-p', 'cond4')
            assert out.getvalue() == 'ifnot: false\n\techo bar\n'

            # Test --dump
            with capture() as (out, err):
                _main('-f', 'C.yml', '--dump')
            assert out.getvalue() == 'a = baz\nb = ghi\nc = xyz\n'
            
            # Test -m
            with capture() as (out, err):
                _main('-f', 'C.yml', '-m' 'a=zab', '-m', 'd=jkl', '--dump')
            assert out.getvalue() == 'a = zab\nb = ghi\nc = xyz\nd = jkl\n'

            # Cover settings
            _main('-f', 'D.yml', '-s', 'silent=false')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
