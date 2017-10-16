from syn.base_utils import topological_sorting
from syn.base import Base, Attr, init_hook
from syn.type import Dict, List
from syn.five import STR

from .base import resolve, ordering_relations, nested_order_relations 
from .context import Context, BUILTIN_CONTEXTS
from .task import Task

#-------------------------------------------------------------------------------

INITIAL_MACROS = {}

#-------------------------------------------------------------------------------
# Env


class Env(Base):
    _attrs = dict(macros = Attr(Dict(STR), init=lambda self: dict()),
                  macro_ordering = Attr(List(STR), init=lambda self: list()),
                  contexts = Attr(Dict(Context), init=lambda self: dict()),
                  tasks = Attr(Dict(Task), init=lambda self: dict()),
                  secret_values = Attr(Dict(STR), init=lambda self: dict()),
                  default_context = Attr(Context))
    _opts = dict(init_validate = True)

    @init_hook
    def _init_populate(self):
        self._init_macro_order()

        self.contexts.update(BUILTIN_CONTEXTS)
        if not hasattr(self, 'default_context'):
            self.default_context = self.contexts['null']

    def _init_macro_order(self):
        self.update_macros(self.macros, init=True)

        self.macros.update(INITIAL_MACROS)
        for name in INITIAL_MACROS:
            self.macro_ordering.insert(0, name)

    def macro_env(self, **kwargs):
        dct = dict(self.macros)
        dct.update(self.secret_values)
        return dct

    def resolve_macros(self, **kwargs):
        env = self.macro_env(**kwargs)
        for name in self.macro_ordering:
            value = resolve(self.macros[name], env)
            self.macros[name] = value
            env[name] = value

    def update_macros(self, macros, **kwargs):
        # TODO: fix bug in syn.type to allow for empty dict to validate
        if Dict(STR).query(macros) or macros == {}:
            for name in macros:
                if name not in self.macro_ordering:
                    self.macro_ordering.append(name)
            self.macros.update(macros)
            
        elif List(Dict(STR)).query(macros):
            rels = ordering_relations(self.macro_ordering)
            rels.extend(nested_order_relations(macros))

            if kwargs.get('init', False):
                self.macros = {}

            for dct in macros:
                self.macros.update(dct)

            self.macro_ordering = topological_sorting(self.macros, rels)
        
        else:
            raise TypeError('Invalid macros type: {}'.format(macros))

    def update_contexts(self, contexts, **kwargs):
        for name, ctx in contexts.items():
            self.contexts[name] = ctx

    def update_tasks(self, tasks, **kwargs):
        for name, task in tasks.items():
            self.tasks[name] = task

    def update(self, env, **kwargs):
        self.secret_values.update(env.secret_values)
        self.update_macros(env.macros, **kwargs)
        self.update_contexts(env.contexts, **kwargs)
        self.update_tasks(env.tasks, **kwargs)

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
