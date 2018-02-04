import sys
from functools import wraps
from syn.base import Base, Attr, create_hook
from syn.base_utils import message, safe_str
from syn.type import Dict
from syn.five import STR

from .base import ValidationError, args_kwargs_from_env, eprint

#-------------------------------------------------------------------------------

CONTEXT_REGISTRY = {}

#-------------------------------------------------------------------------------

def verbose(f):
    @wraps(f)
    def func(self, command, env, **kwargs):
        verbose = kwargs.get('verbose', False)
        preview = kwargs.get('preview', False)
        pre = kwargs.get('preview_pre', '')

        if verbose:
            sys.stdout.write(pre + self.verbose(command, env, **kwargs) + '\n')
            sys.stdout.flush()
            
        if not preview:
            return f(self, command, env, **kwargs)

    return func

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

    run = None

    def validate(self):
        super(Context, self).validate()

        if self._skip_validation:
            return

        for opt in self.required_opts:
            if opt not in self.opts:
                raise ValidationError('Required option "{}" not defined'
                                      .format(opt))

    def verbose(self, command, env, **kwargs):
        raise NotImplementedError


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
# Python


# TODO: separate contexts for python-eval and python-exec
class Python(Context):
    context_name = 'python'

    @verbose
    def run(self, command, env, **kwargs):
        try:
            eval(command)
            return 0
        except Exception as e:
            eprint(message(e))
            return 1

    def verbose(self, command, env, **kwargs):
        return 'Python eval: {}'.format(command)


#-----------------------------------------------------------
# PythonFunction


class PythonCallable(Context):
    context_name = 'python_callable'

    def _args_kwargs(self, env):
        env_ = dict(env.env)
        args, kwargs = args_kwargs_from_env(env_)
        return args, kwargs

    @verbose
    def run(self, command, env, **kwargs_):
        args, kwargs = self._args_kwargs(env)
        return command(env, *args, **kwargs)

    def verbose(self, command, env, **kwargs):
        args, kwargs = self._args_kwargs(env)
        name = command.__name__
        display_kwargs = set(getattr(command, 'display', ()))
        if not display_kwargs:
            display_kwargs = set(kwargs)

        argstr = ', '.join(safe_str(arg) for arg in args)
        kwargstr = ', '.join('{}={}'.format(name, safe_str(value))
                             for name, value in sorted(kwargs.items())
                             if name in display_kwargs)
        
        out = name + '('
        if argstr:
            out += argstr
            if kwargstr:
                out += ', ' + kwargstr
        elif kwargstr:
            out += kwargstr
        out += ')'
        return out


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
                        python = Python(),
                        python_callable = PythonCallable(),
                        ssh = SSH(_skip_validation=True)) # TODO: need a better way of handling this

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Context',)

#-------------------------------------------------------------------------------
