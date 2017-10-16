from syn.base import Base, Attr, init_hook
from syn.type import Dict
from syn.five import STR

from .base import resolve, ordered_macros
from .context import Context, BUILTIN_CONTEXTS
from .task import Task

#-------------------------------------------------------------------------------

INITIAL_MACROS = {}

#-------------------------------------------------------------------------------
# Env


class Env(Base):
    _attrs = dict(macros = Attr(Dict(STR), init=lambda self: dict(),
                                doc='Macro definitions'),
                  contexts = Attr(Dict(Context), init=lambda self: dict(),
                                  doc='Execution context definitions'),
                  tasks = Attr(Dict(Task), init=lambda self: dict(),
                               doc='Task definitions'),
                  secret_values = Attr(Dict(STR), init=lambda self: dict(),
                                       doc='Secret value store'),
                  env = Attr(Dict(STR), init=lambda self: dict(),
                             doc='Current name resolution environment'),
                  default_context = Attr(Context, doc='Execution context to use '
                                         'if none is specified in task definition'))
    _opts = dict(init_validate = True)

    @init_hook
    def _init_populate(self):
        self.macros.update(INITIAL_MACROS)
        self.contexts.update(BUILTIN_CONTEXTS)

        if not hasattr(self, 'default_context'):
            self.default_context = self.contexts['null']

    def macro_env(self, **kwargs):
        dct = dict(self.macros)
        dct.update(self.secret_values)
        return dct

    def resolve_macros(self, **kwargs):
        env = self.macro_env(**kwargs)
        for name, template in ordered_macros(self.macros):
            env[name] = resolve(template, env)
        self.env = env

    def resolve(self, template):
        return resolve(template, self.env)

    def update(self, env, **kwargs):
        self.secret_values.update(env.secret_values)
        self.macros.update(env.macros)
        self.contexts.update(env.contexts)
        self.tasks.update(env.tasks)

        self.default_context = env.default_context

    def validate(self):
        super(Env, self).validate()
        
        for name, ctx in self.contexts.items():
            ctx.validate()

        for name, task in self.tasks.items():
            task.validate()


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Env',)

#-------------------------------------------------------------------------------
