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

Suppose you have the following ``yatrfile.yml`` in your current working directory
::
    tasks:


asdf

.. _Future Features:

Future Features
---------------

The following features are planned for future releases:

* Extension via custom Jinja2 filters.
