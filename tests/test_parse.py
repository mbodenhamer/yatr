import os
from yatr import Document

DIR = os.path.abspath(os.path.dirname(__file__))
TEST1 = os.path.join(DIR, 'test1.yml')

#-------------------------------------------------------------------------------

def test1():
    test1 = Document.from_path(TEST1)
    assert test1.env.macros['abc'] == 'def'
    assert test1.env.macros['def'] == 'ghi'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
