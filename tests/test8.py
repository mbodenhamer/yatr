import os
from yatr import Env
env = Env()

@env.jinja_filter('foo')
def foo(value, **kwargs):
    return '{}_foo'.format(value)

@env.jinja_function('bar')
def bar(value, **kwargs):
    return '{}_bar'.format(value)

@env.task('barfoo')
def barfoo(env, *args, **kwargs):
    print(os.path.join(kwargs['path'], kwargs['baz1']))
