from copy import copy
from functools import partial
from jinja2 import Environment, StrictUndefined
from syn.base import Base, Attr, init_hook
from syn.type import Dict, List, Callable
from syn.five import STR

from .base import resolve, ordered_macros, get_output, DEFAULT_FILTERS
from .context import Context, BUILTIN_CONTEXTS
from .task import Task

#-------------------------------------------------------------------------------

CP = 'copy_copy'
UP = 'dict_update'
AUP = 'assign_update'

#-------------------------------------------------------------------------------

INITIAL_MACROS = {}

#-------------------------------------------------------------------------------
# Copyable


class Copyable(object):
    def copy(self, **kwargs):
        ret = copy(self)
        for attr in self._groups.copy_copy:
            setattr(ret, attr, copy(getattr(ret, attr)))
        return ret


#-------------------------------------------------------------------------------
# Updateable


class Updateable(object):
    def _update_pre(self, other, **kwargs):
        pass

    def update(self, other, **kwargs):
        self._update_pre(other, **kwargs)

        for attr in self._groups.dict_update:
            getattr(self, attr).update(getattr(other, attr, {}))

        for attr in self._groups.assign_update:
            value = getattr(other, attr)
            if not value:
                value = getattr(self, attr)
            setattr(self, attr, value)

        self._update_post(other, **kwargs)

    def _update_post(self, other, **kwargs):
        pass


#-------------------------------------------------------------------------------
# Env


class Env(Base, Copyable, Updateable):
    _groups = (UP, AUP)
    _attrs = dict(macros = Attr(Dict((STR, int, List((STR, int, list)))), 
                                init=lambda self: dict(),
                                doc='Macro definitions', groups=(UP, CP)),
                  contexts = Attr(Dict(Context), init=lambda self: dict(),
                                  doc='Execution context definitions', 
                                  groups=(UP, CP)),
                  tasks = Attr(Dict(Task), init=lambda self: dict(),
                               doc='Task definitions', groups=(UP, CP)),
                  secret_values = Attr(Dict(STR), init=lambda self: dict(),
                                       doc='Secret value store', 
                                       groups=(UP, CP)),
                  captures = Attr(Dict(STR), init=lambda self: dict(),
                                  doc='Commands to captures output of', 
                                  groups=(UP, CP)),
                  settings = Attr(Dict(None), init=lambda self: dict(),
                                  doc='Global settings of various sorts', 
                                  groups=(UP, CP)),
                  filters = Attr(Dict(Callable), 
                                 init=lambda self: dict(DEFAULT_FILTERS),
                                 doc='Custom Jinja2 filters', groups=(UP, CP)),
                  env = Attr(Dict(((STR, List(STR)), int)), 
                             init=lambda self: dict(),
                             doc='Current name resolution environment', 
                             groups=(UP, CP)),
                  jenv = Attr(Environment, doc='Jinja2 environment', group='eq_exclude',
                              init=lambda self: Environment(undefined=StrictUndefined)),
                  default_task = Attr(STR, '', 'Task to run if no task is '
                                      'specified at the command line', 
                                      group=AUP),
                  default_context = Attr(Context, doc='Execution context to use '
                                         'if none is specified in task definition',
                                         group=AUP))
    _opts = dict(init_validate = True)

    @init_hook
    def _init_populate(self):
        self.macros.update(INITIAL_MACROS)
        self.contexts.update(BUILTIN_CONTEXTS)

        if not hasattr(self, 'default_context'):
            self.default_context = self.contexts['null']

    def _update_post(self, other, **kwargs):
         # TODO: should probably also capture settings as **self.settings
        self.filters['commands'] = \
            partial(DEFAULT_FILTERS['commands'], env=self)
        self.jenv.filters.update(self.filters)

    def capture_value(self, cmd, **kwargs):
        out, code = get_output(cmd)
        # These are intended to be macro values, so newlines and extra
        # white space probably aren't desirable
        return out.strip() 

    def macro_env(self, **kwargs):
        dct = dict(self.macros)
        dct.update(self.secret_values)
        return dct

    def resolve_macros(self, **kwargs):
        env = self.macro_env(**kwargs)
        macros = dict(self.macros)
        macros.update(self.captures)

        # TODO: better error message if there is a cycle
        for name, template in ordered_macros(macros):
            if name in self.macros:
                env[name] = resolve(template, env, jenv=self.jenv)
            if name in self.captures:
                cmd = resolve(template, env)
                env[name] = self.capture_value(cmd, **kwargs)

        # Populate task names for task macros
        for name in self.tasks:
            if name not in env:
                env[name] = name

        self.env = env

    def resolve(self, template):
        return resolve(template, self.env, jenv=self.jenv)

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
