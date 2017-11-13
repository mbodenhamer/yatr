.. _yatrfile:

Yatrfile Structure and Features
===============================

.. _main_example:

Suppose you have the following ``yatrfile.yml`` in your `current working directory`_:

.. literalinclude:: ../tests/example/yatrfile.yml
   :language: yaml

As illustrated in this example, yatr currently supports five top-level keys in the yatrfile: ``include``, ``capture``, ``macros``, ``tasks``, and ``default``.  Two other sections, ``settings`` and ``import``, are also supported (see :ref:`settings` and :ref:`import`, respectively).

``macros``
----------

The ``macros`` section must be a mapping of macro names to macro definitions.  Macro definitions may either be plain strings or `Jinja2 templates`_.  Macros that include Jinja2 templates will be rendered according to the values of the macros in terms of which they are defined.  For example, in the above ``macros`` section, two macros ``b`` and ``c`` are defined thusly::

    b: bar
    c: "{{b}} baz"


As such, ``b`` resolves to ``bar`` and ``c`` resolves to ``bar baz``.  As the ``macros`` section is a mapping, and not a list, there is no inherent order to macro definition.  yatr takes care of resolving macros and their dependencies in the right order, provided that there are no cyclic macro definitions (e.g. a macro ``a`` defined in terms of ``b``, which is defined in terms of ``a``).  If any such cycles exist, the program will exit with an error.

.. _include:

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


If no default task is defined, and if yatr is invoked without any arguments, then yatr will exit after printing usage information.

``capture``
-----------

The ``capture`` section defines a special type of macro, specifying a mapping from a macro name to a system command whose captured output is to be the value of the macro.  Values of ``capture`` mappings cannot contain task references, though they may contain references to other macros.  In the main example above, the yatrfile defines a capture macro named ``baz``, whose definition is ``ls {{glob}}``.  In the macro section, ``glob`` is defined as ``*.yml``.  Thus, if yatr is invoked in the `example working directory`_, the value of ``baz`` will resolve to ``A.yml  B.yml  C.yml  D.yml  yatrfile.yml``.

.. _settings:

``settings``
------------

The top-level section ``settings`` allows the global execution behavior of yatr to be modified in various ways.  For example, the ``silent`` setting, if set to ``true``, will suppress all system command output at the console.  Such behavior is disabled by default.

An example of setting setting values in a yatrfile can be found in `D.yml`_, which includes the example yatrfile discussed in :ref:`yatrfile`:

.. literalinclude:: ../tests/example/D.yml
   :language: yaml


In the :ref:`example <main_example>` above, running ``yatr foo`` led to the output ``bar`` being printed to the console.  However, invoking the same task through ``D.yml`` will result in no output being printed::

    $ yatr -f D.yml foo
 

However, any setting can be set or overridden at the command line by supplying the ``-s`` option::

    $ yatr -f D.yml -s silent=false foo
    bar


For boolean-type settings, such as ``silent``, any of the following strings may be used to denote True, regardless of capitalization:  ``yes``, ``true``, ``1``.  Likewise, any of the following strings may be used to denote False, regardless of capitalization:  ``no``, ``false``, ``0``.

The following table lists the available settings:

================================ ================================================================================
Name                             Description
================================ ================================================================================
``loop_count_macro``             The name of the macro that contains the current loop iteration number (string)
``silent``                       If true, suppress task output; false by default (boolean string)
================================ ================================================================================

.. _import:

``import``
----------

The ``import`` feature enables the functionality of yatr to be extended when necessary, while preserving the simplicity of the default YAML specification for the majority of use cases for which the default capabilities of yatr are sufficient.

The ``import`` section must be a list of strings, each of which must be either a filesystem path or a URL specifying the location of a Python module.  Each module so imported must contain a top-level variable named ``env``, which must be an instance of the ``Env`` class (see :ref:`yatr\.env module`).  Modules to be imported in this manner are called "extension modules" (not to be confused with Python extension modules written in C/C++).

The following is an example of a yatr extension module:

.. literalinclude:: ../tests/test8.py
   :language: python

This particular extension module defines a custom Jinja2 function (see :ref:`Custom Jinja2 Functions`) and a custom Jinja2 filter (see :ref:`Custom Jinja2 Filters`).  Macros and tasks can theoretically be defined in an extension module through use of the yatr API, but the straightforward macro and task declaration facilitated by the standard yatrfile YAML syntax makes the use of ``include`` directives a much more efficient and user-friendly alternative.

