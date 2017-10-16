from jinja2 import Template
from itertools import product
from syn.base_utils import Precedes
from syn.five import xrange

#-------------------------------------------------------------------------------

class ValidationError(Exception):
    pass

#-------------------------------------------------------------------------------
# Utilities

def resolve(template, env):
    if '{{' in template:
        return Template(template).render(env)
    elif '{' in template:
        return template.format(**env)
    return template

def ordering_relations(lst):
    if len(lst) < 2:
        return []

    out = []
    for k in xrange(len(lst) - 1):
        out.append(Precedes(lst[k], lst[k+1]))
    return out

def nested_order_relations(lst):
    if len(lst) < 2:
        return []

    out = []
    for k in xrange(len(lst) -1):
        for a, b in product(lst[k], lst[k+1]):
            out.append(Precedes(a, b))
    return out

#-------------------------------------------------------------------------------
# __all__

__all__ = ('ValidationError',)

#-------------------------------------------------------------------------------
