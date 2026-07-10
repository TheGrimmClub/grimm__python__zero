# grimm — API Reference

The `grimm` package (from [grimm__python__zero](https://github.com/TheGrimmClub/grimm__python__zero))
has three public classes:

| Class | What it is |
|-------|------------|
| [`Actor`](#actor) | your first Python class — a character in the Grimm world |
| [`Dungeon`](#dungeon) | a launcher/on-ramp to the real `grimm__dungeon__mono` adventure |
| [`SaveGame`](#savegame) | a read **and write** view of the dungeon's saved game |

```python
from grimm import Actor, Dungeon, SaveGame
```

The package is **dependency-free** and targets **Python ≥ 3.9**.

- [Actor](#actor)
- [Dungeon](#dungeon)
- [SaveGame](#savegame)
- [Save file format](#save-file-format)
- [How it fits together](#how-it-fits-together)

---

## Actor

`grimm.actor.Actor` — a character (a player's avatar). This is the teaching class
of the beginner path.

### Constructor

```python
Actor(name="Namenloser")
```

| Param | Type | Default | Meaning |
|-------|------|---------|---------|
| `name` | `str` | `"Namenloser"` (module constant `DEFAULT_NAME`) | the actor's name |

### Methods

#### `name() -> str`
Return the actor's name.

```python
Actor(name="Hans").name()      # "Hans"
```

#### `enter_dungeon(launch=False) -> int | None`
Tell the story of entering the dungeon (prints a German line and marks the actor
as inside). With `launch=True`, hands off to [`Dungeon().enter()`](#enterbuildtrue---int)
and returns its exit code; otherwise returns `None`.

```python
me = Actor(name="Hans")
me.enter_dungeon()             # prints: Hans betritt das Verlies. … 🕯️
me.enter_dungeon(launch=True)  # …then actually launches the adventure
```

#### `__str__() -> str`
What `print(actor)` shows. Reflects whether the actor has entered:

```python
print(Actor(name="Hans"))      # 🧍 Hans wartet vor dem Verlies.
```

After `enter_dungeon()` the text changes to `… wartet im Verlies.`

#### `__repr__() -> str`
Developer view: `Actor(name='Hans')`.

### Module constant
- `grimm.actor.DEFAULT_NAME` = `"Namenloser"`.

---

## Dungeon

`grimm.dungeon.Dungeon` — finds (or **builds**) the `grimm` console program from
`grimm__dungeon__mono`, seeds the work dir with this package, and launches it.

### Constructor

```python
Dungeon(executable=None, source=None)
```

| Param | Type | Default | Meaning |
|-------|------|---------|---------|
| `executable` | `str \| Path \| None` | `None` | explicit path to a prebuilt `grimm` binary |
| `source` | `str \| Path \| None` | `None` | explicit path to a `grimm__dungeon__mono` checkout to build |

### Discovery

#### `find() -> Path | None`
Return a ready-to-run binary, or `None`. Looks, in order, at: the `executable`
argument or the `GRIMM_BIN` env var, then `PATH` (`shutil.which("grimm")`), then a
prebuilt `bin/grimm` inside a nearby checkout.

#### `find_source() -> Path | None`
Return a **buildable** `grimm__dungeon__mono` checkout nearby, or `None`. A
checkout counts when it has both `go.mod` and `cmd/grimm`.

### Building

#### `build() -> Path | None`
Build the dungeon from a nearby source checkout and return the binary's path.
Prefers `task build`; falls back to `go build`. Returns `None` if there's no
source or the build fails (with a helpful message if neither `task` nor `go` is
installed).

### Work dir

#### `home() -> Path` *(static)*
The dungeon's home, `~/.grimm`.

#### `workspace() -> Path`
The student work dir, `~/.grimm/work` (created on demand).

#### `seed_workspace() -> Path`
Write this package's `grimm` (Actor) into `~/.grimm/work/grimm/` so a solution run
there can `from grimm import Actor`. Idempotent. Returns the seeded package dir.

### Saved game

#### `save() -> SaveGame | None`
Return the saved game as a [`SaveGame`](#savegame), or `None` if there is none.

#### `world_names() -> dict[str, str]`
Map item/room ids to human names, read from a nearby checkout's
`content/world/*.yaml` (`helm` → `"Helm mit Stirnlampe"`). Empty dict if no
checkout is available.

#### `show() -> SaveGame | None`
Print a summary of the saved game (inventory, current room, visited, solved),
using human names when a checkout is present. Returns the `SaveGame`, or `None`
if there's no save.

```python
Dungeon().show()
# 📜 Jäger — zurzeit in: Das Archiv der Versionen
#   Inventar: Helm mit Stirnlampe, Fläschchen Nanostaub, …
#   …
```

### Status & entry

#### `status() -> dict`
Report what the launcher can see:

```python
Dungeon().status()
# {'binary': PosixPath('…/bin/grimm'),   # or None
#  'source': PosixPath('…/grimm__dungeon__mono'),  # or None
#  'workspace': PosixPath('~/.grimm/work'),
#  'buildable': False}                    # True when only source is present
```

#### `enter(build=True) -> int`
Open the door and start the adventure. Resolves the binary (building it if only
source is present and `build` is true), seeds the work dir, sets `GRIMM_BIN` in
the child environment, then hands over the terminal. Returns grimm's exit code,
or `1` if it can't run (prints directions instead of crashing).

```python
from grimm import Dungeon
Dungeon().enter()          # find or build, then play
```

### Module constants
- `grimm.dungeon.EXECUTABLE` — `"grimm"` (`"grimm.exe"` on Windows).
- `grimm.dungeon.CHECKOUT` — `"grimm__dungeon__mono"`.

### Environment
- **`GRIMM_BIN`** — if set, `find()` uses it first; `enter()` also sets it for the
  launched process.

---

## SaveGame

`grimm.save.SaveGame` — a read/write view of the dungeon's save, `~/.grimm/save.yaml`.
Written with a tiny purpose-built YAML reader/emitter, so the package stays
dependency-free and the output is exactly what the Go game reads.

### Constructor

```python
SaveGame(path=None)   # path defaults to ~/.grimm/save.yaml
```

### Attributes
After `load()`, these hold the parsed data:

| Attribute | Type | Meaning |
|-----------|------|---------|
| `version` | `int` | save format version (currently `1`) |
| `title` | `str` | the player's chosen class (e.g. `"Jäger"`) |
| `location` | `str` | current room id |
| `inventory` | `list[str]` | item ids carried |
| `worn` | `list[str]` | item ids worn |
| `visited` | `list[str]` | room ids seen |
| `solved` | `list[str]` | puzzle ids cleared |

### Reading

#### `default_path() -> Path` *(static)*
`~/.grimm/save.yaml`.

#### `exists() -> bool`
Whether a save file is present at `path`.

#### `load() -> SaveGame`
Read and parse the save; returns `self` for chaining. Raises `FileNotFoundError`
if there is no save.

#### `summary(names=None) -> str`
A short human-readable report. `names` optionally maps ids → titles (pass
[`Dungeon().world_names()`](#world_names---dictstr-str) for full names).

#### `actor() -> Actor`
Bridge back to [`Actor`](#actor): an actor named after this save's class.

```python
hero = SaveGame().load().actor()   # Actor(name="Jäger")
```

### Writing

All mutators **return `self`** (chainable) and skip duplicates; call `write()` to
persist. The dungeon loads the result the next time it starts.

#### `grant(*items) -> SaveGame`
Add item ids to the inventory.

#### `drop(*items) -> SaveGame`
Remove item ids from the inventory (and from `worn`).

#### `wear(item) -> SaveGame`
Wear an item, granting it first if needed.

#### `visit(*rooms) -> SaveGame`
Mark room ids as visited.

#### `solve(*puzzles) -> SaveGame`
Mark puzzle ids as solved.

#### `go(room) -> SaveGame`
Set the current room.

#### `write(path=None) -> Path`
Write the save back as YAML the dungeon can load (defaults to `self.path`).
Returns the written path.

```python
save = SaveGame().load()
save.grant("zeitsiegel").wear("helm").visit("archiv").solve("repo-tor").go("halle")
save.write()   # ~/.grimm/save.yaml — verified to load in the Go game's state.Load
```

> **Warning:** `write()` overwrites the whole save with the known v1 fields. If a
> future dungeon version adds fields, bump the writer to match.

---

## Save file format

`~/.grimm/save.yaml` — written by `grimm__dungeon__mono` (Go, `yaml.v3`) and by
`SaveGame.write()`:

```yaml
version: 1
game:
    title: Jäger
    location: archiv
    inventory:
        - helm
        - nanostaub
    worn:
        - helm
    visited:
        - archiv
        - tor
    solved:
        - repo-tor
```

Empty lists are emitted as `inventory: []`. Ids (rooms, items, puzzles) are the
ids from the world content in `grimm__dungeon__mono/content/world/*.yaml`.

---

## How it fits together

```
grimmoire (learn)                 grimm__python__zero (build)         grimm__dungeon__mono (play)
─────────────────                 ──────────────────────────         ───────────────────────────
Actor / Dungeon / SaveGame  ──►   from grimm import Actor      ──►    behavioral puzzles run
                                  Dungeon().enter()  ───────────►     python3 loesung.py  (seeded
                                                                       grimm package → import Actor)
Dungeon().show()  ◄───────────────  reads  ~/.grimm/save.yaml  ◄────  the game writes progress
SaveGame().grant(...).write() ────  writes ~/.grimm/save.yaml  ────►  state.Load reads it back
```

- **Launch**: `Dungeon().enter()` finds/builds the binary, seeds the work dir, plays.
- **Read**: `Dungeon().show()` / `SaveGame().load()` observe your progress.
- **Write**: `SaveGame` mutators + `write()` change it; the Go game loads the result.
- **Bridge**: `SaveGame().actor()` turns saved data back into an `Actor`.

See also the runnable examples: `examples/step1.py … step4.py` (or `task step1`,
`task step2`, `task dungeon`, `task save`).