In this example extension module, a Jinja2 function ``bar`` is defined that appends ``_bar`` to its first argument.  Likewise, a Jinja2 filter ``foo`` is defined that appends ``_foo`` to its first argument.  Because yatr supplies the current yatr definition environment to custom Jinja 2 filters and functions, all such filters and functions defined in extension modules should accept ``**kwargs`` as the final argument, even if the ``kwargs`` variable is not used within the body of the filter or function itself.

Here is an example yatrfile that uses the extension module defined above:

.. literalinclude:: ../tests/test8.yml
   :language: yaml

In addition to ``bar`` and ``foo``, this yatrfile also makes use of the built-in custom Jinja2 function ``env`` (see :ref:`env`).  The task ``baz`` is defined in terms of macros that make use of ``bar`` and ``foo``.  Invoking the task produces the following output::

    $ yatr baz
    baz_foo foo_bar

Custom Jinja2 Functions
-----------------------

The following functions are defined by default for use in Jinja2 templates.

``commands()``
~~~~~~~~~~~~~~

The ``commands`` function takes a single argument and prints the commands corresponding to the execution of the task whose name is the argument.  For example, suppose one is using the example yatrfile of the :ref:`import` section above in order to run a :ref:`render` command on the following template file (``template.j2``):

.. literalinclude:: ../tests/test8.j2
   :language: bash


One could then render the template like so::

    yatr -i template.j2 -o template.bash --render


The resulting output file (``template.bash``) would look like:

.. literalinclude:: ../tests/test8.bash
   :language: bash


.. _env:

``env()``
~~~~~~~~~

The ``env`` function takes either one or two arguments.  In either case, the first argument must be the name of an environment variable.  The ``env`` function will return the value of this environment variable if it is defined.  If the environment variable is undefined and only one argument is supplied to ``env``, the function will raise an exception and halt execution of the task.  On the other hand, if a second argument is supplied to ``env``, it will be returned in the case that the environment variable in question is undefined.

For example, consider the example yatrfile of the :ref:`import` section above.  The ``home`` macro is defined in terms of the environment variable ``PATH``.  In the practically-inconceivable case that ``PATH`` is not defined, yatr will exit with an exception when loading this yatrfile.  On the other hand, in an environment in which ``YATR_BAR`` is not defined, the program will behave as follows::

    $ yatr bar
    baz
    $ YATR_BAR=foo yatr bar
    foo


Custom Jinja2 Filters
---------------------

There are currently no custom Jinja2 filters defined by default for use in Jinja2 templates, but some will probably be added in future releases.

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

List Macros and For Loops
-------------------------

In most use cases, macros will either be plain strings or Jinja2 templates.  However, there are some cases in which it is useful to have a list of strings or macros defined itself as a macro.  To define such a "list macro", simply use YAML list syntax in the macro definition.  For example, consider the following yatrfile:

.. literalinclude:: ../tests/test7.yml
   :language: yaml

The macro ``a`` is a plain string, but both ``b`` and ``c`` are list macros.  List macros can be used for iteration via for loops, as is illustrated by the definitions of the tasks named ``foo`` and ``bar``.

The ``for`` key requires two sub-keys, ``var`` and ``in``.  The ``var`` sub-key defines the iteration variable(s), while the ``in`` sub-key specifies the lists or list macros over which to iterate.  In the case that ``var`` is a string value, ``for`` specifies a simple and intuitive for loop over the values specified by ``in``.  The value of ``in`` may either be the name of a list macro, as in the task named ``foo``, or a list literal, as in the task named ``bar``.  In the case that ``var`` is a list, ``for`` specifies a loop over the Cartesian product of the lists specified by ``in``.  The task named ``foo`` illustrates a 2x2 Cartesian product, while the task named ``bar`` illustrates a simple for loop.

It should be noted that the local variables defined by ``var`` only exist in the context of the execution of the loop.  It should also be noted that the for loop defines a special local variable named ``_n``, which contains the current iteration number.  Note that the task named ``foo`` is defined in terms of ``_n``.  As such::

    $ yatr foo
    x x w 0
    x x z 1
    x y w 2
    x y z 3


The name of ``_n`` may be changed if desired via the ``loop_count_macro`` setting.  For example::

    $ yatr -s loop_count_macro=count bar
    1 0
    2 1
    3 2
    4 3

.. _current working directory: https://github.com/mbodenhamer/yatr/tree/master/tests/example
.. _Jinja2 templates: http://jinja.pocoo.org/docs/latest/templates/
.. _example working directory: https://github.com/mbodenhamer/yatr/tree/master/tests/example
.. _test2.yml: https://github.com/mbodenhamer/yatrfiles/blob/master/yatrfiles/test/test2.yml
.. _D.yml: https://github.com/mbodenhamer/yatr/blob/master/tests/example/D.yml

