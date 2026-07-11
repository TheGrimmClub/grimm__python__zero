"""The Dungeon — a doorway to the *real* Grimm text adventure.

`Actor.enter_dungeon()` tells the story. `Dungeon().enter()` opens the door: it
finds (or **builds**) the `grimm` console program from **grimm__dungeon__mono**,
seeds your work dir with this package, and launches it — a bit like Python's
playful ``import antigravity``, except it starts the adventure in your terminal.

    from grimm import Dungeon

    Dungeon().enter()          # find or build the binary, then play
    Dungeon().status()         # {'binary': ..., 'source': ..., 'workspace': ...}
"""

import os
import shutil
import subprocess
from pathlib import Path

# The compiled dungeon program is called `grimm` (`grimm.exe` on Windows).
EXECUTABLE = "grimm.exe" if os.name == "nt" else "grimm"

# The repository that holds the dungeon's source.
CHECKOUT = "grimm__dungeon__mono"


class Dungeon:
    """A doorway to grimm__dungeon__mono, the Grimm text adventure.

    It resolves the binary from (in order): an explicit path or ``GRIMM_BIN``,
    your ``PATH``, a prebuilt binary in a nearby checkout, or — if only source is
    present — by building it for you.
    """

    def __init__(self, executable=None, source=None):
        # Optionally point us straight at the binary, or at a checkout to build.
        self._executable = executable
        self._source = Path(source).expanduser() if source else None

    # -- discovery ----------------------------------------------------------

    def find(self):
        """Return the path to a ready-to-run `grimm` binary, or ``None``.

        Looks at: an explicit path or ``GRIMM_BIN``, then ``PATH``, then a
        prebuilt binary inside a nearby checkout.
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
            candidate = base / CHECKOUT / "bin" / EXECUTABLE
            if candidate.is_file():
                return candidate
        return None

    def find_source(self):
        """Return a buildable `grimm__dungeon__mono` checkout nearby, or ``None``.

        A checkout is "buildable" when it has both ``go.mod`` and ``cmd/grimm``.
        """
        candidates = [self._source] if self._source else []
        candidates += [base / CHECKOUT for base in self._search_bases()]
        for src in candidates:
            if src and (src / "go.mod").is_file() and (src / "cmd" / "grimm").is_dir():
                return src
        return None

    # -- building -----------------------------------------------------------

    def build(self):
        """Build the dungeon from a nearby source checkout; return the binary.

        Prefers ``task build`` when available, else falls back to ``go build``.
        Returns the built binary's path, or ``None`` if it can't be built.
        """
        src = self.find_source()
        if src is None:
            return None

        print(f"\N{HAMMER} Building the dungeon in {src} …")
        if shutil.which("task") and (src / "Taskfile.yaml").is_file():
            cmd = ["task", "build"]
        elif shutil.which("go"):
            cmd = ["go", "build", "-o", str(Path("bin") / EXECUTABLE), "./cmd/grimm"]
        else:
            print(
                warn("Can't build: neither `task` nor `go` is installed."),
                "\n  Install Go (https://go.dev) — the dungeon is written in Go.",
            )
            return None

        result = subprocess.run(cmd, cwd=str(src))
        if result.returncode != 0:
            print(warn("The build failed."))
            return None

        binary = src / "bin" / EXECUTABLE
        return binary if binary.is_file() else None

    # -- the work dir -------------------------------------------------------

    @staticmethod
    def home():
        """The dungeon's home, ``~/.grimm``."""
        return Path.home() / ".grimm"

    def workspace(self):
        """The student work dir, ``~/.grimm/work`` (created on demand)."""
        work = self.home() / "work"
        work.mkdir(parents=True, exist_ok=True)
        return work

    def seed_workspace(self):
        """Write this package's ``grimm`` (Actor) into the work dir.

        So a solution run there can ``from grimm import Actor`` even before the
        dungeon binary seeds it itself. Idempotent.
        """
        pkg = self.workspace() / "grimm"
        pkg.mkdir(parents=True, exist_ok=True)
        actor_src = Path(__file__).with_name("actor.py")
        (pkg / "actor.py").write_text(actor_src.read_text(encoding="utf-8"), encoding="utf-8")
        (pkg / "__init__.py").write_text(
            '"""grimm — seeded for dungeon puzzles."""\n'
            "from .actor import Actor\n\n"
            '__all__ = ["Actor"]\n',
            encoding="utf-8",
        )
        return pkg

    # -- status & entry -----------------------------------------------------

    def status(self):
        """Report what the launcher can see, as a dict (handy for debugging)."""
        binary = self.find()
        return {
            "binary": binary,
            "source": self.find_source(),
            "workspace": self.home() / "work",
            "buildable": binary is None and self.find_source() is not None,
        }

    # -- saved-game data ----------------------------------------------------

    def game(self):
        """Return the saved game as a `Game`, or ``None`` if there is none."""
        from .game import Game

        game = Game()
        return game if game.exists() else None

    def world_names(self):
        """Map item/room ids to human names, read from a nearby checkout.

        Returns an empty dict when no source checkout is available (then ids are
        shown as-is).
        """
        src = self.find_source()
        names = {}
        if src is None:
            return names
        world = src / "content" / "world"
        if not world.is_dir():
            return names
        for yml in sorted(world.glob("*.yaml")):
            for doc in yml.read_text(encoding="utf-8").split("\n---"):
                ident = _field(doc, "id")
                label = _field(doc, "name") or _field(doc, "title")
                if ident and label:
                    names[ident] = label
        return names

    def show(self):
        """Print a summary of the saved game (inventory, room, progress).

        Uses human names from a nearby checkout when available. Returns the
        `Game`, or ``None`` if there is no save yet.
        """
        game = self.game()
        if game is None:
            print(warn("No saved game yet — play first with Dungeon().enter()."))
            return None
        print(game.summary(self.world_names()))
        return game

    def enter(self, build=True):
        """Open the door and start the adventure.

        Resolves the binary (building it if only source is present and
        ``build`` is true), seeds the work dir with this package, then hands the
        terminal to grimm. Returns grimm's exit code, or ``1`` if it can't run.
        """
        grimm = self.find()
        if grimm is None and build:
            grimm = self.build()
        if grimm is None:
            self._directions()
            return 1

        self.seed_workspace()
        print(f"\N{DOOR} Opening the door to {grimm} …\n")
        # Tell child processes where the binary is; then hand over the terminal.
        env = {**os.environ, "GRIMM_BIN": str(grimm)}
        result = subprocess.run([str(grimm)], env=env)
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
            "\n"
            "With the checkout beside this project, Dungeon().enter() will build\n"
            "and launch it for you. Or point us at a prebuilt binary:\n"
            "  export GRIMM_BIN=/path/to/grimm__dungeon__mono/bin/grimm\n"
        )


def warn(text):
    """A yellow warning marker, kept tiny so the toy package stays dependency-free."""
    return f"\N{WARNING SIGN} {text}"


def _field(doc, key):
    """Return the value of a top-level ``key:`` line in a world YAML document."""
    prefix = key + ":"
    for line in doc.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None
