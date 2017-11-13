.. _install:

Installation
============

.. highlight:: console

To install, simply run::

    $ pip install yatr


Dynamic tab completions for bash are supported.  To install, run::

    $ yatr --install-bash-completions


As with invoking ``pip``, you will need to have root access or use ``sudo``.

.. highlight:: bash

Depending on your system configuration, configurable bash tab completions may not be enabled by default.  If it is infeasible or undesirable to enable such functionality globally, then the file ``/etc/bash_completion.d/yatr`` will need to be sourced in ``~/.bashrc``.  This can be accomplished by adding the following line::

    source /etc/bash_completion.d/yatr

.. highlight:: python
