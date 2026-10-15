<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/ab-logo-white.png">
    <img src="assets/ab-logo-dark.png" alt="Agent Builders Philippines" width="320">
  </picture>
</p>

# Morning Brief Agent: starter template

**Agent Builders PH · Episode 1.** Build a personal agent that reads today's Google Calendar and Todoist to-dos every morning at 6:45 AM PHT and sends exactly five bullets to your phone on Telegram.

You'll build it twice: first the agent loop **by hand** on the Claude API, then the same agent with **Agno**, so you see exactly what a framework does for you.

📘 **Follow [MODULE.md](MODULE.md)**. It walks you through everything, from setup to a daily schedule.

🧭 **Prefer a click-through checklist?** Open [WALKTHROUGH.html](WALKTHROUGH.html) in your browser. It has every step with copy buttons, tick-boxes that remember your progress, and a detailed Google sign-in section. GitHub shows the file as source code, so open your local copy after cloning: `start WALKTHROUGH.html` (Windows) or `open WALKTHROUGH.html` (macOS).

## Get started

```bash
uv venv --python 3.12
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
uv pip install -r requirements.txt

cp .env.example .env            # Windows: copy .env.example .env
python check.py                 # shows what's left to build
```

## How this template works

The project structure is ready. The parts you build are marked **`TODO`**, numbered to match the module:

| TODO | File | Module section |
|---|---|---|
| 0.1 | `brief/tools.py` → `get_todays_tasks` | §5.2 your first tool |
| 0.2, 0.3 | `00_raw_loop.py` → `TOOLS`, `run_agent` | §5.3–5.4 the agent loop by hand |
| 1.1 | `brief/tools.py` → `calendar_tools` | §6.1 read-only calendar |
| 1.2 | `01_calendar_agent.py` | §6.2 the same loop in Agno |
| 2.1, 2.2 | `brief/schema.py` | §7.1 the shape of the brief |
| 2.3 | `brief/prompt.py` | §7.2 the instructions |
| 2.4 | `brief/agent.py` | §7.3 the agent |
| 2.5–2.7 | `main.py` | §7.4 window, safety check, retry |
| 3.1–3.3 | `brief/deliver.py` | §8 Telegram |
| 4.1, 4.2 | `.github/workflows/brief.yml` | §9 daily schedule |

After each TODO, run the offline checks for that phase. No API keys needed, no cost:

```bash
python check.py 0      # PASS / FAIL (with a hint) / TODO
```

When `python check.py` prints `0 failed, 0 still TODO`, you're done. 🎉

## Never commit secrets

`.env`, `credentials.json` and `token.json` are in `.gitignore`. Keep it that way, and keep your own copy of this repo **private**.
