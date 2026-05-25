"""Out-of-process worker scripts (DB, Tester).

These modules are invoked as subprocesses by the orchestrator. They read
JSON / CSV inputs from stdin or a path argument, do their work, and emit
a JSON result on stdout. This is the "hybrid" half of vteam-hybrid.
"""
