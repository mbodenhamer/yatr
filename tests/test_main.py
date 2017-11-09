import os
import sys
import shutil
from jinja2 import UndefinedError
from mock import MagicMock
from nose.tools import assert_raises
from syn.base_utils import capture, assign, chdir, setitem
from yatr.main import _main, main, search_rootward, find_bash_completions,\
    dump_bash_completions, BASH_COMPLETION_MESSAGE, USAGE, OPTION_STRINGS,\
    DEFAULT_SETTINGS
from yatr import __version__ as yver
from yatr import base as ybase
from yatr.base import read, tempdir, ValidationError

DIR = os.path.abspath(os.path.dirname(__file__))
TEST1 = os.path.join(DIR, 'test1.yml')
TEST2 = os.path.join(DIR, 'test2.yml')
TEST3 = os.path.join(DIR, 'test3.yml')
TEST4 = os.path.join(DIR, 'test4.yml')
TEST5 = os.path.join(DIR, 'test5.yml')
TEST6 = os.path.join(DIR, 'test6.yml')
TEST7 = os.path.join(DIR, 'test7.yml')
TEST8 = os.path.join(DIR, 'test8.yml')
TEST8_IN = os.path.join(DIR, 'test8.j2')
TEST8_OUT = os.path.join(DIR, 'test8.bash')
DOCKERFILE = os.path.join(DIR, 'example/render/Dockerfile')
OUT = os.path.join(DIR, 'output')
URL = 'https://raw.githubusercontent.com/mbodenhamer/yatrfiles/master/yatrfiles/test/test1.yml'

def listify(s):
    return [o.strip() for o in s.strip().split()]

#-------------------------------------------------------------------------------

DFRENDER = '''# -*- dockerfile -*-
FROM python:2-alpine

RUN pip install -U --no-cache \\
    syn>=0.0.14

CMD ["python2"]'''

#-------------------------------------------------------------------------------
# Bash completions

