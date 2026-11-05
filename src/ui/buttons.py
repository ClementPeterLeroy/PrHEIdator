"""Navigation and rendering share identical logical button rectangles."""
import pygame
from ..config import CYAN, MUTED_TEXT, PANEL, PURPLE, TEXT


def button_rects(count, layout="side"):
    if layout == "credits":
        return [pygame.Rect(424, 364, 320, 38)]
    if layout == "overlay":
        return [pygame.Rect(260, 214 + i * 52, 280, 42) for i in range(count)]
    if layout == "bottom":
        return [pygame.Rect(210 + i * 200, 364, 180, 44) for i in range(count)]
    return [pygame.Rect(424, 103 + i * 46, 320, 38) for i in range(count)]


def draw_button(surface, rect, label, font, selected=False, hover=0, pressed=False, primary=True):
    panel = tuple(min(255, c + int(hover * 12)) for c in PANEL)
    pygame.draw.rect(surface, panel, rect, border_radius=6)
    color = CYAN if selected else PURPLE if primary else (47, 62, 88)
    if pressed:
        color = TEXT
    pygame.draw.rect(surface, color, rect, 2 if selected else 1, border_radius=6)
    if selected:
        pygame.draw.rect(surface, CYAN, (rect.x, rect.y + 8, 3, rect.height - 16), border_radius=1)
    text = font.render(label, True, TEXT if selected or primary else MUTED_TEXT)
    surface.blit(text, text.get_rect(center=rect.center))
