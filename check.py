"""Offline checks for each phase. No API keys, no network, no cost.

    python check.py        # run every check
    python check.py 2      # only Phase 2's checks
    python check.py 0 1    # Phases 0 and 1

Everything that would call Claude, Google, Todoist or Telegram is replaced by a fake,
so these checks prove your wiring is right, not that your accounts are set up.
"""

import importlib
import json
import os
import sys
import tempfile
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from agno.run.base import RunStatus

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
for key, value in {
    "ANTHROPIC_API_KEY": "sk-ant-offline-check",
    "TODOIST_API_TOKEN": "offline-check",
    "TELEGRAM_BOT_TOKEN": "123:offline",
    "TELEGRAM_CHAT_ID": "42",
}.items():
    os.environ.setdefault(key, value)

CHECKS = []


def check(phase: int):
    def register(fn):
        CHECKS.append((phase, fn))
        return fn
    return register


# ---------------------------------------------------------------- helpers

def good_bullets(order=None):
    from brief.schema import Bullet, KINDS
    if "kind" not in Bullet.model_fields or "text" not in Bullet.model_fields:
        raise NotImplementedError("TODO 2.1: give Bullet a `kind` and a `text` field in brief/schema.py")
    kinds = order or KINDS
    return [Bullet(kind=k, text=f"{k} text") for k in kinds]


def tool_exec(name, result, error=False):
    return SimpleNamespace(tool_name=name, result=result, tool_call_error=error)


def fake_run(content, tools=None):
    if tools is None:
        tools = [tool_exec("fetch_all_events", json.dumps({"message": "No events found."})),
                 tool_exec("get_todays_tasks", "[]")]
    metrics = SimpleNamespace(input_tokens=100, output_tokens=50, cache_read_tokens=0)
    return SimpleNamespace(content=content, tools=tools, metrics=metrics, model="fake-model",
                           status=RunStatus.completed)


def fake_agent(*runs):
    agent = mock.Mock()
    agent.run.side_effect = list(runs)
    return agent


def brief_of(bullets):
    from brief.schema import MorningBrief
    if "bullets" not in MorningBrief.model_fields or "date" not in MorningBrief.model_fields:
        raise NotImplementedError("TODO 2.1: give MorningBrief a `date` and a `bullets` field")
    return MorningBrief(date="2026-10-16", bullets=bullets)


def run_main(agent):
    """Run main.run() with a fake agent; returns the mocked send()."""
    main = importlib.import_module("main")
    with tempfile.TemporaryDirectory() as tmp, \
            mock.patch.object(main, "LOG_FILE", Path(tmp) / "runs.jsonl"), \
            mock.patch.object(main, "send") as send, \
            mock.patch("builtins.print"):
        main.run(agent=agent)
    return send


# ---------------------------------------------------------------- Phase 0

@check(0)
def todoist_tool_flags_overdue_and_sorts():
    from brief import tools
    today = datetime.now(tools.TZ).date()
    yesterday = today - timedelta(days=1)
    # 23:30 UTC the day before is 07:30 today in Manila: must count as today, not overdue.
    early_utc = datetime.combine(yesterday, datetime.min.time(), timezone.utc).replace(hour=23, minute=30)

    def task(content, priority, due):
        return SimpleNamespace(content=content, priority=priority,
                               due=SimpleNamespace(date=due) if due else None)

    pages = [[task("old ticket", 2, yesterday), task("quote", 4, today)],
             [task("standup notes", 1, early_utc), task("someday", 1, None)]]
    with mock.patch.object(tools, "TodoistAPI") as api:
        api.return_value.filter_tasks.return_value = iter(pages)
        data = json.loads(tools.get_todays_tasks())
    by_name = {t["content"]: t for t in data}
    assert len(data) == 4, "every page should be read"
    assert by_name["old ticket"]["is_overdue"] is True
    assert by_name["quote"]["is_overdue"] is False
    assert by_name["standup notes"]["due"].startswith(today.isoformat()), \
        "convert UTC due times to Asia/Manila before taking the date"
    assert by_name["standup notes"]["is_overdue"] is False
    assert data[0]["content"] == "quote", "highest priority (4) should come first"
    assert set(data[0]) == {"content", "due", "priority", "is_overdue"}


