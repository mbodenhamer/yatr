import os
import re
import sys
import json
import shutil
import hashlib
from argparse import ArgumentParser
from .env import INITIAL_MACROS
from .parse import Document, DEFAULT_SETTINGS
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
OPTION_STRINGS.sort()

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

def default_data():
    ret = {}
    ret['tasks'] = []
    ret['macros'] = []
    ret['settings'] = DEFAULT_SETTINGS
    return ret

def data_path_from_yatrfile_path(path, cachedir):
    base = hashlib.sha224(path.encode('utf-8')).hexdigest()
    fname = base + '_compdata'
    fpath = os.path.join(cachedir, fname)
    return fpath

def compile_completion_data(path, cachedir, outpath):
    data = default_data()
    try:
        doc = Document.from_path(path, cachedir=cachedir)
    except:
        return data

    data['tasks'] = sorted(doc.env.tasks.keys())
    data['macros'] = sorted(doc.env.macros.keys())
    data['settings'] = sorted(doc.env.settings.keys())

    if not os.path.isdir(cachedir):
        os.mkdir(cachedir)

    with open(outpath, 'w') as f:
        json.dump(data, f)

    return data

def load_completion_data(yatrfile, cachedir):
    cachedir = os.path.expanduser(cachedir)
    try:
        path = find_yatrfile_path(yatrfile)
    except:
        return default_data()

    dpath = data_path_from_yatrfile_path(path, cachedir)

    if not os.path.isfile(dpath):
        data = compile_completion_data(path, cachedir, dpath)

    elif os.stat(dpath).st_mtime <= os.stat(path).st_mtime:
        data = compile_completion_data(path, cachedir, dpath)

    else:
        with open(dpath, 'r') as f:
            data = json.load(f)

    return data

#-------------------------------------------------------------------------------
# Bash completions

def matches(s, lst):
    return [elem for elem in lst if elem.startswith(s)]

def find_bash_completions(args, idx):
    def find_opt(name, default):
        if name in args:
            n_idx = args.index(name)
            if n_idx == idx - 1:
                return # We are trying to complete a pathname
            elif n_idx < len(args) - 1:
                return args[n_idx + 1]
        return default

    cachedir = find_opt('--cache-dir', DEFAULT_CACHE_DIR)
    if cachedir is None:
        return [] # we are completing directory path; let defaults handle it

    yfpath = find_opt('-f', '')
    if yfpath is None:
        return [] # we are completing a file path; let defaults handle it

    # if query on '-f' returns '', check if '--yatrfile' was given
    if not yfpath:
        yfpath = find_opt('--yatrfile', '')
        if yfpath is None:
            return [] # we are completing a file path; let defaults handle it

    data = load_completion_data(yfpath, cachedir)

    if idx < len(args): # we are completing an already-started word
        word = args[idx]
        if word.startswith('-'):
            return matches(word, OPTION_STRINGS)

        elif idx > 0:
            pword = args[idx - 1]
            if any(w in data['tasks'] for w in args):
                return [] # we are at a task argument; let defaults handle it

            elif pword in ('-m', '--macro'):
                if '=' in word:
                    return [] # we are completing a macro value
                else:
                    return matches(word, data['macros'])

            elif pword in ('-s', '--setting'):
                if '=' in word:
                    return [] # we are completing a setting value
                else:
                    return matches(word, data['settings'])

            else: # The only other option is that we are completing a task name
                return matches(word, data['tasks'])

        else: # The first non-'-'-prefixed argument; must be a task name
            return matches(word, data['tasks'])
    
    else: # we are starting a new word
        if idx == 0: # probably looking for a specific task, so return all names
            return data['tasks']
        
        else:
            pword = args[idx - 1]
            if any(w in data['tasks'] for w in args):
                return [] # we are at a task argument; job for defaults
            
            elif pword in ('-m', '--macro'):
                return data['macros']
            
            elif pword in ('-s', '--setting'):
                return data['settings']

            else: # probably looking for a task at this point
                return data['tasks']

def dump_bash_completions(args, idx):
    comps = find_bash_completions(args, idx)
    out = ' '.join(comps)
    print(out)

BASH_COMPLETION_MESSAGE = '''You may need to add the following line to ~/.bashrc:

    source /etc/bash_completion.d/yatr

which can be accomplished with the following:

    echo "source /etc/bash_completion.d/yatr" >> ~/.bashrc'''

def install_bash_completions():
    script = os.path.join(DIR, 'scripts/completion/yatr')
    shutil.copyfile(script, '/etc/bash_completion.d/yatr')
    print(BASH_COMPLETION_MESSAGE)

#-------------------------------------------------------------------------------
# Main

def _main(*args):
    if args:
        if args[0] == '--dump-bash-completions':
            dump_bash_completions(args[2:], int(args[1]))
            return

    opts = parser.parse_args(args)
    
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

    elif not args:
        print(USAGE)
        sys.exit(1)

#-------------------------------------------------------------------------------

def main():
    _main(*sys.argv[1:])

#-------------------------------------------------------------------------------
