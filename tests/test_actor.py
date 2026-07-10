"""Tests for the Actor class.

These double as examples: each test shows one thing an Actor can do. Run them
with `task test` or `uv run --with pytest pytest`.
"""

from grimm import Actor


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
    me.enter_dungeon()
    printed = capsys.readouterr().out
    assert "Hans" in printed
    assert "Verlies" in printed
