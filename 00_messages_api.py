"""Warm-up: the Messages API in one call. No tools, no loop.

One request = model + system prompt + message history + max_tokens.
One response = content blocks + stop_reason + usage.

    python 00_messages_api.py
"""

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

resp = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=4096,
    system="You are a concise assistant for a busy professional in Manila.",
    messages=[{"role": "user", "content": "Give me 3 tips for planning a busy morning."}],
)

print("stop_reason:", resp.stop_reason)  # "end_turn": Claude finished on its own
print("usage:", resp.usage.input_tokens, "tokens in,", resp.usage.output_tokens, "tokens out")
print()
print("".join(b.text for b in resp.content if b.type == "text"))
