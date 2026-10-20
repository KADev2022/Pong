from pathlib import Path
import sys


def resource_path(relative_path):
    """
    Return the path to a bundled game asset.
    Works in Python and PyInstaller executables.
    """
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return str(base_path / relative_path)


def data_path(filename):
    """
    Return a writable location for saved game data.
    Uses AppData on Windows.
    """
    if sys.platform == "win32":
        import os

        base_path = Path(
            os.environ.get(
                "LOCALAPPDATA",
                Path.home() / "AppData" / "Local"
            )
        ) / "Pong"
    else:
        base_path = Path.home() / ".pong"

    base_path.mkdir(parents=True, exist_ok=True)

    return str(base_path / filename)