import pygame
import pygame_gui
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    PLAYER_HEIGHT,
    COLOR_BLACK,
    COLOR_TITLE_BG,
    COLOR_TITLE_TEXT,
    COLOR_WHITE,
)
from game.game_state import GameState
from game.camera import Camera
from player.player import Player
from world.test_map import TestMap


class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.state = GameState.TITLE
        self.clock = pygame.time.Clock()

        self.ui_manager = pygame_gui.UIManager(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            theme_path="assets/ui/theme.json",
        )

        self.test_map = TestMap()
        spawn_x, spawn_y = self.test_map.get_spawn_position()
        self.player = Player(spawn_x, spawn_y)
        self.camera = Camera(self.test_map.width, self.test_map.height)

        self.title_font = pygame.font.Font(None, 32)
        self.info_font = pygame.font.Font(None, 16)
        self.blink_timer = 0.0
        self.show_press_enter = True

        self._create_title_ui()

    def _create_title_ui(self):
        pass

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            pass

        if self.state == GameState.TITLE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.state = GameState.PLAYING
                    self.ui_manager.clear_and_reset()

        elif self.state == GameState.PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PAUSED
                    self._create_pause_ui()

        elif self.state == GameState.PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING
                    self.ui_manager.clear_and_reset()
                elif event.key == pygame.K_q:
                    self.state = GameState.TITLE
                    self.ui_manager.clear_and_reset()
                    self._create_title_ui()

        self.ui_manager.process_events(event)

    def _create_pause_ui(self):
        self.ui_manager.clear_and_reset()
        btn_w, btn_h = 160, 36
        center_x = SCREEN_WIDTH // 2 - btn_w // 2
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x, SCREEN_HEIGHT // 2 - 60, btn_w, btn_h),
            text="Continue (Esc)",
            manager=self.ui_manager,
        )
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x, SCREEN_HEIGHT // 2, btn_w, btn_h),
            text="Back to Title (Q)",
            manager=self.ui_manager,
        )

    def update(self):
        dt = self.clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        self.ui_manager.update(dt)

        if self.state == GameState.TITLE:
            self.blink_timer += dt
            if self.blink_timer >= 0.8:
                self.blink_timer -= 0.8
                self.show_press_enter = not self.show_press_enter

        elif self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            self.player.update(
                dt, keys,
                self.test_map.collision_map,
                self.test_map.width,
                self.test_map.height,
            )
            self.camera.update(self.player.x, self.player.y - PLAYER_HEIGHT / 2)

    def draw(self):
        self.internal_surface.fill(COLOR_BLACK)

        if self.state == GameState.TITLE:
            self._draw_title()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.PAUSED:
            self._draw_game()
            self._draw_pause_overlay()

        scaled = pygame.transform.scale(
            self.internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.screen.blit(scaled, (0, 0))

        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

    def _draw_title(self):
        self.internal_surface.fill(COLOR_TITLE_BG)

        title_text = self.title_font.render("GuiZiShan Adventure", True, COLOR_TITLE_TEXT)
        title_rect = title_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2 - 30
        )
        self.internal_surface.blit(title_text, title_rect)

        sub_text = self.info_font.render(
            "Campus Mystery Exploration", True, COLOR_WHITE
        )
        sub_rect = sub_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2
        )
        self.internal_surface.blit(sub_text, sub_rect)

        if self.show_press_enter:
            enter_text = self.info_font.render("Press ENTER to Start", True, COLOR_WHITE)
            enter_rect = enter_text.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2 + 40
            )
            self.internal_surface.blit(enter_text, enter_rect)

    def _draw_game(self):
        self.test_map.draw(self.internal_surface, self.camera)
        self.player.draw(self.internal_surface, self.camera)

        pos_text = self.info_font.render(
            f"Pos: ({int(self.player.x)}, {int(self.player.y)})  "
            f"Dir: {self.player.direction}  "
            f"Stamina: {int(self.player.stamina)}",
            True, COLOR_WHITE,
        )
        bg_rect = pos_text.get_rect(topleft=(4, 4))
        bg_surf = pygame.Surface((bg_rect.width + 4, bg_rect.height + 2), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 128))
        self.internal_surface.blit(bg_surf, (2, 3))
        self.internal_surface.blit(pos_text, (4, 4))

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.internal_surface.blit(overlay, (0, 0))

        pause_text = self.title_font.render("PAUSED", True, COLOR_WHITE)
        pause_rect = pause_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2 - 50
        )
        self.internal_surface.blit(pause_text, pause_rect)
