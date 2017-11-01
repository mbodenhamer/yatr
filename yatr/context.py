from syn.base import Base, Attr, create_hook
from syn.type import Dict
from syn.five import STR

from .base import ValidationError

#-------------------------------------------------------------------------------

CONTEXT_REGISTRY = {}

#-------------------------------------------------------------------------------
# Context


class Context(Base):
    context_name = None
    required_opts = ()

    _attrs = dict(inside = Attr(STR, ''),
                  envvars = Attr(Dict(STR), init=lambda self: dict()),
                  opts = Attr(dict, init=lambda self: dict()),
                  _skip_validation = Attr(bool, False, internal=True))
    _opts = dict(init_validate = True)

    @classmethod
    @create_hook
    def _register(cls):
        if cls.context_name:
            CONTEXT_REGISTRY[cls.context_name] = cls

    @classmethod
    def from_yaml(cls, name, dct):
        kwargs = {}
        kwargs['envvars'] = dct.get('env', {})
        kwargs['opts'] = dct.get('opts', {})
        kwargs['inside'] = dct.get('inside', '')

        # TODO: if invalid context specified, raise ValidationError
        cls_ = CONTEXT_REGISTRY.get(dct.get('instanceof', 'null'), cls)
        return cls_(**kwargs)

    def resolve_macros(self, env, **kwargs):
        envvars = dict(self.envvars)
        for key , value in self.envvars.items():
            envvars[key] = env.resolve(value)

        opts = dict(self.opts)
        for key, value in self.opts.items():
            if isinstance(value, STR):
                opts[key] = env.resolve(value)

        return envvars, opts

    def run_command(self, command, env, **kwargs):
        if self.inside:
            ctx = env.contexts[self.inside]
            command = ctx.run_command(command, env, **kwargs)
        return command
            
    def validate(self):
        super(Context, self).validate()

        if self._skip_validation:
            return

        for opt in self.required_opts:
            if opt not in self.opts:
                raise ValidationError('Required option "{}" not defined'
                                      .format(opt))


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


#-----------------------------------------------------------
# CD


class CD(Context):
    context_name = 'cd'


#-----------------------------------------------------------
# Docker


class Docker(Context):
    context_name = 'docker'


#-----------------------------------------------------------
# SSH


class SSH(Context):
    context_name = 'ssh'
    required_opts = ('user', 'hostname')

    def run_command(self, command, env, **kwargs):
        cmd = 'ssh {}@{} "{}"'.format(self.opts['user'],
                                      self.opts['hostname'],
                                      command)
        return super(SSH, self).run_command(cmd, env, **kwargs)


#-----------------------------------------------------------

BUILTIN_CONTEXTS = dict(null = Null(),
                        bash = Bash(),
                        cd = CD(),
                        docker = Docker(),
                        ssh = SSH(_skip_validation=True)) # TODO: need a better way of handling this

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Context',)

#-------------------------------------------------------------------------------
