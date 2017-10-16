from copy import deepcopy

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

    e0 = deepcopy(e1)
    e0.resolve_macros()
    assert e0.macros == dict(a='b',
                             b='bc',
                             c='dbc')

    e1.update(e2)
    e1c = deepcopy(e1)
    e1.resolve_macros()
    assert e1.macros == dict(a='a',
                             b='ac',
                             c='dac',
                             d='dace')
    assert e1.macro_ordering.index('d') == 3

    e2.macros['a'] = 'c'
    e1c.update(e2)
    e1c.resolve_macros()
    assert e1c.macros == dict(a='c',
                              b='cc',
                              c='dcc',
                              d='dcce')


#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
