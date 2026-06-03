import json
import math
import os
import random
import pygame
import pygame_gui
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    TILE_SIZE,
    PLAYER_HEIGHT,
    FONT_PATH,
    FONT_TITLE_SIZE,
    FONT_INFO_SIZE,
    COLOR_BLACK,
    COLOR_TITLE_BG,
    COLOR_TITLE_TEXT,
    COLOR_WHITE,
    INTERACTION_RANGE,
)
from game.game_state import GameState
from game.camera import Camera
from game.clock import GameClock
from game.save_manager import SaveManager
from player.player import Player
from player.inventory import Inventory, get_item_data
from world.tilemap import TileMap
from world.transition import TransitionManager, TransitionType
from ui.dialog_box import DialogBox
from ui.inventory_ui import InventoryUI
from ui.hud import HUD
from ui.minimap import Minimap
from ui.menu import Menu
from puzzle.puzzle_manager import PuzzleManager, PuzzleState
from puzzle.guizhong_puzzle import GuizhongPuzzle
from puzzle.nanhulou_puzzle import NanhulouPuzzle
from puzzle.dining_puzzle import DiningPuzzle
from puzzle.library_puzzle import LibraryPuzzle
from puzzle.boya_puzzle import BoyaPuzzle
from puzzle.gym_puzzle import GymPuzzle
from puzzle.fountain_puzzle import FountainPuzzle

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
    "nanhulou_secret": "nanhulou_secret.tmx",
}

INDOOR_MAPS = {"library_f1", "library_f2", "gym", "dining_hall_f1", "dining_hall_f2",
               "nanhulou_f1", "nanhulou_f2", "nanhulou_secret"}

