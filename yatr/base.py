import os
import shutil
import hashlib
import requests
from tempfile import mkstemp, mkdtemp
from contextlib import contextmanager
from subprocess import call, check_output, CalledProcessError, STDOUT
from jinja2 import Template, Environment, meta, StrictUndefined
from syn.base_utils import Precedes, topological_sorting, assign
from syn.five import STR

DEFAULT_CACHE_DIR = '~/.yatr'

#-------------------------------------------------------------------------------

class ValidationError(Exception):
    pass

#-------------------------------------------------------------------------------
# Filters

# NOTE: this filter cannot be overridden 
def filter_task(name, env=None, **kwargs):
    task = env.tasks[name]
    lines = task.run_commands(env, **kwargs)
    return '\n'.join(lines)

DEFAULT_FILTERS = dict(task = filter_task)

#-------------------------------------------------------------------------------
# Utilities

def resolve(template, env, lenient=False, jenv=None):
    if isinstance(template, list):
        return [resolve(elem, env, lenient) for elem in template]

    if isinstance(template, STR):
        if '{{' in template:
            if lenient:
                return Template(template).render(env)
            else:
                if jenv is None:
                    jenv = Environment(undefined=StrictUndefined)
                return jenv.from_string(template).render(env)
    return template

def variables(template):
    if isinstance(template, list):
        ret = set()
        for elem in template:
            ret.update(variables(elem))
        return ret

    env = Environment()
    return meta.find_undeclared_variables(env.parse(template))

def order_relations_from_macros(macros):
    out = []
    for name, template in macros.items():
        for var in variables(template):
            out.append(Precedes(var, name))
    return out

def ordered_macros(macros, lenient=False):
    rels = order_relations_from_macros(macros)
    names = topological_sorting(macros, rels)

    for name in names:
        if name in macros:
            yield name, macros[name]
        else:
            if not lenient:
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

def resolve_url(url, cachedir=DEFAULT_CACHE_DIR, force=False):
    if '://' in url:
        cachedir = os.path.expanduser(cachedir)

        if not os.path.isdir(cachedir):
            os.mkdir(cachedir)

        fname = hashlib.sha224(url.encode('utf-8')).hexdigest()
        fpath = os.path.join(cachedir, fname)

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

    out[outkey] = in_.get(key, default)
    
    if key in in_:
        del in_[key]

#-------------------------------------------------------------------------------
# __all__

__all__ = ('ValidationError',)

#-------------------------------------------------------------------------------