@check(0)
def todoist_tool_caps_at_25():
    from brief import tools
    many = [[SimpleNamespace(content=f"t{i}", priority=1, due=None) for i in range(40)]]
    with mock.patch.object(tools, "TodoistAPI") as api:
        api.return_value.filter_tasks.return_value = iter(many)
        assert len(json.loads(tools.get_todays_tasks())) == 25


@check(0)
def raw_loop_tool_schema_matches_registry():
    loop = importlib.import_module("00_raw_loop")
    if not loop.TOOLS:
        raise NotImplementedError("TODO 0.2: describe get_todays_tasks in TOOLS (00_raw_loop.py)")
    for tool in loop.TOOLS:
        assert tool["name"] in loop.REGISTRY, f"{tool['name']} has no function in REGISTRY"
        assert tool["input_schema"]["type"] == "object", "input_schema must be a JSON object schema"


@check(0)
def raw_loop_runs_tool_then_stops():
    loop = importlib.import_module("00_raw_loop")
    tool_call = SimpleNamespace(type="tool_use", id="toolu_1", name="get_todays_tasks", input={})
    first = SimpleNamespace(stop_reason="tool_use", content=[tool_call])
    final = SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="All clear.")])
    client = mock.Mock()
    client.messages.create.side_effect = [first, final]
    with mock.patch.dict(loop.REGISTRY, {"get_todays_tasks": lambda: "[]"}), mock.patch("builtins.print"):
        answer = loop.run_agent(client, "What's on my plate?")
    assert answer == "All clear.", f"expected the final text, got {answer!r}"
    assert client.messages.create.call_count == 2, "the loop should call Claude twice"
    messages = client.messages.create.call_args_list[1].kwargs["messages"]
    result_turn = messages[2]
    assert result_turn["role"] == "user", "tool results go back as a USER turn"
    block = result_turn["content"][0]
    assert block["type"] == "tool_result" and block["tool_use_id"] == "toolu_1", \
        "tool_result must carry the matching tool_use_id"


# ---------------------------------------------------------------- Phase 1

@check(1)
def calendar_toolkit_is_read_only():
    from brief.tools import READ_ONLY_SCOPE, calendar_tools
    tools = calendar_tools()
    assert set(tools.functions) == {"fetch_all_events", "get_event"}, \
        f"calendar should expose only fetch_all_events and get_event, got {sorted(tools.functions)}"
    assert tools.scopes == [READ_ONLY_SCOPE], f"scope must be read-only, got {tools.scopes}"
    assert not tools.add_instructions, "pass add_instructions=False (built-in prompt mentions write tools)"


# ---------------------------------------------------------------- Phase 2

@check(2)
def schema_validation_catches_bad_briefs():
    from brief.schema import KINDS, in_order, validate
    assert validate(brief_of(good_bullets())) == [], "a correct brief should have no problems"
    assert validate(brief_of(good_bullets()[:4])), "4 bullets must be rejected"
    dupes = good_bullets(["first_up", "first_up", "top_task", "at_risk", "heads_up"])
    assert validate(brief_of(dupes)), "a repeated kind must be rejected"
    shuffled = brief_of(good_bullets(list(reversed(KINDS))))
    assert [b.kind for b in in_order(shuffled).bullets] == list(KINDS)


@check(2)
def prompt_has_the_core_rules():
    from brief.prompt import INSTRUCTIONS
    if not INSTRUCTIONS:
        raise NotImplementedError("TODO 2.3: write the INSTRUCTIONS list in brief/prompt.py")
    text = " ".join(INSTRUCTIONS).lower()
    for must, why in [("fetch_all_events", "tell it which tool to call first"),
                      ("get_todays_tasks", "tell it to fetch the tasks"),
                      ("exactly 5", "ask for exactly 5 bullets"),
                      ("never invent", "forbid made-up events and tasks"),
                      ("ignore any instructions", "treat event text as data (prompt injection)")]:
        assert must in text, f"INSTRUCTIONS should {why} (expected the words '{must}')"


