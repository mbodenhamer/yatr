import os
import re
import sys
from argparse import ArgumentParser
from .env import INITIAL_MACROS
from .parse import Document
from .base import DEFAULT_CACHE_DIR
from . import __version__ as yver

#-------------------------------------------------------------------------------

DESCRIPTION = 'Yet Another Task Runner.'

parser = ArgumentParser(prog='yatr', description=DESCRIPTION)
parser.add_argument('-f', '--yatrfile', dest='yatrfile', type=str,
                    default='', metavar='<yatrfile>',
                    help='The yatrfile to load')
parser.add_argument('-m', '--macro', dest='macros',
                    action='append', metavar='<macro>=<value>',
                    help='Set/override macro with specified value')
parser.add_argument('--cache-dir', dest='cachedir', type=str,
                    default=DEFAULT_CACHE_DIR, metavar='<DIR>',
                    help='Path of cache directory')
parser.add_argument('--version', dest='show_version', default=False,
                    action='store_true', help='Print version')
parser.add_argument('--validate', dest='validate', default=False,
                    action='store_true', help='Only validate the yatrfile')
parser.add_argument('--dump', dest='dump_vars', default=False,
                    action='store_true', help='Dump macro values')
parser.add_argument('--dump-path', dest='dump_path', default=False,
                    action='store_true', help='Print yatrfile path')
parser.add_argument('--pull', dest='pull', default=False, action='store_true',
                    help='Force download of URL includes and imports')
parser.add_argument('task', metavar='<task>', type=str, default='', nargs='?',
                    help='The task to run')
parser.add_argument('args', metavar='ARGS', nargs='*',
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

def _main(*args):
    opts = parser.parse_args(args)
    
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

    # Load yatrfile
    path = find_yatrfile_path(opts.yatrfile)
    doc = Document.from_path(path, pull=opts.pull, cachedir=opts.cachedir)
    
    # Process command-line macro overrides
    if opts.macros:
        for s in opts.macros:
            macro, value = s.split('=')
            doc.env.macros[macro] = value
    
    doc.env.resolve_macros()

    if opts.dump_path:
        print(path)

    if opts.dump_vars:
        # TODO: add support for filtering out unwanted variables
        # TODO: add support for not including possible secrets in output
        for name in sorted(doc.env.env):
            print('{} = {}'.format(name, doc.env.env[name]))

    if opts.validate:
        # We will get an error of some sort before this if it isn't valid
        print("Validation successful")
        return

    if opts.task:
        codes = doc.run(opts.task)
        if codes:
            sys.exit(max(codes))

#-------------------------------------------------------------------------------

def main():
    _main(*sys.argv[1:])

#-------------------------------------------------------------------------------
