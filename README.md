# grimm__python__zero

**Day two — your first Python.** A tiny package with one class, `Actor`, that you
grow step by step. This is where core coding skills start: classes, objects,
methods, and f-strings — in the Grimm world.

> Set up Python & uv first with [GrimmSetup](https://github.com/TheGrimmClub/GrimmSetup).

## Install

Once published, grab it from PyPI:

```sh
pip install grimm-python-zero      # or: uv add grimm-python-zero
```

```python
from grimm import Actor
print(Actor())
```

To hack on the lessons instead, clone this repo and run the examples with
`task step1` / `task step2` / `task step3`.

## Step 1 — make an actor

```python
from grimm import Actor

me = Actor()
print(me)
```

```
🧍 Namenloser wartet vor dem Verlies.
```

You made an **object** (`me`) from a **class** (`Actor`) and printed it.
Every actor starts nameless — *Namenloser*.

Run it: `task step1`  (or `uv run examples/step1.py`)

## Step 2 — a name, and into the dungeon

```python
from grimm import Actor

me = Actor(name="avatar-name")
print(f"Hello {me.name()}")
me.enter_dungeon()
```

```
Hello avatar-name
avatar-name betritt das Verlies. Die Tür fällt ins Schloss. 🕯️
```

Now the actor has a **name** you passed in, `me.name()` is a **method** that
gives it back, and `me.enter_dungeon()` is a method that *does* something.

Run it: `task step2`  (or `uv run examples/step2.py`)

## Step 4 — read your saved game

Once you've played the dungeon, Python can read your progress from
`~/.grimm/save.yaml`:

```python
from grimm import Dungeon, SaveGame

Dungeon().show()          # inventory, current room, visited, solved

save = SaveGame().load()  # or work with the data directly
print(save.location)      # "archiv"
print(save.inventory)     # ["helm", "nanostaub", ...]
hero = save.actor()       # an Actor named after your class → back to Step 1
```

`Dungeon().show()` resolves ids to full names (`helm` → "Helm mit Stirnlampe")
when a `grimm__dungeon__mono` checkout is nearby. Run it: `task save`.

You can also **write** the save — grant items, mark rooms, then persist. The
dungeon loads it the next time you play:

```python
save = SaveGame().load()
save.grant("zeitsiegel").wear("helm").visit("archiv").solve("repo-tor").go("halle")
save.write()   # writes ~/.grimm/save.yaml — the real dungeon reads it back
```

Mutators (`grant`, `drop`, `wear`, `visit`, `solve`, `go`) chain and skip
duplicates; `write()` emits exactly the YAML the Go game expects.

## Concepts you just met

| Idea | Where you saw it |
|------|------------------|
| **Class** (a blueprint) | `class Actor:` in `grimm/actor.py` |
| **Object / instance** | `me = Actor()` |
| **`__init__`** (set-up) | how the actor remembers its name |
| **`self`** | "this actor" inside the class |
| **Method** | `me.name()`, `me.enter_dungeon()` |
| **Default argument** | `Actor()` works without a name |
| **f-string** | `f"Hello {me.name()}"` |
| **`__str__`** | what `print(me)` shows |

## Try it yourself

- Give the actor a `leave_dungeon()` method.
- Add a `location()` method that returns where the actor is.
- Make `print(me)` change after `enter_dungeon()` — it already does; find out why.

Open a live shell with everything imported: `task repl`, then `from grimm import Actor`.

## Layout

| Path | What |
|------|------|
| `grimm/actor.py` | the `Actor` class — heavily commented, read this first |
| `grimm/__init__.py` | makes `from grimm import Actor` work |
| `examples/step1.py`, `examples/step2.py` | the two steps above |
| `tests/test_actor.py` | tests that double as examples (`task test`) |
| `pyproject.toml` | project + uv config (Python ≥ 3.13) |

## Run the tests

```sh
task test        # or: uv run --with pytest pytest -q
```