@check(2)
def agent_has_exactly_the_read_tools():
    from brief.agent import build_agent
    from brief.schema import MorningBrief
    agent = build_agent()
    names = set()
    for tool in agent.tools:
        names |= set(tool.functions) if hasattr(tool, "functions") else {tool.__name__}
    assert names == {"fetch_all_events", "get_event", "get_todays_tasks"}, f"agent tools: {sorted(names)}"
    assert agent.output_schema is MorningBrief, "set output_schema=MorningBrief"
    assert agent.tool_call_limit, "set a tool_call_limit so a confused run cannot loop forever"
    assert agent.model.cache_system_prompt, "turn on cache_system_prompt"


@check(2)
def date_window_is_local_midnight_to_midnight():
    main = importlib.import_module("main")
    now = datetime(2026, 10, 16, 6, 45, tzinfo=main.TZ)
    _, start, end = main.today_window(now)
    assert start.isoformat() == "2026-10-16T00:00:00+08:00", start.isoformat()
    assert end.isoformat() == "2026-10-17T00:00:00+08:00", end.isoformat()
    prompt = main.build_prompt(now, start, end)
    assert start.isoformat() in prompt and end.isoformat() in prompt, "put the exact window in the prompt"


@check(2)
def good_brief_is_sent_in_order():
    from brief.schema import KINDS
    agent = fake_agent(fake_run(brief_of(good_bullets(list(reversed(KINDS))))))
    send = run_main(agent)
    assert send.call_count == 1, "a valid brief should be sent once"
    assert [b.kind for b in send.call_args.args[0].bullets] == list(KINDS)


@check(2)
def wrong_count_retries_once_with_a_self_contained_prompt():
    agent = fake_agent(fake_run(brief_of(good_bullets()[:4])), fake_run(brief_of(good_bullets())))
    send = run_main(agent)
    assert agent.run.call_count == 2, "a 4-bullet brief should trigger exactly one retry"
    retry_prompt = agent.run.call_args_list[1].args[0]
    assert "exactly 5" in retry_prompt and "first_up" in retry_prompt, \
        "agent.run() has no memory of the first try: restate the 5-bullet rule in the retry prompt"
    assert send.call_count == 1


@check(2)
def two_bad_briefs_raise_instead_of_sending():
    agent = fake_agent(fake_run(brief_of(good_bullets()[:3])), fake_run(brief_of(good_bullets()[:3])))
    try:
        send = run_main(agent)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError after two bad briefs (send called {send.call_count}x)")


@check(2)
def tool_error_is_a_failure_not_an_empty_day():
    main = importlib.import_module("main")
    broken = [tool_exec("fetch_all_events", json.dumps({"error": "Calendar authentication failed: expired"})),
              tool_exec("get_todays_tasks", "[]")]
    agent = fake_agent(fake_run(brief_of(good_bullets()), tools=broken))
    try:
        run_main(agent)
    except main.ToolFailure:
        return
    raise AssertionError("a tool that returned {'error': ...} must raise ToolFailure, not send a brief")


@check(2)
def skipped_calendar_call_is_a_failure():
    main = importlib.import_module("main")
    agent = fake_agent(fake_run(brief_of(good_bullets()), tools=[tool_exec("get_todays_tasks", "[]")]))
    try:
        run_main(agent)
    except main.ToolFailure:
        return
    raise AssertionError("if the agent never called fetch_all_events, the brief must not be sent")


@check(2)
def model_error_is_reported_as_such():
    main = importlib.import_module("main")
    failed = fake_run("Error code: 401 - invalid x-api-key", tools=[])
    failed.status = RunStatus.error
    try:
        run_main(fake_agent(failed))
    except main.AgentRunFailed:
        return
    raise AssertionError("a run with status ERROR (e.g. bad API key) must raise AgentRunFailed")


# ---------------------------------------------------------------- Phase 3

