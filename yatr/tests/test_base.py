from yatr.base import resolve, variables, ordered_macros, get_output

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

def test_get_output():
    out, code = get_output('true')
    assert out == ''
    assert code == 0

    out, code = get_output('false')
    assert out == ''
    assert code == 1

    out, code = get_output('python -c "raise Exception(\\"Test\\")"')
    assert 'Exception' in out
    assert code == 1

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
