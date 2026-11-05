"""Player-facing descriptions generated from the actual default bindings."""
import pygame
from ..config import CONTROLS, ATTACK_KEYS
from ..modes import Mode

MODE_RULES = {
    Mode.AI: ("Beat the tracking computer.", "First to 5 points wins."),
    Mode.WALL: ("Keep the rally alive against the right wall.", "Each wall return scores. One miss ends the run."),
    Mode.CLASSIC: ("Two paddles. One arena. Local competition.", "First to 5 points wins."),
    Mode.PODER: ("Two centre-zone returns fill your charge.", "Fire near your paddle. First to 5 points wins."),
    Mode.FUN: ("Collect power-ups with the ball to change the rally.", "Last hitter owns the pickup. First to 5 points wins."),
    Mode.FOUR: ("Four paddles. Every side is a goal.", "Last hitter scores on any exit. First to 5 wins."),
}


def key_name(key):
    return {pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT"}.get(key, pygame.key.name(key).upper())


def player_controls(mode):
    count = 1 if mode in (Mode.AI, Mode.WALL) else 4 if mode == Mode.FOUR else 2
    roles = ("LEFT", "RIGHT", "TOP", "BOTTOM")
    result = []
    for i in range(count):
        keys = " / ".join(key_name(key) for key in CONTROLS[i])
        result.append((i, roles[i], keys, key_name(ATTACK_KEYS[i]) if mode == Mode.PODER else None))
    return result
