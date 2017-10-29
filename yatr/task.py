import sys
from syn.base import Base, Attr
from syn.type import List
from syn.five import STR

from .base import ValidationError, command

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
        silent = kwargs.get('silent', False)
        cmd = self.run_command(env, **kwargs)
        return command(cmd, silent)


#-------------------------------------------------------------------------------
# Task


class Task(Base):
    _attrs = dict(commands = Attr(List(Command)),
                  condition = Attr(Command, optional=True),
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

                if 'if' in dct:
                    ret.condition = Command(dct['if'])
                    ret.condition_type = True
                elif 'ifnot' in dct:
                    ret.condition = Command(dct['ifnot'])
                    ret.condition_type = False
                return ret

        raise ValidationError('Invalid data for task: {}'.format(name))

    def run_commands(self, env, **kwargs):
        return [cmd.run_command(env, **kwargs) for cmd in self.commands]

    def run(self, env, **kwargs):
        codes = []
        exit_on_error = kwargs.get('exit_on_error', True)

        if self.condition:
            code = self.condition.run(env, **kwargs)
            if ((self.condition_type is True and code != 0) or
                (self.condition_type is False and code == 0)):
                return []

        for cmd in self.commands:
            if cmd.command in env.tasks:
                codes_ = env.tasks[cmd.command].run(env, **kwargs)
                codes.extend(codes_)

            else:
                code = cmd.run(env, **kwargs)
                codes.append(code)

            if exit_on_error and any(c != 0 for c in codes):
                break

        return codes


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Command', 'Task')

#-------------------------------------------------------------------------------
