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
        cmd = self.run_command(env, **kwargs)
        return command(cmd)

#-------------------------------------------------------------------------------
# Task


class Task(Base):
    _attrs = dict(commands = Attr(List(Command)))
    _opts = dict(init_validate = True)

    @classmethod
    def from_yaml(cls, name, dct):
        if isinstance(dct, STR):
            return cls(commands=[Command(dct)])

        elif List(STR).query(dct):
            cmds = [Command(s) for s in dct]
            return cls(commands=cmds)

        elif isinstance(dct, dict):
            if set(dct.keys()) == {'context', 'command'}:
                ret = Task.from_yaml(name, dct['command'])
                for cmd in ret.commands:
                    cmd.context = dct['context']
                return ret

        raise ValidationError('Invalid data for task: {}'.format(name))

    def run_commands(self, env, **kwargs):
        return [cmd.run_command(env, **kwargs) for cmd in self.commands]

    def run(self, env, **kwargs):
        outs = []
        errs = []
        codes = []

        for cmd in self.commands:
            out, err, code = cmd.run(env, **kwargs)
            outs.append(out)
            errs.append(err)
            codes.append(code)

        return outs, errs, codes


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Command', 'Task')

#-------------------------------------------------------------------------------
