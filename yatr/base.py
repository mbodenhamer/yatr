import os
import re
import sys
import shutil
import hashlib
import requests
from uuid import uuid4
from tempfile import mkstemp, mkdtemp
from contextlib import contextmanager
from subprocess import call, check_output, CalledProcessError, STDOUT
from jinja2 import Template, Environment, meta, StrictUndefined, Undefined
from syn.base_utils import Precedes, topological_sorting, assign
from syn.five import STR

DEFAULT_CACHE_DIR = '~/.yatr'
ARG_MACRO_PATTERN = re.compile('^_[0-9]+$')

#-------------------------------------------------------------------------------

class ValidationError(Exception):
    pass

#-------------------------------------------------------------------------------
# Jinja Filters

DEFAULT_JINJA_FILTERS = dict()

#-------------------------------------------------------------------------------
# Jinja Functions

def jfunc_commands(name, **kwargs):
    env = kwargs.pop('env')
    task = env.tasks[name]
    ret = task.run_preview(env, **kwargs)
    return ret

def jfunc_env(name, value=None, **kwargs):
    if value is not None:
        return os.environ.get(name, value)
    return os.environ[name]

DEFAULT_JINJA_FUNCTIONS = dict(commands = jfunc_commands,
                               env = jfunc_env)

#-------------------------------------------------------------------------------
# Utilities

def eprint(out, flush=True):
    sys.stderr.write(out + '\n')
    if flush:
        sys.stderr.flush()

def expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))

def resolve(template, env, lenient=False, jenv=None):
    if isinstance(template, dict):
        return {key: resolve(item, env, lenient, jenv)
                for key, item in template.items()}

    if isinstance(template, list):
        return [resolve(elem, env, lenient, jenv) for elem in template]

    if isinstance(template, STR):
        if '{{' in template:
            if lenient:
                if jenv:
                    with assign(jenv, 'undefined', Undefined):
                        return jenv.from_string(template).render(env)
                return Template(template).render(env)
            else:
                if jenv is None:
                    jenv = Environment(undefined=StrictUndefined)
                return jenv.from_string(template).render(env)
    return template

def variables(template, lenient=False, jenv=None):
    if isinstance(template, dict):
        ret = set()
        for key, item in template.items():
            ret.update(variables(item, lenient, jenv))
        return ret

    if isinstance(template, list):
        ret = set()
        for elem in template:
            ret.update(variables(elem, lenient, jenv))
        return ret

    if jenv is None:
        jenv = Environment()

    try:
        return meta.find_undeclared_variables(jenv.parse(template))
    except Exception as e:
        if lenient:
            return set()
        raise e

def order_relations_from_macros(macros, lenient=False, jenv=None):
    out = []
    for name, template in macros.items():
        for var in variables(template, lenient=lenient, jenv=jenv):
            out.append(Precedes(var, name))
    return out

def ordered_macros(macros, lenient=False, funcs=None, jenv=None):
    funcs = funcs if funcs else []
    rels = order_relations_from_macros(macros, lenient=lenient, jenv=jenv)
    names = topological_sorting(macros, rels)

    for name in names:
        if name in macros:
            yield name, macros[name]
        elif name in funcs:
            pass
        else:
            if not lenient:
                if not re.match(ARG_MACRO_PATTERN, name):
                    raise ValidationError('Referenced macro {} not defined'
                                          .format(name))

def get_output(cmd):
    try:
        code = 0
        out = check_output(cmd, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        code = e.returncode
        out = e.output
        if out:
            print(out)

    out = out.decode('utf-8') if out else ''
    return out, code

def command(cmd, silent=False):
    if silent:
        out, code = get_output(cmd)
    else:
        code = call(cmd, shell=True)
    return code

def download(url, path):
    req = requests.get(url)
    with open(path, 'wb') as f:
        for data in req.iter_content():
            f.write(data)

def cached_path(path, cachedir=DEFAULT_CACHE_DIR):
    fname = hashlib.sha224(path.encode('utf-8')).hexdigest()
    return os.path.join(cachedir, fname)

def resolve_url(url, cachedir=DEFAULT_CACHE_DIR, force=False):
    if '://' in url:
        cachedir = expand_path(cachedir)

        if not os.path.isdir(cachedir):
            os.mkdir(cachedir)

        fpath = cached_path(url, cachedir)

        if not os.path.isfile(fpath) or force:
            download(url, fpath)

        return fpath
    return url

def read(path):
    with open(path, 'r') as f:
        return f.read()

@contextmanager
def tempfile(*args, **kwargs):
    try:
        _, path = mkstemp(*args, **kwargs)
        yield path
    finally:
        os.remove(path)

@contextmanager
def tempdir(*args, **kwargs):
    try:
        path = mkdtemp(*args, **kwargs)
        yield path
    finally:
        shutil.rmtree(path)

def str_to_bool(value):
    if isinstance(value, int):
        return bool(value)
    elif isinstance(value, STR):
        val = value.strip().lower()
        if val in {'yes', 'true', '1'}:
            return True
        if val in {'no', 'false', '0'}:
            return False
    raise TypeError('Invalid type/value for conversion: {}'.format(value))

def get_delete(in_, out, key, default, outkey=None):
    if outkey is None:
        outkey = key
    out[outkey] = in_.pop(key, default)

def fix_functions(template, potential_problems, env):
    if isinstance(template, list):
        return [fix_functions(elem, potential_problems, env)
                for elem in template]

    fixed = template
    for var in potential_problems:
        test = '(\{\{[^}]*\\b)' + var + '(\([^}]*\)[^}]*\}\})'
        if re.search(test, fixed):
            if var in env.function_aliases:
                alias = env.function_aliases[var]
            else:
                # TODO: replace with real gensym
                alias = var + '_' + uuid4().hex
                env.jenv.globals[alias] = env.jenv.globals[var]
                env.function_aliases[var] = alias
                eprint("Warning: '{}' defined as both macro and Jinja2 "
                       "function.  Using function alias '{}'".format(var, alias))
                
            repl = '\\1' + alias + '\\2'
            fixed = re.sub(test, repl, fixed)

    return fixed

def args_kwargs_from_env(env):
    arg_macros = [name for name in env if re.match(ARG_MACRO_PATTERN, name)]
    args = tuple([env[name] for name in sorted(arg_macros)])
    kwargs = {name: env[name] for name in env if name not in arg_macros}
    return args, kwargs

#-------------------------------------------------------------------------------
# __all__

__all__ = ('ValidationError',)

#-------------------------------------------------------------------------------
