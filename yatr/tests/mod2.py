from yatr import Context, Env

class Foo(Context):
    context_name = 'foo'

env = Env(contexts=dict(foo=Foo()))
