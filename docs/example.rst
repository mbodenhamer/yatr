.. _example:

Example(s)
==========

Suppose you have the following ``yatrfile.yml`` in your `current working directory`_:

.. literalinclude:: ../tests/example/yatrfile.yml
   :language: yaml

As illustrated in this example, yatr currently supports five top-level keys in the yatrfile: ``include``, ``capture``, ``macros``, ``tasks``, and ``default``.  A sixth top-level section ``settings`` is also supported (see :ref:`settings`).

``macros``
----------

The ``macros`` section must be a mapping of macro names to macro definitions.  Macro definitions may either be plain strings or `Jinja2 templates`_.  Macros that include Jinja2 templates will be rendered according to the values of the macros in terms of which they are defined.  For example, in the above ``macros`` section, two macros ``b`` and ``c`` are defined thusly::

    b: bar
    c: "{{b}} baz"


As such, ``b`` resolves to ``bar`` and ``c`` resolves to ``bar baz``.  As the ``macros`` section is a mapping, and not a list, there is no inherent order to macro definition.  yatr takes care of resolving macros and their dependencies in the right order, provided that there are no cyclic macro definitions (e.g. a macro ``a`` defined in terms of ``b``, which is defined in terms of ``a``).  If any such cycles exist, the program will exit with an error.

``include``
-----------

The ``include`` section must be a list of strings, each of which must be either a filesystem path or a URL specifying the location of another yatrfile.  When a yatrfile is "included" in this manner, its macros and tasks are added to the macros and tasks defined by the main yatrfile.  Nested includes are supported, following the rule that conflicts in macro or task names are resolved by favoring the definition closest to the main yatrfile.  

For example, suppose yatr is invoked on a yatrfile named ``C.yml``, which includes ``B.yml``, which includes ``A.yml``, as follows:

``A.yml``:

.. literalinclude:: ../tests/example/A.yml
   :language: yaml


``B.yml``:

.. literalinclude:: ../tests/example/B.yml
   :language: yaml


.. _c.yml:

``C.yml``:

.. literalinclude:: ../tests/example/C.yml
   :language: yaml


In this case, the macro values would resolve as follows::

    $ yatr -f C.yml --dump
    a = baz
    b = ghi
    c = xyz


Name conflicts of tasks from includes are resolved the same way as for macros.  

Include paths or URLs may use macros, as the main yatrfile above demonstrates, having an include defined in terms of the ``urlbase`` macro.  However, any such macros must be defined in the yatrfile itself, and cannot be defined in an included yatrfile or depend on the macros defined in an included yatrfile for their proper resolution.

If an include path is a URL, yatr will attempt to download the file and save it in a cache directory.  By default, the cache directory is set to ``~/.yatr/``, but this may be changed through the ``--cache-dir`` option.  If the URL file already exists in the cache directory, yatr will load the cached file without downloading.  To force yatr to re-download all URL includes specified by the yatrfile, run ``yatr --pull`` at the command line.

``tasks``
---------

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
-----------

The ``default`` section, if specified, must contain the name of a task to be run if no task names are provided at the command line.  In this example, the default task is set to ``foo``::

    default: foo


As such, running ``yatr`` at the command line is equivalent to running ``yatr foo``::

    $ yatr
    bar


``capture``
-----------

The ``capture`` section defines a special type of macro, specifying a mapping from a macro name to a system command whose captured output is to be the value of the macro.  Values of ``capture`` mappings cannot contain task references, though they may contain references to other macros.  In the main example above, the yatrfile defines a capture macro named ``baz``, whose definition is ``ls {{glob}}``.  In the macro section, ``glob`` is defined as ``*.yml``.  Thus, if yatr is invoked in the `example working directory`_, the value of ``baz`` will resolve to ``A.yml  B.yml  C.yml  D.yml  yatrfile.yml``.

Conditional Task Execution
--------------------------

Tasks may be defined to execute conditionally upon the successful execution of a command, using the keys ``if`` and ``ifnot``.  If these or other command options are used, the command itself must be explicitly identified by use of the ``command`` key.  These principles are illustrated in the ``cond1``, ``cond2``, ``cond3``, and ``cond4`` tasks::

    $ yatr cond1
    A.yml  B.yml  C.yml  D.yml  yatrfile.yml
    $ yatr cond2
    $ yatr cond3
    $ yatr cond4
    bar


The values supplied to ``if`` and ``ifnot`` may be anything that would otherwise constitute a valid task definition.  If a value is supplied for ``if``, the command will be executed only if the return code of the test command is zero.  Likewise, if a value is supplied for ``ifnot``, the command will be executed only if the return code of the test command is non-zero.


.. _current working directory: https://github.com/mbodenhamer/yatr/tree/master/tests/example
.. _Jinja2 templates: http://jinja.pocoo.org/docs/latest/templates/
.. _example working directory: https://github.com/mbodenhamer/yatr/tree/master/tests/example
.. _test2.yml: https://github.com/mbodenhamer/yatrfiles/blob/master/yatrfiles/test/test2.yml
