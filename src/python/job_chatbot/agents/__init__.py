"""In-process agents (CompanyConfirm, Scraper).

These run inside the orchestrator process and are invoked through the
Anthropic SDK's tool-use loop. The "out-of-process" half of the hybrid lives
in ``job_chatbot.workers``.
"""
