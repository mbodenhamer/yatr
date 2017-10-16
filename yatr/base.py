from jinja2 import Template

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

#-------------------------------------------------------------------------------
# __all__

__all__ = ('ValidationError',)

#-------------------------------------------------------------------------------
