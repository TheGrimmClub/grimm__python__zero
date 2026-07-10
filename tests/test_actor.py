"""Tests for the Actor class.

These double as examples: each test shows one thing an Actor can do. Run them
with `task test` or `uv run --with pytest pytest`.
"""

from grimm import Actor, Dungeon


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
