"""Small validated JSON preferences; failure to save never stops a match."""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path


def settings_path():
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Predator" / "settings.json"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "predator" / "settings.json"


@dataclass
class Settings:
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    muted: bool = False
    fullscreen: bool = False
    reduced_flash: bool = False

    @classmethod
    def load(cls, path=None):
        try:
            data = json.loads(Path(path or settings_path()).read_text(encoding="utf-8"))
            result = cls()
            for name in ("music_volume", "sfx_volume"):
                value = data.get(name)
                if type(value) in (int, float) and 0 <= value <= 1:
                    setattr(result, name, float(value))
            for name in ("muted", "fullscreen", "reduced_flash"):
                if type(data.get(name)) is bool:
                    setattr(result, name, data[name])
            return result
        except (OSError, ValueError, TypeError, AttributeError):
            return cls()

    def save(self, path=None):
        destination = Path(path or settings_path())
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(".tmp")
            temporary.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")
            temporary.replace(destination)
            return True
        except OSError:
            return False
