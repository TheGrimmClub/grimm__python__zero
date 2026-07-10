"""Step 4 — read your saved game from Python.

After you've played the dungeon, this peeks at ~/.grimm/save.yaml: your class,
where you are, what you carry, which rooms you've seen and puzzles you've solved.
Ids are resolved to human names when a grimm__dungeon__mono checkout is nearby.

Run it:  uv run examples/step4.py   (or:  python examples/step4.py)
"""

from grimm import Dungeon, SaveGame

# A one-line summary (inventory, room, progress):
Dungeon().show()

# Or work with the data directly:
save = SaveGame()
if save.exists():
    save.load()
    print("\nRooms visited:", len(save.visited))
    print("Puzzles solved:", len(save.solved))
    # Bridge back to your Actor:
    hero = save.actor()
    print(hero)
