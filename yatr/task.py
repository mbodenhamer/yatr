from jinja2 import Template

from syn.base import Base, Attr
from syn.type import List
from syn.five import STR

from .base import ValidationError

#-------------------------------------------------------------------------------
# Command


class Command(Base):
    _attrs = dict(command = Attr(STR),
                  context = Attr(STR, '')) # string used to look up context object in env

    def resolve_macros(self, env, **kwargs):
        self.command = Template(self.command).render(env)

        if self.context:
            self.context = Template(self.context).render(env)

    def run(self, env, **kwargs):
        context_name = kwargs.get('context', self.context)
        if not context_name:
            context = env.default_context
        else:
            context = env.contexts[context_name]

        context.run(self.command, env, **kwargs)


#-------------------------------------------------------------------------------
# Task


class Task(Base):
    _attrs = dict(name = Attr(STR),
                  commands = Attr(List(Command)))

    @classmethod
    def from_yaml(cls, name, dct):
        if isinstance(dct, STR):
            return cls(name=name, commands=[dct])

        elif List(STR).query(dct):
            return cls(name=name, commands=dct)

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

    def run(self, env, **kwargs):
        for cmd in self.commands:
            cmd.run(env, **kwargs)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Command', 'Task')

#-------------------------------------------------------------------------------
