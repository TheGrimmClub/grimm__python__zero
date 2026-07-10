"""Step 3 — open the door and enter the real dungeon.

`Dungeon().enter()` finds the `grimm` console program (from
grimm__dungeon__mono) and starts it — like `import antigravity`, but it launches
the adventure in your terminal instead of a browser.

Run it:  uv run examples/step3.py   (or:  python examples/step3.py)

If the dungeon isn't installed yet, it prints directions instead of crashing.
"""

from grimm import Actor, Dungeon

me = Actor(name="avatar-name")
print(f"Hello {me.name()}")

# Either open the door directly...
Dungeon().enter()

# ...or let your actor do it in one line:
#   me.enter_dungeon(launch=True)
