"""Setup helper: sign in to Google once and list your calendars. Costs no Claude tokens.

Needs credentials.json (OAuth client, type "Desktop app") in the project root.
A browser opens for consent; afterwards token.json is saved next to it.

    python scripts/google_login.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agno.tools.google.calendar import GoogleCalendarTools  # noqa: E402

from brief.tools import READ_ONLY_SCOPE, ROOT  # noqa: E402

if not (ROOT / "credentials.json").exists():
    sys.exit("credentials.json not found in the project root. See MODULE.md, Setup step 3.")

tools = GoogleCalendarTools(
    credentials_path=str(ROOT / "credentials.json"),
    token_path=str(ROOT / "token.json"),
    scopes=[READ_ONLY_SCOPE],
    include_tools=["list_calendars"],
    add_instructions=False,
)
data = json.loads(tools.list_calendars())
if "error" in data:
    sys.exit(f"Google sign-in failed: {data['error']}")

print("Signed in. token.json saved. Your calendars:\n")
for cal in data["calendars"]:
    marker = "  <- primary" if cal["primary"] else ""
    print(f"  {cal['id']}  ({cal['name']}){marker}")
print("\nUse 'primary' for your main calendar, or set GOOGLE_CALENDAR_ID in .env.")
