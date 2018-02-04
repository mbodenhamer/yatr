from functools import wraps
from syn.base import Attr, Base
from syn.base_utils import message
from syn.five import STR
from .base import eprint
from .env import Env
from .task import Command
from .task import Task as Task_

#-------------------------------------------------------------------------------
# EnvDecorator


class EnvDecorator(Base):
    _attrs = dict(name = Attr(STR),
                  parent = Attr(Env))
    _opts = dict(init_validate = True,
                 args = ('parent', 'name'))

    def __call__(self, func):
        raise NotImplementedError


#-------------------------------------------------------------------------------
# JinjaFilter


class JinjaFilter(EnvDecorator):
    def __call__(self, func):
        self.parent.jinja_filters[self.name] = func
        return func


#-------------------------------------------------------------------------------
# JinjaFunction


class JinjaFunction(EnvDecorator):
    def __call__(self, func):
        self.parent.jinja_functions[self.name] = func
        return func


#-------------------------------------------------------------------------------
# Task


class Task(EnvDecorator):
    _attrs = dict(display = Attr(tuple, (), 
                                 'Names of kwargs to display in verbose'))

    def __call__(self, f):
        @wraps(f)
        def func(env, *args, **kwargs):
            try:
                f(env, *args, **kwargs)
                return 0

            except Exception as e:
                eprint(message(e))
                return 1

        func.display = self.display
        task = Task_(commands=[Command(func, context='python_callable')],
                     name=self.name)
        self.parent.tasks[self.name] = task
        return func


#-------------------------------------------------------------------------------
# __all__

__all__ = ()

#-------------------------------------------------------------------------------
