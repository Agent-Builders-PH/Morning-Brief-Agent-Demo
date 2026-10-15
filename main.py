"""Entry point: build today's window, run the agent, check the brief, send it.

    python main.py             # run and send to Telegram
    python main.py --dry-run   # run and print the brief instead (no Telegram needed)
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from agno.run.base import RunStatus
from dotenv import load_dotenv

load_dotenv()  # before importing brief: it reads BRIEF_NAME and MORNING_BRIEF_MODEL

from brief.agent import build_agent  # noqa: E402
from brief.deliver import format_brief, send, send_failure  # noqa: E402
from brief.schema import MorningBrief, in_order, validate  # noqa: E402

TZ = ZoneInfo("Asia/Manila")
REQUIRED_TOOLS = {"fetch_all_events", "get_todays_tasks"}
LOG_FILE = Path(__file__).resolve().parent / "logs" / "runs.jsonl"


class AgentRunFailed(RuntimeError):
    """The model call itself failed (bad API key, outage, rate limit)."""


class ToolFailure(RuntimeError):
    """A data source failed, so any brief written from it would be wrong."""


def today_window(now: datetime | None = None) -> tuple[datetime, datetime, datetime]:
    """Return (now, local midnight today, local midnight tomorrow), all in PHT."""
    # TODO 2.5 (MODULE.md §7.4, job 1):
    #   now = now or the current time in TZ
    #   start = now with hour, minute, second and microsecond set to 0
    #   end = start + one day
    raise NotImplementedError("TODO 2.5: write today_window() in main.py")


def build_prompt(now: datetime, start: datetime, end: datetime) -> str:
    # The exact window does two jobs: Claude knows what "today" is, and it passes
    # correct +08:00 timestamps to the calendar tool.
    return (
        f"Today is {now:%A, %B %d, %Y}. Timezone Asia/Manila (+08:00).\n"
        f"Fetch events from {start.isoformat()} to {end.isoformat()}, "
        f"then today's tasks, then write the brief."
    )


def check_run(result) -> None:
    """Raise if the run failed, or if a data source errored or was never read.

    Agno does not raise on these. A model error comes back as a run with status ERROR,
    and a tool error comes back to Claude as text. Without this check, an expired
    Google login turns into a confident "no meetings today".
    """
    # TODO 2.6 (MODULE.md §7.4, job 2):
    #   1. if result.status == RunStatus.error: raise AgentRunFailed(...)
    #   2. for each t in result.tools (may be None):
    #        remember t.tool_name
    #        if t.tool_call_error: raise ToolFailure(...)
    #        if json.loads(t.result) is a dict with an "error" key: raise ToolFailure(...)
    #        (skip results that aren't valid JSON)
    #   3. if any of REQUIRED_TOOLS was never called: raise ToolFailure(...)
    raise NotImplementedError("TODO 2.6: write check_run() in main.py")


def as_brief(content) -> MorningBrief:
    """Agno returns a MorningBrief when structured output worked; accept dict/JSON too."""
    if isinstance(content, MorningBrief):
        return content
    if isinstance(content, dict):
        return MorningBrief.model_validate(content)
    return MorningBrief.model_validate_json(content or "")


def log_run(result, attempt: int) -> None:
    """Append one line per run: which tools ran and how many tokens it cost."""
    m = result.metrics
    entry = {
        "at": datetime.now(TZ).isoformat(timespec="seconds"),
        "attempt": attempt,
        "model": result.model,
        "tools": [t.tool_name for t in result.tools or []],
        "input_tokens": getattr(m, "input_tokens", None),
        "output_tokens": getattr(m, "output_tokens", None),
        "cache_read_tokens": getattr(m, "cache_read_tokens", None),
    }
    print("run:", json.dumps(entry))
    LOG_FILE.parent.mkdir(exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def run(dry_run: bool = False, agent=None) -> MorningBrief:
    now, start, end = today_window()
    prompt = build_prompt(now, start, end)
    agent = agent or build_agent()
    # TODO 2.7 (MODULE.md §7.4, job 3): try at most twice.
    #   for attempt in (1, 2):
    #     result = agent.run(prompt); log_run(result, attempt); check_run(result)
    #     brief = as_brief(result.content); problems = validate(brief)
    #       (a ValueError from as_brief also counts as a problem)
    #     if no problems: put bullets in order, set date to start.date().isoformat(),
    #       print format_brief(brief) if dry_run else send(brief); return brief
    #     otherwise rebuild the prompt + a SELF-CONTAINED reminder of the 5-kind rule
    #       and the problems (agent.run() has no memory of the first try)
    #   after two failures: raise ValueError(...)
    raise NotImplementedError("TODO 2.7: write the attempt loop in run() in main.py")


def main() -> None:
    parser = argparse.ArgumentParser(description="Send today's 5-bullet morning brief.")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the brief instead of sending it to Telegram")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # the brief has emoji; old Windows consoles choke
    try:
        run(dry_run=args.dry_run)
    except Exception as e:
        if not args.dry_run:
            try:
                send_failure(e)
            except Exception as alert_error:
                print(f"Could not send the failure alert either: {alert_error!r}")
        raise


if __name__ == "__main__":
    main()
