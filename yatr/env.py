import re

from copy import copy
from functools import partial
from jinja2 import Environment, StrictUndefined
from random import choice
from syn.base import Attr, Base, init_hook
from syn.base_utils import message
from syn.five import STR
from syn.type import Dict, List, Callable

from .base import resolve, ordered_macros, get_output, DEFAULT_JINJA_FILTERS, \
    DEFAULT_JINJA_FUNCTIONS, fix_functions, variables, ValidationError
from .context import Context, BUILTIN_CONTEXTS
from .task import Task

#-------------------------------------------------------------------------------

CP = 'copy_copy'
UP = 'dict_update'
AUP = 'assign_update'
SUP = 'set_update'

#-------------------------------------------------------------------------------

BUILTIN_PATTERNS = {'_n', '_[0-9]+'} # Conditionally-defined builtin macros
BUILTIN_LISTS = {'ARGS'} # Conditionally-defined builtin list macros

#-------------------------------------------------------------------------------

INITIAL_MACROS = {}

#-------------------------------------------------------------------------------
# DefaultList


class DefaultList(list):
    '''List wrapper that returns a default value for invalid indices.'''
    def __init__(self, lst=[], default=0):
        super(DefaultList, self).__init__(lst)
        self.default_value = default

    def __delitem__(self, idx):
        try:
            super(DefaultList, self).__delitem__(idx)
        except IndexError:
            pass

    def __getitem__(self, idx):
        try:
            return super(DefaultList, self).__getitem__(idx)
        except IndexError:
            return self.default_value


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

        for attr in self._groups.set_update:
            getattr(self, attr).update(getattr(other, attr, set()))

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
    _attrs = dict(macros = Attr(Dict((STR, int, float, 
                                      List((STR, int, float, list, dict)),
                                      Dict((STR, int, float, list, dict)))), 
                                init=lambda self: dict(),
                                doc='Macro definitions', groups=(UP, CP)),
                  commandline_macros = Attr(Dict(STR), init=lambda self: dict(),
                                            doc='Macros defined with -m',
                                            groups=(UP, CP)),
                  contexts = Attr(Dict(Context), init=lambda self: dict(),
                                  doc='Execution context definitions', 
                                  groups=(UP, CP)),
                  declares = Attr(set, init=lambda self: set(),
                                  doc='Declared runtime-defined macros',
                                  groups=(SUP, CP)),
                  tasks = Attr(Dict(Task), init=lambda self: dict(),
                               doc='Task definitions', groups=(UP, CP)),
                  secret_values = Attr(Dict(STR), init=lambda self: dict(),
                                       doc='Secret value store', 
                                       groups=(UP, CP)),
                  captures = Attr(Dict(STR), init=lambda self: dict(),
                                  doc='Commands to captures output of', 
                                  groups=(UP, CP)),
                  files = Attr(Dict(STR), init=lambda self: dict(),
                               doc='File name macros', groups=(UP, CP)),
                  settings = Attr(Dict(None), init=lambda self: dict(),
                                  doc='Global settings of various sorts', 
                                  groups=(UP, CP)),
                  jinja_filters = Attr(Dict(Callable), 
                                       init=lambda self: \
                                       dict(DEFAULT_JINJA_FILTERS),
                                       doc='Custom Jinja2 filters', 
                                       groups=(UP, CP)),
                  jinja_functions = Attr(Dict(Callable),
                                         init=lambda self: \
                                         dict(DEFAULT_JINJA_FUNCTIONS),
                                         doc='Custom Jinja2 functions',
                                         groups=(UP, CP)),
                  function_aliases = Attr(Dict(STR), init=lambda self: dict(),
                                          internal=True, groups=(UP, CP),
                                          doc='Jinja function aliases'),
                  env = Attr(Dict((STR, int, float, 
                                   List((STR, int, float, list, dict)),
                                   Dict((STR, int, float, list, dict)))),
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

    def __getitem__(self, key):
        return self.env[key]

    @init_hook
    def _init_populate(self):
        self.macros.update(INITIAL_MACROS)
        self.contexts.update(BUILTIN_CONTEXTS)

        if not hasattr(self, 'default_context'):
            self.default_context = self.contexts['null']

    @init_hook
    def _set_jenv(self, **kwargs):
        filts = dict(self.jinja_filters)
        for name, filt in filts.items():
            filts[name] = partial(filt, env=self)
        self.jenv.filters.update(filts)

        funcs = dict(self.jinja_functions)
        for name, func in funcs.items():
            funcs[name] = partial(func, env=self)
        self.jenv.globals.update(funcs)

    def _update_post(self, other, **kwargs):
        self._set_jenv(**kwargs)

    def capture_value(self, cmd, **kwargs):
        out, code = get_output(cmd)
        # These are intended to be macro values, so newlines and extra
        # white space probably aren't desirable
        return out.strip() 

    def jinja_filter(self, name, *args, **kwargs):
        from .env_decorators import JinjaFilter
        return JinjaFilter(self, name, *args, **kwargs)

    def jinja_function(self, name, *args, **kwargs):
        from .env_decorators import JinjaFunction
        return JinjaFunction(self, name, *args, **kwargs)

    def macro_env(self, **kwargs):
        dct = dict(self.macros)
        dct.update(self.secret_values)
        dct.update(self.files)
        return dct

    def resolve_macros(self, **kwargs):
        env = self.macro_env(**kwargs)
        macros = dict(self.macros)
        macros.update(self.captures)
        macros.update(self.commandline_macros)

        # TODO: better error message if there is a cycle
        potential_problems = set(env) & set(self.jinja_functions)
        for name, template in ordered_macros(macros, jenv=self.jenv,
                                             funcs=self.jinja_functions):
            if name in self.macros or name in self.commandline_macros:
                fixed = fix_functions(template, potential_problems, self)
                env[name] = self.resolve(fixed, env=env, **kwargs)

            if name in self.captures:
                cmd = resolve(template, env, jenv=self.jenv)
                env[name] = self.capture_value(cmd, **kwargs)

        self.env = env

    def resolve(self, template, **kwargs):
        env = dict(kwargs.get('env', self.env))

        if kwargs.get('from_validate', False):
            names = variables(template, jenv=self.jenv)

            patterns = set(BUILTIN_PATTERNS)
            patterns.update(self.declares)
            patterns = [re.compile(p) for p in patterns]

            # If the builtin/declared macro isn't defined, set it to ''
            # so that it can validate
            for name in names:
                if name not in env:
                    for p in patterns:
                        if re.match(p, name):
                            env[name] = ''
                            break

                if name in BUILTIN_LISTS:
                    lst = list(env.get(name, []))
                    env[name] = DefaultList(lst)
            
            # Inject value for '' into any dict macros, so that they will validate
            # for keys like _1, etc.
            for name, value in env.items():
                if isinstance(value, dict):
                    if '' not in value and value:
                        dct = dict(value)
                        dct[''] = choice(list(dct.values()))
                        env[name] = dct

        try:
            return resolve(template, env, jenv=self.jenv)

        except Exception as e:
            raise ValidationError('Error validating "{}": {}'.format(template, message(e)))

    def task(self, name, *args, **kwargs):
        from .env_decorators import Task
        return Task(self, name, *args, **kwargs)

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
