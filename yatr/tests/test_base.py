from itertools import product
from nose.tools import assert_raises
from yatr.base import resolve, ordering_relations, nested_order_relations
from syn.base_utils import topological_sorting, rand_list, Precedes
from syn.five import xrange

#-------------------------------------------------------------------------------
# Utilities

def test_resolve():
    assert resolve('abc', {}) == 'abc'
    assert_raises(KeyError, resolve, 'ab{c}', {})
    assert resolve('ab{c}', dict(c='d')) == 'abd'
    assert resolve('ab{{c}}', {}) == 'ab'
    assert resolve('ab{{c}}', dict(c='d')) == 'abd'

def test_ordering_relations():
    assert ordering_relations([]) == []
    assert ordering_relations(['a']) == []
    assert ordering_relations(['a', 'b']) != []

    lst = rand_list(min_len=10, max_len=10, types=[str])
    rels = ordering_relations(lst)
    for k in xrange(5):
        assert topological_sorting(lst, rels) == lst

def test_nested_order_relations():
    assert nested_order_relations([]) == []
    assert nested_order_relations([dict(a='1')]) == []

    out = nested_order_relations([dict(a='1'), dict(b='2')])
    assert len(out) == 1
    assert isinstance(out[0], Precedes)
    assert out[0].A == 'a' and out[0].B == 'b'

    A = rand_list(min_len=1, max_len=5, types=[str])
    B = rand_list(min_len=1, max_len=5, types=[str])
    rels = nested_order_relations([A, B])
    for k in xrange(5):
        lst = topological_sorting(A + B, rels)
        
        for a, b in product(A, B):
            assert lst.index(a) <= lst.index(b)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
