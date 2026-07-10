# grimm — API Reference

The full, rendered API reference lives in the Grimmoire (searchable, kept
in sync with the site):

**→ <https://thegrimmclub.github.io/grimmoire/en/api-reference/>**

It documents every public method of the three classes:

- **`Actor`** — `name()`, `enter_dungeon(launch)`, `__str__`/`__repr__`
- **`Dungeon`** — `find()`, `find_source()`, `build()`, `workspace()`,
  `seed_workspace()`, `save()`, `world_names()`, `show()`, `status()`,
  `enter(build)`
- **`SaveGame`** — `load()`, `summary()`, `actor()`, and the write mutators
  `grant` / `drop` / `wear` / `visit` / `solve` / `go` + `write()`

…plus the `~/.grimm/save.yaml` schema and a data-flow diagram.

```python
from grimm import Actor, Dungeon, SaveGame
```

The classes themselves are heavily commented — `grimm/actor.py`,
`grimm/dungeon.py`, `grimm/save.py` — and `tests/test_actor.py` doubles as usage
examples.
