from yatr import Env

def foo(value, **kwargs):
    return '{}_foo'.format(value)

def bar(value, **kwargs):
    return '{}_bar'.format(value)

env = Env(jinja_filters=dict(foo=foo),
          jinja_functions=dict(bar=bar))