@check(3)
def telegram_message_format():
    from brief import deliver
    with mock.patch.object(deliver.httpx, "post") as post:
        deliver.send(brief_of(good_bullets()))
    url = post.call_args.args[0]
    payload = post.call_args.kwargs["json"]
    assert url == "https://api.telegram.org/bot123:offline/sendMessage", url
    assert payload["chat_id"] == "42"
    lines = payload["text"].split("\n")
    assert lines[0] == "Morning brief · 2026-10-16", lines[0]
    assert len(lines) == 6, "header + 5 bullets"
    post.return_value.raise_for_status.assert_called_once()


@check(3)
def failure_alert_hides_details():
    from brief import deliver
    with mock.patch.object(deliver.httpx, "post") as post:
        deliver.send_failure(ValueError("token=abc123 leaked"))
    text = post.call_args.kwargs["json"]["text"]
    assert "ValueError" in text and "abc123" not in text, f"alert should name the error type only: {text!r}"


@check(3)
def crash_sends_failure_alert():
    main = importlib.import_module("main")
    with mock.patch.object(main, "run", side_effect=RuntimeError("boom")), \
            mock.patch.object(main, "send_failure") as alert, \
            mock.patch.object(sys, "argv", ["main.py"]):
        try:
            main.main()
        except RuntimeError:
            pass
        else:
            raise AssertionError("main() should re-raise so the Actions run is marked failed")
    assert alert.call_count == 1, "a crash must send the 'brief failed' message"


# ---------------------------------------------------------------- Phase 4

@check(4)
def workflow_schedule_and_secrets():
    raw = (ROOT / ".github" / "workflows" / "brief.yml").read_text(encoding="utf-8")
    # Ignore YAML comments, so a TODO hint can't satisfy the check.
    text = "\n".join(line.split(" #")[0] for line in raw.splitlines()
                     if not line.lstrip().startswith("#"))
    if "schedule:" not in text:
        raise NotImplementedError("TODO 4.1: add the daily schedule to .github/workflows/brief.yml")
    if "secrets." not in text:
        raise NotImplementedError("TODO 4.2: pass the secrets in .github/workflows/brief.yml")
    assert '"45 22 * * *"' in text, "cron should be 45 22 * * * (06:45 Manila)"
    assert "workflow_dispatch" in text, "keep the manual Run workflow button"
    assert "setup-python" in text, "install Python 3.12 before uv pip install --system"
    for secret in ("ANTHROPIC_API_KEY", "TODOIST_API_TOKEN", "TELEGRAM_BOT_TOKEN",
                   "TELEGRAM_CHAT_ID", "GOOGLE_CREDENTIALS", "GOOGLE_TOKEN"):
        assert f"secrets.{secret}" in text, f"workflow is missing secrets.{secret}"
    assert "GOOGLE_OAUTH_NONINTERACTIVE" in text, "headless runs should fail fast, not wait for a browser"


@check(4)
def secrets_are_ignored_and_deps_pinned():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").split()
    for name in (".env", "credentials.json", "token.json"):
        assert name in ignored, f"{name} must be in .gitignore"
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            assert "==" in line, f"pin the version: {line}"


# ---------------------------------------------------------------- runner

def main() -> int:
    phases = {int(a) for a in sys.argv[1:]} or {p for p, _ in CHECKS}
    passed = failed = todo = 0
    for phase, fn in CHECKS:
        if phase not in phases:
            continue
        label = f"Phase {phase} | {fn.__name__.replace('_', ' ')}"
        try:
            fn()
        except NotImplementedError as e:
            todo += 1
            print(f"  TODO  {label}\n        -> {e}")
        except Exception as e:
            failed += 1
            reason = str(e) or type(e).__name__
            print(f"  FAIL  {label}\n        -> {reason}")
            if os.getenv("CHECK_VERBOSE"):
                traceback.print_exc()
        else:
            passed += 1
            print(f"  PASS  {label}")
    print(f"\n{passed} passed, {failed} failed, {todo} still TODO")
    if failed:
        print("Set CHECK_VERBOSE=1 to see full tracebacks.")
    return 0 if failed == 0 and todo == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
