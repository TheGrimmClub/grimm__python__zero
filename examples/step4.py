"""Step 4 — read your saved game from Python.

After you've played the dungeon, this peeks at ~/.grimm/save.yaml: your class,
where you are, what you carry, which rooms you've seen and puzzles you've solved.
Ids are resolved to human names when a grimm__dungeon__mono checkout is nearby.

Run it:  uv run examples/step4.py   (or:  python examples/step4.py)
"""

from grimm import Dungeon, Game

# A one-line summary (inventory, room, progress):
Dungeon().show()

# Or work with the data directly — Game() loads your save automatically:
game = Game()
if game.exists():
    print("\nRooms visited:", len(game.visited))
    print("Puzzles solved:", len(game.solved))
    # Bridge back to your Actor:
    hero = game.actor()
    print(hero)

    # You can also WRITE the save — grant items, mark rooms, then persist.
    # The dungeon loads it next time you play. (Commented so this example
    # doesn't change your real save; uncomment to try it.)
    #
    #   game.grant("zeitsiegel").wear("helm").visit("archiv").solve("repo-tor")
    #   game.write()
