yatr
====

.. image:: https://travis-ci.org/mbodenhamer/yatr.svg?branch=master
    :target: https://travis-ci.org/mbodenhamer/yatr
    
.. image:: https://img.shields.io/coveralls/mbodenhamer/yatr.svg
    :target: https://coveralls.io/r/mbodenhamer/yatr

.. image:: https://readthedocs.org/projects/yatr/badge/?version=latest
    :target: http://yatr.readthedocs.org/en/latest/?badge=latest

Yet Another Task Runner.  Or alternatively, YAml Task Runner.  Yatr is a YAML-based task runner that attempts to implement and extend the best features of GNU Make for 21st-century software development contexts that are not centered around the compilation of C/C++ code.

Installation
------------
::

    $ pip install yatr


Usage
-----
::

    usage: yatr [-h] [-f <yatrfile>] [--version] [--validate] [--dump]
            [--dump-path] [--pull]
            [<task>] [ARGS [ARGS ...]]

    Yet Another Task Runner.

    positional arguments:
      <task>                The task to run
      ARGS                  Additional arguments for the task

    optional arguments:
      -h, --help            show this help message and exit
      -f <yatrfile>, --yatrfile <yatrfile>
			    The yatrfile to load
      --version             Print version
      --validate            Only validate the yatrfile
      --dump                Dump macro values
      --dump-path           Print yatrfile path
      --pull                Force download of URL includes and imports


If not supplied, ``<yatrfile>`` will default to a file matching the regular expression ``^[Yy]atrfile(.yml)?$``.  If such a file is not present in the current working directory, yatr will search rootward up the filesystem tree looking for a file that matches the expression.  This is intended as a feature of convenience, so that tasks can be easily executed when working in a project sub-directory.

Example(s)
----------

Suppose you have the following ``yatrfile.yml`` in your current working directory::

    include:
      - "{{urlbase}}/test/test2.yml"

    macros:
      urlbase: https://raw.githubusercontent.com/mbodenhamer/yatrfiles/master/yatrfiles
      b: bar
      c: "{{b}} baz"

    tasks:
      cwd: pwd

      bar:
	- foo
	- "echo {{c}} {{_1}}"

      cond1:
	command: foo
	if: "true"

      cond2:
	command: foo
	if: "false"

      cond3:
	command: foo
	ifnot: "true"

      cond4:
	command: foo
	ifnot: "false"


As illustrated in this example, yatr currently supports three top-level keys in the yatrfile: ``include``, ``macros``, and ``tasks``.  The ``macros`` section must be a mapping of macro names to macro definitions.  Macro definitions may either be plain strings or `Jinja2 templates`_.

The ``include`` section must be a list of strings, each of which must be either a filesystem path or a URL specifying the location of another yatrfile.  When a yatrfile is "included" in this manner, its macros and tasks are added to the macros and tasks defined by the main yatrfile.  Nested includes are supported, with the rule that conflicts in macro or task names are resolved by favoring the definition closest to the main yatrfile.  

For example, suppose ``yatr`` is invoked on a yatrfile named ``C.yml``, which includes ``B.yml``, which includes ``A.yml``, as follows:

``A.yml``::

    macros:
      a: foo
      b: def
      c: xyz

``B.yml``::

    include:
      - A.yml

    macros:
      a: bar
      b: ghi

``C.yml``::

    include:
      - B.yml

    macros:
      a: baz

In this case, the macro values would resolve as follows::

    $ yatr -f C.yml --dump
    a = baz
    b = ghi
    c = xyz


Include paths or URLs may use macros, as the main example above demonstrates.  However, any such macros must be defined in the yatrfile itself, and cannot be defined in an included yatrfile.

If an include path is a URL, yatr will attempt to download the file and save it in a cache directory.  The cache directory is currently set to ``~/.yatr/``, but future releases will make this configurable.  If the URL file already exists in the cache directory, yatr will load the cached file without downloading.  To force yatr to re-download all URL includes in the yatrfile, supply the ``--pull`` option at the command line.

Tasks

name conflicts from includes resolved the same way as macros

Tasks may be defined as a single command string.  For example, if your current working directory is ``/foo/baz``, then in this example::

    $ yatr cwd
    /foo/baz

After includes are processed, macros are not resolved until task runtime, as the main example demonstrates.  That yatrfile specifies the inclusion of a file named `test2.yml`_, which defines a task named ``foo``.  However, ``foo`` is defined in terms of a macro named ``b``, which is not defined in ``test2.yml``.  The macro ``b`` is defined in the main yatrfile, however, which induces the following behavior::

    $ yatr foo
    bar

Tasks may also be defined as a list of command strings, to be executed one after the other::

    $ yatr bar foo
    foo
    bar baz foo

In that example, command line args...
Task name reference...

Lastly, tasks may be defined to execute conditionally upon the successful execution of a command::

    $ yatr cond1
    bar
    $ yatr cond2
    $ yatr cond3
    $ yatr cond4
    bar

adslfkj

.. _Jinja2 templates: http://jinja.pocoo.org/docs/latest/templates/
.. _test2.yml: https://github.com/mbodenhamer/yatrfiles/blob/master/yatrfiles/test/test2.yml

.. _Future Features:

Future Features
---------------

As an inspection of the source code might reveal, three additional top-level keys are also allowed in a yatrfile:  ``import``, ``secrets``, and ``contexts``.  The ``import`` section, much like ``include``, specifies a list of paths or URLs.  However, unlike ``include``, which specifies other yatrfiles, the ``import`` section specifies Python modules to import that will extend the functionality of yatr.  While implemented at a basic level, the future shape of this feature is uncertain and thus its use is not recommended at this time.  However, the goal of this feature is to enable the functionality of yatr to be extended in arbitrarily-complex ways when necessary, while preserving the simplicity of the default YAML specification for the other 95% of use cases that do not require such complexity.

The ``secrets`` section specifies a list of names corresponding to secrets that should not be stored on disk in plaintext.  In future releases, yatr will attempt to find these values in the user keyring, and then prompt the user to enter their values via stdin if not present.  There will also be an option to store these values in the user keyring to avoid having to re-enter them on future task invocations.  No support for secrets is implemented at present, however.

The ``contexts`` section allows the specification of custom execution contexts in which tasks are invoked.  For example, one might define a custom shell execution context that specifies the values of various environment variables to avoid cluttering up a task definition with extra macros or statements.  This feature is not currently supported, and its future is uncertain.

A top-level ``settings`` section is also planned for configuring the default behavior of tasks in various ways.
