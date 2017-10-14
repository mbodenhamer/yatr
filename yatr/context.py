from jinja2 import Template

from syn.base import Base, Attr, create_hook
from syn.type import Dict
from syn.five import STR

#-------------------------------------------------------------------------------

CONTEXT_REGISTRY = {}

#-------------------------------------------------------------------------------
# Context


class Context(Base):
    context_name = None
    _attrs = dict(name = Attr(STR, ''),
                  inside = Attr(STR, ''),
                  env = Attr(Dict(STR), init=lambda self: dict()),
                  opts = Attr(dict, init=lambda self: dict()))
    _opts = dict(init_validate = True)

    @classmethod
    @create_hook
    def _register(cls):
        if cls.context_name:
            CONTEXT_REGISTRY[cls.context_name] = cls

    @classmethod
    def from_yaml(cls, name, dct):
        kwargs = dict(name=name)
        kwargs['env'] = dct.get('env', {})
        kwargs['opts'] = dct.get('opts', {})

        cls_ = CONTEXT_REGISTRY.get(dct.get('instanceof', ''), cls)
        return cls_(**kwargs)

    def resolve_macros(self, env, **kwargs):
        for key , value in self.env.items():
            self.env[key] = Template(value).render(env)

        for key, value in self.opts.items():
            if isinstance(value, STR):
                self.opts[key] = Template(value).render(env)

    def run_command(self, command, env, **kwargs):
        raise NotImplementedError
            

#-------------------------------------------------------------------------------
# Builtins

#-----------------------------------------------------------
# Bash

# TODO

# 1. No Popen here;  just implement run_command for each context, and do Popen in Command.run
# 2. Pass env to run_command, for nested subclass lookups;  use attribute "inside"
# 3. Validation in each Context subclass; check for invalid opts, etc.


class Bash(Context):
    context_name = 'bash'

    def run_command(self, command, env, **kwargs):
        cmd = 'bash -c "{}"'.format(command)
        
        if self.inside:
            ctx = env.contexts[self.inside]
            cmd = ctx.run_command(cmd, env, **kwargs)

        return cmd


#-----------------------------------------------------------

BUILTIN_CONTEXTS = dict(bash = Bash(name='bash'))

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Context',)

#-------------------------------------------------------------------------------
