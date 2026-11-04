"""Shared dimensions, timing, controls and colours from the school game."""

from pathlib import Path

import pygame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 800, 450
FPS = 100
STEP = 1 / FPS
MAX_FRAME_TIME = 0.1
WINNING_SCORE = 5
PADDLE_SPEED = 300
HORIZONTAL_SPEED = 500
AI_SPEED = 400
BALL_RADIUS = 5
INTRO_SECONDS = 9.2
GAME_OVER_SECONDS = 2.8
FLASH_SECONDS = 0.15

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
SCORE_GRAY = (150, 150, 150)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PLAYER_COLORS = (BLUE, RED, GREEN, YELLOW)
CHARGE_COLORS = (WHITE, GRAY, RED, BLUE, GREEN, YELLOW)
CONTROLS = (
    (pygame.K_a, pygame.K_q),
    (pygame.K_UP, pygame.K_DOWN),
    (pygame.K_t, pygame.K_y),
    (pygame.K_v, pygame.K_b),
)
ATTACK_KEYS = (pygame.K_s, pygame.K_LEFT)
