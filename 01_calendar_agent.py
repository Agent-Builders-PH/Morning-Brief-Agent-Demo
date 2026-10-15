"""Phase 1: the same loop in Agno, calendar only. About 8 lines of real code.

The first run opens a browser for Google sign-in and writes token.json
(unless you already ran scripts/google_login.py).

    python 01_calendar_agent.py
"""

from dotenv import load_dotenv

load_dotenv()

from agno.agent import Agent  # noqa: E402
from agno.models.anthropic import Claude  # noqa: E402

from brief.tools import calendar_tools  # noqa: E402

# TODO 1.2 (MODULE.md §6.2): build an Agent and ask it about today.
#   agent = Agent(
#       model=Claude(id="claude-sonnet-5-5"),
#       tools=[...the calendar toolkit...],
#       add_datetime_to_context=True,      # tells Claude today's date
#       timezone_identifier="Asia/Manila",
#       markdown=True,
#   )
#   agent.print_response("What's on my calendar today?", stream=True)
raise NotImplementedError("TODO 1.2: build the Agno agent in 01_calendar_agent.py")
