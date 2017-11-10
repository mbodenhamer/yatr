.. _settings:

Settings
========

The top-level section ``settings`` allows the global execution behavior of yatr to be modified in various ways.  Only one setting (``silent``) is currently supported, but more will be added as more features are implemented.  The ``silent`` setting, if set to ``true``, will suppress all system command output at the console.  Such behavior is disabled by default.

An example of settings can be found in `D.yml`_, which includes the main yatrfile discussed in :ref:`example`:

.. literalinclude:: ../tests/example/D.yml
   :language: yaml


In the example above, running ``yatr foo`` led to the output ``bar`` being printed to the console.  However, invoking the same task through ``D.yml`` will result in no output being printed::

    $ yatr -f D.yml foo
 

However, any setting can be set or overridden at the command line by supplying the ``-s`` option::

    $ yatr -f D.yml -s silent=false foo
    bar


For boolean-type settings, such as ``silent``, any of the following strings may be used to denote True, regardless of capitalization:  ``yes``, ``true``, ``1``.  Likewise, any of the following strings may be used to denote False, regardless of capitalization:  ``no``, ``false``, ``0``.

.. _D.yml: https://github.com/mbodenhamer/yatr/blob/master/tests/example/D.yml
