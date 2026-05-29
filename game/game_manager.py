from enum import Enum, auto

import pygame

from config import INTERNAL_WIDTH, INTERNAL_HEIGHT, BLACK, WHITE
from game.font import get_font


class GameState(Enum):
    TITLE = auto()
    INTRO = auto()
    PLAYING = auto()
    PAUSED = auto()
    INVENTORY = auto()
    MAP_VIEW = auto()
    DIALOG = auto()
    PUZZLE = auto()
    OUTRO = auto()


class GameManager:
    def __init__(self):
        self.state = GameState.TITLE
        self._previous_state = None

    def change_state(self, new_state):
        self._previous_state = self.state
        self.state = new_state

    def restore_previous_state(self):
        if self._previous_state is not None:
            self.state = self._previous_state
            self._previous_state = None

    def is_playing(self):
        return self.state == GameState.PLAYING

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        key = event.key

        if self.state == GameState.TITLE:
            if key == pygame.K_RETURN:
                self.change_state(GameState.PLAYING)

        elif self.state == GameState.PLAYING:
            if key == pygame.K_ESCAPE:
                self.change_state(GameState.PAUSED)
            elif key == pygame.K_TAB or key == pygame.K_i:
                self.change_state(GameState.INVENTORY)
            elif key == pygame.K_m:
                self.change_state(GameState.MAP_VIEW)

        elif self.state == GameState.PAUSED:
            if key == pygame.K_ESCAPE:
                self.change_state(GameState.PLAYING)
            elif key == pygame.K_t:
                self.change_state(GameState.TITLE)

        elif self.state == GameState.INVENTORY:
            if key == pygame.K_ESCAPE or key == pygame.K_TAB or key == pygame.K_i:
                self.change_state(GameState.PLAYING)

        elif self.state == GameState.MAP_VIEW:
            if key == pygame.K_ESCAPE or key == pygame.K_m:
                self.change_state(GameState.PLAYING)

        elif self.state == GameState.DIALOG:
            pass

        elif self.state == GameState.PUZZLE:
            pass

    def update(self, dt):
        pass

    def draw(self, surface):
        if self.state == GameState.TITLE:
            self._draw_title(surface)
        elif self.state == GameState.PAUSED:
            self._draw_pause(surface)
        elif self.state == GameState.INVENTORY:
            self._draw_inventory_placeholder(surface)
        elif self.state == GameState.MAP_VIEW:
            self._draw_map_view_placeholder(surface)

    def _draw_title(self, surface):
        surface.fill(BLACK)
        font = get_font(24)
        title_text = font.render("桂子山校园秘境探险", True, WHITE)
        title_rect = title_text.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2 - 20))
        surface.blit(title_text, title_rect)

        hint_font = get_font(14)
        hint_text = hint_font.render("按 Enter 开始游戏", True, WHITE)
        hint_rect = hint_text.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2 + 20))
        surface.blit(hint_text, hint_rect)

    def _draw_pause(self, surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        font = get_font(20)
        pause_text = font.render("暂停", True, WHITE)
        pause_rect = pause_text.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2 - 20))
        surface.blit(pause_text, pause_rect)

        hint_font = get_font(12)
        hint1 = hint_font.render("ESC - 继续", True, WHITE)
        hint2 = hint_font.render("T - 返回标题", True, WHITE)
        surface.blit(hint1, hint1.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2 + 10)))
        surface.blit(hint2, hint2.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2 + 28)))

    def _draw_inventory_placeholder(self, surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        font = get_font(16)
        text = font.render("背包 (Tab/I 关闭)", True, WHITE)
        text_rect = text.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2))
        surface.blit(text, text_rect)

    def _draw_map_view_placeholder(self, surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        font = get_font(16)
        text = font.render("地图 (M 关闭)", True, WHITE)
        text_rect = text.get_rect(center=(INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2))
        surface.blit(text, text_rect)
