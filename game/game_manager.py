import os
import pygame
import pygame_gui
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    PLAYER_HEIGHT,
    FONT_PATH,
    FONT_TITLE_SIZE,
    FONT_INFO_SIZE,
    COLOR_BLACK,
    COLOR_TITLE_BG,
    COLOR_TITLE_TEXT,
    COLOR_WHITE,
)
from game.game_state import GameState
from game.camera import Camera
from player.player import Player
from world.tilemap import TileMap

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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

        tmx_path = os.path.join(PROJECT_ROOT, "world", "map_data", "test_map.tmx")
        self.tile_map = TileMap(tmx_path)
        spawn_x, spawn_y = self.tile_map.get_spawn_position()
        self.player = Player(spawn_x, spawn_y)
        self.camera = Camera(self.tile_map.width, self.tile_map.height)

        self.title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        self.info_font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.blink_timer = 0.0
        self.show_press_enter = True

        self._pause_continue_btn = None
        self._pause_title_btn = None
        self._create_title_ui()

    def _create_title_ui(self):
        pass

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if self.state == GameState.PAUSED:
                if event.ui_element == self._pause_continue_btn:
                    self.state = GameState.PLAYING
                    self.ui_manager.clear_and_reset()
                elif event.ui_element == self._pause_title_btn:
                    self.state = GameState.TITLE
                    self.ui_manager.clear_and_reset()
                    self._create_title_ui()

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
        self._pause_continue_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x, SCREEN_HEIGHT // 2 - 60, btn_w, btn_h),
            text="继续游戏 (Esc)",
            manager=self.ui_manager,
        )
        self._pause_title_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x, SCREEN_HEIGHT // 2, btn_w, btn_h),
            text="返回标题 (Q)",
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
                self.tile_map.collision_map,
                self.tile_map.width,
                self.tile_map.height,
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

        title_text = self.title_font.render("桂子山秘境探险", True, COLOR_TITLE_TEXT)
        title_rect = title_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2 - 30
        )
        self.internal_surface.blit(title_text, title_rect)

        sub_text = self.info_font.render(
            "校园秘境探险", True, COLOR_WHITE
        )
        sub_rect = sub_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2
        )
        self.internal_surface.blit(sub_text, sub_rect)

        if self.show_press_enter:
            enter_text = self.info_font.render("按 回车键 开始游戏", True, COLOR_WHITE)
            enter_rect = enter_text.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2 + 40
            )
            self.internal_surface.blit(enter_text, enter_rect)

    def _draw_game(self):
        self.tile_map.draw(self.internal_surface, self.camera)
        self.player.draw(self.internal_surface, self.camera)

        pos_text = self.info_font.render(
            f"位置:({int(self.player.x)},{int(self.player.y)}) "
            f"方向:{self.player.direction} "
            f"体力:{int(self.player.stamina)}",
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

        pause_text = self.title_font.render("暂停", True, COLOR_WHITE)
        pause_rect = pause_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2 - 50
        )
        self.internal_surface.blit(pause_text, pause_rect)
