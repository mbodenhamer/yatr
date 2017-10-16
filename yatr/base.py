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

#-------------------------------------------------------------------------------
# __all__

__all__ = ('ValidationError',)

#-------------------------------------------------------------------------------
