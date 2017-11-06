import re
import sys
from itertools import product

from syn.base import Base, Attr
from syn.type import List, This
from syn.five import STR

from .base import ValidationError, command, get_delete

#-------------------------------------------------------------------------------

FOREX = re.compile('([a-zA-Z_][a-zA-Z0-9_-]*)\s+in\s+([a-zA-Z_][a-zA-Z0-9_-]*)')

#-------------------------------------------------------------------------------
# For


class For(Base):
    _attrs = dict(var = Attr((STR, List(STR)), doc='The loop variable(s)'),
                  in_ = Attr((STR, List((STR, int, list))), 
                             doc='Name(s) of list macro(s) to loop over'))
    _opts = dict(init_validate = True, 
                 args = ('var', 'in_'))

    @classmethod
    def from_yaml(cls, dct):
        if isinstance(dct, STR):
            m = re.match(FOREX, dct)
            if m:
                return cls(var=m.groups()[0], in_=m.groups()[1])
            else:
                raise ValidationError('Invalid for loop specifier: {}'
                                      .format(dct))

        kwargs = {}
        get_delete(dct, kwargs, 'var', None)
        get_delete(dct, kwargs, 'in', None, 'in_')
        
        if dct:
            raise ValidationError('Invalid for keys: {}'
                                  .format(','.join(dct.keys())))
        return cls(**kwargs)

    def resolve_macros(self, env, **kwargs):
        var = self.var
        in_ = self.in_
        if not isinstance(var, list):
            var = [self.var]
            in_ = [self.in_]

        outs = []
        for k, v in enumerate(var):
            name = in_[k]
            if isinstance(name, list):
                val = name
            else:
                val = env.env[name]
                if not isinstance(val, list):
                    raise ValidationError('For loop "in" specifier must be name of '
                                          'list macro: {}'.format(in_[k]))
            outs.append(val)
        return var, outs

    def loop(self, env, **kwargs):
        var, in_ = self.resolve_macros(env, **kwargs)
        
        for tup in product(*in_):
            yld = env.copy(**kwargs)
            for name, val in zip(var, tup):
                yld.env[name] = val
            yield yld

    def validate(self):
        super(For, self).validate()
        
        if isinstance(self.var, list):
            if len(self.var) != len(self.in_):
                raise ValidationError('"var" and "in" lists must be same '
                                      'length')


#-------------------------------------------------------------------------------
# Command


class Command(Base):
    _attrs = dict(command = Attr(STR),
                  context = Attr(STR, '')) # string used to look up context object in env
    _opts = dict(init_validate = True,
                 args = ('command',))

    def resolve_macros(self, env, **kwargs):
        command = env.resolve(self.command)
        context = env.resolve(kwargs.get('context', self.context))
        return command, context

    def run_command(self, env, **kwargs):
        command, context_name = self.resolve_macros(env, **kwargs)

        if not context_name:
            context = env.default_context
        else:
            context = env.contexts[context_name]

        return context.run_command(command, env, **kwargs)

    def run(self, env, **kwargs):
        verbose = kwargs.get('verbose', False)
        preview = kwargs.get('preview', False)
        silent = kwargs.get('silent', env.settings.get('silent', False))

        pre = ''
        if preview:
            pre = kwargs.get('preview_pre', '')

        cmd = self.run_command(env, **kwargs)
        if verbose:
            sys.stdout.write(pre + cmd + '\n')
            sys.stdout.flush()
        
        if not preview:
            return command(cmd, silent)


#-------------------------------------------------------------------------------
# Task


class Task(Base):
    _attrs = dict(commands = Attr(List(Command)),
                  condition = Attr(This, optional=True),
                  loop = Attr(For, optional=True),
                  condition_type = Attr(bool, True))
    _opts = dict(init_validate = True,
                 optional_none = True)

    @classmethod
    def from_yaml(cls, name, dct):
        if isinstance(dct, STR):
            return cls(commands=[Command(dct)])

        elif List(STR).query(dct):
            cmds = [Command(s) for s in dct]
            return cls(commands=cmds)

        elif isinstance(dct, dict):
            if set(dct.keys()).issuperset({'command'}):
                ret = Task.from_yaml(name, dct['command'])

                if 'context' in dct:
                    for cmd in ret.commands:
                        cmd.context = dct['context']

                if 'for' in dct:
                    ret.loop = For.from_yaml(dct['for'])

                if 'if' in dct:
                    ret.condition = Task.from_yaml(name + '-if', dct['if'])
                    ret.condition_type = True
                elif 'ifnot' in dct:
                    ret.condition = Task.from_yaml(name + '-ifnot', dct['ifnot'])
                    ret.condition_type = False
                return ret

        raise ValidationError('Invalid data for task: {}'.format(name))

    def run_commands(self, env, **kwargs):
        return [cmd.run_command(env, **kwargs) for cmd in self.commands]

    def run(self, env, **kwargs):
        codes = []
        looping = kwargs.get('looping', False)
        exit_on_error = kwargs.get('exit_on_error', True)

        if self.condition and not looping:
            kwargs['preview_pre'] = 'if: ' if self.condition_type else 'ifnot: '
            codes_ = self.condition.run(env, **kwargs)
            code = max(codes_)
            if (((self.condition_type is True and code != 0) or
                 (self.condition_type is False and code == 0)) and 
                code is not None):
                return []
            kwargs['preview_pre'] = '\t'

        if self.loop and not looping:
            n = 0
            kwargs['looping'] = True
            for env_ in self.loop.loop(env, **kwargs):
                env_.env[env_.settings['loop_count_macro']] = n
                codes_ = self.run(env_, **kwargs)
                codes.extend(codes_)
                n += 1
            return codes

        for cmd in self.commands:
            if cmd.command in env.tasks:
                codes_ = env.tasks[cmd.command].run(env, **kwargs)
                codes.extend(codes_)

            else:
                code = cmd.run(env, **kwargs)
                codes.append(code)

            if exit_on_error and any(c != 0 for c in codes if c is not None):
                break

        return codes


#-------------------------------------------------------------------------------
# __all__

__all__ = ('For', 'Command', 'Task')

#-------------------------------------------------------------------------------
