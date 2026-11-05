"""Launch the real entry point briefly, muted and offline, on native SDL."""
import os
os.environ.pop("SDL_VIDEODRIVER", None)
os.environ.pop("SDL_AUDIODRIVER", None)
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from pathlib import Path
import runpy
import socket
import sys
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame
from src.app import Application
from src.config import PROJECT_ROOT
from src.settings import Settings


def main():
    frames = 0
    states = set()
    drivers = set()
    get_events = pygame.event.get
    draw = Application.draw

    def observe(app):
        states.add(app.navigation.screen.name)
        drivers.add(pygame.display.get_driver())
        draw(app)

    def events():
        nonlocal frames
        frames += 1
        if frames in (10, 20, 30, 40):
            return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]
        if frames in (365, 385):
            return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
        if frames >= 410:
            return [pygame.event.Event(pygame.QUIT)]
        return get_events()

    with patch("src.app.Settings.load", return_value=Settings(muted=True)), \
         patch.object(socket.socket, "connect", side_effect=AssertionError("Network attempted")), \
         patch.object(socket, "create_connection", side_effect=AssertionError("Network attempted")), \
         patch.object(pygame.event, "get", events), \
         patch.object(Application, "draw", observe):
        runpy.run_path(str(PROJECT_ROOT / "main.py"), run_name="__main__")
    assert "dummy" not in drivers, drivers
    assert not pygame.display.get_init()
    assert pygame.mixer.get_init() is None
    print(f"Native offline launch passed: driver={sorted(drivers)}, frames={frames}, screens={sorted(states)}")


if __name__ == "__main__":
    main()
