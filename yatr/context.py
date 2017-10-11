import shlex
from jinja2 import Template
from subprocess import Popen, PIPE

from syn.base import Base, Attr, create_hook
from syn.type import Dict
from syn.five import STR

#-------------------------------------------------------------------------------

CONTEXT_REGISTRY = {}

#-------------------------------------------------------------------------------
# Context


class Context(Base):
    context_name = None
    _attrs = dict(name = Attr(STR),
                  env = Attr(Dict(STR), init=lambda self: dict()),
                  opts = Attr(Dict(STR), init=lambda self: dict()))

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
        for key in self.env:
            self.env[key] = Template(self.env[key]).render(env)

        for key in self.opts:
            self.opts[key] = Template(self.opts[key]).render(env)

    def run(self, env, **kwargs):
        raise NotImplementedError
            

#-------------------------------------------------------------------------------
# Builtins

#-----------------------------------------------------------
# Bash


class Bash(Context):
    context_name = 'bash'

    def run(self, command, env, **kwargs):
        cmd = 'bash -c "{}"'.format(command)
        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out, err
        

#-----------------------------------------------------------

BUILTIN_CONTEXTS = dict(bash = Bash(name='bash'))

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Context',)

#-------------------------------------------------------------------------------
