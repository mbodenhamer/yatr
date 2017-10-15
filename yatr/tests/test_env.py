from yatr import Env
from yatr import env as ye
from syn.base_utils import assign

#-------------------------------------------------------------------------------
# Env

def test_env():
    with assign(ye, 'INITIAL_MACROS', dict(a='1', b='2')):
        e = Env()
        
        assert e.macros
        assert e.contexts
        assert e.default_context
        assert not e.tasks
        assert not e.secret_values

    e1 = Env(macros = [dict(a='b'),
                       dict(b='{{a}}c'),
                       dict(c='d{{b}}')])
    e2 = Env(macros = dict(a='a',
                           d='{{c}}e'))

    e1.update(e2)
    assert e1.macros == dict(a='a',
                             b='bc',
                             c='dbc',
                             d='dbce')

    e2.macros['a'] = 'c'
    e1.update(e2)
    assert e1.macros == dict(a='c',
                             b='bc',
                             c='dbc',
                             d='dbce')


#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
