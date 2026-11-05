"""Shared translucent panels for countdown, pause and results."""
import pygame
from ..config import CYAN, PANEL


def overlay(surface):
    shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    shade.fill((3, 5, 15, 205))
    surface.blit(shade, (0, 0))
    rect = pygame.Rect(220, 75, 360, 320)
    pygame.draw.rect(surface, PANEL, rect, border_radius=12)
    pygame.draw.rect(surface, CYAN, rect, 1, border_radius=12)
