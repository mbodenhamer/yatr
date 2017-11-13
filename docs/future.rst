Future Features
===============

As an inspection of the source code might reveal, two additional top-level keys are also allowed in a yatrfile:  ``secrets``, and ``contexts``.  The ``secrets`` section defines a special type of macro, specifying a list of names corresponding to secrets that should not be stored as plaintext.  In future releases, yatr will attempt to find these values in the user keyring, and then prompt the user to enter their values via stdin if not present.  There will also be an option to store values so entered in the user keyring to avoid having to re-enter them on future task invocations.  No support for secrets is implemented at present, however.

The ``contexts`` section allows the specification of custom execution contexts in which tasks are invoked.  For example, one might define a custom shell execution context that specifies the values of various environment variables to avoid cluttering up a task definition with extra macros or statements.  This feature is not currently supported, and its future is uncertain.
