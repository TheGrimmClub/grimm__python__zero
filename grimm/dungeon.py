"""The Dungeon — a doorway to the *real* Grimm text adventure.

`Actor.enter_dungeon()` tells the story. `Dungeon().enter()` opens the door: it
finds and launches the `grimm` console program from **grimm__dungeon__mono** — a
bit like Python's playful ``import antigravity``, except instead of opening a
comic in your browser it starts the adventure right in your terminal.

    from grimm import Dungeon

    Dungeon().enter()
"""

import os
import shutil
import subprocess
from pathlib import Path

# The compiled dungeon program is called `grimm` (`grimm.exe` on Windows).
EXECUTABLE = "grimm.exe" if os.name == "nt" else "grimm"


class Dungeon:
    """A doorway to grimm__dungeon__mono, the Grimm text adventure."""

    def __init__(self, executable=None):
        # Optionally point us straight at the binary if you know where it is.
        self._executable = executable

    def find(self):
        """Return the path to the `grimm` executable, or ``None`` if missing.

        We look in three places, in order:
        1. an explicit path — the constructor argument or the ``GRIMM_BIN`` env var,
        2. anything called ``grimm`` already on your ``PATH``,
        3. a local checkout of ``grimm__dungeon__mono`` nearby.
        """
        explicit = self._executable or os.environ.get("GRIMM_BIN")
        if explicit:
            path = Path(explicit).expanduser()
            if path.is_file():
                return path

        on_path = shutil.which("grimm")
        if on_path:
            return Path(on_path)

        for base in self._search_bases():
            candidate = base / "grimm__dungeon__mono" / "bin" / EXECUTABLE
            if candidate.is_file():
                return candidate
        return None

    def enter(self):
        """Open the door and start the adventure.

        Returns the program's exit code. If the dungeon can't be found, prints
        directions instead of crashing (and returns ``1``).
        """
        grimm = self.find()
        if grimm is None:
            self._directions()
            return 1

        print(f"\N{DOOR} Opening the door to {grimm} ...\n")
        # Hand the terminal over to grimm — the student now plays it directly.
        result = subprocess.run([str(grimm)])
        return result.returncode

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _search_bases():
        """Folders that might contain a grimm__dungeon__mono checkout."""
        here = Path(__file__).resolve()
        return [
            Path.cwd(),
            here.parent.parent.parent,  # a sibling folder of grimm__python__zero
            Path.home(),
        ]

    @staticmethod
    def _directions():
        print(
            "\N{CANDLE} The Grimm dungeon isn't here yet.\n"
            "\n"
            "Get it, then try again:\n"
            "  git clone git@github.com:TheGrimmClub/grimm__dungeon__mono.git\n"
            "  cd grimm__dungeon__mono\n"
            "  task run          # builds ./bin/grimm and starts it\n"
            "\n"
            "Then point grimm.Dungeon at the binary, e.g.:\n"
            "  export GRIMM_BIN=$(pwd)/bin/grimm\n"
        )
