import json
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
from ui.dialog_box import DialogBox

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.state = GameState.TITLE
        self.clock = pygame.time.Clock()

        theme_path = os.path.join(PROJECT_ROOT, "assets", "ui", "theme.json")
        self.ui_manager = pygame_gui.UIManager(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            theme_path=theme_path,
        )

        tmx_path = os.path.join(PROJECT_ROOT, "world", "map_data", "main_campus.tmx")
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

        self.dialog_box = DialogBox()
        self._dialogues_cache = {}
        self._nearby_interactable = None
        self._nearby_type = None

        self.interactive_objects = list(self.tile_map.interactive_objects)
        self.npcs = list(self.tile_map.npcs)
        self.triggers = list(self.tile_map.triggers)

        self._setup_test_entities()

    def _setup_test_entities(self):
        from entities.npc import NPC
        from entities.interactive_object import InteractiveObject

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        test_npc = NPC(
            x=spawn_x + 48, y=spawn_y,
            npc_id="librarian",
            dialogue_id="librarian",
            properties={"direction": "down"},
        )
        self.npcs.append(test_npc)

        test_npc2 = NPC(
            x=spawn_x - 48, y=spawn_y,
            npc_id="senior_student",
            dialogue_id="senior_student",
            properties={
                "direction": "right",
                "body_color": (80, 140, 80),
                "hair_color": (40, 30, 20),
            },
        )
        self.npcs.append(test_npc2)

        test_obj = InteractiveObject(
            x=spawn_x + 80, y=spawn_y - 16,
            width=16, height=16,
            interactive_type="examine",
            properties={"prompt_text": "查看告示牌", "color": (160, 140, 100)},
        )
        test_obj.on_interact = lambda obj: {
            "type": "dialog",
            "dialogue_id": "_builtin",
            "dialogue_data": {
                "default": [
                    {"speaker": "", "text": "告示牌上写着：欢迎来到桂子山！请注意校园内的安全提示。"},
                ]
            },
        }
        self.interactive_objects.append(test_obj)

    def _load_dialogue(self, dialogue_id):
        if dialogue_id in self._dialogues_cache:
            return self._dialogues_cache[dialogue_id]

        dialogue_path = os.path.join(
            PROJECT_ROOT, "data", "dialogues", f"{dialogue_id}.json"
        )
        if os.path.exists(dialogue_path):
            with open(dialogue_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._dialogues_cache[dialogue_id] = data
            return data
        return None

    def _create_title_ui(self):
        pass

    def handle_event(self, event):
        if self.state == GameState.DIALOG:
            consumed = self.dialog_box.handle_event(event)
            if consumed:
                return
            if not self.dialog_box.active:
                self.state = GameState.PLAYING
            self.ui_manager.process_events(event)
            return

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
                elif event.key == pygame.K_f:
                    self._handle_interaction()

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

    def _handle_interaction(self):
        if self._nearby_interactable is None:
            return

        result = self._nearby_interactable.interact()
        if result is None:
            return

        if result.get("type") == "dialog":
            dialogue_id = result.get("dialogue_id", "")
            dialogue_data = result.get("dialogue_data")

            if dialogue_data is None:
                dialogue_data = self._load_dialogue(dialogue_id)

            if dialogue_data is None:
                dialogue_data = {
                    "default": [
                        {"speaker": "", "text": "..."},
                    ]
                }

            portrait_color = None
            if self._nearby_type == "npc":
                portrait_color = getattr(self._nearby_interactable, "body_color", None)

            self.state = GameState.DIALOG
            self.dialog_box.start(
                dialogue_data,
                start_key="default",
                on_complete=self._on_dialog_complete,
                portrait_color=portrait_color,
            )

    def _on_dialog_complete(self):
        self.state = GameState.PLAYING

    def _create_pause_ui(self):
        self.ui_manager.clear_and_reset()
        btn_w, btn_h = 160, 36
        center_x = SCREEN_WIDTH // 2 - btn_w // 2
        self._pause_continue_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x, SCREEN_HEIGHT // 2 - 60, btn_w, btn_h),
            text="Continue (Esc)",
            manager=self.ui_manager,
        )
        self._pause_title_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x, SCREEN_HEIGHT // 2, btn_w, btn_h),
            text="Quit to Title (Q)",
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

            for npc in self.npcs:
                npc.update(dt)

            self._check_nearby_interactables()

        elif self.state == GameState.DIALOG:
            self.dialog_box.update(dt)

    def _check_nearby_interactables(self):
        px, py = self.player.x, self.player.y
        self._nearby_interactable = None
        self._nearby_type = None

        best_dist = float("inf")
        for npc in self.npcs:
            if npc.is_player_nearby(px, py):
                dx = px - npc.x
                dy = py - npc.y
                dist = dx * dx + dy * dy
                if dist < best_dist:
                    best_dist = dist
                    self._nearby_interactable = npc
                    self._nearby_type = "npc"

        for obj in self.interactive_objects:
            if obj.is_player_nearby(px, py):
                dx = px - obj.center_x
                dy = py - obj.center_y
                dist = dx * dx + dy * dy
                if dist < best_dist:
                    best_dist = dist
                    self._nearby_interactable = obj
                    self._nearby_type = "object"

    def draw(self):
        self.internal_surface.fill(COLOR_BLACK)

        if self.state == GameState.TITLE:
            self._draw_title()
        elif self.state == GameState.PLAYING:
            self._draw_game()
            self._draw_interaction_prompts()
        elif self.state == GameState.PAUSED:
            self._draw_game()
            self._draw_pause_overlay()
        elif self.state == GameState.DIALOG:
            self._draw_game()
            self.dialog_box.draw(self.internal_surface)

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

        for obj in self.interactive_objects:
            obj.draw(self.internal_surface, self.camera)

        for npc in self.npcs:
            npc.draw(self.internal_surface, self.camera)

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

    def _draw_interaction_prompts(self):
        if self._nearby_interactable is not None:
            self._nearby_interactable.draw_prompt(
                self.internal_surface, self.camera, self.info_font
            )

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.internal_surface.blit(overlay, (0, 0))

        pause_text = self.title_font.render("暂停", True, COLOR_WHITE)
        pause_rect = pause_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2 - 50
        )
        self.internal_surface.blit(pause_text, pause_rect)
