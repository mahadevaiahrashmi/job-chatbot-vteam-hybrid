"""Multi-agent job-search chatbot built on the vteam-hybrid template.

The package exposes a small set of agents organized around the hybrid
orchestration pattern:

* In-process agents (``agents/``) are invoked directly from the
  orchestrator via Anthropic tool-use.
* Out-of-process worker scripts (``workers/``) are invoked as
  subprocesses, demonstrating the "hybrid" half of vteam-hybrid.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
