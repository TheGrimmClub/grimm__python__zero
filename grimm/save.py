"""Read the dungeon's saved game from Python.

grimm__dungeon__mono writes your progress to ``~/.grimm/save.yaml`` as simple,
versioned YAML. This module reads it — inventory, current room, visited rooms,
solved puzzles — with a tiny purpose-built parser, so this package stays
dependency-free.

    from grimm import SaveGame

    save = SaveGame().load()
    print(save.location)     # e.g. "archiv"
    print(save.inventory)    # ["helm", "nanostaub", ...]
"""

from pathlib import Path


def _scalar(text):
    """Turn a YAML scalar into an int where obvious, else leave it a string."""
    if text.lstrip("-").isdigit():
        return int(text)
    return text


def _extend(dst, items):
    """Append items to dst, skipping ones already present (order preserved)."""
    for it in items:
        if it not in dst:
            dst.append(it)


def _parse_save(text):
    """Parse the save's small, fixed YAML shape into a plain dict.

    The file only ever has a top-level ``version`` and a ``game`` mapping whose
    values are scalars or lists of ids — so we don't need a full YAML library.
    """
    data = {"version": None, "game": {}}
    game = data["game"]
    in_game = False
    current_list = None

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()

        if indent == 0:  # top level: `version:` or `game:`
            in_game = line == "game:"
            current_list = None
            if not in_game and line.startswith("version:"):
                data["version"] = _scalar(line.split(":", 1)[1].strip())
            continue

        if not in_game:
            continue

        if line.startswith("- "):  # an item of the current list
            if current_list is not None:
                current_list.append(line[2:].strip())
            continue

        key, _, val = line.partition(":")  # a field under `game`
        key, val = key.strip(), val.strip()
        if val:
            game[key] = _scalar(val)
            current_list = None
        else:
            current_list = []
            game[key] = current_list

    return data


class SaveGame:
    """A read-only view of a saved Grimm game (``~/.grimm/save.yaml``)."""

    def __init__(self, path=None):
        self.path = Path(path).expanduser() if path else self.default_path()
        self.version = None
        self.title = ""       # the player's chosen class, e.g. "Jäger"
        self.location = ""    # current room id
        self.inventory = []   # item ids the player carries
        self.worn = []        # item ids the player wears
        self.visited = []     # room ids seen
        self.solved = []      # puzzle ids cleared

    @staticmethod
    def default_path():
        return Path.home() / ".grimm" / "save.yaml"

    def exists(self):
        return self.path.is_file()

    def load(self):
        """Read and parse the save. Returns ``self`` for chaining.

        Raises ``FileNotFoundError`` if there is no save yet.
        """
        data = _parse_save(self.path.read_text(encoding="utf-8"))
        game = data.get("game", {})
        self.version = data.get("version")
        self.title = game.get("title", "")
        self.location = game.get("location", "")
        self.inventory = list(game.get("inventory", []))
        self.worn = list(game.get("worn", []))
        self.visited = list(game.get("visited", []))
        self.solved = list(game.get("solved", []))
        return self

    def summary(self, names=None):
        """A short human-readable report. ``names`` optionally maps ids → titles."""
        names = names or {}

        def show(ids):
            return ", ".join(names.get(i, i) for i in ids) or "—"

        where = names.get(self.location, self.location) or "unbekannt"
        lines = [
            f"\N{SCROLL} {self.title or 'Namenloser'} — zurzeit in: {where}",
            f"  Inventar: {show(self.inventory)}",
            f"  Getragen: {show(self.worn)}",
            f"  Besucht:  {show(self.visited)}",
            f"  Gelöst:   {show(self.solved)}",
        ]
        return "\n".join(lines)

    def actor(self):
        """Make an `Actor` named after this save's class/title.

        The bridge from saved game data back to the toy `Actor` you built:

            hero = SaveGame().load().actor()
            print(hero)
        """
        from .actor import Actor

        return Actor(name=self.title or "Namenloser")

    # -- writing (grant items, visit rooms, …) ------------------------------
    #
    # Each mutator returns ``self`` so you can chain them, then ``write()``:
    #     SaveGame().load().grant("zeitsiegel").visit("archiv").write()

    def grant(self, *items):
        """Add item ids to the inventory (no duplicates)."""
        _extend(self.inventory, items)
        return self

    def drop(self, *items):
        """Remove item ids from the inventory (and from worn)."""
        for it in items:
            while it in self.inventory:
                self.inventory.remove(it)
            while it in self.worn:
                self.worn.remove(it)
        return self

    def wear(self, item):
        """Wear an item — granting it first if needed."""
        _extend(self.inventory, [item])
        _extend(self.worn, [item])
        return self

    def visit(self, *rooms):
        """Mark room ids as visited."""
        _extend(self.visited, rooms)
        return self

    def solve(self, *puzzles):
        """Mark puzzle ids as solved."""
        _extend(self.solved, puzzles)
        return self

    def go(self, room):
        """Set the current room."""
        self.location = room
        return self

    def write(self, path=None):
        """Write the save back as YAML the dungeon can load. Returns the path."""
        target = Path(path).expanduser() if path else self.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self._dump(), encoding="utf-8")
        return target

    def _dump(self):
        """Serialize to the exact YAML shape the dungeon writes (indent 4)."""

        def scalar(v):
            return v if v else '""'

        def block(name, items):
            if not items:
                return f"    {name}: []"
            return "\n".join([f"    {name}:"] + [f"        - {i}" for i in items])

        return (
            "\n".join(
                [
                    f"version: {self.version or 1}",
                    "game:",
                    f"    title: {scalar(self.title)}",
                    f"    location: {scalar(self.location)}",
                    block("inventory", self.inventory),
                    block("worn", self.worn),
                    block("visited", self.visited),
                    block("solved", self.solved),
                ]
            )
            + "\n"
        )

    def __str__(self):
        return self.summary()

    def __repr__(self):
        return f"SaveGame(location={self.location!r}, items={len(self.inventory)})"
