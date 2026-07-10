"""grimm — your first Python package (TheGrimmClub, day two).

A *package* is just a folder of Python files that belong together. This line…

    from grimm import Actor

…works because we re-export `Actor` here, so you don't have to know it lives in
`grimm/actor.py`.

    me = Actor()
    print(me)
"""

from .actor import Actor

__all__ = ["Actor"]
__version__ = "0.1.0"
