from syn.base import Attr, Base
from syn.five import STR
from .env import Env

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
# __all__

__all__ = ()

#-------------------------------------------------------------------------------
