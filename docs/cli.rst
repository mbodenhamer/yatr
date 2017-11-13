Command-Line Interface
======================

Usage
-----

.. literalinclude:: help.txt
   :language: console


Options
-------

``--cachedir``
~~~~~~~~~~~~~~

Certain yatr features make use of a cache directory to increase the efficiency of repeated yatr invocations.  The cache directory is currently used for processing yatrfiles included via URL (see :ref:`include`), extension modules included via URL (see :ref:`import`), as well as for populating bash tab completion values.  By default, the cache directory is set to ``~/.yatr/``, but this may be changed like so::

    $ yatr --cache-dir /path/to/cache/dir <some task or command>


``-f`` (``--yatrfile``)
~~~~~~~~~~~~~~~~~~~~~~~

Specify the yatrfile to load.  If this option is not supplied, yatr will try to load a file whose filename matches the regular expression ``^[Yy]atrfile(.yml)?$``.  If such a file is not present in the current working directory, yatr will search rootward up the filesystem tree looking for a file that matches the expression.  This is intended as a feature of convenience, so that tasks can be easily executed when working in a project sub-directory.  If it is unclear which yatrfile has been loaded, ``yatr --dump-path`` may be run to disambiguate.

``-i`` and ``-o``
~~~~~~~~~~~~~~~~~

The ``-i`` and ``-o`` options specify input and output files, respectively.  These options have no effect when invoking yatr to run a task, and are only used by specific yatr commands that require them, such as :ref:`render`.

``-m`` (``--macro``)
~~~~~~~~~~~~~~~~~~~~

Macro values may also be set or overridden at the command line by supplying the ``-m`` (or ``--macro``) option.  For example::

    $ yatr -f C.yml -m a=zab --macro d=jkl --dump
    a = zab
    b = ghi
    c = xyz
    d = jkl


(See :ref:`C.yml <c.yml>`)


``-s`` (``--setting``)
~~~~~~~~~~~~~~~~~~~~~~

Any setting value may be set or overridden at the command line by supplying the ``-s`` (or ``--setting``) option.  For example::

    $ yatr -f D.yml -s silent=false foo
    bar


(See :ref:`D.yml <settings>`)

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


(See :ref:`main example <main_example>`)

Commands
--------

As its name implies, yatr is primarily a task runner.  As such, its default execution behavior is to run tasks defined in a yatrfile.  However, when using a task runner in real-world applications, there are often situations where other execution behaviors become desirable.  For example, if it becomes necessary to debug a particular yatrfile, dumping the values of the macros (via ``yatr --dump``) might prove helpful.  As such, yatr supports a number of special execution behaviors, called "commands", which do not run tasks.  To avoid unnecessarily restricting the set of potential task names, all yatr commands are prefixed by ``--``.  However, unlike normal command-line options, at most one command should be specified at the command line for any yatr invocation.

The following table lists the available commands:

=============================== =========================================================================
Name                            Description
=============================== =========================================================================
``--dump``                      Dump macro values to ``stdout``
``--dump-path``                 Print yatrfile path to ``stdout``
``--install-bash-completions``  Install bash tab completion script in ``/etc/bash_completions.d/``
``--pull``                      Download all URL includes and imports defined in yatrfile
``--render``                    Use macros to render a Jinja2 template file (requires ``-i`` and ``-o``)
``--validate``                  Validate the yatrfile
``--version``                   Print version information to ``stdout``
=============================== =========================================================================

A discussion of each command is provided below.

``--dump``
~~~~~~~~~~

Prints macro values (including ``capture`` values) to ``stdout``.  For example, with :ref:`C.yml <c.yml>`, running ``--dump`` produces the following::

    $ yatr -f C.yml --dump
    a = baz
    b = ghi
    c = xyz

``--dump-path``
~~~~~~~~~~~~~~~

Prints the absolute path of the loaded yatrfile.  For example::

    $ yatr -f /path/to/yatrfile.yml --dump-path
    /path/to/yatrfile.yml


``--install-bash-completions``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installs script for dynamic bash tab completion support.  See :ref:`install`.

``--pull``
~~~~~~~~~~

Downloads all URL includes and imports defined in the loaded yatrfile.  If included yatrfiles define URL imports or includes, these will also be downloaded.

.. _render:

``--render``
~~~~~~~~~~~~

The ``--render`` command renders a Jinja2 template file using the macros defined by a yatrfile.  For example, suppose one has the following template for a Dockerfile named ``Dockerfile.j2``:

.. literalinclude:: ../tests/example/render/Dockerfile.j2
		    

Suppose one also has the following ``yatrfile.yml`` in the same directory:

.. literalinclude:: ../tests/example/render/yatrfile.yml
   :language: yaml


One could then run::

    $ yatr build


to generate the desired Dockerfile and then build the desired Docker image.  The generated Dockerfile would look like:

.. literalinclude:: ../tests/example/render/Dockerfile

``--validate``
~~~~~~~~~~~~~~

Validates the loaded yatrfile.  A number of validation tasks are performed during the course of loading a yatrfile (such as validating proper YAML syntax) even if the ``--validate`` command is not given.  However, the ``--validate`` command validates further aspects of the loaded task environment, such as ensuring that no task definitions contain undefined macros.  If an error is found, an exception will be raised and the program will terminate with a non-zero exit status.

``--version``
~~~~~~~~~~~~~

Prints the program name and current version to ``stdout``.