def test_bash_completions():
    settings = DEFAULT_SETTINGS
    
    with chdir(DIR):
        out = find_bash_completions(['--cache-dir', '/app', 'print'], 1)
        assert out == []

        out = find_bash_completions(['-f', '/app', 'print'], 1)
        assert out == []

        out = find_bash_completions(['--yatrfile', '/app', 'print'], 1)
        assert out == []


        out = find_bash_completions(['-'], 0)
        assert out == OPTION_STRINGS

        out = find_bash_completions(['p'], 0)
        assert out == ['print']

        out = find_bash_completions(['xyz'], 0)
        assert out == []

        out = find_bash_completions(['-m', 'a'], 1)
        assert out == ['a']

        out = find_bash_completions(['--macro', 'a'], 1)
        assert out == ['a']

        out = find_bash_completions(['-m', 'a='], 1)
        assert out == []

        out = find_bash_completions(['-s', 's'], 1)
        assert out == ['silent']

        out = find_bash_completions(['--setting', 's'], 1)
        assert out == ['silent']

        out = find_bash_completions(['-s', 'silent='], 1)
        assert out == []

        out = find_bash_completions(['--dump-path', 'p'], 1)
        assert out == ['print']

        out = find_bash_completions(['print', 'xyz'], 1)
        assert out == []
        
        out = find_bash_completions(['-i', '/app'], 1)
        assert out == []

        out = find_bash_completions(['-o', '/app'], 1)
        assert out == []


        out = find_bash_completions([], 0)
        assert out == ['print']

        out = find_bash_completions(['-m'], 1)
        assert out == ['a', 'b', 'c']

        out = find_bash_completions(['--macro'], 1)
        assert out == ['a', 'b', 'c']

        out = find_bash_completions(['-s'], 1)
        assert out == settings

        out = find_bash_completions(['--setting'], 1)
        assert out == settings

        out = find_bash_completions(['-m', 'a=xyz'], 2)
        assert out == ['print']

        out = find_bash_completions(['-m', 'a=xyz', 'print'], 3)
        assert out == []

        out = find_bash_completions(['-i'], 1)
        assert out == []

        out = find_bash_completions(['-o'], 1)
        assert out == []

        with capture() as (out, err):
            dump_bash_completions(['-m'], 1)
        assert out.getvalue() == 'a b c\n'

        with capture() as (out, err):
            _main('--dump-bash-completions', '1', '--macro')
        assert out.getvalue() == 'a b c\n'

    with tempdir() as d:
        with chdir(d):
            out = find_bash_completions(['-'], 0)
            assert out == OPTION_STRINGS

            out = find_bash_completions([], 0)
            assert out == []

            out = find_bash_completions(['-m'], 1)
            assert out == []

            out = find_bash_completions(['-s'], 1)
            assert out == settings

            yfpath = os.path.join(DIR, 'yatrfile.yml')
            out = find_bash_completions(['-f', yfpath], 2)
            assert out == ['print']

            out = find_bash_completions(['--yatrfile', yfpath], 2)
            assert out == ['print']

            out = find_bash_completions(['-f', yfpath, '-s'], 3)
            assert out == settings

            yfpath = os.path.join(DIR, 'yatrfile.yaml')
            out = find_bash_completions(['-f', yfpath], 2)
            assert out == []
            
            yfpath = os.path.join(d, 'yatrfile.yml')
            shutil.copyfile(os.path.join(DIR, 'test2.yml'), yfpath)
            out = find_bash_completions([], 0)
            assert out == ['bad', 'good']
            
            with tempdir() as d2:
                cd = os.path.join(d2, 'foo')
                out = find_bash_completions(['--cache-dir', cd], 2)
                assert out == ['bad', 'good']
                
                with open(yfpath, 'r') as f:
                    data = f.read()
                out = data.replace('bad', 'dad')
                with open(yfpath, 'w') as f:
                    f.write(out)

                out = find_bash_completions(['--cache-dir', cd], 2)
                assert out == ['dad', 'good']

    spath = os.path.join(os.path.abspath(os.path.dirname(ybase.__file__)),
                         'scripts/completion/yatr')
    dpath = '/etc/bash_completion.d/yatr'
    with assign(shutil, 'copyfile', MagicMock()):
        with capture() as (out, err):
            _main('--install-bash-completions')
        assert out.getvalue() == BASH_COMPLETION_MESSAGE + '\n'
        assert shutil.copyfile.call_count == 1
        shutil.copyfile.assert_any_call(spath, dpath)

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

        # Test default task
        with capture() as (out, err):
            _main('-f', TEST2, '-p')
        assert out.getvalue() == 'true\n'

        # Test --dump and task command-line arg passing
        with chdir(os.path.join(DIR, 'foo')):
            with capture() as (out, err):
                _main('--dump')
            assert out.getvalue() == ('a = abc\nb = abcdef\nc = abcdefghi\n'
                                      'pwd = {}\n'.format(DIR))

            _main('print', '5')
            assert read(OUT) == 'abcdefghi 5\n'

            with capture() as (out, err):
                _main()
            assert out.getvalue() == USAGE + '\n'

        # Test task referencing in task definition
        _main('-f', TEST3, 'a')
        assert read(OUT) == 'abc\n'

        _main('-f', TEST3, 'b')
        assert read(OUT) == 'abc\ndef\n'

        # Test --render
        with chdir(DIR):
            with capture() as (out, err):
                _main('--render', 
                      '-i', os.path.join(DIR, 'test1.j2'),
                      '-o', os.path.join(DIR, 'test1.txt'))
            assert out.getvalue() == ''
            assert err.getvalue() == ''

            with open(os.path.join(DIR, 'test1.txt'), 'r') as f:
                txt = f.read()
            assert txt == 'First abc, then abcdef, then abcdefghi.'

            assert_raises(RuntimeError, _main, '--render')
            assert_raises(RuntimeError, _main, '--render', '-i', '/foo/bar/baz')
            assert_raises(RuntimeError, _main, '--render', '-i', 
                          os.path.join(DIR, 'test1.j2'))

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

        # Test default_task inheritance
        with capture() as (out, err):
            _main('-f', TEST5, '-p')
        assert out.getvalue() == 'true\n'

        with capture() as (out, err):
            _main('-f', TEST6, '-p')
        assert out.getvalue() == 'false\ntrue\n'

        # Test for and list macros
        with capture() as (out, err):
            _main('-f', TEST7, '-p', 'foo')
        assert out.getvalue() == 'echo x x w 0\n' \
            'echo x x z 1\n' \
            'echo x y w 2\n' \
            'echo x y z 3\n'

        with capture() as (out, err):
            _main('-f', TEST7, '-p', '-s', 'loop_count_macro=count', 'bar')
        assert out.getvalue() == 'echo 1 0\n' \
            'echo 2 1\n' \
            'echo 3 2\n' \
            'echo 4 3\n'

        # Test commands function
        with capture() as (out, err):
            _main('-f', TEST8, '-i', TEST8_IN, '-o', TEST8_OUT, '--render')
        with open(TEST8_OUT, 'r') as f:
            txt = f.read()
            assert txt == '#!/bin/bash\necho foo\necho bar\necho baz'

        # Test env function
        with capture() as (out, err):
            _main('-f', TEST8, '-p', 'home')
        assert out.getvalue() == 'echo {}\n'.format(os.environ['PATH'])

        with capture() as (out, err):
            _main('-f', TEST8, '-p', 'bar')
        assert out.getvalue() == 'echo baz\n'

        with capture() as (out, err):
            with setitem(os.environ, 'YATR_BAR', 'foo'):
                _main('-f', TEST8, '-p', 'bar')
        assert out.getvalue() == 'echo foo\n'

        with capture() as (out, err):
            _main('-f', TEST8, '-p', 'baz')
        assert out.getvalue() == 'echo baz_foo foo_bar\n'

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

        # Verify render example
        with chdir(os.path.join(DIR, 'example/render')):
            with capture() as (out, err):
                _main('render')
            assert out.getvalue() == ''
            
            with open(DOCKERFILE, 'r') as f:
                txt = f.read()
            assert txt == DFRENDER

            with capture() as (out, err):
                _main('-p', 'build')
            assert out.getvalue() == \
                ('yatr --render -i Dockerfile.j2 -o Dockerfile\n'
                 'docker build -t foo:latest .\n')
            
#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
