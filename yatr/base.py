import shlex
from subprocess import Popen, PIPE
from jinja2 import Template, Environment, meta
from syn.base_utils import Precedes, topological_sorting

#-------------------------------------------------------------------------------

class ValidationError(Exception):
    pass

#-------------------------------------------------------------------------------
# Utilities

def resolve(template, env):
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

def ordered_macros(macros):
    rels = order_relations_from_macros(macros)
    names = topological_sorting(macros, rels)

    for name in names:
        yield name, macros[name]

def command(cmd, shell=False):
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, shell=shell)
    out, err = p.communicate()
    out = out.decode('utf-8') if out else ''
    err = err.decode('utf-8') if err else ''
    return out, err, p.returncode

#-------------------------------------------------------------------------------
# __all__

__all__ = ('ValidationError',)

#-------------------------------------------------------------------------------
