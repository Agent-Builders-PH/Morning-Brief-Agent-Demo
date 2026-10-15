"""Phase 0: the agent loop, written by hand. One tool, no framework.

An agent is a model in a loop with tools. Watch for three things:
  1. TOOLS: the JSON schema that tells Claude the tool exists
  2. stop_reason: "tool_use" means "run this and call me again"; anything else means done
  3. tool_result: goes back as a *user* turn, matched by tool_use_id

    python 00_raw_loop.py
"""

import anthropic
from dotenv import load_dotenv

from brief.tools import get_todays_tasks

MODEL = "claude-sonnet-5-5"

# TODO 0.2 (MODULE.md §5.3): describe get_todays_tasks to Claude.
#   One dict with "name", "description" and "input_schema".
#   The tool takes no inputs: {"type": "object", "properties": {}}
TOOLS = []

REGISTRY = {"get_todays_tasks": get_todays_tasks}


def run_agent(client: anthropic.Anthropic, question: str) -> str:
    messages = [{"role": "user", "content": question}]
    # TODO 0.3 (MODULE.md §5.4): the agent loop.
    #   while True:
    #     1. resp = client.messages.create(model=MODEL, max_tokens=4096, tools=TOOLS, messages=messages)
    #     2. append Claude's whole reply: {"role": "assistant", "content": resp.content}
    #     3. if resp.stop_reason != "tool_use": break
    #     4. for each block with block.type == "tool_use":
    #          run REGISTRY[block.name](**block.input) and collect
    #          {"type": "tool_result", "tool_use_id": block.id, "content": output}
    #     5. append all results as ONE user turn: {"role": "user", "content": results}
    #   finally return the text blocks of the last reply joined together
    raise NotImplementedError("TODO 0.3: write the agent loop in 00_raw_loop.py")


if __name__ == "__main__":
    load_dotenv()
    print(run_agent(anthropic.Anthropic(), "What's on my plate today? 3 bullets."))
