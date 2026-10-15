"""The agent's two read-only data sources.

1. Google Calendar: Agno's ready-made toolkit, trimmed to two read tools.
2. Todoist: a tool we write ourselves. A plain Python function becomes a tool;
   Claude sees its name, type hints and docstring as the tool description.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from agno.tools.google.calendar import GoogleCalendarTools
from todoist_api_python.api import TodoistAPI

TZ = ZoneInfo("Asia/Manila")
ROOT = Path(__file__).resolve().parent.parent
READ_ONLY_SCOPE = "https://www.googleapis.com/auth/calendar.readonly"
MAX_TASKS = 25


def calendar_tools(calendar_id: str | None = None) -> GoogleCalendarTools:
    """Google Calendar toolkit that can only read."""
    # TODO 1.1 (MODULE.md §6.1): return a GoogleCalendarTools(...) that can only read.
    #   - credentials_path=str(ROOT / "credentials.json"), token_path=str(ROOT / "token.json")
    #   - scopes: only READ_ONLY_SCOPE                        (lock 1: Google refuses writes)
    #   - calendar_id: calendar_id, else env GOOGLE_CALENDAR_ID, else "primary"
    #   - include_tools: only "fetch_all_events" and "get_event"   (lock 2)
    #   - add_instructions=False  (the built-in prompt talks about write tools)
    raise NotImplementedError("TODO 1.1: build the read-only calendar toolkit in brief/tools.py")


def _due_to_str(due) -> str | None:
    """Todoist due dates come back as a date, a local datetime, or a UTC datetime."""
    if due is None:
        return None
    value = due.date
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(TZ)  # a UTC time near midnight is a different PHT day
        return value.isoformat(timespec="minutes")
    return value.isoformat()


def get_todays_tasks() -> str:
    """Return today's and overdue to-dos as a JSON list.

    Each item has: content, due (date or datetime), priority (4 = highest),
    is_overdue. Call this once per brief.
    """
    # TODO 0.1 (MODULE.md §5.2): fetch today's + overdue tasks from Todoist.
    #   1. today = today's date in Manila (TZ) as "YYYY-MM-DD"
    #   2. api = TodoistAPI(os.environ["TODOIST_API_TOKEN"])
    #   3. api.filter_tasks(query="today | overdue") yields PAGES (lists of tasks):
    #      loop over pages, then over tasks in each page
    #   4. for each task keep only: content, due (use _due_to_str(t.due)),
    #      priority, is_overdue (due's first 10 chars < today)
    #   5. sort: highest priority first, then earliest due
    #   6. return json.dumps(...) of at most MAX_TASKS items
    raise NotImplementedError("TODO 0.1: write get_todays_tasks in brief/tools.py")
