from yatr.main import main

#-------------------------------------------------------------------------------
# main

def test_main():
    main()

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
