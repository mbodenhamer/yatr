import os
import imp
import yaml
from syn.base_utils import chdir
from syn.base import Base, Attr, init_hook
from syn.type import List, Dict
from syn.five import STR

from .base import ValidationError, resolve_url, resolve, ordered_macros
from .context import Context
from .task import Task
from .env import Env

STRList = List(STR)

#-------------------------------------------------------------------------------
# Utilities

def get_delete(in_, out, key, default, outkey=None):
    if outkey is None:
        outkey = key

    out[outkey] = in_.get(key, default)
    
    if key in in_:
        del in_[key]

#-------------------------------------------------------------------------------
# Document

class Document(Base):
    _attrs = dict(imports = Attr(List(STR), init=lambda self:list()),
                  includes = Attr(List(STR), init=lambda self: list()),
                  secrets = Attr(List(STR), init=lambda self: list()),
                  macros = Attr(Dict((STR, int)), init=lambda self: dict()),
                  contexts = Attr(Dict(Context), init=lambda self: dict()),
                  tasks = Attr(Dict(Task), init=lambda self: dict()),
                  secret_values = Attr(Dict(STR), init=lambda self: dict()),
                  env = Attr(Env, init=lambda self: Env(), internal=True),
                  dirname = Attr(STR, doc='Relative path for includes'),
                  pull = Attr(bool, False, 'Force-pull URLs'),
                 )
    _opts = dict(init_validate = True)

    @classmethod
    def from_path(cls, path):
        with open(path, 'r') as f:
            dct = yaml.load(f)
            return cls.from_yaml(dct, os.path.abspath(os.path.dirname(path)))

    @classmethod
    def from_yaml(cls, dct, dirname, **kwargs):
        get_delete(dct, kwargs, 'import', [], 'imports')
        get_delete(dct, kwargs, 'include', [], 'includes')
        get_delete(dct, kwargs, 'secrets', [])
        get_delete(dct, kwargs, 'macros', {})
        get_delete(dct, kwargs, 'contexts', {})
        get_delete(dct, kwargs, 'tasks', {})

        if dct:
            raise ValidationError('Invalid top-level keys: {}'
                                  .format(','.join(dct.keys())))

        for key in list(kwargs['contexts'].keys()):
            kwargs['contexts'][key] = \
                Context.from_yaml(key, kwargs['contexts'][key])

        for key in list(kwargs['tasks'].keys()):
            kwargs['tasks'][key] = \
                Task.from_yaml(key, kwargs['tasks'][key])

        kwargs['dirname'] = dirname
        return cls(**kwargs)

    @init_hook
    def process(self, **kwargs):
        pre_macros = dict(self.macros)
        for name, macro in ordered_macros(pre_macros):
            pre_macros[name] = resolve(macro, pre_macros)

        def process(path):
            return resolve_url(resolve(path, pre_macros))

        with chdir(self.dirname):
            for path in map(process, self.imports):
                if not os.path.exists(path):
                    raise ValidationError("Module path does not exist: {}"
                                          .format(path))
                self.process_import(path, **kwargs)

            for path in map(process, self.includes):
                if not os.path.isfile(path):
                    raise ValidationError("Include path does not exist: {}"
                                          .format(path))
                self.process_include(path, **kwargs)

        for name in self.secrets:
            self.process_secret(name, **kwargs)

        env = Env(macros=self.macros, contexts=self.contexts, tasks=self.tasks,
                  secret_values=self.secret_values)
        self.env.update(env, **kwargs)

    def process_import(self, path, **kwargs):
        mod = imp.load_source('yatr_module_import', path)
        
        if not hasattr(mod, 'env'):
            raise ImportError("yatr extension module '{}' has no env"
                              .format(path))

        self.env.update(mod.env, **kwargs)

    def process_include(self, path, **kwargs):
        # TODO: support for ':' in path to restrict include scope
        # TODO: when implementing :-support, will need to modify path validation
        doc = Document.from_path(path)
        doc.process(**kwargs)
        self.env.update(doc.env, **kwargs)

    def process_secret(self, name, **kwargs):
        raise NotImplementedError('Secrets currently unsupported')

    def run(self, name, **kwargs):
        return self.tasks[name].run(self.env, **kwargs)

    def validate(self):
        super(Document, self).validate()
        self.env.validate()


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Document',)

#-------------------------------------------------------------------------------
