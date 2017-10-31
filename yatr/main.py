import os
import re
import sys
import json
import shutil
import hashlib
from argparse import ArgumentParser
from .env import INITIAL_MACROS
from .parse import Document
from .base import DEFAULT_CACHE_DIR
from . import __version__ as yver

DIR = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------------------------------------------------

OPTION_STRINGS = []

def add_argument(parser, *args, **kwargs):
    opt = parser.add_argument(*args, **kwargs)
    OPTION_STRINGS.extend(opt.option_strings)

#-------------------------------------------------------------------------------

DESCRIPTION = 'Yet Another Task Runner.'

parser = ArgumentParser(prog='yatr', description=DESCRIPTION)
add_argument(parser, '-f', '--yatrfile', dest='yatrfile', type=str,
             default='', metavar='<yatrfile>', help='The yatrfile to load')
add_argument(parser, '-m', '--macro', dest='macros',
             action='append', metavar='<macro>=<value>',
             help='Set/override macro with specified value')
add_argument(parser, '-s', '--setting', dest='settings',
             action='append', metavar='<setting>=<value>',
             help='Set/override setting with specified value')
add_argument(parser, '--cache-dir', dest='cachedir', type=str,
             default=DEFAULT_CACHE_DIR, metavar='<DIR>',
             help='Path of cache directory')
add_argument(parser, '--dump-bash-completions', dest='dump_bash_completions',
             default=False, action='store_true',
             help='Dump data for the bash tab-completion script')
add_argument(parser, '--install-bash-completions', default=False,
             dest='install_bash_completions', action='store_true',
             help='Install bash tab completion script globally')
add_argument(parser, '-v', '--verbose', dest='verbose', default=False,
             action='store_true', help='Print commands to be run')
add_argument(parser, '-p', '--preview', dest='preview', default=False,
             action='store_true', help='Preview commands to be run '
             'without running them (implies -v)')
add_argument(parser, '--version', dest='show_version', default=False,
             action='store_true', help='Print version')
add_argument(parser, '--validate', dest='validate', default=False,
             action='store_true', help='Only validate the yatrfile')
add_argument(parser, '--dump', dest='dump_vars', default=False,
             action='store_true', help='Dump macro values')
add_argument(parser, '--dump-path', dest='dump_path', default=False,
             action='store_true', help='Print yatrfile path')
add_argument(parser, '--pull', dest='pull', default=False, action='store_true',
             help='Force download of URL includes and imports')
add_argument(parser, 'task', metavar='<task>', type=str, default='', nargs='?',
             help='The task to run')
add_argument(parser, 'args', metavar='ARGS', nargs='*',
             help='Additional arguments for the task')

USAGE = parser.format_usage().strip()

#-------------------------------------------------------------------------------
# Yatrfile search

YATRFILE_PATTERN = re.compile('^[Yy]atrfile(.yml)?$')

def search_dir(path):
    for name in os.listdir(path):
        if re.match(YATRFILE_PATTERN, name):
            if os.path.isfile(os.path.join(path, name)):
                return os.path.join(path, name)

def search_rootward(path):
    res = search_dir(path)

    if res:
        return res
    if path == '/':
        raise RuntimeError('Unable to find yatrfile')
        
    return search_rootward(os.path.dirname(path))

def find_yatrfile_path(path):
    if path:
        return path
    return search_rootward(os.path.abspath(os.getcwd()))

#-------------------------------------------------------------------------------
# Completion data

def data_path_from_yatrfile_path(path, cachedir):
    base = hashlib.sha224(path.encode('utf-8')).hexdigest()
    fname = base + '_compdata'
    fpath = os.path.join(cachedir, fname)
    return fpath

def compile_completion_data(path, cachedir, outpath):
    doc = Document.from_path(path, cachedir=cachedir)

    data = {}
    data['tasks'] = sorted(doc.env.tasks.keys())
    data['macros'] = sorted(doc.env.macros.keys())
    data['settings'] = sorted(doc.env.settings.keys())

    with open(outpath, 'w') as f:
        json.dump(data, f)

    return data

def load_completion_data(yatrfile, cachedir):
    path = find_yatrfile_path(yatrfile)
    dpath = data_path_from_yatrfile_path(path, cachedir)

    if not os.path.isfile(dpath):
        data = compile_completion_data(path, cachedir, dpath)

    elif os.stat(dpath).st_mtime < os.stat(path).st_mtime:
        data = compile_completion_data(path, cachedir, dpath)

    else:
        with open(dpath, 'r') as f:
            data = json.load(f)

    data['options'] = OPTION_STRINGS
    return data

#-------------------------------------------------------------------------------
# Bash completions

def print_bash_completion_data(data):
    out = ' '.join(data)
    print(out)

def dump_bash_completions():
    line = os.environ['COMP_LINE']
    n_word = os.environ['COMP_CWORD']
    idx = os.environ['COMP_POINT']
    print('a')

MESSAGE = '''You may need to add the following line to ~/.bashrc:

    source /etc/bash_completion.d/yatr

OR run the following:

    echo "source /etc/bash_completion.d/yatr" >> ~/.bashrc
'''

def install_bash_completions():
    script = os.path.join(DIR, 'scripts/completion/yatr')
    shutil.copyfile(script, '/etc/bash_completion.d/yatr')
    print(MESSAGE)

#-------------------------------------------------------------------------------
# Main

def _main(*args):
    opts = parser.parse_args(args)
    
    # TODO: if yatrfile isn't found on search, don't error; just return and print nothing
    # TODO: if they are completing -f, though, you will need to complete based on files;  however, the options to complete in the bash script should take care of that

    if opts.dump_bash_completions:
        dump_bash_completions()
        return

    if opts.install_bash_completions:
        install_bash_completions()
        return

    # Show version if requested
    if opts.show_version:
        print('yatr {}'.format(yver))
        return

    # Populate position arg macros
    for key in list(INITIAL_MACROS.keys()):
        del INITIAL_MACROS[key]
    for k, arg in enumerate(opts.args):
        key = '_{}'.format(k+1)
        INITIAL_MACROS[key] = arg

    # Process settings
    settings = {}
    if opts.settings:
        for s in opts.settings:
            setting, value = s.split('=')
            settings[setting] = value

    # Load yatrfile
    path = find_yatrfile_path(opts.yatrfile)
    doc = Document.from_path(path, pull=opts.pull, cachedir=opts.cachedir,
                             settings=settings)
    
    # Process command-line macro overrides
    if opts.macros:
        for s in opts.macros:
            macro, value = s.split('=')
            doc.env.macros[macro] = value
    
    doc.post_process()

    if opts.dump_path:
        print(path)

    if opts.dump_vars:
        # TODO: add support for filtering out unwanted variables
        # TODO: add support for not including possible secrets in output
        for name in sorted(doc.env.env):
            print('{} = {}'.format(name, doc.env.env[name]))

    if opts.validate:
        # Check that there are no undefined macros in task definitions
        for task in doc.env.tasks.values():
            task.run_commands(doc.env)

        print("Validation successful")
        return

    if opts.preview:
        opts.verbose = True

    if opts.task:
        codes = doc.run(opts.task, preview=opts.preview, verbose=opts.verbose)
        if codes:
            sys.exit(max(codes))

#-------------------------------------------------------------------------------

def main():
    _main(*sys.argv[1:])

#-------------------------------------------------------------------------------
