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
from player.inventory import Inventory, get_item_data
from world.tilemap import TileMap
from world.transition import TransitionManager, TransitionType
from ui.dialog_box import DialogBox
from ui.inventory_ui import InventoryUI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAP_FILES = {
    "main_campus": "main_campus.tmx",
    "library_f1": "library_f1.tmx",
    "library_f2": "library_f2.tmx",
    "gym": "gym.tmx",
    "dining_hall_f1": "dining_hall_f1.tmx",
    "dining_hall_f2": "dining_hall_f2.tmx",
    "nanhu_campus": "nanhu_campus.tmx",
    "nanhulou_f1": "nanhulou_f1.tmx",
    "nanhulou_f2": "nanhulou_f2.tmx",
}

INDOOR_MAPS = {"library_f1", "library_f2", "gym", "dining_hall_f1", "dining_hall_f2",
               "nanhulou_f1", "nanhulou_f2"}

NANHU_MAPS = {"nanhu_campus", "nanhulou_f1", "nanhulou_f2"}


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

        self.current_map_id = "main_campus"
        tmx_path = self._get_tmx_path("main_campus")
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
        self.inventory_ui = InventoryUI()
        self._dialogues_cache = {}
        self._nearby_interactable = None
        self._nearby_type = None
        self._puzzle_states = {}
        self._dialog_flags = {}
        self._visited_nanhu = False
        self._pending_nanhu_intro = False

        self.transition_manager = TransitionManager()
        self._map_cache = {}
        self._map_cache["main_campus"] = self.tile_map

        self.interactive_objects = list(self.tile_map.interactive_objects)
        self.npcs = list(self.tile_map.npcs)
        self.triggers = list(self.tile_map.triggers)

        self._setup_test_entities()

    def _get_tmx_path(self, map_id):
        filename = MAP_FILES.get(map_id, f"{map_id}.tmx")
        return os.path.join(PROJECT_ROOT, "world", "map_data", filename)

    def _load_map(self, map_id, spawn_point="default"):
        if map_id == self.current_map_id:
            new_tile_map = self.tile_map
        elif map_id in self._map_cache:
            new_tile_map = self._map_cache[map_id]
        else:
            tmx_path = self._get_tmx_path(map_id)
            new_tile_map = TileMap(tmx_path)
            self._map_cache[map_id] = new_tile_map

        self.current_map_id = map_id
        self.tile_map = new_tile_map

        spawn_x, spawn_y = self.tile_map.get_spawn_position(spawn_point)
        self.player.x = spawn_x
        self.player.y = spawn_y

        self.camera = Camera(self.tile_map.width, self.tile_map.height)
        self.camera.update(self.player.x, self.player.y - PLAYER_HEIGHT / 2)

        self.interactive_objects = list(self.tile_map.interactive_objects)
        self.npcs = list(self.tile_map.npcs)
        self.triggers = list(self.tile_map.triggers)

        if map_id == "main_campus":
            self._setup_test_entities()
        elif map_id == "nanhu_campus":
            self._setup_nanhu_entities()
        elif map_id == "nanhulou_f1":
            self._setup_nanhulou_f1_entities()

    def _start_transition(self, transition_type, target_map, spawn_point):
        self.transition_manager.start_transition(
            transition_type, target_map, spawn_point,
            on_load_callback=self._on_transition_load,
        )

    def _on_transition_load(self, target_map, spawn_point):
        self._load_map(target_map, spawn_point)

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

        pickup_obj1 = InteractiveObject(
            x=spawn_x - 32, y=spawn_y - 32,
            width=12, height=12,
            interactive_type="pickup",
            properties={
                "prompt_text": "拾取桂花枝",
                "color": (180, 160, 60),
                "item_id": "osmanthus_branch",
                "pickup_text": "拾取了桂花枝！散发着淡淡的桂花清香。",
            },
        )
        self.interactive_objects.append(pickup_obj1)

        pickup_obj2 = InteractiveObject(
            x=spawn_x - 56, y=spawn_y - 32,
            width=12, height=12,
            interactive_type="pickup",
            properties={
                "prompt_text": "拾取古旧书签",
                "color": (140, 100, 60),
                "item_id": "old_bookmark",
                "pickup_text": "拾取了古旧书签！一枚精致的竹制书签。",
            },
        )
        self.interactive_objects.append(pickup_obj2)

        pickup_obj3 = InteractiveObject(
            x=spawn_x + 32, y=spawn_y - 32,
            width=12, height=12,
            interactive_type="pickup",
            properties={
                "prompt_text": "拾取水壶",
                "color": (100, 160, 220),
                "item_id": "water_bottle",
                "pickup_text": "拾取了水壶！可以恢复体力。",
            },
        )
        self.interactive_objects.append(pickup_obj3)

        pickup_obj4 = InteractiveObject(
            x=spawn_x + 56, y=spawn_y - 32,
            width=12, height=12,
            interactive_type="pickup",
            properties={
                "prompt_text": "拾取旧校徽",
                "color": (180, 180, 60),
                "item_id": "old_badge",
                "pickup_text": "拾取了旧校徽！表面似乎有隐藏的纹路。",
            },
        )
        self.interactive_objects.append(pickup_obj4)

        pickup_obj5 = InteractiveObject(
            x=spawn_x + 80, y=spawn_y - 32,
            width=12, height=12,
            interactive_type="pickup",
            properties={
                "prompt_text": "拾取放大镜",
                "color": (160, 200, 220),
                "item_id": "magnifying_glass",
                "pickup_text": "拾取了放大镜！也许能发现隐藏的细节。",
            },
        )
        self.interactive_objects.append(pickup_obj5)

    def _setup_nanhu_entities(self):
        from entities.npc import NPC

        if not self._visited_nanhu:
            self._visited_nanhu = True
            self._pending_nanhu_intro = True

    def _setup_nanhulou_f1_entities(self):
        from entities.npc import NPC

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        senior_student = NPC(
            x=spawn_x + 32, y=spawn_y - 16,
            npc_id="senior_student",
            dialogue_id="senior_student",
            properties={
                "direction": "down",
                "body_color": (80, 140, 80),
                "hair_color": (40, 30, 20),
            },
        )
        self.npcs.append(senior_student)

    def _trigger_nanhu_intro(self):
        intro_data = {
            "default": [
                {"speaker": "", "text": "校车缓缓驶入南湖校区……"},
                {"speaker": "", "text": "眼前是一片宁静的校园，远处波光粼粼的南湖映着天空的倒影。"},
                {"speaker": "", "text": "综合楼矗立在校区中央，似乎隐藏着什么秘密……"},
                {"speaker": "", "text": "也许该去综合楼里看看。"},
            ]
        }
        self.state = GameState.DIALOG
        self.dialog_box.start(
            intro_data,
            start_key="default",
            on_complete=self._on_dialog_complete,
            game_state=self._get_dialog_game_state(),
        )

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
        if self.transition_manager.is_active:
            return

        if self.state == GameState.DIALOG:
            self.dialog_box.handle_event(event)
            if not self.dialog_box.active:
                self._on_dialog_complete()
            self.ui_manager.process_events(event)
            return

        if self.state == GameState.INVENTORY:
            self.inventory_ui.handle_event(event)
            if not self.inventory_ui.active:
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
                elif event.key in (pygame.K_TAB, pygame.K_i):
                    self._open_inventory()

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

    def _open_inventory(self):
        self.inventory_ui.open(self.player.inventory, self.player)
        self.state = GameState.INVENTORY

    def _handle_interaction(self):
        if self._nearby_interactable is None:
            return

        result = self._nearby_interactable.interact()
        if result is None:
            return

        interact_type = result.get("type", "")

        if interact_type == "enter":
            obj = result.get("object", self._nearby_interactable)
            target_map = None
            spawn_point = None
            transition_type_str = "indoor_enter"

            if hasattr(obj, "properties"):
                target_map = obj.properties.get("target_map")
                spawn_point = obj.properties.get("spawn_point")
                transition_type_str = obj.properties.get(
                    "transition_type", "indoor_enter"
                )

            if not target_map:
                if hasattr(obj, "target_map"):
                    target_map = obj.target_map
                if hasattr(obj, "spawn_point"):
                    spawn_point = obj.spawn_point

            if target_map:
                try:
                    t_type = TransitionType(transition_type_str)
                except ValueError:
                    if target_map in INDOOR_MAPS:
                        t_type = TransitionType.INDOOR_ENTER
                    else:
                        t_type = TransitionType.CAMPUS_BUS
                self._start_transition(t_type, target_map, spawn_point or "default")
            return

        if interact_type == "dialog":
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
                game_state=self._get_dialog_game_state(),
            )
        elif interact_type == "examine":
            examine_text = result.get("text", "")
            if not examine_text:
                obj = result.get("object")
                if obj and hasattr(obj, "properties"):
                    examine_text = obj.properties.get("examine_text", "没有什么特别的。")
                else:
                    examine_text = "没有什么特别的。"
            self.state = GameState.DIALOG
            self.dialog_box.start(
                {"default": [{"speaker": "", "text": examine_text}]},
                start_key="default",
                on_complete=self._on_dialog_complete,
                game_state=self._get_dialog_game_state(),
            )
        elif interact_type == "pickup":
            obj = result.get("object")
            item_id = ""
            if obj and hasattr(obj, "item_id"):
                item_id = obj.item_id
            if obj and hasattr(obj, "properties"):
                item_id = item_id or obj.properties.get("item_id", "")

            if item_id:
                item_data = get_item_data(item_id)
                item_name = item_data.get("name", item_id) if item_data else item_id
                if self.player.inventory.add_item(item_id):
                    if obj:
                        obj.interacted = True
                    pickup_text = f"拾取了{item_name}！"
                else:
                    pickup_text = "背包已满，无法拾取！"
            else:
                if obj:
                    obj.interacted = True
                pickup_text = "拾取了物品。"
                if obj and hasattr(obj, "properties"):
                    pickup_text = obj.properties.get("pickup_text", "拾取了物品。")

            self.state = GameState.DIALOG
            self.dialog_box.start(
                {"default": [{"speaker": "", "text": pickup_text}]},
                start_key="default",
                on_complete=self._on_dialog_complete,
                game_state=self._get_dialog_game_state(),
            )
        elif interact_type == "use":
            obj = result.get("object")
            use_text = "使用了物品。"
            if obj and hasattr(obj, "properties"):
                use_text = obj.properties.get("use_text", "使用了物品。")
            self.state = GameState.DIALOG
            self.dialog_box.start(
                {"default": [{"speaker": "", "text": use_text}]},
                start_key="default",
                on_complete=self._on_dialog_complete,
                game_state=self._get_dialog_game_state(),
            )
        elif interact_type == "mechanism":
            obj = result.get("object")
            mech_text = "操作了机关。"
            if obj and hasattr(obj, "properties"):
                mech_text = obj.properties.get("mechanism_text", "操作了机关。")
            self.state = GameState.DIALOG
            self.dialog_box.start(
                {"default": [{"speaker": "", "text": mech_text}]},
                start_key="default",
                on_complete=self._on_dialog_complete,
                game_state=self._get_dialog_game_state(),
            )

    def _get_dialog_game_state(self):
        return {
            "puzzle_states": getattr(self, "_puzzle_states", {}),
            "dialog_flags": getattr(self, "_dialog_flags", {}),
        }

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

        self.transition_manager.update(dt)

        if self.transition_manager.is_active:
            return

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
            self._check_auto_triggers()

            if self._pending_nanhu_intro:
                self._pending_nanhu_intro = False
                self._trigger_nanhu_intro()

        elif self.state == GameState.DIALOG:
            self.dialog_box.update(dt)
            for npc in self.npcs:
                npc.update(dt)
            if not self.dialog_box.active:
                self._on_dialog_complete()

        elif self.state == GameState.INVENTORY:
            self.inventory_ui.update(dt)

    def _check_auto_triggers(self):
        player_rect = self.player.get_hitbox_rect()
        for trigger in self.triggers:
            if not trigger.auto_trigger:
                continue
            if trigger.overlaps_rect(player_rect):
                target_map = trigger.target_map or trigger.properties.get("target_map")
                spawn_point = trigger.spawn_point or trigger.properties.get("spawn_point")
                transition_type_str = trigger.properties.get(
                    "transition_type", "indoor_exit"
                )
                if target_map:
                    try:
                        t_type = TransitionType(transition_type_str)
                    except ValueError:
                        t_type = TransitionType.INDOOR_EXIT
                    self._start_transition(t_type, target_map, spawn_point or "default")
                    return

    def _check_nearby_interactables(self):
        px, py = self.player.x, self.player.y
        self._nearby_interactable = None
        self._nearby_type = None

        best_dist = float("inf")
        for npc in self.npcs:
            if npc.is_player_nearby(px, py):
                dx = px - npc.x
                dy = py - (npc.y - npc.height / 2)
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

        for trigger in self.triggers:
            if trigger.auto_trigger:
                continue
            if trigger.contains_point(px, py):
                target_map = trigger.target_map or trigger.properties.get("target_map")
                if target_map:
                    dx = px - (trigger.x + trigger.width / 2)
                    dy = py - (trigger.y + trigger.height / 2)
                    dist = dx * dx + dy * dy
                    if dist < best_dist:
                        best_dist = dist
                        self._nearby_interactable = trigger
                        self._nearby_type = "trigger"

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
        elif self.state == GameState.INVENTORY:
            self._draw_game()
            self.inventory_ui.draw(self.internal_surface)

        self.transition_manager.draw(self.internal_surface)

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

        badge_count = self.player.inventory.get_badge_count()
        map_label = "室内" if self.current_map_id in INDOOR_MAPS else "室外"
        campus_label = "南湖" if self.current_map_id in NANHU_MAPS else "本部"
        pos_text = self.info_font.render(
            f"{campus_label}{map_label} "
            f"位置:({int(self.player.x)},{int(self.player.y)}) "
            f"方向:{self.player.direction} "
            f"体力:{int(self.player.stamina)} "
            f"徽章:{badge_count}/7 "
            f"背包:Tab",
            True, COLOR_WHITE,
        )
        bg_rect = pos_text.get_rect(topleft=(4, 4))
        bg_surf = pygame.Surface((bg_rect.width + 4, bg_rect.height + 2), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 128))
        self.internal_surface.blit(bg_surf, (2, 3))
        self.internal_surface.blit(pos_text, (4, 4))

    def _draw_interaction_prompts(self):
        if self._nearby_interactable is not None:
            if self._nearby_type == "trigger":
                trigger = self._nearby_interactable
                sx, sy = self.camera.apply(
                    trigger.x + trigger.width / 2,
                    trigger.y - 4,
                )
                transition_type_str = trigger.properties.get(
                    "transition_type", "indoor_enter"
                )
                if transition_type_str == "floor_change":
                    prompt = "按 F 切换楼层"
                elif transition_type_str == "campus_bus":
                    prompt = "按 F 乘校车"
                else:
                    prompt = "按 F 进入"
                text_surf = self.info_font.render(prompt, True, (255, 255, 255))
                text_rect = text_surf.get_rect(centerx=int(sx), bottom=int(sy))
                bg_rect = text_rect.inflate(6, 4)
                bg_surf = pygame.Surface(
                    (bg_rect.width, bg_rect.height), pygame.SRCALPHA
                )
                bg_surf.fill((0, 0, 0, 160))
                self.internal_surface.blit(bg_surf, bg_rect.topleft)
                self.internal_surface.blit(text_surf, text_rect)
            else:
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
