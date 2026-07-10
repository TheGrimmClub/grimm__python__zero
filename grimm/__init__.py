"""grimm — your first Python package (TheGrimmClub, day two).

A *package* is just a folder of Python files that belong together. This line…

    from grimm import Actor

…works because we re-export `Actor` here, so you don't have to know it lives in
`grimm/actor.py`.

    me = Actor()
    print(me)
"""

from .actor import Actor
from .dungeon import Dungeon

__all__ = ["Actor", "Dungeon"]
__version__ = "0.1.0"
