yatr
====

.. image:: https://travis-ci.org/mbodenhamer/yatr.svg?branch=master
    :target: https://travis-ci.org/mbodenhamer/yatr
    
.. image:: https://img.shields.io/coveralls/mbodenhamer/yatr.svg
    :target: https://coveralls.io/r/mbodenhamer/yatr

.. image:: https://readthedocs.org/projects/yatr/badge/?version=latest
    :target: http://yatr.readthedocs.org/en/latest/?badge=latest

Yet Another Task Runner.  Or alternatively, YAml Task Runner.  Yatr is a YAML-based task runner that attempts to implement and extend the best features of GNU Make for 21st-century software development contexts that are not centered around the compilation of C/C++ code.  The project is in preliminary development, but is nonetheless functional for basic applications.

Installation
------------
::

    $ pip install yatr


Dynamic bash tab completions are supported.  To install, run::

    $ yatr --install-bash-completions


As with invoking ``pip``, you will need to have root access or use ``sudo``.  Depending on your system configuration, configurable bash tab completions may not be enabled by default.  If it is infeasible or undesirable to enable such functionality globally, the above command also prints out instructions for how to enable tab completions for ``yatr`` locally.

Usage
-----
::

    usage: yatr [-h] [-f <yatrfile>] [-i <file>] [-o <file>] [-m <macro>=<value>]
		[-s <setting>=<value>] [--cache-dir <DIR>] [-v] [-p] [--dump]
		[--dump-path] [--pull] [--render] [--version] [--validate]
		[--install-bash-completions]
		[<task>] [ARGS [ARGS ...]]

    Yet Another Task Runner.

    positional arguments:
      <task>                The task to run
      ARGS                  Additional arguments for the task

    optional arguments:
      -h, --help            show this help message and exit
      -f <yatrfile>, --yatrfile <yatrfile>
			    The yatrfile to load
      -i <file>             Input file
      -o <file>             Output file
      -m <macro>=<value>, --macro <macro>=<value>
			    Set/override macro with specified value
      -s <setting>=<value>, --setting <setting>=<value>
			    Set/override setting with specified value
      --cache-dir <DIR>     Path of cache directory
      -v, --verbose         Print commands to be run
      -p, --preview         Preview commands to be run without running them
			    (implies -v)
      --dump                Dump macro values and exit
      --dump-path           Print yatrfile path and exit
      --pull                Download all URL includes and imports, then exit
      --render              Use macros to render a Jinja2 template file (requires
			    -i and -o)
      --version             Print version info and exit
      --validate            Validate the yatrfile and exit
      --install-bash-completions
			    Install bash tab completion script globally, then exit


If not supplied, ``<yatrfile>`` will default to a file matching the regular expression ``^[Yy]atrfile(.yml)?$``.  If such a file is not present in the current working directory, yatr will search rootward up the filesystem tree looking for a file that matches the expression.  This is intended as a feature of convenience, so that tasks can be easily executed when working in a project sub-directory.  If it is unclear which yatrfile has been loaded, ``yatr --dump-path`` may be run to disambiguate.  Likewise, the ``-f`` option may be supplied in order to force the loading of a particular yatrfile.

Example(s)
----------

Suppose you have the following ``yatrfile.yml`` in your `current working directory`_::

    include:
      - "{{urlbase}}/test/test2.yml"

    capture:
      baz: "ls {{glob}}"
    
    macros:
      urlbase: https://raw.githubusercontent.com/mbodenhamer/yatrfiles/master/yatrfiles
      b: bar
      c: "{{b}} baz"
      canard: "false"
      glob: "*.yml"
    
    default: foo

    tasks:
      cwd: pwd

      bar:
	- foo
	- "echo {{c}} {{_1|default('xyz')}}"

      verily: "true"

      cond1:
	command: 'echo "{{baz}}"'
	if: "true"

      cond2:
	command: foo
	if: "false"

      cond3:
	command: foo
	ifnot: verily

      cond4:
	command: foo
	ifnot: "{{canard}}"


As illustrated in this example, yatr currently supports five top-level keys in the yatrfile: ``include``, ``capture``, ``macros``, ``tasks``, and ``default``.  A sixth top-level section ``settings`` is also supported (see Settings_).

``macros``
~~~~~~~~~~

The ``macros`` section must be a mapping of macro names to macro definitions.  Macro definitions may either be plain strings or `Jinja2 templates`_.  Macros that include Jinja2 templates will be rendered according to the values of the macros in terms of which they are defined.  For example, in the above ``macros`` section, two macros ``b`` and ``c`` are defined thusly::

    b: bar
    c: "{{b}} baz"


As such, ``b`` resolves to ``bar`` and ``c`` resolves to ``bar baz``.  As the ``macros`` section is a mapping, and not a list, there is no inherent order to macro definition.  yatr takes care of resolving macros and their dependencies in the right order, provided that there are no cyclic macro definitions (e.g. a macro ``a`` defined in terms of ``b``, which is defined in terms of ``a``).  If any such cycles exist, the program will exit with an error.

``include``
~~~~~~~~~~~

