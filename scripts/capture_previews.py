"""Reproduce UI previews using explicit fixtures and the actual SDL renderer."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pygame
from src.app import Application
from src.config import PROJECT_ROOT
from src.modes import Mode
from src.navigation import Screen
from src.powerups import Pickup, PowerUp
from src.settings import Settings


def main():
    destination = PROJECT_ROOT / "docs" / "previews"
    destination.mkdir(parents=True, exist_ok=True)
    app = Application(settings=Settings(muted=True), persist=False)

    def save(name):
        app.draw()
        pygame.image.save(app.window, str(destination / f"{name}.png"))

    try:
        for screen, name in ((Screen.MAIN, "home"), (Screen.OPTIONS, "options"), (Screen.CREDITS, "credits")):
            app.transition(screen)
            save(name)
        for mode, name in ((Mode.FUN, "fun-briefing"), (Mode.FOUR, "free-for-all-briefing"), (Mode.PODER, "poder-briefing")):
            app.transition(mode)
            save(name)
        app.transition(Mode.FUN)
        app.start_match()
        save("countdown")
        app.transition(Screen.PLAYING)
        app.match.scores[:] = [2, 3]
        app.match.ball.position.update(470, 190)
        app.match.powerups.pickup = Pickup(PowerUp.SHIELD, pygame.Vector2(395, 260))
        save("fun-pickup")
        app.match.powerups.activate(app.match, PowerUp.GIANT, 0)
        save("fun-arena")
        app.pause()
        save("pause")
        app.resume()
        app.match.finished = True
        app.match.winner = 1
        app.match.scores[:] = [2, 5]
        app.transition(Screen.GAME_OVER)
        save("results")
        app.transition(Mode.FOUR)
        app.start_match()
        app.transition(Screen.PLAYING)
        app.match.scores[:] = [1, 3, 2, 4]
        save("free-for-all")
    finally:
        app.close()
    print(f"12 renderer previews saved to {destination}")


if __name__ == "__main__":
    main()
