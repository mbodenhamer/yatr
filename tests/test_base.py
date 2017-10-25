import os
from yatr import Document
from yatr.base import resolve_url

DIR = os.path.abspath(os.path.dirname(__file__))
YF1 = os.path.join(DIR, 'yatrfile1.yml')
URL = 'https://raw.githubusercontent.com/mbodenhamer/yatrfiles/master/yatrfiles/python/project.yml'

#-------------------------------------------------------------------------------
# Utilities

def test_resolve_url():
    assert resolve_url(YF1) == YF1
    Document.from_path(YF1).env.resolve_macros()

    path = resolve_url(URL)
    assert path.startswith('/root')
    Document.from_path(path).env.resolve_macros()

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