The ``include`` section must be a list of strings, each of which must be either a filesystem path or a URL specifying the location of another yatrfile.  When a yatrfile is "included" in this manner, its macros and tasks are added to the macros and tasks defined by the main yatrfile.  Nested includes are supported, following the rule that conflicts in macro or task names are resolved by favoring the definition closest to the main yatrfile.  

For example, suppose yatr is invoked on a yatrfile named ``C.yml``, which includes ``B.yml``, which includes ``A.yml``, as follows:

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


Name conflicts of tasks from includes are resolved the same way as for macros.  

Macro values may also be set or overridden at the command line by supplying the ``-m`` option.  For example::

    $ yatr -f C.yml -m a=zab -m d=jkl --dump
    a = zab
    b = ghi
    c = xyz
    d = jkl

Include paths or URLs may use macros, as the main example above demonstrates, as it has an include defined in terms of the ``urlbase`` macro.  However, any such macros must be defined in the yatrfile itself, and cannot be defined in an included yatrfile or depend on the macros defined in an included yatrfile for their proper resolution.

If an include path is a URL, yatr will attempt to download the file and save it in a cache directory.  By default, the cache directory is set to ``~/.yatr/``, but this may be changed through the ``--cache-dir`` option.  If the URL file already exists in the cache directory, yatr will load the cached file without downloading.  To force yatr to re-download all URL includes specified by the yatrfile, run ``yatr --pull`` at the command line.

``tasks``
~~~~~~~~~

Tasks are defined in the ``tasks`` section of the yatrfile.  Tasks may be defined as a single command string.  In this example, the task ``cwd`` is simply defined as the system command ``pwd``.  If your current working directory happens to be ``/foo/baz``, then::

    $ yatr cwd
    /foo/baz


Macros are not fully resolved until task runtime.  The example yatrfile specifies the inclusion of a file named `test2.yml`_, which defines a task named ``foo``.  However, ``foo`` is defined in terms of a macro named ``b``, which is not defined in ``test2.yml``.  The macro ``b`` is defined in the main yatrfile, however, which induces the following behavior::

    $ yatr foo
    bar


If no default task is defined, and if yatr is invoked without any arguments, then yatr will exit after printing usage information.

Tasks may also be defined as a list of command strings, to be executed one after the other, as illustrated by ``bar``::

    $ yatr bar
    bar
    bar baz xyz


If the command string is the name of a defined task, then yatr will simply execute that task instead of trying to execute that string as a system command.  The ``bar`` task will first execute the ``foo`` task defined in `test2.yml`_, and then run the ``echo`` command.

The ``bar`` task also illustrates another feature of yatr:  command-line arguments may be passed to tasks for execution.  For example::

    $ yatr bar foo
    bar
    bar baz foo


Unless, explicitly re-defined, the macro ``_1`` denotes the first task command-line argument, ``_2`` denotes the second task command-line argument, and so on.  Default values may be specified using the Jinja2 ``default`` filter, as is illustrated in the definition of ``bar``.

``default``
~~~~~~~~~~~

The ``default`` section, if specified, must contain the name of a task to be run if no task names are provided at the command line.  In this example, the default task is set to ``foo``::

    default: foo


As such, running ``yatr`` at the command line is equivalent to running ``yatr foo``::

    $ yatr
    bar


``-v`` and ``-p``
~~~~~~~~~~~~~~~~~

If the ``-v`` option is supplied at the command line, yatr will print the commands to be run before running them::

    $ yatr -v bar foo
    echo bar
    bar
    echo bar baz foo
    bar baz foo


If the ``-p`` option is supplied, yatr will simply print the commands without running them::

    $ yatr -p bar foo
    echo bar
    echo bar baz foo


``capture``
~~~~~~~~~~~
The ``capture`` section defines a special type of macro, specifying a mapping from a macro name to a system command whose captured output is to be the value of the macro.  Values of ``capture`` mappings cannot contain task references, though they may contain references to other macros.  In the main example above, the yatrfile defines a capture macro named ``baz``, whose definition is ``ls {{glob}}``.  In the macro section, ``glob`` is defined as ``*.yml``.  Thus, if yatr is invoked in the `example working directory`_, the value of ``baz`` will resolve to ``A.yml  B.yml  C.yml  D.yml  yatrfile.yml``.

Conditional Task Execution
~~~~~~~~~~~~~~~~~~~~~~~~~~

Tasks may be defined to execute conditionally upon the successful execution of a command, using the keys ``if`` and ``ifnot``.  If these or other command options are used, the command itself must be explicitly identified by use of the ``command`` key.  These principles are illustrated in the ``cond1``, ``cond2``, ``cond3``, and ``cond4`` tasks::

    $ yatr cond1
    A.yml  B.yml  C.yml  D.yml  yatrfile.yml
    $ yatr cond2
    $ yatr cond3
    $ yatr cond4
    bar


The values supplied to ``if`` and ``ifnot`` may be anything that would otherwise constitute a valid task definition.  If a value is supplied for ``if``, the command will be executed only if the return code of the test command is zero.  Likewise, if a value is supplied for ``ifnot``, the command will be executed only if the return code of the test command is non-zero.

