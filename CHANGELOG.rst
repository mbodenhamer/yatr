Changelog
---------

0.0.11 (2018-xx-xx)
~~~~~~~~~~~~~~~~~~~

* Added [] read-only access to ``env.Env``.
* Added validation support for dict macros indexed by runtime-defined macros.
* Added better error messages for validation failures.
* Added macro resolution for task ``args`` and ``kwargs``.

0.0.10 (2018-03-28)
~~~~~~~~~~~~~~~~~~~
* Fixed issue where ``-m``-defined macros didn't override ``capture`` macros.
* Fixed issue where ``~`` and environment variables are not expanded in some paths.
* Added ``declare`` section, and fixed issue of yatrfiles with runtime-defined macros not validating.

0.0.9 (2018-02-03)
~~~~~~~~~~~~~~~~~~
* Added Env decorators.
* Added anonymous task definitions.
* Added support for importing extension modules with Python ``import`` statement-style names.

0.0.8 (2017-11-28)
~~~~~~~~~~~~~~~~~~

* Added ``--cache``.
* Added dictionary macros.

0.0.7 (2017-11-15)
~~~~~~~~~~~~~~~~~~

* Added ``files`` section and functionality.
* Refactored ``Command.run()``; removed ``Task.run_commands()`` and ``Command.run_command()``.
* Added arguments for calling tasks.
* Added more efficient ``yatr`` calls within yatrfiles.
* Added some builtin macros.

0.0.6 (2017-11-13)
~~~~~~~~~~~~~~~~~~

* Fixed default task specification not inheriting.
* Added for loop tasks and list macros.
* Added support for custom Jinja2 functions and filters.

0.0.5 (2017-11-02)
~~~~~~~~~~~~~~~~~~

* Fixed issue of capture command execution directory.
* Added default task section.
* Added ``--render``.

0.0.4 (2017-11-01)
~~~~~~~~~~~~~~~~~~

* Added bash tab completions.

0.0.3 (2017-10-29)
~~~~~~~~~~~~~~~~~~

* Fixed process management for running tasks.
* Added ``-m`` option.
* Added ``--cache-dir`` option.
* Added ``-p`` and ``-v`` options.
* Added support for macros and task references in ``if`` and ``ifnot`` keys.
* Added ``capture`` section and functionality.
* Added ``settings`` section.

0.0.2 (2017-10-26)
~~~~~~~~~~~~~~~~~~

* Added conditional task execution.
* Added URL support for includes and imports.
* Added support for macros in includes and imports.
* Added exit with task error return code.
* Added task referencing in task definition.

0.0.1 (2017-10-18)
~~~~~~~~~~~~~~~~~~

Initial release.
