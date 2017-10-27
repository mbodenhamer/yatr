import os
import shlex
import hashlib
import requests
from subprocess import Popen, PIPE
from jinja2 import Template, Environment, meta
from syn.base_utils import Precedes, topological_sorting
from syn.five import STR

#-------------------------------------------------------------------------------

class ValidationError(Exception):
    pass

#-------------------------------------------------------------------------------
# Utilities

def resolve(template, env):
    if isinstance(template, STR):
        if '{{' in template:
            return Template(template).render(env)
    return template

def variables(template):
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

def command(cmd, shell=False):
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=shell)
    out, err = p.communicate()
    out = out.decode('utf-8') if out else ''
    err = err.decode('utf-8') if err else ''
    return out, err, p.returncode

def download(url, path):
    req = requests.get(url)
    with open(path, 'wb') as f:
        for data in req.iter_content():
            f.write(data)

def resolve_url(url, cachedir=None, force=False):
    if '://' in url:
        if cachedir is None:
            cachedir = os.path.expanduser('~/.yatr')

            if not os.path.isdir(cachedir):
                os.mkdir(cachedir)

        fname = hashlib.sha224(url.encode('utf-8')).hexdigest()
        fpath = os.path.join(cachedir, fname)

        if not os.path.isfile(fpath) or force:
            download(url, fpath)

        return fpath
    return url

#-------------------------------------------------------------------------------
# __all__

__all__ = ('ValidationError',)

#-------------------------------------------------------------------------------
