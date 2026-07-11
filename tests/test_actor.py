"""Tests for the Actor class.

These double as examples: each test shows one thing an Actor can do. Run them
with `task test` or `uv run --with pytest pytest`.
"""

from grimm import Actor, Dungeon, Game

SAMPLE_SAVE = """version: 1
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
"""


def test_default_actor_has_a_name():
    me = Actor()
    assert me.name() == "Namenloser"


def test_named_actor_keeps_its_name():
    me = Actor(name="avatar-name")
    assert me.name() == "avatar-name"


def test_printing_an_actor_shows_its_name():
    me = Actor(name="avatar-name")
    assert "avatar-name" in str(me)


def test_enter_dungeon_announces_the_actor(capsys):
    me = Actor(name="Hans")
    me.enter_dungeon()  # launch=False by default — just tells the story
    printed = capsys.readouterr().out
    assert "Hans" in printed
    assert "Verlies" in printed


def test_dungeon_finds_an_explicit_executable(tmp_path):
    fake = tmp_path / "grimm"
    fake.write_text("#!/bin/sh\n")
    assert Dungeon(executable=str(fake)).find() == fake


def test_dungeon_shows_directions_when_missing(capsys, monkeypatch):
    door = Dungeon()
    # Pretend nothing is found; build=False so no real build is attempted.
    monkeypatch.setattr(door, "find", lambda: None)
    code = door.enter(build=False)
    printed = capsys.readouterr().out
    assert code == 1
    assert "grimm__dungeon__mono" in printed


def test_dungeon_finds_a_buildable_source(tmp_path):
    src = tmp_path / "grimm__dungeon__mono"
    (src / "cmd" / "grimm").mkdir(parents=True)
    (src / "go.mod").write_text("module x\n")
    assert Dungeon(source=str(src)).find_source() == src


def test_seed_workspace_writes_the_package(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    pkg = Dungeon().seed_workspace()
    assert (pkg / "actor.py").is_file()
    assert "class Actor" in (pkg / "actor.py").read_text()
    assert "Actor" in (pkg / "__init__.py").read_text()
    # Idempotent.
    Dungeon().seed_workspace()


def test_status_reports_what_it_sees(monkeypatch):
    door = Dungeon()
    monkeypatch.setattr(door, "find", lambda: None)
    monkeypatch.setattr(door, "find_source", lambda: None)
    st = door.status()
    assert st["binary"] is None
    assert st["buildable"] is False
    assert st["workspace"].name == "work"


def test_game_autoloads_on_construction(tmp_path):
    p = tmp_path / "save.yaml"
    p.write_text(SAMPLE_SAVE, encoding="utf-8")
    g = Game(str(p))  # no explicit .load()
    assert g.location == "archiv"
    assert "helm" in g.inventory


def test_savegame_parses_the_save(tmp_path):
    p = tmp_path / "save.yaml"
    p.write_text(SAMPLE_SAVE, encoding="utf-8")
    s = Game(str(p)).load()
    assert s.version == 1
    assert s.title == "Jäger"
    assert s.location == "archiv"
    assert s.inventory == ["helm", "nanostaub"]
    assert s.worn == ["helm"]
    assert "tor" in s.visited
    assert s.solved == ["repo-tor"]


def test_savegame_summary_resolves_names(tmp_path):
    p = tmp_path / "save.yaml"
    p.write_text(SAMPLE_SAVE, encoding="utf-8")
    out = Game(str(p)).load().summary({"helm": "Helm mit Stirnlampe", "archiv": "Das Archiv"})
    assert "Helm mit Stirnlampe" in out
    assert "Das Archiv" in out


def test_dungeon_world_names_from_source(tmp_path):
    src = tmp_path / "grimm__dungeon__mono"
    (src / "cmd" / "grimm").mkdir(parents=True)
    (src / "go.mod").write_text("module x\n")
    world = src / "content" / "world"
    world.mkdir(parents=True)
    (world / "items.yaml").write_text(
        "kind: item\nid: helm\nname: Helm mit Stirnlampe\n"
        "---\nkind: room\nid: archiv\ntitle: Das Archiv\n",
        encoding="utf-8",
    )
    names = Dungeon(source=str(src)).world_names()
    assert names["helm"] == "Helm mit Stirnlampe"
    assert names["archiv"] == "Das Archiv"


def test_savegame_grant_visit_and_write_roundtrip(tmp_path):
    p = tmp_path / "save.yaml"
    p.write_text(SAMPLE_SAVE, encoding="utf-8")
    (
        Game(str(p))
        .load()
        .grant("zeitsiegel", "helm")  # helm already there — no duplicate
        .visit("halle")
        .solve("lern-actor")
        .go("halle")
        .write()
    )
    again = Game(str(p)).load()
    assert again.inventory.count("helm") == 1
    assert "zeitsiegel" in again.inventory
    assert "halle" in again.visited
    assert "lern-actor" in again.solved
    assert again.location == "halle"


def test_savegame_drop_removes_item_and_worn(tmp_path):
    p = tmp_path / "save.yaml"
    p.write_text(SAMPLE_SAVE, encoding="utf-8")
    Game(str(p)).load().drop("helm").write()
    again = Game(str(p)).load()
    assert "helm" not in again.inventory
    assert "helm" not in again.worn


def test_savegame_writes_empty_lists(tmp_path):
    p = tmp_path / "save.yaml"
    Game(str(p)).go("tor").write()  # fresh, empty inventory/visited/...
    text = p.read_text(encoding="utf-8")
    assert "inventory: []" in text
    assert Game(str(p)).load().location == "tor"


def test_savegame_makes_an_actor(tmp_path):
    p = tmp_path / "save.yaml"
    p.write_text(SAMPLE_SAVE, encoding="utf-8")
    hero = Game(str(p)).load().actor()
    assert isinstance(hero, Actor)
    assert hero.name() == "Jäger"


def test_dungeon_show_without_save(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))  # empty home → no save
    result = Dungeon().show()
    printed = capsys.readouterr().out
    assert result is None
    assert "No saved game" in printed
