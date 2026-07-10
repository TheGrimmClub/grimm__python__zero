"""Step 2 — give your actor a name and send it into the dungeon.

Run it:  uv run examples/step2.py   (or:  python examples/step2.py)
"""

from grimm import Actor

me = Actor(name="avatar-name")
print(f"Hello {me.name()}")
me.enter_dungeon()
