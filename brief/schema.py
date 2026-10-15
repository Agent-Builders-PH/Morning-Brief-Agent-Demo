"""The shape of the brief.

Claude fills in a MorningBrief through structured outputs (Agno's output_schema).
The schema stays simple on purpose: Claude's structured outputs do not accept every
JSON Schema constraint (like "exactly 5 items"), so the count and the order are
checked in Python by validate() instead.
"""

from typing import Literal  # noqa: F401  (you'll use it in TODO 2.1)

from pydantic import BaseModel, Field  # noqa: F401

# The five bullet kinds, in the order they appear in every brief.
KINDS = ("first_up", "day_shape", "top_task", "at_risk", "heads_up")


# TODO 2.1 (MODULE.md §7.1): define the two models.
#   Bullet:
#     kind: Literal[...the five KINDS...]
#     text: str = Field(..., description="One line, at most 20 words, times in PHT")
#   MorningBrief:
#     date: str = Field(..., description="YYYY-MM-DD")
#     bullets: list[Bullet]
class Bullet(BaseModel):
    pass


class MorningBrief(BaseModel):
    pass


def validate(brief: MorningBrief) -> list[str]:
    """Return a list of problems with the brief. An empty list means it is good to send."""
    # TODO 2.2 (MODULE.md §7.1): collect problems as short strings.
    #   - not exactly 5 bullets
    #   - not exactly one bullet of each kind in KINDS
    #   - any bullet text that spans more than one line
    raise NotImplementedError("TODO 2.2: write validate() in brief/schema.py")


def in_order(brief: MorningBrief) -> MorningBrief:
    """Return the brief with its bullets sorted into the fixed KINDS order."""
    bullets = sorted(brief.bullets, key=lambda b: KINDS.index(b.kind))
    return brief.model_copy(update={"bullets": bullets})