.. _Jinja2 templates: http://jinja.pocoo.org/docs/latest/templates/
.. _test2.yml: https://github.com/mbodenhamer/yatrfiles/blob/master/yatrfiles/test/test2.yml
.. _current working directory: https://github.com/mbodenhamer/yatr/tree/master/tests/example
.. _example working directory: https://github.com/mbodenhamer/yatr/tree/master/tests/example

Settings
--------

The top-level section ``settings`` allows the global execution behavior of yatr to be modified in various ways.  Only one setting (``silent``) is currently supported, but more will be added as more features are implemented.  The ``silent`` setting, if set to ``true``, will suppress all system command output at the console.  Such behavior is disabled by default.

An example of settings can be found in `D.yml`_, which includes the main example yatrfile discussed above::

    include:
      - yatrfile.yml

    settings:
      silent: true


In the example above, running ``yatr foo`` led to the output ``bar`` being printed to the console.  However, invoking the same task through `D.yml`_ will result in no output being printed::

    $ yatr -f D.yml foo
 

However, any setting can be set or overridden at the command line by supplying the ``-s`` option::

    $ yatr -f D.yml -s silent=false foo
    bar


For boolean-type settings, such as ``silent``, any of the following strings may be used to denote True, regardless of capitalization:  ``yes``, ``true``, ``1``.  Likewise, any of the following strings may be used to denote False, regardless of capitalization:  ``no``, ``false``, ``0``.

.. _D.yml: https://github.com/mbodenhamer/yatr/blob/master/tests/example/D.yml

Commands
--------

As its name implies, yatr is primarily a task runner.  As such, its default execution behavior is to run tasks defined in a yatrfile.  However, when using a task runner in real-world applications, there are often situations where other execution behaviors become desirable.  For example, if it becomes necessary to debug a particular yatrfile, dumping the values of the macros (via ``yatr --dump``) might prove helpful.  As such, yatr supports a number of special execution behaviors, called "commands", which do not run tasks.  To avoid unnecessarily restricting the set of potential task names, all yatr commands are prefixed by ``--``.  However, unlike normal command-line options, at most one command should be specified at the command line for any yatr invocation.

The following table lists the available commands:

=============================== =========================================================================
Name                            Description
=============================== =========================================================================
``--dump``                      Dump macro values to ``stdout``
``--dump-path``                 Print yatrfile path to ``stdout``
``--pull``                      Download all URL includes and imports defined in yatrfile
``--render``                    Use macros to render a Jinja2 template file (requires ``-i`` and ``-o``)
``--version``                   Print version information to ``stdout``
``--validate``                  Validate the yatrfile
``--install-bash-completions``  Install bash tab completion script in ``/etc/bash_completions.d/``
=============================== =========================================================================

Most of the commands are self-explanatory, or have already been discussed in the examples above.  Those that do not fit this description are discussed in more detail below.

``--render``
~~~~~~~~~~~~

The ``--render`` command renders a Jinja2 template file using the macros defined by a yatrfile.  This can be useful in certain cases where it is desirable to have scripts or configuration files that always contain the latest values for things such as version numbers whenever a task is run, which can be stored and modified in one central location whenever they need to be updated.  For example, suppose you have the following template for a Dockerfile named ``Dockerfile.j2``::

    FROM python:2-alpine

    RUN pip install -U --no-cache \
	syn>={{version}}

    CMD ["python2"]


Suppose one also has the following ``yatrfile.yml`` in the same directory::

    macros:
      version: 0.0.14
      image: foo

    tasks:
      render: yatr --render -i Dockerfile.j2 -o Dockerfile
      build:
        - render
	- "docker build -t {{image}}:latest ."


One could then run::

    $ yatr build


to generate the desired Dockerfile (i.e. resolve the ``{{version}}`` macro in the Dockerfile template to ``0.0.14``) and then build the desired Docker image.

Future Features
---------------

As an inspection of the source code might reveal, three additional top-level keys are also allowed in a yatrfile:  ``import``, ``secrets``, and ``contexts``.  The ``import`` section, much like ``include``, specifies a list of paths or URLs.  However, unlike ``include``, which specifies other yatrfiles, the ``import`` section specifies Python modules to import that will extend the functionality of yatr.  While implemented at a basic level, the future shape of this feature is uncertain and thus its use is not recommended at this time.  However, the goal of this feature is to enable the functionality of yatr to be extended in arbitrarily-complex ways when necessary, while preserving the simplicity of the default YAML specification for the other 95% of use cases that do not require such complexity.

The ``secrets`` section defines a special type of macro, specifying a list of names corresponding to secrets that should not be stored as plaintext.  In future releases, yatr will attempt to find these values in the user keyring, and then prompt the user to enter their values via stdin if not present.  There will also be an option to store values so entered in the user keyring to avoid having to re-enter them on future task invocations.  No support for secrets is implemented at present, however.

The ``contexts`` section allows the specification of custom execution contexts in which tasks are invoked.  For example, one might define a custom shell execution context that specifies the values of various environment variables to avoid cluttering up a task definition with extra macros or statements.  This feature is not currently supported, and its future is uncertain.
