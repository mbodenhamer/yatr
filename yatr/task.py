import shlex
from jinja2 import Template
from subprocess import Popen, PIPE

from syn.base import Base, Attr
from syn.type import List
from syn.five import STR

from .base import ValidationError

#-------------------------------------------------------------------------------
# Command


class Command(Base):
    _attrs = dict(command = Attr(STR),
                  context = Attr(STR, '')) # string used to look up context object in env
    _opts = dict(init_validate = True,
                 args = ('command',))

    def resolve_macros(self, env, **kwargs):
        self.command = Template(self.command).render(env)

        if self.context:
            self.context = Template(self.context).render(env)

    def run_command(self, env, **kwargs):
        context_name = kwargs.get('context', self.context)
        if not context_name:
            context = env.default_context
        else:
            context = env.contexts[context_name]

        dct = env.macro_env(**kwargs)
        return context.run_command(self.command, dct, **kwargs)

    def run(self, env, **kwargs):
        cmd = self.run_command(env, **kwargs)
        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out, err
        

#-------------------------------------------------------------------------------
# Task


class Task(Base):
    _attrs = dict(name = Attr(STR),
                  commands = Attr(List(Command)))
    _opts = dict(init_validate = True)

    @classmethod
    def from_yaml(cls, name, dct):
        if isinstance(dct, STR):
            return cls(name=name, commands=[Command(dct)])

        elif List(STR).query(dct):
            cmds = [Command(s) for s in dct]
            return cls(name=name, commands=cmds)

        elif isinstance(dct, dict):
            if set(dct.keys()) == {'context', 'command'}:
                ret = Task.from_yaml(name, dct['command'])
                for cmd in ret.commands:
                    cmd.context = dct['context']
                return ret

        raise ValidationError('Invalid data for task: {}'.format(name))

    def resolve_macros(self, env, **kwargs):
        for cmd in self.commands:
            cmd.resolve_macros(env, **kwargs)

    def run_commands(self, env, **kwargs):
        return [cmd.run_command(env, **kwargs) for cmd in self.commands]

    def run(self, env, **kwargs):
        outs = []
        errs = []

        for cmd in self.commands:
            out, err = cmd.run(env, **kwargs)
            outs.append(out)
            errs.append(err)

        return outs, errs


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Command', 'Task')

#-------------------------------------------------------------------------------
