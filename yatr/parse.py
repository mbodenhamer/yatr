import os
import imp
import yaml
from syn.base_utils import chdir
from syn.base import Base, Attr, init_hook
from syn.type import List, Dict
from syn.five import STR

from .base import ValidationError, resolve_url, resolve, ordered_macros,\
    DEFAULT_CACHE_DIR, str_to_bool, get_delete
from .context import Context
from .task import Task
from .env import Env

STRList = List(STR)

#-------------------------------------------------------------------------------
# Document

class Document(Base):
    _attrs = dict(imports = Attr(List(STR), init=lambda self:list()),
                  includes = Attr(List(STR), init=lambda self: list()),
                  secrets = Attr(List(STR), init=lambda self: list()),
                  macros = Attr(Dict((STR, int, List((STR, int, list)))), 
                                init=lambda self: dict()),
                  contexts = Attr(Dict(Context), init=lambda self: dict()),
                  tasks = Attr(Dict(Task), init=lambda self: dict()),
                  secret_values = Attr(Dict(STR), init=lambda self: dict()),
                  captures = Attr(Dict(STR), init=lambda self: dict()),
                  settings = Attr(Dict(None), init=lambda self: dict()),
                  default_task = Attr(STR, '', 'Task to run if no task is '
                                      'specified at the command line'),
                  env = Attr(Env, init=lambda self: Env(), internal=True),
                  dirname = Attr(STR, doc='Relative path for includes'),
                  cachedir = Attr(STR, '', 'Directory to store downloaded files'),
                  pull = Attr(bool, False, 'Force-pull URLs'),
                 )
    _opts = dict(init_validate = True)

    @classmethod
    def from_path(cls, path, **kwargs):
        with open(path, 'r') as f:
            dct = yaml.load(f)
            return cls.from_yaml(dct,
                                 os.path.abspath(os.path.dirname(path)), 
                                 **kwargs)

    @classmethod
    def from_yaml(cls, dct, dirname, **kwargs):
        get_delete(dct, kwargs, 'import', [], 'imports')
        get_delete(dct, kwargs, 'include', [], 'includes')
        get_delete(dct, kwargs, 'capture', {}, 'captures')
        get_delete(dct, kwargs, 'secrets', [])
        get_delete(dct, kwargs, 'macros', {})
        get_delete(dct, kwargs, 'contexts', {})
        get_delete(dct, kwargs, 'tasks', {})
        get_delete(dct, kwargs, 'default', '', 'default_task')

        settings = dict(dct.get('settings', {}))
        settings.update(kwargs.get('settings', {}))
        kwargs['settings'] = settings
        if 'settings' in dct:
            del dct['settings']

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
        cachedir = DEFAULT_CACHE_DIR
        if self.cachedir:
            cachedir = self.cachedir

        self.process_settings(**kwargs)

        jenv = Env().jenv
        pre_macros = dict(self.macros)
        for name, macro in ordered_macros(pre_macros, lenient=True):
            try:
                pre_macros[name] = resolve(macro, pre_macros, lenient=True,
                                           jenv=jenv)
            except:
                pass # There might be macros defined in terms of
                     # jinja_functions to be imported

        def process(path):
            return resolve_url(resolve(path, pre_macros, jenv=jenv), 
                               cachedir=cachedir, force=self.pull)

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
                  secret_values=self.secret_values, captures=self.captures,
                  settings=self.settings, default_task=self.default_task)
        self.env.update(env, **kwargs)

    def post_process(self, **kwargs):
        with chdir(self.dirname):
            self.env.resolve_macros()
            self.validate()

    def process_import(self, path, **kwargs):
        mod = imp.load_source('yatr_module_import', path)
        
        if not hasattr(mod, 'env'):
            raise ImportError("yatr extension module '{}' has no env"
                              .format(path))

        self.env.update(mod.env, **kwargs)

    def process_include(self, path, **kwargs):
        doc = Document.from_path(path, pull=self.pull, cachedir=self.cachedir,
                                 settings=self.settings)
        self.env.update(doc.env, **kwargs)

    def process_secret(self, name, **kwargs):
        raise NotImplementedError('Secrets currently unsupported')

    def process_settings(self, **kwargs):
        self.settings['silent'] = \
            str_to_bool(self.settings.get('silent', False))
        self.settings['loop_count_macro'] = \
            self.settings.get('loop_count_macro', '_n')

    def run(self, name, **kwargs):
        try:
            with chdir(self.dirname):
                return self.env.tasks[name].run(self.env, **kwargs)
        except KeyError:
            raise RuntimeError('No such task: {}'.format(name))

    def validate(self):
        super(Document, self).validate()
        self.env.validate()


#-------------------------------------------------------------------------------

DEFAULT_SETTINGS = sorted(Document(dirname=os.getcwd()).env.settings.keys())

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Document',)

#-------------------------------------------------------------------------------
