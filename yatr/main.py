from . import __version__ as yver
from .env import INITIAL_MACROS

def main():
    print('yatr {}'.format(yver))

    # arg parsing

    # populate position arg macros
    args = []
    for k, arg in enumerate(args):
        key = '_{}'.format(k+1)
        INITIAL_MACROS[key] = arg

    # execute

    # TODO: if validate, do nothing other than doc.env.resolve_macros()

    # TODO: show command, which dumps specified variables or all (if none specified)
