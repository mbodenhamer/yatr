from yatr.base import resolve, variables, ordered_macros

#-------------------------------------------------------------------------------
# Utilities

def test_resolve():
    assert resolve('abc', {}) == 'abc'
    assert resolve('ab{{c}}', {}) == 'ab'
    assert resolve('ab{{c}}', dict(c='d')) == 'abd'

def test_variables():
    assert variables('{{a}} {{b}}') == {'a', 'b'}

def test_ordered_macros():
    assert list(ordered_macros({})) == []

    dct = dict(a = 'b')
    assert list(ordered_macros(dct)) == [('a', 'b')]

    dct = dict(a = 'b',
               b = '{{a}}',
               c = '{{b}}')
    assert list(ordered_macros(dct)) == [('a', 'b'), 
                                         ('b', '{{a}}'),
                                         ('c', '{{b}}')]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