NANHU_MAPS = {"nanhu_campus", "nanhulou_f1", "nanhulou_f2", "nanhulou_secret"}


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
        self.camera.update(self.player.x, self.player.y - PLAYER_HEIGHT / 2)

        self.title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        self.info_font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.blink_timer = 0.0
        self.show_press_enter = True

        # 标题画面菜单
        self._title_menu_items = ["开始游戏", "继续游戏", "设置"]
        self._title_menu_index = 0
        self._title_menu_active = False  # 是否在菜单选择模式
        self._title_anim_timer = 0.0
        self._title_logo_y = -30  # Logo初始位置（从上方滑入）
        self._title_logo_settled = False

        # 开场动画
        self._intro_phase = 0  # 0=黑屏文字, 1=校门场景, 2=秘境降临
        self._intro_timer = 0.0
        self._intro_text_alpha = 0
        self._intro_player_y = 0.0
        self._intro_fade_alpha = 255

        # 结局动画
        self._outro_phase = 0  # 0=光芒, 1=秘境消散, 2=结局文字, 3=制作组
        self._outro_timer = 0.0
        self._outro_fade_alpha = 0
        self._outro_ending_type = "normal"  # normal/good/true
        self._outro_text_shown = False

        self._create_title_ui()

        self.dialog_box = DialogBox()
        self.inventory_ui = InventoryUI()
        self.hud = HUD()
        self.minimap = Minimap()
        self.menu = Menu()
        self.save_manager = SaveManager()
        self._dialogues_cache = {}
        self._nearby_interactable = None
        self._nearby_type = None
        self._dialog_flags = {}
        self._visited_nanhu = False
        self._pending_nanhu_intro = False

        self.puzzle_manager = PuzzleManager()
        self.guizhong_puzzle = GuizhongPuzzle(self.puzzle_manager, self.player.inventory)
        self.nanhulou_puzzle = NanhulouPuzzle(self.puzzle_manager, self.player.inventory)
        self.dining_puzzle = DiningPuzzle(self.puzzle_manager, self.player.inventory)
        self.library_puzzle = LibraryPuzzle(self.puzzle_manager, self.player.inventory)
        self.boya_puzzle = BoyaPuzzle(self.puzzle_manager, self.player.inventory)
        self.gym_puzzle = GymPuzzle(self.puzzle_manager, self.player.inventory)
        self.fountain_puzzle = FountainPuzzle(self.puzzle_manager, self.player.inventory)
        self._active_puzzle = None
        self.game_clock = GameClock()

        self._overlay_surface = pygame.Surface(
            (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
        )

        self._guizhong_tree_obj = None
        self._guizhong_badge_obj = None

        self._nanhulou_bookshelf_obj = None
        self._nanhulou_bookshelf_base_x = 0
        self._nanhulou_bookshelf_animating = False
        self._nanhulou_bookshelf_anim_timer = 0.0
        self._nanhulou_bookshelf_anim_duration = 1.5

        self._boya_sculpture_obj = None
        self._boya_badge_obj = None
        self._gym_equipment_cabinet_obj = None
        self._gym_scoreboard_obj = None
        self._library_bookshelf_obj = None
        self._library_badge_obj = None
        self._pending_library_quiz = False
        self._pending_gym_shooting = False

        self._realm_triggered = False
        self._realm_animating = False
        self._realm_anim_timer = 0.0
        self._realm_anim_duration = 3.0
        self._realm_first_night_shown = False
        self._realm_hint_timer = 0.0
        self._realm_hint_duration = 5.0
        self._realm_hint_active = False
        self._tutorial_shown = False

        self.transition_manager = TransitionManager()
        self._map_cache = {}
        self._map_cache["main_campus"] = self.tile_map

        self.interactive_objects = list(self.tile_map.interactive_objects)
        self.npcs = list(self.tile_map.npcs)
        self.triggers = list(self.tile_map.triggers)

        self._setup_test_entities()
        self._update_npc_visibility()

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
        elif map_id == "nanhulou_f2":
            self._setup_nanhulou_f2_entities()
        elif map_id == "dining_hall_f1":
            self._setup_dining_hall_f1_entities()
        elif map_id == "dining_hall_f2":
            self._setup_dining_hall_f2_entities()
        elif map_id == "nanhulou_secret":
            self._setup_nanhulou_secret_entities()
        elif map_id == "library_f1":
            self._setup_library_f1_entities()
        elif map_id == "library_f2":
            self._setup_library_f2_entities()
        elif map_id == "gym":
            self._setup_gym_entities()

        self._update_npc_visibility()

    def _start_transition(self, transition_type, target_map, spawn_point):
        bus_label = ""
        if transition_type == TransitionType.CAMPUS_BUS:
            if target_map in NANHU_MAPS:
                bus_label = "前往南湖校区..."
            else:
                bus_label = "返回本部校区..."
        self.transition_manager.start_transition(
            transition_type, target_map, spawn_point,
            on_load_callback=self._on_transition_load,
            bus_label=bus_label,
        )

    def _on_transition_load(self, target_map, spawn_point):
        self._load_map(target_map, spawn_point)
        # 进/出室内或跨校区时自动存档
        self._auto_save()

    def _setup_test_entities(self):
        from entities.npc import NPC
        from entities.interactive_object import InteractiveObject

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        passing_student = NPC(
            x=spawn_x + 48, y=spawn_y,
            npc_id="passing_student",
            dialogue_id="passing_student",
            properties={
                "direction": "left",
                "body_color": (120, 100, 160),
                "hair_color": (50, 30, 20),
            },
        )
        passing_student.on_interact = lambda npc_self: {
            "type": "dialog",
            "dialogue_data": {
                "default": [
                    {"speaker": "路过的学生", "text": "听说图书馆最近在搞读书活动，往西北方向走就能看到。"},
                ]
            },
        }
        self.npcs.append(passing_student)

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

        self._setup_guizhong_entities()
        self._setup_boya_entities()
        self._setup_fountain_entities()

    def _setup_guizhong_entities(self):
        from entities.interactive_object import InteractiveObject

        tree_positions = []
        for obj in self.interactive_objects:
            if hasattr(obj, 'properties'):
                if obj.properties.get("type") == "osmanthus_tree":
                    cx = obj.x + obj.width / 2
                    cy = obj.y
                    tree_positions.append((cx, cy))
                    if len(tree_positions) >= GuizhongPuzzle.TREE_COUNT:
                        break

        if len(tree_positions) < GuizhongPuzzle.TREE_COUNT:
            road_y_north = 35 * TILE_SIZE
            road_center_x = 60 * TILE_SIZE
            for i in range(GuizhongPuzzle.TREE_COUNT - len(tree_positions)):
                tx = road_center_x - 240 + i * 80
                ty = road_y_north
                tree_positions.append((tx, ty))

        self.guizhong_puzzle.setup_trees(tree_positions)

        if self.puzzle_manager.get_state("guizhong") == PuzzleState.SOLVED:
            return

        if self.guizhong_puzzle.is_badge_dropped:
            self._create_guizhong_badge_pickup()
            return

        glowing_pos = self.guizhong_puzzle.get_glowing_tree_pos()
        if glowing_pos is None:
            return

        glow_tree = InteractiveObject(
            x=glowing_pos[0] - 8, y=glowing_pos[1] - 16,
            width=16, height=24,
            interactive_type="mechanism",
            properties={
                "prompt_text": "查看",
                "color": (100, 200, 80),
                "puzzle_id": "guizhong",
                "mechanism_text": "",
                "invisible": True,
            },
        )

        puzzle_ref = self.guizhong_puzzle
        gm = self

        def on_glow_tree_interact(obj):
            if gm.puzzle_manager.get_state("guizhong") == PuzzleState.SOLVED:
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "这棵桂花树已经不再发光了……"}]
                }}
            if not gm.game_clock.is_night():
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "这棵桂花树看起来很普通，也许夜晚会有不同……"}]
                }}
            state = puzzle_ref.state
            if state == GuizhongPuzzle.STATE_IDLE:
                puzzle_ref.examine_tree()
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "这棵桂花树散发着微光，似乎在呼唤你……"}]
                }}
            elif state == GuizhongPuzzle.STATE_EXAMINED:
                puzzle_ref.shake_tree()
                if obj in gm.interactive_objects:
                    gm.interactive_objects.remove(obj)
                gm._guizhong_tree_obj = None
                return None
            return None

        glow_tree.on_interact = on_glow_tree_interact
        self.interactive_objects.append(glow_tree)
        self._guizhong_tree_obj = glow_tree

    def _create_guizhong_badge_pickup(self):
        from entities.interactive_object import InteractiveObject

        pos = self.guizhong_puzzle.get_glowing_tree_pos()
        if pos is None:
            return

        badge_obj = InteractiveObject(
            x=pos[0] - 6, y=pos[1] + 2,
            width=12, height=12,
            interactive_type="pickup",
            properties={
                "prompt_text": "拾取徽章碎片",
                "invisible": True,
                "item_id": "badge_1",
                "pickup_text": "获得了桂花徽章碎片·壹！",
            },
        )

        puzzle_ref = self.guizhong_puzzle
        gm = self

        def on_badge_pickup(obj):
            obj.interacted = True
            gm.player.inventory.add_item("badge_1")
            puzzle_ref.mark_solved()
            if obj in gm.interactive_objects:
                gm.interactive_objects.remove(obj)
            gm._guizhong_badge_obj = None
            return {
                "type": "dialog",
                "dialogue_data": {
                    "default": [{"speaker": "", "text": "获得了桂花徽章碎片·壹！"}]
                },
            }

        badge_obj.on_interact = on_badge_pickup
        self.interactive_objects.append(badge_obj)
        self._guizhong_badge_obj = badge_obj

    def _setup_nanhu_entities(self):
        from entities.npc import NPC

        if not self._visited_nanhu:
            self._visited_nanhu = True
            self._pending_nanhu_intro = True

    def _setup_nanhulou_f1_entities(self):
        from entities.npc import NPC
        from entities.interactive_object import InteractiveObject

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

        if self.puzzle_manager.get_state("nanhulou") != PuzzleState.SOLVED:
            bulletin = InteractiveObject(
                x=spawn_x - 48, y=spawn_y - 16,
                width=16, height=16,
                interactive_type="examine",
                properties={
                    "prompt_text": "查看公告栏",
                    "color": (180, 160, 120),
                    "puzzle_id": "nanhulou",
                },
            )

            def on_bulletin_interact(obj):
                if self.player.inventory.has_item("bulletin_scrap"):
                    return {
                        "type": "dialog",
                        "dialogue_data": {
                            "default": [
                                {"speaker": "", "text": "公告栏上那张泛黄的残页，上面写着'1903年，华师肇始'。"},
                            ]
                        }
                    }
                self.player.inventory.add_item("bulletin_scrap")
                self.puzzle_manager.discover("nanhulou")
                return {
                    "type": "dialog",
                    "dialogue_data": {
                        "default": [
                            {"speaker": "", "text": "公告栏上有一张泛黄的残页……上面写着'1903年，华师肇始'。"},
                            {"speaker": "", "text": "你将残页小心取下，收入背包。"},
                        ]
                    }
                }

            bulletin.on_interact = on_bulletin_interact
            self.interactive_objects.append(bulletin)

    def _setup_nanhulou_f2_entities(self):
        from entities.interactive_object import InteractiveObject

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        if self.nanhulou_puzzle.secret_room_open:
            self._add_secret_room_entrance(spawn_x, spawn_y)
            return

        computer = InteractiveObject(
            x=spawn_x, y=spawn_y - 16,
            width=16, height=16,
            interactive_type="mechanism",
            properties={
                "prompt_text": "使用电脑",
                "color": (80, 80, 120),
                "puzzle_id": "nanhulou",
                "mechanism_text": "",
            },
        )

        puzzle_ref = self.nanhulou_puzzle

        def on_computer_interact(obj):
            if self.puzzle_manager.get_state("nanhulou") == PuzzleState.SOLVED:
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "电脑屏幕已经关闭了。"}]
                }}
            self._active_puzzle = puzzle_ref
            self.state = GameState.PUZZLE
            puzzle_ref.start(on_complete=self._on_puzzle_complete)
            return None

        computer.on_interact = on_computer_interact
        self.interactive_objects.append(computer)

        bookshelf = InteractiveObject(
            x=spawn_x + 8, y=spawn_y - 16,
            width=16, height=16,
            interactive_type="examine",
            properties={
                "prompt_text": "查看书架",
                "color": (120, 80, 40),
                "examine_text": "一个摆满书籍的书架，看起来很普通。",
            },
        )
        self.interactive_objects.append(bookshelf)
        self._nanhulou_bookshelf_obj = bookshelf
        self._nanhulou_bookshelf_base_x = bookshelf.x

    def _add_secret_room_entrance(self, spawn_x, spawn_y):
        from entities.interactive_object import InteractiveObject

        entrance = InteractiveObject(
            x=spawn_x + 8, y=spawn_y - 16,
            width=16, height=16,
            interactive_type="mechanism",
            properties={
                "prompt_text": "进入密室",
                "color": (40, 30, 20),
                "target_map": "nanhulou_secret",
                "spawn_point": "nanhulou_secret_entrance",
                "transition_type": "indoor_enter",
                "mechanism_text": "",
            },
        )

        def on_entrance_interact(obj):
            return {
                "type": "enter",
                "object": obj,
            }

        entrance.on_interact = on_entrance_interact
        self.interactive_objects.append(entrance)

    def _setup_nanhulou_secret_entities(self):
        from entities.interactive_object import InteractiveObject

        if self.puzzle_manager.get_state("nanhulou") == PuzzleState.SOLVED:
            return

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        badge_pedestal = InteractiveObject(
            x=spawn_x, y=spawn_y - 16,
            width=16, height=16,
            interactive_type="pickup",
            properties={
                "prompt_text": "拾取徽章碎片",
                "color": (255, 215, 0),
                "item_id": "badge_2",
                "pickup_text": "在密室的基座上，你发现了桂花徽章碎片·贰！散发着温润的光芒……",
            },
        )

        puzzle_ref = self.nanhulou_puzzle

        original_interact = badge_pedestal.on_interact

        def on_badge_pickup(obj):
            result = original_interact(obj) if original_interact else {
                "type": "pickup", "object": obj
            }
            self.puzzle_manager.solve("nanhulou")
            return result

        badge_pedestal.on_interact = on_badge_pickup
        self.interactive_objects.append(badge_pedestal)

    def _setup_dining_hall_f1_entities(self):
        from entities.npc import NPC

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        auntie = NPC(
            x=spawn_x + 16, y=spawn_y - 16,
            npc_id="cafeteria_auntie",
            dialogue_id="cafeteria_auntie",
            properties={
                "direction": "down",
                "body_color": (200, 120, 80),
                "hair_color": (60, 40, 20),
            },
        )

        puzzle_ref = self.dining_puzzle

        def on_auntie_interact(npc_self):
            if puzzle_ref.card_found and not puzzle_ref.card_returned:
                dialogue_data = self._load_dialogue("cafeteria_auntie")
                if dialogue_data and "card_returned" in dialogue_data:
                    puzzle_ref.return_card()
                    return {
                        "type": "dialog",
                        "dialogue_data": dialogue_data,
                        "start_key": "card_returned",
                    }
            if puzzle_ref.card_returned:
                dialogue_data = self._load_dialogue("cafeteria_auntie")
                if dialogue_data and "after_return" in dialogue_data:
                    return {
                        "type": "dialog",
                        "dialogue_data": dialogue_data,
                        "start_key": "after_return",
                    }
            return {
                "type": "dialog",
                "dialogue_id": "cafeteria_auntie",
                "dialogue_data": None,
            }

        auntie.on_interact = on_auntie_interact
        self.npcs.append(auntie)

        self.puzzle_manager.discover("dining_hall")

    def _setup_dining_hall_f2_entities(self):
        from entities.interactive_object import InteractiveObject

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        if self.puzzle_manager.get_state("dining_hall") == PuzzleState.SOLVED:
            return

        if not self.dining_puzzle.card_found:
            self._add_dining_search_tables(spawn_x, spawn_y)
        else:
            hint_obj = InteractiveObject(
                x=spawn_x, y=spawn_y - 16,
                width=16, height=16,
                interactive_type="examine",
                properties={
                    "prompt_text": "查看餐桌",
                    "color": (120, 100, 80),
                    "examine_text": "已经找到饭卡了，快去还给食堂阿姨吧！",
                },
            )
            self.interactive_objects.append(hint_obj)

    def _add_dining_search_tables(self, spawn_x, spawn_y):
        from entities.interactive_object import InteractiveObject

        puzzle_ref = self.dining_puzzle

        for i in range(DiningPuzzle.TABLE_COUNT):
            tx = spawn_x - 40 + i * 32
            ty = spawn_y - 32

            table = InteractiveObject(
                x=tx, y=ty,
                width=20, height=14,
                interactive_type="examine",
                properties={
                    "prompt_text": f"搜索餐桌{i + 1}",
                    "color": (120, 100, 80),
                    "puzzle_id": "dining_hall",
                    "examine_text": "",
                },
            )

            table_idx = i

            def make_table_interact(idx):
                def on_table_interact(obj):
                    if puzzle_ref.card_found:
                        return {"type": "dialog", "dialogue_data": {
                            "default": [{"speaker": "", "text": "已经找到饭卡了，不用再搜了。"}]
                        }}
                    result = puzzle_ref.search_table(idx)
                    if result.get("already_searched"):
                        return {"type": "dialog", "dialogue_data": {
                            "default": [{"speaker": "", "text": "已经搜索过这张桌子了。"}]
                        }}
                    elif result.get("found"):
                        return {"type": "dialog", "dialogue_data": {
                            "default": [{"speaker": "", "text": "找到了饭卡！赶紧还给食堂阿姨吧！"}]
                        }}
                    else:
                        return {"type": "dialog", "dialogue_data": {
                            "default": [{"speaker": "", "text": "这里没有……试试其他桌子吧。"}]
                        }}
                return on_table_interact

            table.on_interact = make_table_interact(i)
            self.interactive_objects.append(table)

    def _setup_boya_entities(self):
        from entities.interactive_object import InteractiveObject
        from entities.npc import NPC

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        sculpture_x = spawn_x + 96
        sculpture_y = spawn_y + 64

        sculpture = InteractiveObject(
            x=sculpture_x, y=sculpture_y,
            width=16, height=16,
            interactive_type="examine",
            properties={
                "prompt_text": "查看雕塑",
                "color": (180, 180, 160),
                "puzzle_id": "boya",
            },
        )

        gm = self

        def on_sculpture_interact(obj):
            if gm.puzzle_manager.get_state("boya") == PuzzleState.SOLVED:
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "雕塑底座的铭文已经看过了，地砖阵法也已破解。"}]
                }}
            if gm.player.inventory.has_item("sculpture_rubbing"):
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "雕塑底座铭文：'东·南·西·北·中·东南·西北·东北·西南'。你已经拓印过了。"}]
                }}
            gm.player.inventory.add_item("sculpture_rubbing")
            gm.puzzle_manager.discover("boya")
            return {"type": "dialog", "dialogue_data": {
                "default": [
                    {"speaker": "", "text": "雕塑底座刻着古老的铭文：'东·南·西·北·中·东南·西北·东北·西南'"},
                    {"speaker": "", "text": "你将铭文拓印下来，收入背包。广场上的异色地砖似乎与这顺序有关……"},
                ]
            }}

        sculpture.on_interact = on_sculpture_interact
        self.interactive_objects.append(sculpture)
        self._boya_sculpture_obj = sculpture

        tile_entrance = InteractiveObject(
            x=sculpture_x + 20, y=sculpture_y,
            width=16, height=16,
            interactive_type="mechanism",
            properties={
                "prompt_text": "地砖阵法",
                "color": (100, 100, 140),
                "puzzle_id": "boya",
                "mechanism_text": "",
            },
        )

        puzzle_ref = self.boya_puzzle

        def on_tile_entrance_interact(obj):
            if gm.puzzle_manager.get_state("boya") == PuzzleState.SOLVED:
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "地砖阵法已经破解了。"}]
                }}
            gm._active_puzzle = puzzle_ref
            gm.state = GameState.PUZZLE
            puzzle_ref.start(on_complete=gm._on_puzzle_complete)
            return None

        tile_entrance.on_interact = on_tile_entrance_interact
        self.interactive_objects.append(tile_entrance)

        dancing_auntie = NPC(
            x=sculpture_x - 16, y=sculpture_y + 16,
            npc_id="dancing_auntie",
            dialogue_id="dancing_auntie",
            properties={
                "direction": "down",
                "body_color": (200, 100, 160),
                "hair_color": (60, 40, 30),
            },
        )
        self.npcs.append(dancing_auntie)

    def _setup_fountain_entities(self):
        from entities.interactive_object import InteractiveObject
        from entities.npc import NPC

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        fountain_x = spawn_x
        fountain_y = spawn_y + 96

        fountain = InteractiveObject(
            x=fountain_x, y=fountain_y,
            width=20, height=20,
            interactive_type="mechanism",
            properties={
                "prompt_text": "喷泉基座",
                "color": (100, 140, 180),
                "puzzle_id": "fountain",
                "mechanism_text": "",
            },
        )

        gm = self
        puzzle_ref = self.fountain_puzzle

        def on_fountain_interact(obj):
            if not gm.puzzle_manager.is_fountain_unlocked():
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "喷泉被一层神秘的力量封锁着……需要集齐六枚徽章碎片才能解除。"}]
                }}
            if gm.puzzle_manager.get_state("fountain") == PuzzleState.SOLVED:
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "喷泉散发着温暖的光芒，封印已经解除了。"}]
                }}
            gm._active_puzzle = puzzle_ref
            gm.state = GameState.PUZZLE
            puzzle_ref.start(on_complete=gm._on_puzzle_complete)
            return None

        fountain.on_interact = on_fountain_interact
        self.interactive_objects.append(fountain)

        guardian = NPC(
            x=fountain_x + 24, y=fountain_y,
            npc_id="guardian",
            dialogue_id="guardian",
            properties={
                "direction": "left",
                "body_color": (120, 100, 180),
                "hair_color": (180, 180, 200),
            },
        )

        def on_guardian_interact(npc_self):
            if not gm.puzzle_manager.is_fountain_unlocked():
                return {"type": "dialog", "dialogue_data": {
                    "default": [
                        {"speaker": "秘境守护者", "text": "……还不到时候。"},
                        {"speaker": "秘境守护者", "text": "集齐六枚徽章碎片后，再来找我吧。"},
                    ]
                }}
            return {"type": "dialog", "dialogue_id": npc_self.dialogue_id, "npc": npc_self}

        guardian.on_interact = on_guardian_interact
        self.npcs.append(guardian)

    def _setup_library_f1_entities(self):
        from entities.npc import NPC

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        librarian = NPC(
            x=spawn_x + 16, y=spawn_y - 16,
            npc_id="librarian",
            dialogue_id="librarian",
            properties={
                "direction": "down",
                "body_color": (100, 120, 180),
                "hair_color": (60, 40, 30),
            },
        )

        gm = self
        puzzle_ref = self.library_puzzle

        def on_librarian_interact(npc_self):
            if gm.puzzle_manager.get_state("library") == PuzzleState.SOLVED:
                return {"type": "dialog", "dialogue_id": "librarian", "dialogue_data": None}
            if gm.library_puzzle.quiz_passed:
                return {"type": "dialog", "dialogue_data": {
                    "default": [
                        {"speaker": "图书管理员", "text": "你已经通过答题了！快去2楼找到对应的书架放置书籍吧。"},
                    ]
                }}
            gm._pending_library_quiz = True
            dialogue_data = gm._load_dialogue("librarian")
            return {
                "type": "dialog",
                "dialogue_data": dialogue_data,
                "start_key": "default",
            }

        librarian.on_interact = on_librarian_interact
        self.npcs.append(librarian)

        self.puzzle_manager.discover("library")

    def _setup_library_f2_entities(self):
        from entities.interactive_object import InteractiveObject

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        if self.puzzle_manager.get_state("library") == PuzzleState.SOLVED:
            return

        bookshelf = InteractiveObject(
            x=spawn_x, y=spawn_y - 16,
            width=16, height=16,
            interactive_type="mechanism",
            properties={
                "prompt_text": "放置书籍",
                "color": (120, 80, 40),
                "puzzle_id": "library",
                "mechanism_text": "",
            },
        )

        gm = self

        def on_bookshelf_interact(obj):
            if gm.puzzle_manager.get_state("library") == PuzzleState.SOLVED:
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "书架已经归位了。"}]
                }}
            if not gm.library_puzzle.quiz_passed:
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "这个书架上方标着'K291.5/Z3'。也许需要先通过管理员的答题挑战……"}]
                }}
            if not gm.player.inventory.has_item("special_book"):
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "书架上方标着'K291.5/Z3'。你似乎需要找到对应的书籍才能放置……"}]
                }}
            gm.player.inventory.remove_item("special_book")
            gm.player.inventory.remove_item("call_number_note")
            gm.puzzle_manager.solve("library", gm.player.inventory)
            if obj in gm.interactive_objects:
                gm.interactive_objects.remove(obj)
            gm._library_bookshelf_obj = None
            return {"type": "dialog", "dialogue_data": {
                "default": [
                    {"speaker": "", "text": "你将古旧典籍放回书架……"},
                    {"speaker": "", "text": "书架缓缓移开，露出了隐藏的密室！"},
                    {"speaker": "", "text": "获得了桂花徽章碎片·叁！"},
                ]
            }}

        bookshelf.on_interact = on_bookshelf_interact
        self.interactive_objects.append(bookshelf)
        self._library_bookshelf_obj = bookshelf

    def _setup_gym_entities(self):
        from entities.npc import NPC
        from entities.interactive_object import InteractiveObject

        spawn_x, spawn_y = self.tile_map.get_spawn_position()

        pe_teacher = NPC(
            x=spawn_x + 16, y=spawn_y - 16,
            npc_id="pe_teacher",
            dialogue_id="pe_teacher",
            properties={
                "direction": "down",
                "body_color": (80, 140, 80),
                "hair_color": (40, 30, 20),
            },
        )

        gm = self
        puzzle_ref = self.gym_puzzle

        def on_pe_teacher_interact(npc_self):
            if gm.puzzle_manager.get_state("gym") == PuzzleState.SOLVED:
                return {"type": "dialog", "dialogue_id": "pe_teacher", "dialogue_data": None}
            if gm.gym_puzzle.shooting_passed:
                if not gm.player.inventory.has_item("equipment_key"):
                    gm.player.inventory.add_item("equipment_key")
                    return {"type": "dialog", "dialogue_data": {
                        "default": [
                            {"speaker": "体育老师", "text": "不错不错！这把器材室钥匙给你。"},
                            {"speaker": "体育老师", "text": "器材室里那个旧记分牌，你留意一下上面的数字。"},
                        ]
                    }}
                return {"type": "dialog", "dialogue_id": "pe_teacher", "dialogue_data": None}
            gm._pending_gym_shooting = True
            dialogue_data = gm._load_dialogue("pe_teacher")
            return {
                "type": "dialog",
                "dialogue_data": dialogue_data,
                "start_key": "default",
            }

        pe_teacher.on_interact = on_pe_teacher_interact
        self.npcs.append(pe_teacher)

        shooting_station = InteractiveObject(
            x=spawn_x - 32, y=spawn_y - 16,
            width=16, height=16,
            interactive_type="mechanism",
            properties={
                "prompt_text": "投篮",
                "color": (180, 120, 60),
                "puzzle_id": "gym",
                "mechanism_text": "",
            },
        )

        def on_shooting_interact(obj):
            if gm.puzzle_manager.get_state("gym") == PuzzleState.SOLVED:
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "投篮挑战已经完成了。"}]
                }}
            if gm.gym_puzzle.shooting_passed:
                return {"type": "dialog", "dialogue_data": {
                    "default": [{"speaker": "", "text": "你已经通过投篮挑战了！"}]
                }}
            gm._active_puzzle = puzzle_ref
            gm.state = GameState.PUZZLE
            puzzle_ref.start_shooting(on_complete=gm._on_puzzle_complete)
            return None

        shooting_station.on_interact = on_shooting_interact
        self.interactive_objects.append(shooting_station)

        cabinet_obj = None
        scoreboard_obj = None
        for obj in self.interactive_objects:
            if hasattr(obj, 'properties'):
                obj_type = obj.properties.get("display_name", "")
                if obj_type == "器材柜":
                    cabinet_obj = obj
                elif obj_type == "记分牌":
                    scoreboard_obj = obj

        if cabinet_obj is not None:
            gm_ref = self

            def on_cabinet_interact(obj):
                if gm_ref.player.inventory.has_item("scoreboard_note"):
                    return {"type": "dialog", "dialogue_data": {
                        "default": [{"speaker": "", "text": "器材柜已经打开过了。"}]
                    }}
                if not gm_ref.player.inventory.has_item("equipment_key"):
                    return {"type": "dialog", "dialogue_data": {
                        "default": [{"speaker": "", "text": "器材柜锁着，需要钥匙才能打开。"}]
                    }}
                gm_ref.player.inventory.remove_item("equipment_key")
                gm_ref.player.inventory.add_item("scoreboard_note")
                return {"type": "dialog", "dialogue_data": {
                    "default": [
                        {"speaker": "", "text": "用器材室钥匙打开了柜子！"},
                        {"speaker": "", "text": "柜子里有一张便条：'将记分牌拨至1-9-0-3'。"},
                    ]
                }}

            cabinet_obj.on_interact = on_cabinet_interact
            cabinet_obj.interactive_type = "mechanism"
            cabinet_obj.properties["prompt_text"] = "查看器材柜"
            self._gym_equipment_cabinet_obj = cabinet_obj

        if scoreboard_obj is not None:
            gm_ref = self

            def on_scoreboard_interact(obj):
                if gm_ref.puzzle_manager.get_state("gym") == PuzzleState.SOLVED:
                    return {"type": "dialog", "dialogue_data": {
                        "default": [{"speaker": "", "text": "记分牌已经拨到正确位置了。"}]
                    }}
                if not gm_ref.player.inventory.has_item("scoreboard_note"):
                    return {"type": "dialog", "dialogue_data": {
                        "default": [{"speaker": "", "text": "记分牌上显示着一些数字，但看不太清楚……"}]
                    }}
                if gm_ref.gym_puzzle.scoreboard_opened:
                    return {"type": "dialog", "dialogue_data": {
                        "default": [{"speaker": "", "text": "记分牌已经拨到正确位置了。"}]
                    }}
                gm_ref._active_puzzle = gm_ref.gym_puzzle
                gm_ref.state = GameState.PUZZLE
                gm_ref.gym_puzzle.start_scoreboard(on_complete=gm_ref._on_puzzle_complete)
                return None

            scoreboard_obj.on_interact = on_scoreboard_interact
            scoreboard_obj.interactive_type = "mechanism"
            scoreboard_obj.properties["prompt_text"] = "拨动记分牌"
            self._gym_scoreboard_obj = scoreboard_obj

        self.puzzle_manager.discover("gym")

    def _on_puzzle_complete(self):
        puzzle = self._active_puzzle
        self._active_puzzle = None
        self.state = GameState.PLAYING
        # 解谜后自动存档
        self._auto_save()

        if puzzle is self.nanhulou_puzzle:
            if self.nanhulou_puzzle.secret_room_open and \
               self.puzzle_manager.get_state("nanhulou") != PuzzleState.SOLVED:
                self._start_bookshelf_animation()

        elif puzzle is self.library_puzzle:
            if self.library_puzzle.quiz_passed:
                self.player.inventory.add_item("special_book")
                self.player.inventory.add_item("call_number_note")
                self.state = GameState.DIALOG
                self.dialog_box.start(
                    {"default": [
                        {"speaker": "", "text": "全部答对！管理员递给你一本古旧典籍和一张索书号便签。"},
                        {"speaker": "", "text": "索书号便签上写着：'K291.5/Z3'。去2楼找到对应的书架放置书籍吧！"},
                    ]},
                    start_key="default",
                    on_complete=self._on_dialog_complete,
                    game_state=self._get_dialog_game_state(),
                )

        elif puzzle is self.boya_puzzle:
            if self.boya_puzzle.solved:
                self.puzzle_manager.solve("boya", self.player.inventory)
                self.state = GameState.DIALOG
                self.dialog_box.start(
                    {"default": [
                        {"speaker": "", "text": "地砖阵法破解！广场中央的雕塑缓缓移开了……"},
                        {"speaker": "", "text": "获得了桂花徽章碎片·肆！"},
                    ]},
                    start_key="default",
                    on_complete=self._on_dialog_complete,
                    game_state=self._get_dialog_game_state(),
                )

        elif puzzle is self.gym_puzzle:
            if self.gym_puzzle.scoreboard_opened and \
                 self.puzzle_manager.get_state("gym") != PuzzleState.SOLVED:
                self.puzzle_manager.solve("gym", self.player.inventory)
                self.state = GameState.DIALOG
                self.dialog_box.start(
                    {"default": [
                        {"speaker": "", "text": "数字正确！暗门缓缓开启……"},
                        {"speaker": "", "text": "获得了桂花徽章碎片·伍！"},
                    ]},
                    start_key="default",
                    on_complete=self._on_dialog_complete,
                    game_state=self._get_dialog_game_state(),
                )
            elif self.gym_puzzle.shooting_passed and not self.player.inventory.has_item("equipment_key"):
                self.player.inventory.add_item("equipment_key")
                self.state = GameState.DIALOG
                self.dialog_box.start(
                    {"default": [
                        {"speaker": "", "text": "投篮挑战成功！获得了器材室钥匙！"},
                        {"speaker": "", "text": "用钥匙打开器材柜，看看里面有什么……"},
                    ]},
                    start_key="default",
                    on_complete=self._on_dialog_complete,
                    game_state=self._get_dialog_game_state(),
                )

        elif puzzle is self.fountain_puzzle:
            if self.fountain_puzzle.solved:
                self.game_clock.dispel_realm()
                # 根据收集情况决定结局类型
                self._determine_ending_type()
                self.state = GameState.OUTRO
                self._outro_phase = 0
                self._outro_timer = 0.0
                self._outro_fade_alpha = 0

    def _start_bookshelf_animation(self):
        if self._nanhulou_bookshelf_obj is None:
            spawn_x, spawn_y = self.tile_map.get_spawn_position()
            self._add_secret_room_entrance(spawn_x, spawn_y)
            return
        self._nanhulou_bookshelf_animating = True
        self._nanhulou_bookshelf_anim_timer = 0.0
        self._nanhulou_bookshelf_base_x = self._nanhulou_bookshelf_obj.x

    def _trigger_nanhu_intro(self):
        intro_data = self._load_dialogue("nanhu_intro")
        if intro_data is None:
            intro_data = {
                "default": [
                    {"speaker": "", "text": "校车缓缓驶入南湖校区……"},
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
                if self.inventory_ui.pending_badge_reveal:
                    badge_id = self.inventory_ui.pending_badge_reveal
                    self.inventory_ui.pending_badge_reveal = None
                    self.dining_puzzle.reveal_badge()
                    self.state = GameState.PLAYING
                    badge_data = get_item_data(badge_id)
                    badge_name = badge_data.get("name", badge_id) if badge_data else badge_id
                    self.state = GameState.DIALOG
                    self.dialog_box.start(
                        {"default": [{"speaker": "", "text": f"获得了{badge_name}！桂花糕中竟然藏着这样的秘密……"}]},
                        start_key="default",
                        on_complete=self._on_dialog_complete,
                        game_state=self._get_dialog_game_state(),
                    )
                else:
                    self.state = GameState.PLAYING
            self.ui_manager.process_events(event)
            return

        if self.state == GameState.PUZZLE:
            if self._active_puzzle:
                self._active_puzzle.handle_event(event)
            self.ui_manager.process_events(event)
            return

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            pass  # pygame_gui按钮事件已由Menu模块替代

        if self.state == GameState.TITLE:
            if event.type == pygame.KEYDOWN:
                if not self._title_menu_active:
                    # 任意键进入菜单模式
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE,
                                     pygame.K_UP, pygame.K_DOWN,
                                     pygame.K_w, pygame.K_s):
                        self._title_menu_active = True
                        self._title_menu_index = 0
                        # 如果没有存档，跳过"继续游戏"
                        if not self.save_manager.has_any_save():
                            self._title_menu_items = ["开始游戏", "设置"]
                        else:
                            self._title_menu_items = ["开始游戏", "继续游戏", "设置"]
                else:
                    # 菜单导航
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self._title_menu_index = (self._title_menu_index - 1) % len(self._title_menu_items)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self._title_menu_index = (self._title_menu_index + 1) % len(self._title_menu_items)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_f):
                        self._title_menu_select()
                    elif event.key == pygame.K_ESCAPE:
                        self._title_menu_active = False

        elif self.state == GameState.PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PAUSED
                    self._create_pause_ui()
                elif event.key == pygame.K_f:
                    self._handle_interaction()
                elif event.key in (pygame.K_TAB, pygame.K_i):
                    self._open_inventory()
                elif event.key == pygame.K_m:
                    self.state = GameState.MAP_VIEW

        elif self.state == GameState.INTRO:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_f):
                    # 跳过当前阶段
                    self._intro_skip_current_phase()

        elif self.state == GameState.OUTRO:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_f):
                    # 跳过当前阶段或加速
                    self._outro_skip_current_phase()
                elif event.key == pygame.K_ESCAPE and self._outro_phase >= 2:
                    # 结局文字后可返回标题
                    self._return_to_title()

        elif self.state == GameState.PAUSED:
            menu_action = self.menu.handle_event(event)

            # 读档确认（返回tuple）
            if isinstance(menu_action, tuple) and menu_action[0] == "load_confirm":
                slot_id = menu_action[1]
                save_data = self.save_manager.load(slot_id)
                if save_data:
                    self.save_manager.apply_save_data(save_data, self)
                    self.menu.close()
                    self.state = GameState.PLAYING
                    self.ui_manager.clear_and_reset()

            elif menu_action == "continue":
                # 从标题画面进入的读档菜单，Esc返回标题
                if self.menu.current_menu == "title_load":
                    self.menu.close()
                    self.state = GameState.TITLE
                else:
                    self.menu.close()
                    self.state = GameState.PLAYING

            elif menu_action == "cancel_title_load":
                self.menu.close()
                self.state = GameState.TITLE

            elif menu_action == "inventory":
                self.menu.close()
                self._open_inventory()

            elif menu_action == "map":
                self.menu.close()
                self.state = GameState.MAP_VIEW

            elif menu_action == "open_save":
                save_infos = self.save_manager.get_all_save_info()
                self.menu.set_save_infos(save_infos)

            elif menu_action == "open_load":
                save_infos = self.save_manager.get_all_save_info()
                self.menu.set_save_infos(save_infos)

            elif menu_action == "open_settings":
                pass

            elif menu_action == "quit_title":
                self.save_manager.auto_save(self)
                self.menu.close()
                self._return_to_title()

            elif menu_action in ("auto_save", "slot_1", "slot_2"):
                # 存档槽位确认
                slot_map = {"auto_save": "auto", "slot_1": "slot_1", "slot_2": "slot_2"}
                slot_id = slot_map.get(menu_action)
                if slot_id:
                    if self.save_manager.save(slot_id, self):
                        self.menu.set_save_message("存档成功！")
                        save_infos = self.save_manager.get_all_save_info()
                        self.menu.set_save_infos(save_infos)
                    else:
                        self.menu.set_save_message("存档失败！")

        elif self.state == GameState.MAP_VIEW:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_m, pygame.K_ESCAPE, pygame.K_TAB):
                    self.state = GameState.PLAYING

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
            start_key = result.get("start_key", "default")

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
                start_key=start_key,
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
                    # 拾取关键道具时自动存档
                    if item_data and item_data.get("category") == "key_item":
                        self._auto_save()
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
            if mech_text:
                self.state = GameState.DIALOG
                self.dialog_box.start(
                    {"default": [{"speaker": "", "text": mech_text}]},
                    start_key="default",
                    on_complete=self._on_dialog_complete,
                    game_state=self._get_dialog_game_state(),
                )

    def _get_dialog_game_state(self):
        states_dict = {}
        for pid, pstate in self.puzzle_manager._states.items():
            states_dict[pid] = pstate.value
        inventory_items = []
        if self.player and self.player.inventory:
            inventory_items = [item.id for item in self.player.inventory.items]
        return {
            "puzzle_states": states_dict,
            "dialog_flags": self._dialog_flags,
            "inventory": inventory_items,
        }

    def _on_dialog_complete(self):
        if self.state != GameState.DIALOG:
            return
        if self._pending_library_quiz:
            self._pending_library_quiz = False
            # 注意：dialog_box.current_key 在 _end_dialogue() 中不会被重置，
            # 因此此处可以正确读取到对话结束时的分支 key（如 "start_quiz"）
            if self.dialog_box.current_key == "start_quiz":
                self._active_puzzle = self.library_puzzle
                if not self.library_puzzle.start(on_complete=self._on_puzzle_complete):
                    self._active_puzzle = None
                    self.state = GameState.PLAYING
                else:
                    self.state = GameState.PUZZLE
                return
        if self._pending_gym_shooting:
            self._pending_gym_shooting = False
            if self.dialog_box.current_key == "start_shooting":
                self._active_puzzle = self.gym_puzzle
                if not self.gym_puzzle.start_shooting(on_complete=self._on_puzzle_complete):
                    self._active_puzzle = None
                    self.state = GameState.PLAYING
                else:
                    self.state = GameState.PUZZLE
                return
        self.state = GameState.PLAYING

    def _create_pause_ui(self):
        self.menu.open("pause")
        save_infos = self.save_manager.get_all_save_info()
        self.menu.set_save_infos(save_infos)

    def update(self):
        dt = self.clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        self.ui_manager.update(dt)

        self.transition_manager.update(dt)

        if self.transition_manager.is_active:
            return

        # 累计游戏时间（存档用）
        if self.state == GameState.PLAYING:
            self.save_manager.update_play_time(dt)

        if self.state == GameState.TITLE:
            self.blink_timer += dt
            if self.blink_timer >= 0.8:
                self.blink_timer -= 0.8
                self.show_press_enter = not self.show_press_enter
            # Logo滑入动画
            self._title_anim_timer += dt
            if not self._title_logo_settled:
                self._title_logo_y = min(INTERNAL_HEIGHT // 2 - 40, self._title_logo_y + 60 * dt)
                if self._title_logo_y >= INTERNAL_HEIGHT // 2 - 40:
                    self._title_logo_y = INTERNAL_HEIGHT // 2 - 40
                    self._title_logo_settled = True

        elif self.state == GameState.INTRO:
            self._update_intro(dt)

        elif self.state == GameState.OUTRO:
            self._update_outro(dt)

        elif self.state == GameState.PLAYING:
            self.game_clock.update(dt)
            self._update_npc_visibility()

            if not self._tutorial_shown:
                self._tutorial_shown = True
                self._show_tutorial()
                return

            if self._realm_animating:
                self._realm_anim_timer += dt
                if self._realm_anim_timer >= self._realm_anim_duration:
                    self._realm_animating = False
                    self._realm_anim_timer = self._realm_anim_duration
                    self._on_realm_anim_complete()
                return

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

            # 更新小地图探索区域
            player_tile_x = int(self.player.x / TILE_SIZE)
            player_tile_y = int(self.player.y / TILE_SIZE)
            self.minimap.mark_explored(self.current_map_id, player_tile_x, player_tile_y)
            self.minimap.update(dt)

            if not self._realm_triggered and self.current_map_id == "main_campus":
                if not self.game_clock.is_realm_active():
                    self._check_realm_trigger()

            if self.game_clock.is_realm_active() and not self._realm_first_night_shown:
                if self.game_clock.is_night():
                    self._realm_first_night_shown = True
                    self._show_first_night_hint()

            if self._realm_hint_active:
                self._realm_hint_timer += dt
                if self._realm_hint_timer >= self._realm_hint_duration:
                    self._realm_hint_active = False

            if self._pending_nanhu_intro:
                self._pending_nanhu_intro = False
                self._trigger_nanhu_intro()

            if self.guizhong_puzzle.is_animating:
                was_badge_dropped = self.guizhong_puzzle.is_badge_dropped
                self.guizhong_puzzle.update(dt)
                if not was_badge_dropped and self.guizhong_puzzle.is_badge_dropped:
                    if self.current_map_id == "main_campus":
                        self._create_guizhong_badge_pickup()

            if self._nanhulou_bookshelf_animating and self._nanhulou_bookshelf_obj:
                self._nanhulou_bookshelf_anim_timer += dt
                progress = min(
                    self._nanhulou_bookshelf_anim_timer / self._nanhulou_bookshelf_anim_duration,
                    1.0,
                )
                self._nanhulou_bookshelf_obj.x = (
                    self._nanhulou_bookshelf_base_x + 32.0 * progress
                )
                if progress >= 1.0:
                    self._nanhulou_bookshelf_animating = False
                    if self._nanhulou_bookshelf_obj in self.interactive_objects:
                        self.interactive_objects.remove(self._nanhulou_bookshelf_obj)
                    self._nanhulou_bookshelf_obj = None
                    spawn_x, spawn_y = self.tile_map.get_spawn_position()
                    self._add_secret_room_entrance(spawn_x, spawn_y)
                    self.state = GameState.DIALOG
                    self.dialog_box.start(
                        {"default": [{"speaker": "", "text": "你注意到角落的书架缓缓移开了，里面似乎有一条暗道……"}]},
                        start_key="default",
                        on_complete=self._on_dialog_complete,
                        game_state=self._get_dialog_game_state(),
                    )

        elif self.state == GameState.DIALOG:
            self.dialog_box.update(dt)
            for npc in self.npcs:
                npc.update(dt)
            if not self.dialog_box.active:
                self._on_dialog_complete()

        elif self.state == GameState.INVENTORY:
            self.inventory_ui.update(dt)

        elif self.state == GameState.PAUSED:
            self.menu.update(dt)

        elif self.state == GameState.PUZZLE:
            if self._active_puzzle:
                self._active_puzzle.update(dt)

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
        elif self.state == GameState.INTRO:
            self._draw_intro()
        elif self.state == GameState.OUTRO:
            self._draw_outro()
        elif self.state == GameState.PLAYING:
            self._draw_game()
            self._draw_interaction_prompts()
        elif self.state == GameState.PAUSED:
            if self.menu.current_menu == "title_load":
                # 标题画面的读档菜单：显示标题背景+菜单
                self._draw_title()
            else:
                self._draw_game()
            self.menu.draw(self.internal_surface)
        elif self.state == GameState.DIALOG:
            self._draw_game()
            self.dialog_box.draw(self.internal_surface)
        elif self.state == GameState.INVENTORY:
            self._draw_game()
            self.inventory_ui.draw(self.internal_surface)
        elif self.state == GameState.PUZZLE:
            self._draw_game()
            if self._active_puzzle:
                self._active_puzzle.draw(self.internal_surface)
        elif self.state == GameState.MAP_VIEW:
            self._draw_map_view()

        self.transition_manager.draw(self.internal_surface)

        scaled = pygame.transform.scale(
            self.internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.screen.blit(scaled, (0, 0))

        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

    def _draw_title(self):
        self.internal_surface.fill(COLOR_TITLE_BG)

        # 装饰性粒子效果（模拟桂花飘落）
        self._draw_title_particles()

        # Logo滑入动画
        logo_y = int(self._title_logo_y)

        # 标题
        title_text = self.title_font.render("桂子山秘境探险", True, COLOR_TITLE_TEXT)
        title_rect = title_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=logo_y
        )
        self.internal_surface.blit(title_text, title_rect)

        # 副标题
        sub_text = self.info_font.render(
            "校园秘境探险", True, COLOR_WHITE
        )
        sub_rect = sub_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=logo_y + 20
        )
        self.internal_surface.blit(sub_text, sub_rect)

        if not self._title_menu_active:
            # 闪烁提示
            if self.show_press_enter:
                enter_text = self.info_font.render("按任意键开始", True, COLOR_WHITE)
                enter_rect = enter_text.get_rect(
                    centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2 + 50
                )
                self.internal_surface.blit(enter_text, enter_rect)
        else:
            # 菜单项
            menu_start_y = INTERNAL_HEIGHT // 2 + 30
            for i, item in enumerate(self._title_menu_items):
                is_selected = (i == self._title_menu_index)
                color = COLOR_TITLE_TEXT if is_selected else (150, 150, 170)
                text = self.info_font.render(item, True, color)
                text_rect = text.get_rect(
                    centerx=INTERNAL_WIDTH // 2, centery=menu_start_y + i * 18
                )
                self.internal_surface.blit(text, text_rect)
                # 选中指示器（用绘制三角形代替字体字符，避免Zpix不支持▶）
                if is_selected:
                    ind_x = text_rect.left - 8
                    ind_y = text_rect.centery
                    pygame.draw.polygon(self.internal_surface, COLOR_TITLE_TEXT, [
                        (ind_x, ind_y - 4),
                        (ind_x + 5, ind_y),
                        (ind_x, ind_y + 4),
                    ])

    def _draw_title_particles(self):
        """绘制标题画面的桂花飘落粒子效果"""
        t = self._title_anim_timer
        for i in range(8):
            # 每个粒子有不同的速度和起始位置
            seed_x = (i * 67 + 23) % INTERNAL_WIDTH
            speed = 15 + (i * 7) % 10
            x = (seed_x + t * speed * (0.5 + (i % 3) * 0.3)) % INTERNAL_WIDTH
            y = (t * speed + i * 40) % INTERNAL_HEIGHT
            # 小桂花点
            alpha = 120 + int(40 * ((t * 2 + i) % 1.0))
            color = (255, 220, 100, min(255, alpha))
            particle_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (1, 1), 1)
            self.internal_surface.blit(particle_surf, (int(x), int(y)))

    def _draw_game(self):
        self.tile_map.draw(self.internal_surface, self.camera)

        if self.current_map_id == "main_campus" and self.guizhong_puzzle.tree_positions:
            self.guizhong_puzzle.draw(
                self.internal_surface, self.camera, self.game_clock.is_night()
            )

        for obj in self.interactive_objects:
            obj.draw(self.internal_surface, self.camera)

        for npc in self.npcs:
            npc.draw(self.internal_surface, self.camera)

        self.player.draw(self.internal_surface, self.camera)

        self._draw_day_night_overlay()

        if self._realm_animating:
            self._draw_realm_animation()

        if self._realm_hint_active:
            self._draw_realm_hint()

        # 使用独立HUD模块绘制
        self.hud.draw(
            self.internal_surface, self.player,
            self.puzzle_manager, self.game_clock,
        )

        # 绘制小地图
        self.minimap.draw(
            self.internal_surface, self.tile_map,
            self.current_map_id, self.player, self.camera,
        )

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
            elif self._nearby_interactable is self._guizhong_tree_obj:
                self._draw_guizhong_tree_prompt()
            else:
                self._nearby_interactable.draw_prompt(
                    self.internal_surface, self.camera, self.info_font
                )

    def _draw_guizhong_tree_prompt(self):
        obj = self._guizhong_tree_obj
        if obj is None:
            return
        state = self.guizhong_puzzle.state
        if state == GuizhongPuzzle.STATE_IDLE:
            prompt = "按 F 查看"
        elif state == GuizhongPuzzle.STATE_EXAMINED:
            prompt = "按 F 摇树"
        else:
            return
        sx, sy = self.camera.apply(obj.center_x, obj.y - 4)
        text_surf = self.info_font.render(prompt, True, (255, 255, 255))
        text_rect = text_surf.get_rect(centerx=int(sx), bottom=int(sy))
        bg_rect = text_rect.inflate(6, 4)
        bg_surf = pygame.Surface(
            (bg_rect.width, bg_rect.height), pygame.SRCALPHA
        )
        bg_surf.fill((0, 0, 0, 160))
        self.internal_surface.blit(bg_surf, bg_rect.topleft)
        self.internal_surface.blit(text_surf, text_rect)

    def _draw_day_night_overlay(self):
        overlay_color = self.game_clock.get_overlay_color()
        if overlay_color[3] == 0:
            return
        self._overlay_surface.fill(overlay_color)
        self.internal_surface.blit(self._overlay_surface, (0, 0))

        if self.game_clock.is_night() and self.current_map_id == "main_campus":
            self._draw_night_lights()

    def _draw_night_lights(self):
        is_awakened = self.game_clock.is_realm_awakened()
        light_radius = 24
        light_surf = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
        if is_awakened:
            light_color = (150, 255, 160)
        else:
            light_color = (255, 240, 180)
        for r in range(light_radius, 0, -1):
            alpha = int(40 * (1 - r / light_radius))
            pygame.draw.circle(light_surf, (*light_color, alpha), (light_radius, light_radius), r)
        for obj in self.interactive_objects:
            if hasattr(obj, 'properties'):
                itype = obj.properties.get("interactive_type", "")
                if itype in ("examine", "mechanism"):
                    sx, sy = self.camera.apply(obj.center_x, obj.center_y)
                    self.internal_surface.blit(
                        light_surf,
                        (int(sx) - light_radius, int(sy) - light_radius),
                    )

        if is_awakened:
            self._draw_realm_glow_points()

    def _draw_realm_glow_points(self):
        glow_radius = 16
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        for r in range(glow_radius, 0, -1):
            alpha = int(25 * (1 - r / glow_radius))
            pygame.draw.circle(glow_surf, (100, 220, 120, alpha), (glow_radius, glow_radius), r)

        for npc in self.npcs:
            if not npc.visible:
                continue
            sx, sy = self.camera.apply(npc.x, npc.y - npc.height / 2)
            self.internal_surface.blit(
                glow_surf,
                (int(sx) - glow_radius, int(sy) - glow_radius),
            )

        for obj in self.interactive_objects:
            if hasattr(obj, 'properties'):
                itype = obj.properties.get("interactive_type", "")
                if itype in ("dialog", "pickup"):
                    sx, sy = self.camera.apply(obj.center_x, obj.center_y)
                    self.internal_surface.blit(
                        glow_surf,
                        (int(sx) - glow_radius, int(sy) - glow_radius),
                    )

    def _update_npc_visibility(self):
        for npc in self.npcs:
            if hasattr(npc, 'npc_id'):
                should_show = self.game_clock.should_npc_appear(npc.npc_id)
                npc.visible = should_show

    def _check_realm_trigger(self):
        px = self.player.x / TILE_SIZE
        py = self.player.y / TILE_SIZE
        if 55 <= px <= 65 and 37 <= py <= 42:
            self._trigger_realm_descent()

    def _trigger_realm_descent(self):
        self._realm_triggered = True
        self._realm_animating = True
        self._realm_anim_timer = 0.0

    def _on_realm_anim_complete(self):
        self.game_clock.activate_realm()
        self.state = GameState.DIALOG
        self.dialog_box.start(
            {"default": [
                {"speaker": "秘境守护者", "text": "你感受到了吗？桂子山的秘境已经苏醒。"},
                {"speaker": "秘境守护者", "text": "七处校园地标被秘境力量笼罩，每处都隐藏着一枚桂花徽章碎片。"},
                {"speaker": "秘境守护者", "text": "唯有集齐全部七枚碎片，才能解开秘境封印，回到现实。"},
                {"speaker": "秘境守护者", "text": "去探索吧……白日里秘境蛰伏，入夜后力量觉醒，隐藏的线索才会显现。"},
            ]},
            start_key="default",
            on_complete=self._on_realm_dialog_complete,
            game_state=self._get_dialog_game_state(),
        )

    def _on_realm_dialog_complete(self):
        if self.state != GameState.DIALOG:
            return
        self.state = GameState.PLAYING
        self._realm_hint_active = True
        self._realm_hint_timer = 0.0

    def _show_tutorial(self):
        self.state = GameState.DIALOG
        tutorial_data = {
            "default": [
                {"speaker": "", "text": "欢迎来到桂子山！这里有一些基本操作提示："},
                {"speaker": "", "text": "WASD 或 方向键：移动角色"},
                {"speaker": "", "text": "按住 Shift：冲刺（消耗体力）"},
                {"speaker": "", "text": "靠近物体或NPC时，按 F 键互动"},
                {"speaker": "", "text": "按 Esc 键暂停游戏"},
                {"speaker": "", "text": "探索校园，解开谜题，收集七枚徽章碎片吧！"},
            ]
        }
        self.dialog_box.start(
            tutorial_data,
            start_key="default",
            on_complete=self._on_dialog_complete,
            game_state=self._get_dialog_game_state(),
        )

    def _show_first_night_hint(self):
        self.state = GameState.DIALOG
        self.dialog_box.start(
            {"default": [
                {"speaker": "秘境守护者", "text": "夜幕降临，秘境觉醒……去桂中路看看吧。"},
            ]},
            start_key="default",
            on_complete=self._on_dialog_complete,
            game_state=self._get_dialog_game_state(),
        )

    def _draw_realm_animation(self):
        progress = self._realm_anim_timer / self._realm_anim_duration
        anim_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)

        if progress < 0.33:
            green_alpha = int(180 * (progress / 0.33))
            anim_surf.fill((60, 180, 80, green_alpha))
        elif progress < 0.5:
            white_alpha = int(255 * ((progress - 0.33) / 0.17))
            anim_surf.fill((255, 255, 255, white_alpha))
        elif progress < 0.75:
            white_alpha = int(255 * (1 - (progress - 0.5) / 0.25))
            anim_surf.fill((255, 255, 255, white_alpha))
        else:
            pass

        self.internal_surface.blit(anim_surf, (0, 0))

    def _draw_realm_hint(self):
        if self._realm_hint_timer >= self._realm_hint_duration:
            return
        fade_in = min(1.0, self._realm_hint_timer / 0.5)
        fade_out_start = self._realm_hint_duration - 1.0
        fade_out = 1.0
        if self._realm_hint_timer > fade_out_start:
            fade_out = max(0.0, 1.0 - (self._realm_hint_timer - fade_out_start) / 1.0)
        alpha = int(220 * fade_in * fade_out)

        hint_text = self.info_font.render("探索校园，寻找七个被秘境笼罩的地点", True, COLOR_WHITE)
        text_rect = hint_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2 + 40
        )
        bg_rect = text_rect.inflate(12, 8)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, min(180, alpha)))
        self.internal_surface.blit(bg_surf, bg_rect.topleft)

        hint_surf = pygame.Surface(hint_text.get_size(), pygame.SRCALPHA)
        hint_surf.blit(hint_text, (0, 0))
        hint_surf.set_alpha(alpha)
        self.internal_surface.blit(hint_surf, text_rect)

    def _draw_map_view(self):
        """绘制全局地图视图（全屏，已探索区域清晰，未探索区域迷雾）"""
        self.internal_surface.fill((20, 20, 30))

        # 标题
        title = self.title_font.render("校园地图", True, COLOR_TITLE_TEXT)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=15,
        )
        self.internal_surface.blit(title, title_rect)

        # 使用minimap的draw_fullscreen绘制全屏地图
        all_maps = {}
        for map_id, tile_map in self._map_cache.items():
            all_maps[map_id] = tile_map

        self.minimap.draw_fullscreen(
            self.internal_surface, self.tile_map,
            self.current_map_id, self.player, all_maps,
        )

        # 提示
        hint = self.info_font.render("按 M 或 Esc 返回游戏", True, (180, 180, 200))
        hint_rect = hint.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT - 10,
        )
        self.internal_surface.blit(hint, hint_rect)

    def _auto_save(self):
        """触发自动存档"""
        self.save_manager.auto_save(self)

    def _title_menu_select(self):
        """标题画面菜单选择"""
        selected = self._title_menu_items[self._title_menu_index]
        if selected == "开始游戏":
            self._start_intro()
        elif selected == "继续游戏":
            if self.save_manager.has_any_save():
                self.menu.open("title_load")
                save_infos = self.save_manager.get_all_save_info()
                self.menu.set_save_infos(save_infos)
                self.state = GameState.PAUSED
        elif selected == "设置":
            self.menu.open("settings")
            self.state = GameState.PAUSED

    def _start_intro(self):
        """开始开场动画"""
        self.state = GameState.INTRO
        self._intro_phase = 0
        self._intro_timer = 0.0
        self._intro_text_alpha = 0
        self._intro_fade_alpha = 255
        self.ui_manager.clear_and_reset()

    def _update_intro(self, dt):
        """更新开场动画"""
        self._intro_timer += dt

        if self._intro_phase == 0:
            # 阶段0：黑屏 + 开场文字淡入
            self._intro_text_alpha = min(255, int(self._intro_timer * 120))
            if self._intro_timer > 3.5:
                self._intro_phase = 1
                self._intro_timer = 0.0
                self._intro_fade_alpha = 255
                self._intro_player_y = INTERNAL_HEIGHT + 20  # 从画面下方开始

        elif self._intro_phase == 1:
            # 阶段1：俯视角校门场景，角色从下往上走进校园
            self._intro_fade_alpha = max(0, int(255 - self._intro_timer * 180))
            # 角色从画面下方走到中间偏上位置
            target_y = INTERNAL_HEIGHT // 2 - 20
            speed = 50  # 像素/秒
            self._intro_player_y = max(target_y, self._intro_player_y - speed * dt)
            if self._intro_timer > 4.5:
                self._intro_phase = 2
                self._intro_timer = 0.0

        elif self._intro_phase == 2:
            # 阶段2：微弱绿光暗示 + 旁白
            if self._intro_timer > 3.0:
                self._intro_phase = 3
                self._intro_timer = 0.0

        elif self._intro_phase == 3:
            # 阶段3：淡出过渡到游戏
            self._intro_fade_alpha = min(255, int(self._intro_timer * 200))
            if self._intro_timer > 1.5:
                self._finish_intro()

    def _intro_skip_current_phase(self):
        """跳过当前开场动画阶段"""
        if self._intro_phase == 0:
            self._intro_phase = 1
            self._intro_timer = 0.0
            self._intro_fade_alpha = 255
            self._intro_player_y = INTERNAL_HEIGHT + 20
        elif self._intro_phase == 1:
            self._intro_phase = 2
            self._intro_timer = 0.0
        elif self._intro_phase == 2:
            self._intro_phase = 3
            self._intro_timer = 0.0
        elif self._intro_phase == 3:
            self._finish_intro()

    def _finish_intro(self):
        """开场动画结束，进入游戏（秘境由玩家走到桂中路时自然触发）"""
        self.state = GameState.PLAYING

    def _draw_intro(self):
        """绘制开场动画"""
        self.internal_surface.fill(COLOR_BLACK)

        if self._intro_phase == 0:
            self._draw_intro_text_phase()

        elif self._intro_phase == 1:
            self._draw_intro_campus_scene()
            # 淡入效果
            if self._intro_fade_alpha > 0:
                fade_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
                fade_surf.fill((0, 0, 0, self._intro_fade_alpha))
                self.internal_surface.blit(fade_surf, (0, 0))

        elif self._intro_phase == 2:
            self._draw_intro_campus_scene()
            self._draw_intro_hint_effect()

        elif self._intro_phase == 3:
            self._draw_intro_campus_scene()
            # 淡出到黑屏
            if self._intro_fade_alpha > 0:
                fade_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
                fade_surf.fill((0, 0, 0, self._intro_fade_alpha))
                self.internal_surface.blit(fade_surf, (0, 0))

    def _draw_intro_text_phase(self):
        """绘制开场文字阶段"""
        texts = [
            "九月，桂花飘香的季节……",
            "你作为一名新生，第一次踏入桂子山校园。",
        ]
        y_offset = INTERNAL_HEIGHT // 2 - 15
        for i, text in enumerate(texts):
            alpha = max(0, min(255, self._intro_text_alpha - i * 50))
            text_surf = self.info_font.render(text, True, COLOR_WHITE)
            text_surf.set_alpha(alpha)
            text_rect = text_surf.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=y_offset + i * 20
            )
            self.internal_surface.blit(text_surf, text_rect)

    def _draw_intro_campus_scene(self):
        """绘制开场动画中的俯视角校门场景"""
        surf = self.internal_surface
        cx = INTERNAL_WIDTH // 2

        # === 地面：草地 ===
        surf.fill((72, 112, 56))

        # 草地纹理变化
        for y in range(0, INTERNAL_HEIGHT, 4):
            for x in range(0, INTERNAL_WIDTH, 8):
                seed = (x * 7 + y * 13) % 37
                if seed < 8:
                    shade = (68 + seed, 108 + seed, 52 + seed)
                    pygame.draw.rect(surf, shade, (x, y, 8, 4))

        # === 道路（从画面下方延伸到上方，角色沿此路走进） ===
        road_w = 36
        road_color = (170, 155, 130)
        road_edge = (140, 125, 100)
        # 主道路
        pygame.draw.rect(surf, road_color, (cx - road_w // 2, 0, road_w, INTERNAL_HEIGHT))
        # 道路边线
        pygame.draw.line(surf, road_edge, (cx - road_w // 2, 0), (cx - road_w // 2, INTERNAL_HEIGHT), 1)
        pygame.draw.line(surf, road_edge, (cx + road_w // 2, 0), (cx + road_w // 2, INTERNAL_HEIGHT), 1)
        # 道路中线（虚线）
        for y in range(0, INTERNAL_HEIGHT, 12):
            pygame.draw.rect(surf, (190, 175, 150), (cx - 1, y, 2, 6))

        # === 校门牌坊（画面上方） ===
        gate_y = 40
        # 左柱
        pygame.draw.rect(surf, (170, 160, 140), (cx - 28, gate_y, 8, 30))
        pygame.draw.rect(surf, (150, 140, 120), (cx - 28, gate_y, 8, 30), 1)
        # 右柱
        pygame.draw.rect(surf, (170, 160, 140), (cx + 20, gate_y, 8, 30))
        pygame.draw.rect(surf, (150, 140, 120), (cx + 20, gate_y, 8, 30), 1)
        # 横梁
        pygame.draw.rect(surf, (155, 140, 115), (cx - 30, gate_y - 4, 60, 6))
        pygame.draw.rect(surf, (135, 120, 95), (cx - 30, gate_y - 4, 60, 6), 1)
        # 顶部装饰
        pygame.draw.rect(surf, (145, 130, 105), (cx - 32, gate_y - 8, 64, 5))
        # 校名（简化为文字）
        name_surf = self.info_font.render("桂子山", True, (200, 180, 140))
        name_rect = name_surf.get_rect(centerx=cx, centery=gate_y + 12)
        surf.blit(name_surf, name_rect)

        # === 桂花树（使用精灵或手绘） ===
        tree_positions = [
            (cx - 60, 80), (cx + 60, 80),   # 校门两侧
            (cx - 80, 160), (cx + 80, 160),  # 道路两侧远处
            (cx - 55, 200), (cx + 55, 200),  # 道路两侧近处
        ]
        # 尝试加载桂花树精灵
        tree_sprite = self._load_intro_sprite("osmanthus_tree.png")
        tree_glow_sprite = self._load_intro_sprite("osmanthus_tree_glow.png")

        for i, (tx, ty) in enumerate(tree_positions):
            if tree_sprite is not None:
                # 使用精灵
                sprite_w = tree_sprite.get_width()
                sprite_h = tree_sprite.get_height()
                # 底部对齐到树根位置
                surf.blit(tree_sprite, (tx - sprite_w // 2, ty - sprite_h))
            else:
                # 降级：手绘桂花树
                # 树干
                pygame.draw.rect(surf, (100, 70, 30), (tx - 2, ty - 20, 4, 20))
                # 树冠
                pygame.draw.circle(surf, (55, 130, 45), (tx, ty - 25), 11)
                pygame.draw.circle(surf, (65, 145, 55), (tx - 3, ty - 22), 8)
                pygame.draw.circle(surf, (65, 145, 55), (tx + 3, ty - 22), 8)
                # 桂花点
                for j in range(6):
                    fx = tx + ((j * 7 + 3 + i * 5) % 19 - 9)
                    fy = ty - 25 + ((j * 11 + 5 + i * 3) % 19 - 9)
                    pygame.draw.circle(surf, (255, 220, 80), (fx, fy), 1)

        # === 桂花飘落粒子 ===
        self._draw_intro_petals()

        # === 玩家（使用精灵表，从下往上走） ===
        player_x = cx
        player_y = int(self._intro_player_y)
        self._draw_intro_player(surf, player_x, player_y)

    def _load_intro_sprite(self, filename):
        """加载开场动画用的精灵（带缓存）"""
        if not hasattr(self, '_intro_sprite_cache'):
            self._intro_sprite_cache = {}
        if filename in self._intro_sprite_cache:
            return self._intro_sprite_cache[filename]
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "assets", "sprites", filename)
        if os.path.exists(path):
            sprite = pygame.image.load(path).convert_alpha()
            self._intro_sprite_cache[filename] = sprite
            return sprite
        self._intro_sprite_cache[filename] = None
        return None

    def _draw_intro_player(self, surf, px, py):
        """绘制开场动画中的玩家（使用精灵表）"""
        # 尝试加载玩家精灵表
        from player.player import Player
        Player._load_sprites()
        sprite_sheet = Player._sprite_sheet

        if sprite_sheet is not None:
            # 使用精灵表：朝上方向（row=3），根据时间选择动画帧
            row = 3  # up direction
            frame = int(self._intro_timer * 4) % 4  # 行走动画
            src_rect = pygame.Rect(
                frame * 16, row * 24,
                16, 24,
            )
            # 精灵底部对齐到角色脚底位置
            surf.blit(sprite_sheet, (px - 8, py - 24), src_rect)
        else:
            # 降级：手绘像素角色（朝上）
            # 身体
            pygame.draw.rect(surf, (80, 120, 200), (px - 4, py - 18, 8, 10))
            # 头
            pygame.draw.rect(surf, (240, 210, 180), (px - 3, py - 24, 6, 6))
            # 头发
            pygame.draw.rect(surf, (60, 40, 20), (px - 3, py - 25, 6, 3))
            # 腿（行走动画）
            frame = int(self._intro_timer * 4) % 4
            if frame in (1, 3):
                offset = 1 if frame == 1 else -1
                pygame.draw.rect(surf, (60, 80, 160), (px - 3, py - 8 + offset, 2, 4))
                pygame.draw.rect(surf, (60, 80, 160), (px + 1, py - 8 - offset, 2, 4))
            else:
                pygame.draw.rect(surf, (60, 80, 160), (px - 3, py - 8, 2, 4))
                pygame.draw.rect(surf, (60, 80, 160), (px + 1, py - 8, 2, 4))

    def _draw_intro_petals(self):
        """绘制开场动画中的桂花飘落粒子"""
        t = self._intro_timer + getattr(self, '_intro_total_time', 0)
        for i in range(12):
            seed_x = (i * 67 + 23) % INTERNAL_WIDTH
            speed = 12 + (i * 7) % 8
            drift = 8 * math.sin(t * 1.5 + i * 0.7)
            x = (seed_x + drift + t * speed * 0.3) % INTERNAL_WIDTH
            y = (t * speed + i * 30) % INTERNAL_HEIGHT
            # 桂花小点
            alpha = 160 + int(40 * math.sin(t * 2 + i))
            color = (255, 220, 80, min(255, alpha))
            petal_surf = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(petal_surf, color, (1, 1), 1)
            self.internal_surface.blit(petal_surf, (int(x), int(y)))

    def _draw_intro_hint_effect(self):
        """绘制开场动画阶段2：微弱绿光暗示效果"""
        progress = self._intro_timer / 3.0

        # 极淡的绿色脉冲（秘境暗示）
        if progress < 0.6:
            # 绿光在远处桂花树上微微闪烁
            pulse = 0.5 + 0.5 * math.sin(self._intro_timer * 3)
            green_alpha = int(25 * pulse)  # 非常淡
            hint_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
            # 只在树的位置附近添加绿光
            cx = INTERNAL_WIDTH // 2
            for tx in [cx - 60, cx + 60]:
                glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (80, 200, 80, green_alpha), (15, 15), 15)
                hint_surf.blit(glow_surf, (tx - 15, 65))
            self.internal_surface.blit(hint_surf, (0, 0))

        # 旁白文字
        if progress > 0.3:
            text_alpha = min(255, int((progress - 0.3) * 300))
            hint_text = self.info_font.render("不知为何，你感到一阵莫名的悸动……", True, (200, 230, 200))
            hint_text.set_alpha(text_alpha)
            hint_rect = hint_text.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT - 25
            )
            # 文字背景
            bg_rect = hint_rect.inflate(10, 6)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, min(180, text_alpha)))
            self.internal_surface.blit(bg_surf, bg_rect.topleft)
            self.internal_surface.blit(hint_text, hint_rect)

    def _determine_ending_type(self):
        """根据游戏表现决定结局类型"""
        # 普通结局：正常通关
        # 好结局：在3天内通关
        # 真结局：在2天内通关且收集了所有道具
        day = self.game_clock.day_count
        item_count = len(self.player.inventory.items)

        if day <= 2 and item_count >= 14:
            self._outro_ending_type = "true"
        elif day <= 3:
            self._outro_ending_type = "good"
        else:
            self._outro_ending_type = "normal"

    def _update_outro(self, dt):
        """更新结局动画"""
        self._outro_timer += dt

        if self._outro_phase == 0:
            # 阶段0：七徽归位光芒
            self._outro_fade_alpha = min(255, int(self._outro_timer * 100))
            if self._outro_timer > 3.0:
                self._outro_phase = 1
                self._outro_timer = 0.0

        elif self._outro_phase == 1:
            # 阶段1：秘境消散
            self._outro_fade_alpha = max(0, int(255 - self._outro_timer * 80))
            if self._outro_timer > 4.0:
                self._outro_phase = 2
                self._outro_timer = 0.0
                self._outro_text_shown = False

        elif self._outro_phase == 2:
            # 阶段2：结局文字
            self._outro_text_shown = True
            if self._outro_timer > 5.0:
                self._outro_phase = 3
                self._outro_timer = 0.0

        elif self._outro_phase == 3:
            # 阶段3：制作组
            if self._outro_timer > 5.0:
                pass  # 等待玩家按键返回标题

    def _outro_skip_current_phase(self):
        """跳过当前结局动画阶段"""
        if self._outro_phase == 0:
            self._outro_phase = 1
            self._outro_timer = 0.0
        elif self._outro_phase == 1:
            self._outro_phase = 2
            self._outro_timer = 0.0
            self._outro_text_shown = True
        elif self._outro_phase == 2:
            self._outro_phase = 3
            self._outro_timer = 0.0
        elif self._outro_phase == 3:
            self._return_to_title()

    def _draw_outro(self):
        """绘制结局动画"""
        self.internal_surface.fill(COLOR_BLACK)

        if self._outro_phase == 0:
            # 七徽归位光芒
            progress = self._outro_timer / 3.0
            # 中心光芒
            cx, cy = INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2
            for r in range(60, 0, -5):
                alpha = int(min(255, progress * 200) * (1 - r / 60))
                glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 220, 100, alpha), (r, r), r)
                self.internal_surface.blit(glow_surf, (cx - r, cy - r))
            # 七枚徽章环绕
            for i in range(7):
                angle = (i / 7) * 360 + self._outro_timer * 60
                rad = math.radians(angle)
                bx = cx + int(40 * math.cos(rad))
                by = cy + int(40 * math.sin(rad))
                pygame.draw.circle(self.internal_surface, (255, 200, 50), (bx, by), 4)
                pygame.draw.circle(self.internal_surface, (255, 240, 150), (bx, by), 2)
            # 文字
            if progress > 0.5:
                text_alpha = min(255, int((progress - 0.5) * 2 * 255))
                text = self.title_font.render("七徽归位，封印解除", True, COLOR_TITLE_TEXT)
                text.set_alpha(text_alpha)
                text_rect = text.get_rect(centerx=cx, centery=cy + 60)
                self.internal_surface.blit(text, text_rect)

        elif self._outro_phase == 1:
            # 秘境消散
            # 先画游戏场景（简化版）
            self.internal_surface.fill((40, 80, 40))
            # 绿色消散效果
            if self._outro_fade_alpha > 0:
                fade_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
                fade_surf.fill((60, 180, 80, self._outro_fade_alpha))
                self.internal_surface.blit(fade_surf, (0, 0))
            # 消散文字
            if self._outro_timer > 1.0:
                text_alpha = min(255, int((self._outro_timer - 1.0) * 150))
                text = self.info_font.render("秘境之力缓缓消散……桂子山重归现实。", True, COLOR_WHITE)
                text.set_alpha(text_alpha)
                text_rect = text.get_rect(
                    centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT // 2
                )
                self.internal_surface.blit(text, text_rect)

        elif self._outro_phase == 2:
            # 结局文字
            self._draw_outro_ending_text()

        elif self._outro_phase == 3:
            # 制作组
            self.internal_surface.fill(COLOR_BLACK)
            texts = [
                "桂子山秘境探险",
                "",
                "制作组",
                "",
                "策划 · 程序 · 美术",
                "",
                "感谢游玩！",
                "",
                "按 Esc 返回标题",
            ]
            y = INTERNAL_HEIGHT // 2 - 60
            for text in texts:
                if text:
                    t_surf = self.info_font.render(text, True, COLOR_WHITE)
                    t_rect = t_surf.get_rect(centerx=INTERNAL_WIDTH // 2, centery=y)
                    self.internal_surface.blit(t_surf, t_rect)
                y += 14

    def _draw_outro_ending_text(self):
        """绘制结局差异文字"""
        self.internal_surface.fill((20, 20, 40))

        if self._outro_ending_type == "true":
            title = "真结局·桂花永绽"
            lines = [
                "七枚徽章碎片合而为一，绽放出璀璨的金色光芒。",
                "秘境守护者微笑着点了点头：",
                "「你不仅解开了封印，更理解了桂子山的真谛。」",
                "「桂花的芬芳，将永远守护这片校园。」",
                "金色的桂花在校园中永远绽放，",
                "桂子山迎来了最美好的秋天。",
            ]
        elif self._outro_ending_type == "good":
            title = "好结局·秋日重归"
            lines = [
                "七枚徽章碎片归位，秘境的力量逐渐消散。",
                "秘境守护者轻声说道：",
                "「你做得很好，桂子山恢复了平静。」",
                "「但秘境的痕迹，或许永远不会完全消失……」",
                "校园恢复了往日的宁静，",
                "只是偶尔，桂花树下似乎还有微光闪烁。",
            ]
        else:
            title = "普通结局·秘境消散"
            lines = [
                "七枚徽章碎片归位，秘境的力量消散了。",
                "校园恢复了正常，一切仿佛从未发生。",
                "但你知道，那段秘境中的经历，",
                "将永远铭刻在你的记忆中。",
                "桂子山的秋天，依然美丽如初。",
            ]

        # 标题
        title_surf = self.title_font.render(title, True, COLOR_TITLE_TEXT)
        title_rect = title_surf.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=30
        )
        self.internal_surface.blit(title_surf, title_rect)

        # 分隔线
        pygame.draw.line(self.internal_surface, (100, 100, 140),
                         (INTERNAL_WIDTH // 4, 48),
                         (3 * INTERNAL_WIDTH // 4, 48), 1)

        # 文字逐行显示
        y = 60
        for i, line in enumerate(lines):
            # 逐行延迟显示
            line_delay = i * 0.6
            if self._outro_timer > line_delay:
                alpha = min(255, int((self._outro_timer - line_delay) * 200))
                line_surf = self.info_font.render(line, True, COLOR_WHITE)
                line_surf.set_alpha(alpha)
                line_rect = line_surf.get_rect(
                    centerx=INTERNAL_WIDTH // 2, centery=y
                )
                self.internal_surface.blit(line_surf, line_rect)
            y += 16

        # 提示
        if self._outro_timer > len(lines) * 0.6 + 1.0:
            hint = self.info_font.render("按 回车键 继续", True, (150, 150, 170))
            hint_rect = hint.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT - 15
            )
            self.internal_surface.blit(hint, hint_rect)

    def _return_to_title(self):
        """返回标题画面"""
        self.state = GameState.TITLE
        self._title_menu_active = False
        self._title_menu_index = 0
        self._title_logo_settled = False
        self._title_logo_y = -30
        self._title_anim_timer = 0.0
        # 重置游戏状态
        self._reset_game_state()

    def _reset_game_state(self):
        """重置游戏状态（用于新游戏）"""
        self.current_map_id = "main_campus"
        tmx_path = self._get_tmx_path("main_campus")
        self.tile_map = TileMap(tmx_path)
        spawn_x, spawn_y = self.tile_map.get_spawn_position()
        self.player = Player(spawn_x, spawn_y)
        self.camera = Camera(self.tile_map.width, self.tile_map.height)
        self.camera.update(self.player.x, self.player.y - PLAYER_HEIGHT / 2)

        self.interactive_objects = list(self.tile_map.interactive_objects)
        self.npcs = list(self.tile_map.npcs)
        self.triggers = list(self.tile_map.triggers)

        self._setup_test_entities()
        self._update_npc_visibility()

        self.puzzle_manager = PuzzleManager()
        self.guizhong_puzzle = GuizhongPuzzle(self.puzzle_manager, self.player.inventory)
        self.nanhulou_puzzle = NanhulouPuzzle(self.puzzle_manager, self.player.inventory)
        self.dining_puzzle = DiningPuzzle(self.puzzle_manager, self.player.inventory)
        self.library_puzzle = LibraryPuzzle(self.puzzle_manager, self.player.inventory)
        self.boya_puzzle = BoyaPuzzle(self.puzzle_manager, self.player.inventory)
        self.gym_puzzle = GymPuzzle(self.puzzle_manager, self.player.inventory)
        self.fountain_puzzle = FountainPuzzle(self.puzzle_manager, self.player.inventory)

        self.game_clock = GameClock()
        self._dialog_flags = {}
        self._realm_triggered = False
        self._realm_animating = False
        self._realm_first_night_shown = False
        self._tutorial_shown = False
        self._visited_nanhu = False
        self._pending_nanhu_intro = False
        self._active_puzzle = None
        self._map_cache = {"main_campus": self.tile_map}
