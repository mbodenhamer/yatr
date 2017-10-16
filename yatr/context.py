from syn.base import Base, Attr, create_hook
from syn.type import Dict
from syn.five import STR

from .base import resolve

#-------------------------------------------------------------------------------

CONTEXT_REGISTRY = {}

#-------------------------------------------------------------------------------
# Context


class Context(Base):
    context_name = None
    _attrs = dict(inside = Attr(STR, ''),
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
        kwargs = {}
        kwargs['env'] = dct.get('env', {})
        kwargs['opts'] = dct.get('opts', {})

        # TODO: if invalid context specified, raise ValidationError
        cls_ = CONTEXT_REGISTRY.get(dct.get('instanceof', 'null'), cls)
        return cls_(**kwargs)

    def resolve_macros(self, env, **kwargs):
        env_ = dict(self.env)
        for key , value in self.env.items():
            env_[key] = resolve(value, env)

        opts = dict(self.opts)
        for key, value in self.opts.items():
            if isinstance(value, STR):
                opts[key] = resolve(value, env)

        return env_, opts

    def run_command(self, command, env, **kwargs):
        if self.inside:
            ctx = env.contexts[self.inside]
            command = ctx.run_command(command, env, **kwargs)
        return command
            

#-------------------------------------------------------------------------------
# Builtins

#-----------------------------------------------------------
# Null


class Null(Context):
    context_name = 'null'


#-----------------------------------------------------------
# Bash


class Bash(Context):
    context_name = 'bash'

    def run_command(self, command, env, **kwargs):
        # TODO: quote string here
        cmd = 'bash -c "{}"'.format(command)
        return super(Bash, self).run_command(cmd, env, **kwargs)

    def validate(self):
        super(Bash, self).validate()

        # TODO: check for invalid opts, etc.


#-----------------------------------------------------------
# Docker


class Docker(Context):
    context_name = 'docker'


#-----------------------------------------------------------
# SSH


class SSH(Context):
    context_name = 'ssh'


#-----------------------------------------------------------

BUILTIN_CONTEXTS = dict(null = Null(),
                        bash = Bash(),
                        docker = Docker(),
                        ssh = SSH())

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Context',)

#-------------------------------------------------------------------------------
