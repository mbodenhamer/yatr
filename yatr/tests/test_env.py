from copy import deepcopy
from nose.tools import assert_raises

from yatr import Env
from yatr import env as ye
from yatr.env import Updateable
from syn.base_utils import assign, assert_equivalent

#-------------------------------------------------------------------------------
# Env

def test_env():
    Updateable()._update_pre({})
    Updateable()._update_post({})

    with assign(ye, 'INITIAL_MACROS', dict(a='1', b='2')):
        e = Env()
        
        assert e.macros
        assert e.contexts
        assert e.default_context
        assert not e.tasks
        assert not e.secret_values

    e1 = Env(macros = dict(a='b',
                           b='{{a}}c',
                           c='d{{b}}'))
    e2 = Env(macros = dict(a='a',
                           d='{{c}}e'))
    e3 = Env(macros = dict(a='{{d}}'))

    e1c = e1.copy()
    assert_equivalent(e1, e1c)
    assert_equivalent(e1.macros, e1c.macros)

    e0 = deepcopy(e1)
    e0.resolve_macros()
    assert e0.env == dict(a='b',
                          b='bc',
                          c='dbc')

    e1.update(e2)
    e1c = deepcopy(e1)
    e1.resolve_macros()
    assert e1.env == dict(a='a',
                          b='ac',
                          c='dac',
                          d='dace')

    e2.macros['a'] = 'c'
    e1c.update(e2)
    e1c2 = deepcopy(e1c)
    e1c.resolve_macros()
    assert e1c.env == dict(a='c',
                           b='cc',
                           c='dcc',
                           d='dcce')

    e1c2.update(e3)
    assert_raises(ValueError, e1c2.resolve_macros)

    e = Env(default_task='foo')
    e.update(Env())
    assert e.default_task == 'foo'
    e.update(Env(default_task='bar'))
    assert e.default_task == 'bar'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
