"""The Morning Brief agent, built with Agno.

Everything 00_raw_loop.py does by hand (tool schemas, the while loop, parsing the
answer) happens inside Agent.run(). The loop is still there; you just stop writing it.
"""

import os

from agno.agent import Agent  # noqa: F401
from agno.models.anthropic import Claude  # noqa: F401

from brief.prompt import INSTRUCTIONS  # noqa: F401
from brief.schema import MorningBrief  # noqa: F401
from brief.tools import calendar_tools, get_todays_tasks  # noqa: F401

MODEL_ID = os.getenv("MORNING_BRIEF_MODEL") or "claude-sonnet-5-5"


def build_agent() -> Agent:
    # TODO 2.4 (MODULE.md §7.3): return an Agent with
    #   name="Morning Brief"
    #   model=Claude(id=MODEL_ID, cache_system_prompt=True)
    #   tools=[the calendar toolkit, get_todays_tasks]
    #   instructions=INSTRUCTIONS
    #   output_schema=MorningBrief
    #   tool_call_limit=6
    raise NotImplementedError("TODO 2.4: write build_agent() in brief/agent.py")
