from pathlib import Path

from PyQt6.QtGui import QIcon


BASE_DIR = Path(__file__).resolve().parent.parent
ICONS_DIR = BASE_DIR / "assets" / "icons"


def load_icon(name: str) -> QIcon:
    return QIcon(str(ICONS_DIR / f"{name}.svg"))
