"""Delivery: one HTTP call to the Telegram Bot API.

To deliver somewhere else (email, Slack, Discord), only this file changes.
"""

import os  # noqa: F401

import httpx  # noqa: F401

ICON = {"first_up": "⏰", "day_shape": "📅", "top_task": "✅",
        "at_risk": "⚠️", "heads_up": "💡"}


def _post(text: str) -> None:
    # TODO 3.1 (MODULE.md §8): POST to Telegram's sendMessage.
    #   url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    #   json body: {"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=20
    #   call .raise_for_status() on the response so errors are not silent
    raise NotImplementedError("TODO 3.1: write _post() in brief/deliver.py")


def format_brief(brief) -> str:
    # TODO 3.2 (MODULE.md §8): first line "Morning brief · <date>",
    #   then one line per bullet: "<icon> <text>" (use ICON, fall back to "•").
    raise NotImplementedError("TODO 3.2: write format_brief() in brief/deliver.py")


def send(brief) -> None:
    _post(format_brief(brief))


def send_failure(err: Exception) -> None:
    # TODO 3.3 (MODULE.md §8): send "Morning brief failed: <ErrorType>. Check the Actions log."
    #   Only the error TYPE, never the message: it could contain calendar text or tokens.
    raise NotImplementedError("TODO 3.3: write send_failure() in brief/deliver.py")
