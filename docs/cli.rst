Command-Line Interface
======================

Usage
-----

.. literalinclude:: help.txt
   :language: console


If not supplied, ``<yatrfile>`` will default to a file matching the regular expression ``^[Yy]atrfile(.yml)?$``.  If such a file is not present in the current working directory, yatr will search rootward up the filesystem tree looking for a file that matches the expression.  This is intended as a feature of convenience, so that tasks can be easily executed when working in a project sub-directory.  If it is unclear which yatrfile has been loaded, ``yatr --dump-path`` may be run to disambiguate.  Likewise, the ``-f`` option may be supplied in order to force the loading of a particular yatrfile.

Options
-------

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


``-m``
~~~~~~

Macro values may also be set or overridden at the command line by supplying the ``-m`` option.  For example::

    $ yatr -f C.yml -m a=zab -m d=jkl --dump
    a = zab
    b = ghi
    c = xyz
    d = jkl


(See :ref:`C.yml <c.yml>`)


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

Many of the commands are self-explanatory, and their usage is illustrated in :ref:`example`.  Less-straightforward commands are discussed in more detail below.

``--render``
~~~~~~~~~~~~

The ``--render`` command renders a Jinja2 template file using the macros defined by a yatrfile.  This can be useful in certain cases where it is desirable to have scripts or configuration files that always contain the latest values for things such as version numbers whenever a task is run, which can be stored and modified in one central location whenever they need to be updated.  For example, suppose you have the following template for a Dockerfile named ``Dockerfile.j2``:

.. literalinclude:: ../tests/example/render/Dockerfile.j2
		    

Suppose one also has the following ``yatrfile.yml`` in the same directory:

.. literalinclude:: ../tests/example/render/yatrfile.yml
   :language: yaml


One could then run::

    $ yatr build


to generate the desired Dockerfile (i.e. resolve the ``{{version}}`` macro in the Dockerfile template to ``0.0.14``) and then build the desired Docker image.  The generated Dockerfile would look like:

.. literalinclude:: ../tests/example/render/Dockerfile


