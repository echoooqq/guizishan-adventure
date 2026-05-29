import pygame
import sys
import os
import math
import random

from player import Player, Camera
from world import MainWorld, NanhuWorld, MAP_WIDTH, MAP_HEIGHT, NANHU_MAP_WIDTH, NANHU_MAP_HEIGHT
from interact import (Bag, PuzzleManager, ScoreSystem, SaveSystem,
                       PUZZLE_DATA, ITEM_DATA, SCENE_UNLOCK_CHAINS)

pygame.init()

WINDOW_WIDTH = 1050
WINDOW_HEIGHT = 650
VIEW_W = 800
VIEW_H = 600
BAG_PANEL_X = VIEW_W
BAG_PANEL_W = WINDOW_WIDTH - VIEW_W
STATUS_H = WINDOW_HEIGHT - VIEW_H
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
LIGHT_BLUE = (100, 180, 255)
DARK_BG = (15, 18, 32)
BUTTON_COLOR = (50, 85, 140)
BUTTON_HOVER = (70, 115, 185)
UI_ACCENT = (70, 160, 220)
UI_GOLD = (255, 210, 90)
UI_GREEN = (80, 200, 120)
UI_RED = (220, 90, 90)

SPAWN_MAIN_X = 500
SPAWN_MAIN_Y = 950
SPAWN_NANHU_X = 400
SPAWN_NANHU_Y = 450


class Button:
    def __init__(self, x, y, w, h, text, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hovered = False

    def draw(self, surface, font):
        base_color = BUTTON_HOVER if self.hovered else self.color
        r, g, b = base_color
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 50))
        surface.blit(shadow_surf, shadow_rect.topleft)

        grad_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for row in range(self.rect.height):
            t = row / self.rect.height
            gr = int(r + (min(255, r + 40) - r) * (1 - t))
            gg = int(g + (min(255, g + 40) - g) * (1 - t))
            gb = int(b + (min(255, b + 40) - b) * (1 - t))
            pygame.draw.line(grad_surf, (gr, gg, gb),
                             (0, row), (self.rect.width, row))

        highlight_surf = pygame.Surface((self.rect.width - 8, 3), pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, 60))
        surface.blit(grad_surf, self.rect.topleft)
        surface.blit(highlight_surf,
                     (self.rect.x + 4, self.rect.y + 4))

        border_c = UI_GOLD if self.hovered else (80, 110, 160)
        pygame.draw.rect(surface, border_c, self.rect, 2, border_radius=8)

        text_surf = font.render(self.text, True, WHITE)
        if self.hovered:
            shadow_ts = font.render(self.text, True, (0, 0, 0))
            surface.blit(shadow_ts,
                         (text_surf.get_rect(center=self.rect.center).x + 1,
                          text_surf.get_rect(center=self.rect.center).y + 1))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def check_click(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("桂子山校园秘境探险 v2.0")
        self.clock = pygame.time.Clock()

        self.font_large = self._load_font(36)
        self.font_medium = self._load_font(24)
        self.font_small = self._load_font(18)
        self.font_tiny = self._load_font(14)

        self.main_world = MainWorld()
        self.nanhu_world = NanhuWorld()
        self.current_map = "main"
        self.player = Player(SPAWN_MAIN_X, SPAWN_MAIN_Y)
        self.camera = Camera(VIEW_W, VIEW_H, MAP_WIDTH, MAP_HEIGHT)
        self.bag = Bag()
        self.puzzle_manager = PuzzleManager()
        self.score_system = ScoreSystem()

        self.state = "menu"
        self.message = ""
        self.message_timer = 0
        self.hint_text = ""
        self.hint_timer = 0
        self.popup_active = False
        self.popup_title = ""
        self.popup_lines = []
        self.popup_button = None
        self._pending_popup = None

        self.transition_alpha = 0
        self.transitioning = False
        self.transition_target = None

        self.night_secret_unlocked = False
        self.game_won = False
        self.win_anim_timer = 0

        self.dialog_text = ""
        self.dialog_timer = 0
        self.dialog_source = ""

        self.menu_buttons = []
        self.puzzle_buttons = []
        self._build_menu_buttons()
        self.map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        self.nanhu_surface = pygame.Surface((NANHU_MAP_WIDTH, NANHU_MAP_HEIGHT))

    @staticmethod
    def _load_font(size):
        font_dir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
        candidates = [
            os.path.join(font_dir, "simhei.ttf"),
            os.path.join(font_dir, "msyh.ttc"),
            os.path.join(font_dir, "simsun.ttc"),
            os.path.join(font_dir, "simkai.ttf"),
        ]
        for fp in candidates:
            if os.path.exists(fp):
                try:
                    f = pygame.font.Font(fp, size)
                    test = f.render("测试", True, (255, 255, 255))
                    if test.get_width() > 10:
                        return f
                except Exception:
                    continue
        return pygame.font.Font(None, size)

    def _build_menu_buttons(self):
        cx = WINDOW_WIDTH // 2
        self.menu_buttons = [
            Button(cx - 120, 300, 240, 50, "开始新游戏", (40, 120, 80)),
            Button(cx - 120, 370, 240, 50, "继续游戏", (60, 100, 160)),
            Button(cx - 120, 440, 240, 50, "退出游戏", (140, 60, 60)),
        ]

    def show_message(self, text, duration=2.5):
        self.message = text
        self.message_timer = duration

    def show_hint(self, text, duration=4.0):
        self.hint_text = text
        self.hint_timer = duration

    def show_dialog(self, source_name, text, duration=2.5):
        self.dialog_source = source_name
        self.dialog_text = text
        self.dialog_timer = duration

    def show_popup(self, title, lines):
        self.popup_active = True
        self.popup_title = title
        self.popup_lines = lines
        cx = WINDOW_WIDTH // 2
        self.popup_button = Button(cx - 80, 400, 160, 42, "确 定", (40, 120, 80))

    def _close_popup(self):
        self.popup_active = False
        self.popup_title = ""
        self.popup_lines = []
        self.popup_button = None

    def start_transition(self, target_map):
        self.transitioning = True
        self.transition_alpha = 0
        self.transition_target = target_map

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)

            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        if self.state == "playing":
                            self._do_save()
                        running = False
                        continue
                    self._handle_event(event)

                self._update(dt)
                self._draw()
                pygame.display.flip()
            except Exception as e:
                try:
                    self.screen.fill(DARK_BG)
                    err = self.font_medium.render(f"运行异常: {str(e)}", True, UI_RED)
                    hint = self.font_small.render("游戏继续运行", True, (180, 180, 180))
                    self.screen.blit(err,
                                       (WINDOW_WIDTH // 2 - err.get_width() // 2,
                                        WINDOW_HEIGHT // 2 - 15))
                    self.screen.blit(hint,
                                       (WINDOW_WIDTH // 2 - hint.get_width() // 2,
                                        WINDOW_HEIGHT // 2 + 15))
                    pygame.display.flip()
                except Exception:
                    pass

        pygame.quit()
        sys.exit()

    def _handle_event(self, event):
        handlers = {
            "menu": self._handle_menu_event,
            "playing": self._handle_playing_event,
            "puzzle": self._handle_puzzle_event,
            "travel": self._handle_travel_event,
            "win": self._handle_win_event,
            "transition": lambda e: None,
        }
        handler = handlers.get(self.state)
        if handler:
            handler(event)

    def _handle_menu_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            for btn in self.menu_buttons:
                btn.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.menu_buttons[0].check_click(event.pos):
                self._new_game()
            elif self.menu_buttons[1].check_click(event.pos):
                if SaveSystem.has_save() and self._load_game():
                    pass
                else:
                    self.show_message("没有找到存档", 2.0)
            elif self.menu_buttons[2].check_click(event.pos):
                pygame.quit()
                sys.exit()

    def _handle_playing_event(self, event):
        if self.popup_active:
            if event.type == pygame.MOUSEMOTION and self.popup_button:
                self.popup_button.check_hover(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.popup_button and self.popup_button.check_click(event.pos):
                    self._close_popup()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._close_popup()
            return

        if event.type == pygame.KEYDOWN:
            self.player.handle_key(event.key, True)
            if event.key == pygame.K_e:
                self._try_interact_nearby()
            elif event.key == pygame.K_ESCAPE:
                self._do_save()
                self.state = "menu"
        elif event.type == pygame.KEYUP:
            self.player.handle_key(event.key, False)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            try:
                bag_panel_rect = pygame.Rect(BAG_PANEL_X, 0, BAG_PANEL_W, VIEW_H)
                clicked_item = self.bag.handle_click(event.pos, bag_panel_rect)
                if clicked_item:
                    if clicked_item.usable:
                        if clicked_item.item_id == "bookmark":
                            hint = self._use_bookmark()
                            if hint:
                                self.show_hint(hint, 4.0)
                            else:
                                self.show_message("书签已使用但无谜题提示", 2.0)
                        else:
                            self.show_message("该道具在场景中自动使用", 2.0)
                    return

                world_x = event.pos[0] + self.camera.x
                world_y = event.pos[1] + self.camera.y
                if self.current_map == "main":
                    world = self.main_world
                else:
                    world = self.nanhu_world
                    world_x = event.pos[0]
                    world_y = event.pos[1]

                for obj in world.objects:
                    if obj.visible and obj.check_click(event.pos,
                                                      self.camera.x if self.current_map == "main" else 0,
                                                      self.camera.y if self.current_map == "main" else 0):
                        if obj.obj_type == "item" and not obj.interacted:
                            puzzle_type = ""
                            area = self.main_world.get_area_at(obj.center[0], obj.center[1])
                            if area:
                                p = PUZZLE_DATA.get(area.area_id)
                                if p:
                                    puzzle_type = p.get("type", "")
                            if puzzle_type in ("choice", "true_false"):
                                if not area or not area.puzzle_solved:
                                    self.show_message("需要先答对区域谜题才能获取宝物！", 2.0)
                                else:
                                    if self._collect_item(world, obj):
                                        pass
                            else:
                                if self._collect_item(world, obj):
                                    pass
                        elif obj.obj_type == "portal":
                            if obj.name == "南湖传送门":
                                self.start_transition("nanhu")
                            elif obj.name == "返回传送门":
                                self.start_transition("main")
                        elif obj.obj_type == "decoration":
                            self.show_dialog(obj.name, obj.description, 2.5)
                        break
            except Exception as e:
                self.show_message(f"操作异常: {e}", 2.0)

    def _handle_puzzle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            for btn in self.puzzle_buttons:
                btn.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.puzzle_manager.puzzle_active:
                for i, btn in enumerate(self.puzzle_buttons):
                    if btn.check_click(event.pos):
                        self._submit_answer(i)
                        break
            else:
                for i, btn in enumerate(self.puzzle_buttons):
                    if btn.check_click(event.pos):
                        if btn.text == "继续":
                            self._close_puzzle_and_show_result()
                        break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._close_puzzle_and_show_result()

    def _handle_travel_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_t):
                self.state = "playing"

    def _handle_win_event(self, event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            if self.win_anim_timer > 2.0:
                self.state = "menu"
                self._new_game()

    def _update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
        if self.hint_timer > 0:
            self.hint_timer -= dt
        if self.dialog_timer > 0:
            self.dialog_timer -= dt

        if self.transitioning:
            self.transition_alpha += dt * 300
            if self.transition_alpha >= 255:
                self._execute_transition()
            return

        if self.state == "playing":
            if self.popup_active:
                world = self.main_world if self.current_map == "main" else self.nanhu_world
                if world:
                    world.update(dt)
                return

            collision = None
            if self.current_map == "main":
                collision = self.main_world.collision
            else:
                collision = self.nanhu_world.collision
            self.player.move(dt, collision)
            self.player.update(dt)

            if self.current_map == "main":
                self.camera.follow(self.player.x, self.player.y, dt)
                self.main_world.update(dt)
                self._check_proximity_interactions()
            else:
                self.nanhu_world.update(dt)
                self._check_nanhu_proximity()

        elif self.state == "win":
            self.win_anim_timer += dt

    def _draw(self):
        draw_handlers = {
            "menu": self._draw_menu,
            "playing": self._draw_playing,
            "puzzle": self._draw_puzzle,
            "travel": self._draw_travel,
            "win": self._draw_win,
            "transition": self._draw_transition,
        }
        handler = draw_handlers.get(self.state)
        if handler:
            handler()

    def _new_game(self):
        self.main_world = MainWorld()
        self.nanhu_world = NanhuWorld()
        self.current_map = "main"
        self.player = Player(SPAWN_MAIN_X, SPAWN_MAIN_Y)
        self.camera = Camera(VIEW_W, VIEW_H, MAP_WIDTH, MAP_HEIGHT)
        self.bag = Bag()
        self.puzzle_manager = PuzzleManager()
        self.score_system = ScoreSystem()
        self.night_secret_unlocked = False
        self.game_won = False
        self.win_anim_timer = 0
        self.state = "playing"
        self.show_message("欢迎来到桂子山！WASD移动，E键交互，点击传送门切换地图", 4.0)

    def _do_save(self):
        px = int(self.player.x)
        py = int(self.player.y)
        SaveSystem.save_game(self.score_system, self.bag,
                             self.main_world if self.current_map == "main" else self.nanhu_world,
                             (px, py), self.current_map)

    def _load_game(self):
        data = SaveSystem.load_game()
        if data is None:
            return False
        self.score_system.score = data.get("score", 0)
        self.score_system.items_collected = data.get("items_collected", 0)
        self.score_system.areas_unlocked = data.get("areas_unlocked", 6)
        self.score_system.puzzles_solved = data.get("puzzles_solved", 0)
        self.bag = Bag.from_list(data.get("bag", []))
        self.current_map = data.get("current_map", "main")

        if self.current_map == "main":
            self.main_world = MainWorld()
            self.player = Player(data.get("player_x", SPAWN_MAIN_X),
                                  data.get("player_y", SPAWN_MAIN_Y))
            self.camera = Camera(VIEW_W, VIEW_H, MAP_WIDTH, MAP_HEIGHT)
            ws = data.get("world_state", {})
            self.main_world.load_state(ws)
        else:
            self.nanhu_world = NanhuWorld()
            self.player = Player(data.get("player_x", SPAWN_NANHU_X),
                                  data.get("player_y", SPAWN_NANHU_Y))
            self.camera = Camera(VIEW_W, VIEW_H, NANHU_MAP_WIDTH, NANHU_MAP_HEIGHT)

        all_normal_solved = True
        for aid in ["guizhong_road", "boya_square", "youming_gym",
                     "dining_hall", "fountain_square"]:
            a = self.main_world.areas.get(aid)
            if a and not a.puzzle_solved:
                all_normal_solved = False
                break
        if all_normal_solved:
            self.night_secret_unlocked = True
            night = self.main_world.areas.get("night_secret")
            if night:
                night.unlocked = True

        self.state = "playing"
        self.show_message("读档成功！继续探索吧", 2.0)
        return True

    def _try_interact_nearby(self):
        px, py = self.player.center
        if self.current_map == "main":
            nearby = self.main_world.get_nearby_objects(px, py, max_dist=45)
        else:
            nearby = self.nanhu_world.get_nearby_objects(px, py, max_dist=45)

        for obj in nearby:
            if obj.obj_type == "puzzle":
                area = self.main_world.get_area_at(obj.center[0], obj.center[1]) \
                    if self.current_map == "main" else None
                if area and area.puzzle_solved:
                    continue
                if self.current_map == "nanhu":
                    self._start_puzzle_for_area("nanhu_building")
                elif area:
                    self._start_puzzle_for_area(area.area_id)
                return
            elif obj.obj_type == "item" and not obj.interacted:
                world = self.main_world if self.current_map == "main" else self.nanhu_world
                self._collect_item(world, obj)
                return
            elif obj.obj_type == "decoration":
                self.show_dialog(obj.name, obj.description, 2.5)
                return
            elif obj.obj_type == "portal":
                if obj.name == "南湖传送门":
                    self.start_transition("nanhu")
                elif obj.name == "返回传送门":
                    self.start_transition("main")
                return

    def _check_proximity_interactions(self):
        px, py = self.player.center
        nearby = self.main_world.get_nearby_objects(px, py, max_dist=40)
        for obj in nearby:
            if obj.obj_type == "decoration" and not obj.triggered_dialog:
                self.show_dialog(obj.name, obj.description, 2.0)
                obj.triggered_dialog = True
                break

    def _check_nanhu_proximity(self):
        px, py = self.player.center
        nearby = self.nanhu_world.get_nearby_objects(px, py, max_dist=40)
        for obj in nearby:
            if obj.obj_type == "decoration" and not obj.triggered_dialog:
                self.show_dialog(obj.name, obj.description, 2.0)
                obj.triggered_dialog = True
                break

    def _collect_item(self, world, obj):
        if obj.item_id and not obj.interacted:
            if self.bag.add_item(obj.item_id):
                obj.interacted = True
                self.score_system.on_item_collected()
                name = ITEM_DATA.get(obj.item_id, {}).get("name", "道具")
                self.show_message(f"获得道具：{name}！", 2.0)
                world.add_particle(obj.center[0], obj.center[1], (255, 255, 100))
                self._check_guizhong_collect()
                return True
        return False

    def _check_guizhong_collect(self):
        area = self.main_world.areas.get("guizhong_road")
        if area and area.puzzle_solved:
            return
        count = self.bag.get_item_count("osmanthus_badge")
        puzzle = PUZZLE_DATA.get("guizhong_road")
        if puzzle and count >= puzzle.get("target_count", 3):
            area.puzzle_solved = True
            self.score_system.on_puzzle_solved()
            self._unlock_chain("guizhong_road")
            self.show_popup("通关成功！",
                            [puzzle.get("success_text", "桂中路秘境已解锁！")])

    def _start_puzzle_for_area(self, area_id):
        puzzle = PUZZLE_DATA.get(area_id)
        if not puzzle:
            return
        if puzzle["type"] == "find_item":
            target = puzzle.get("target_item")
            if self.bag.has_item(target):
                area = self.main_world.areas.get(area_id)
                if area:
                    area.puzzle_solved = True
                self.score_system.on_puzzle_solved()
                self._unlock_chain(area_id)
                self.show_popup("通关成功！", [puzzle.get("success_text", "通关！")])
            else:
                self.show_message("需要先找到隐藏的道具才能通关此场景！", 2.5)
            return
        if puzzle["type"] == "collect":
            self.show_message("此区域需要收集指定数量的道具", 2.0)
            return
        if self.puzzle_manager.start_puzzle(area_id):
            self.state = "puzzle"
            self.selected_option = -1
            self._build_puzzle_buttons()

    def _submit_answer(self, option_index):
        pm = self.puzzle_manager
        puzzle = pm.current_puzzle
        if not puzzle:
            return

        if puzzle["type"] == "choice":
            correct = pm.check_choice_answer(option_index)
            if correct:
                self.puzzle_result = True
                self._solve_current_puzzle()
                rewards = self._collect_area_rewards(pm.current_area_id)
                lines = [puzzle.get("success_text", "回答正确！"), ""]
                lines.extend(rewards)
                self._pending_popup = ("通关成功！", lines)
            else:
                self.puzzle_result = False
                self.show_message(puzzle.get("fail_text", "回答错误！"), 2.5)
            self.puzzle_manager.puzzle_active = False
            self._build_puzzle_result_buttons()

        elif puzzle["type"] == "true_false":
            answer = (option_index == 0)
            result = pm.check_true_false(answer)
            if result is None:
                self._build_puzzle_buttons()
            elif result:
                self.puzzle_result = True
                self._solve_current_puzzle()
                rewards = self._collect_area_rewards(pm.current_area_id)
                lines = [puzzle.get("success_text", "全部正确！"), ""]
                lines.extend(rewards)
                self._pending_popup = ("通关成功！", lines)
                self.puzzle_manager.puzzle_active = False
                self._build_puzzle_result_buttons()
            else:
                self.puzzle_result = False
                self.show_message(puzzle.get("fail_text", "有题目答错了！"), 2.5)
                self.puzzle_manager.puzzle_active = False
                self._build_puzzle_result_buttons()

    def _solve_current_puzzle(self):
        aid = self.puzzle_manager.current_area_id
        area = self.main_world.areas.get(aid)
        if area:
            area.puzzle_solved = True
        self.score_system.on_puzzle_solved()
        self._unlock_chain(aid)
        self._check_night_secret()

    def _collect_area_rewards(self, area_id):
        rewards = []
        for obj in self.main_world.objects:
            if obj.obj_type == "item" and not obj.interacted and obj.item_id:
                area = self.main_world.areas.get(area_id)
                if area and area.contains(obj.center[0], obj.center[1]):
                    if self.bag.add_item(obj.item_id):
                        obj.interacted = True
                        self.score_system.on_item_collected()
                        name = ITEM_DATA.get(obj.item_id, {}).get("name", "道具")
                        rewards.append(f"获得道具：{name}")
                        self.main_world.add_particle(obj.center[0],
                                                       obj.center[1],
                                                       (255, 255, 100))
        return rewards

    def _unlock_chain(self, solved_id):
        for target, required in SCENE_UNLOCK_CHAINS.items():
            if required == solved_id:
                area = self.main_world.areas.get(target)
                if area and not area.unlocked:
                    area.unlocked = True
                    self.score_system.on_area_unlocked()

    def _check_night_secret(self):
        all_done = True
        for aid in ["guizhong_road", "library", "boya_square",
                     "youming_gym", "dining_hall", "fountain_square",
                     "nanhu_building"]:
            area = self.main_world.areas.get(aid)
            if area and not area.puzzle_solved:
                all_done = False
                break
        if all_done and not self.night_secret_unlocked:
            self.night_secret_unlocked = True
            night = self.main_world.areas.get("night_secret")
            if night:
                night.unlocked = True
            self.score_system.on_area_unlocked()

    def _use_bookmark(self):
        if self.bag.use_item("bookmark"):
            puzzle = self.puzzle_manager.current_puzzle
            if puzzle and "hint" in puzzle:
                return puzzle["hint"]
            return "当前没有可用的提示。"
        return None

    def _close_puzzle_and_show_result(self):
        self.puzzle_manager.close_puzzle()
        if self._pending_popup:
            title, lines = self._pending_popup
            self._pending_popup = None
            self.show_popup(title, lines)
        self.state = "playing"
        self._check_win()

    def _check_win(self):
        if not self.night_secret_unlocked:
            return False
        night = self.main_world.areas.get("night_secret")
        if night and night.puzzle_solved:
            self.game_won = True
            self.state = "win"
            self.win_anim_timer = 0
            return True
        return False

    def _execute_transition(self):
        target = self.transition_target
        self.transitioning = False
        self.transition_alpha = 0
        if target == "nanhu":
            self.current_map = "nanhu"
            self.player.x = float(SPAWN_NANHU_X)
            self.player.y = float(SPAWN_NANHU_Y)
            self.camera = Camera(VIEW_W, VIEW_H, NANHU_MAP_WIDTH, NANHU_MAP_HEIGHT)
            self.camera.snap_to(self.player.x, self.player.y)
            self.nanhu_world = NanhuWorld()
        else:
            self.current_map = "main"
            self.player.x = float(SPAWN_MAIN_X)
            self.player.y = float(SPAWN_MAIN_Y)
            self.camera = Camera(VIEW_W, VIEW_H, MAP_WIDTH, MAP_HEIGHT)
            self.camera.snap_to(self.player.x, self.player.y)
        self.state = "playing"

    def _build_puzzle_buttons(self):
        pm = self.puzzle_manager
        puzzle = pm.current_puzzle
        if not puzzle:
            return
        self.puzzle_buttons = []
        cx = WINDOW_WIDTH // 2
        if puzzle["type"] == "choice":
            options = puzzle["options"]
            start_y = 320
            for i, opt in enumerate(options):
                self.puzzle_buttons.append(
                    Button(cx - 200, start_y + i * 55, 400, 45, opt))
        elif puzzle["type"] == "true_false":
            q = pm.get_tf_question()
            if q:
                self.puzzle_buttons = [
                    Button(cx - 200, 350, 190, 45, "正确 ✓"),
                    Button(cx + 10, 350, 190, 45, "错误 ✗", (160, 60, 60)),
                ]

    def _build_puzzle_result_buttons(self):
        cx = WINDOW_WIDTH // 2
        self.puzzle_buttons = [Button(cx - 100, 420, 200, 45, "继续")]

    # ========== DRAW METHODS ==========

    def _draw_menu(self):
        for y in range(WINDOW_HEIGHT):
            t = y / WINDOW_HEIGHT
            r = int(12 + t * 10)
            g = int(14 + t * 8)
            b = int(28 + t * 15)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        title_shadow = self.font_large.render("桂子山校园秘境探险", True, (30, 30, 50))
        self.screen.blit(title_shadow,
                           (WINDOW_WIDTH // 2 - title_shadow.get_width() // 2 + 2, 102))
        title = self.font_large.render("桂子山校园秘境探险", True, UI_GOLD)
        self.screen.blit(title,
                           (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))

        sub = self.font_medium.render("华中师范大学 · 星露谷风格探索版 v2.0",
                                     True, UI_ACCENT)
        self.screen.blit(sub,
                           (WINDOW_WIDTH // 2 - sub.get_width() // 2, 155))

        info_lines = [
            "WASD: 移动角色   E键: 交互/对话   鼠标: 点击拾取/传送门切换地图",
            "ESC: 返回菜单并保存进度",
        ]
        for i, line in enumerate(info_lines):
            s = self.font_small.render(line, True, (160, 170, 195))
            self.screen.blit(s,
                             (WINDOW_WIDTH // 2 - s.get_width() // 2, 215 + i * 26))

        for btn in self.menu_buttons:
            btn.draw(self.screen, self.font_medium)

        if not SaveSystem.has_save():
            self.menu_buttons[1].color = (45, 48, 62)
        else:
            self.menu_buttons[1].color = BUTTON_COLOR

        ver = self.font_tiny.render(
            "v2.0 | Python+Pygame | 华中师范大学 计算机学院",
            True, (80, 85, 110))
        self.screen.blit(ver,
                           (WINDOW_WIDTH // 2 - ver.get_width() // 2,
                            WINDOW_HEIGHT - 28))

    def _draw_playing(self):
        try:
            if self.current_map == "main":
                self.map_surface.fill((0, 0, 0))
                self.main_world.draw(self.map_surface, self.font_small,
                                    self.camera.x, self.camera.y)
                self.player.draw(self.map_surface, self.camera.x, self.camera.y)
                self.screen.blit(self.map_surface, (0, 0))
            else:
                self.nanhu_surface.fill((0, 0, 0))
                self.nanhu_world.draw(self.nanhu_surface, self.font_small)
                self.player.draw(self.nanhu_surface)
                self.screen.blit(self.nanhu_surface, (0, 0))
        except Exception as e:
            self.screen.fill(DARK_BG)
            err = self.font_medium.render(f"场景渲染异常: {e}", True, UI_RED)
            self.screen.blit(err,
                               (VIEW_W // 2 - err.get_width() // 2,
                                VIEW_H // 2 - 15))

        bag_panel_rect = pygame.Rect(BAG_PANEL_X, 0, BAG_PANEL_W, VIEW_H)
        self.bag.draw(self.screen, self.font_small, self.font_tiny,
                      bag_panel_rect)
        self._draw_status_bar()

        if self.message_timer > 0:
            self._draw_message()
        if self.hint_timer > 0:
            self._draw_hint()
        if self.dialog_timer > 0:
            self._draw_dialog()
        if self.popup_active:
            try:
                self._draw_popup()
            except Exception as e:
                self.show_message(f"弹窗异常: {e}", 2.0)

    def _draw_status_bar(self):
        bar_rect = pygame.Rect(0, VIEW_H, WINDOW_WIDTH, STATUS_H)
        bar_bg = pygame.Surface((WINDOW_WIDTH, STATUS_H), pygame.SRCALPHA)
        for y in range(STATUS_H):
            t = y / STATUS_H
            c = int(18 + t * 8)
            pygame.draw.line(bar_bg, (c, c + 4, c + 14), (0, y), (WINDOW_WIDTH, y))
        self.screen.blit(bar_bg, bar_rect.topleft)
        pygame.draw.line(self.screen, UI_ACCENT, (0, VIEW_H),
                         (WINDOW_WIDTH, VIEW_H), 2)

        ss = self.score_system
        icons = [("积分", str(ss.score), UI_GOLD),
                 ("道具", str(ss.items_collected), (180, 220, 100)),
                 ("区域", f"{ss.areas_unlocked}/8", UI_ACCENT),
                 ("谜题", f"{ss.puzzles_solved}/7", (200, 160, 220))]
        x = 16
        for label, value, color in icons:
            bg = pygame.Surface((80, 26), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 60))
            self.screen.blit(bg, (x, VIEW_H + 6))
            self.screen.blit(self.font_tiny.render(label, True, (140, 150, 170)),
                              (x + 5, VIEW_H + 8))
            self.screen.blit(self.font_small.render(value, True, color),
                              (x + 38, VIEW_H + 6))
            x += 90

        map_name = "本部校园" if self.current_map == "main" else "南湖综合楼"
        area = self.main_world.get_area_at(self.player.x, self.player.y) \
            if self.current_map == "main" else None
        area_name = area.name if area else map_name
        loc_bg = pygame.Surface((180, 26), pygame.SRCALPHA)
        loc_bg.fill((0, 0, 0, 60))
        self.screen.blit(loc_bg, (x, VIEW_H + 6))
        self.screen.blit(self.font_small.render(f"位置: {area_name}", True, WHITE),
                          (x + 5, VIEW_H + 7))

        help_text = "E:交互 ESC:菜单 鼠标:点击"
        hs = self.font_tiny.render(help_text, True, (110, 120, 145))
        hbg = pygame.Surface((hs.get_width() + 14, 20), pygame.SRCALPHA)
        hbg.fill((0, 0, 0, 50))
        self.screen.blit(hbg,
                         (WINDOW_WIDTH - hs.get_width() - 18, VIEW_H + 28))
        self.screen.blit(hs,
                         (WINDOW_WIDTH - hs.get_width() - 11, VIEW_H + 30))

    def _draw_message(self):
        if not self.message:
            return
        alpha = min(1.0, self.message_timer / 0.5) * 255
        surf = self.font_small.render(self.message, True, WHITE)
        bw = surf.get_width() + 30
        bh = surf.get_height() + 16
        bx = (VIEW_W - bw) // 2
        by = VIEW_H - 58
        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg.fill((0, 0, 0, int(alpha * 0.7)))
        self.screen.blit(bg, (bx, by))
        pygame.draw.rect(self.screen, (100, 180, 255, int(alpha)),
                         (bx, by, bw, bh), 2, border_radius=6)
        self.screen.blit(surf, (bx + 15, by + 8))

    def _draw_hint(self):
        if not self.hint_text:
            return
        alpha = min(1.0, self.hint_timer / 0.5) * 255
        surf = self.font_small.render(f"\U0001f4a1 {self.hint_text}",
                                      True, (255, 255, 150))
        bw = surf.get_width() + 20
        bh = surf.get_height() + 12
        bx = (VIEW_W - bw) // 2
        by = 48
        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg.fill((40, 40, 0, int(alpha * 0.8)))
        self.screen.blit(bg, (bx, by))
        pygame.draw.rect(self.screen, (255, 255, 100, int(alpha)),
                         (bx, by, bw, bh), 2, border_radius=6)
        self.screen.blit(surf, (bx + 10, by + 6))

    def _draw_dialog(self):
        if not self.dialog_text:
            return
        alpha = min(1.0, self.dialog_timer / 0.3) * 255
        src = f"[{self.dialog_source}] {self.dialog_text}"
        surf = self.font_small.render(src, True, (230, 225, 200))
        bw = min(surf.get_width() + 30, VIEW_W - 40)
        bh = surf.get_height() + 16
        bx = (VIEW_W - bw) // 2
        by = VIEW_H - 95
        bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
        bg.fill((20, 18, 35, int(alpha * 0.85)))
        self.screen.blit(bg, (bx, by))
        pygame.draw.rect(self.screen, (180, 160, 100, int(alpha)),
                         (bx, by, bw, bh), 2, border_radius=6)
        self.screen.blit(surf, (bx + 15, by + 8))

    def _draw_popup(self):
        if not self.popup_active:
            return
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        pw, ph = 460, 380
        panel_x = (WINDOW_WIDTH - pw) // 2
        panel_y = (WINDOW_HEIGHT - ph) // 2
        pygame.draw.rect(self.screen, (25, 30, 55),
                         (panel_x, panel_y, pw, ph), border_radius=14)
        pygame.draw.rect(self.screen, GOLD,
                         (panel_x, panel_y, pw, ph), 3, border_radius=14)

        inner = pygame.Rect(panel_x + 6, panel_y + 6, pw - 12, ph - 12)
        pygame.draw.rect(self.screen, (35, 40, 70), inner, border_radius=10)

        title = self.font_medium.render(self.popup_title, True, GOLD)
        self.screen.blit(title,
                         (panel_x + (pw - title.get_width()) // 2, panel_y + 15))
        pygame.draw.line(self.screen, (80, 100, 160),
                         (panel_x + 30, panel_y + 52),
                         (panel_x + pw - 30, panel_y + 52), 1)

        y = panel_y + 62
        for line in self.popup_lines:
            if line == "":
                y += 8
                continue
            c = UI_GREEN if "获得道具" in line else (220, 220, 240)
            s = self.font_small.render(line, True, c)
            self.screen.blit(s, (panel_x + 30, y))
            y += 28

        if self.popup_button:
            self.popup_button.rect.centerx = panel_x + pw // 2
            self.popup_button.rect.top = panel_y + ph - 55
            self.popup_button.draw(self.screen, self.font_small)

    def _draw_puzzle(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pm = self.puzzle_manager
        puzzle = pm.current_puzzle
        if not puzzle:
            return

        pw, ph = 500, 400
        px = (WINDOW_WIDTH - pw) // 2
        py = (WINDOW_HEIGHT - ph) // 2
        pygame.draw.rect(self.screen, (30, 30, 60), (px, py, pw, ph),
                         border_radius=12)
        pygame.draw.rect(self.screen, LIGHT_BLUE, (px, py, pw, ph), 3,
                         border_radius=12)

        area_name = {"nanhu_building": "南湖综合楼"}.get(
            pm.current_area_id, pm.current_area_id)
        title = self.font_medium.render(f"【{area_name}·谜题】", True, GOLD)
        self.screen.blit(title, (px + (pw - title.get_width()) // 2, py + 15))

        if pm.puzzle_active:
            if puzzle["type"] == "choice":
                qs = self.font_small.render(puzzle["question"], True, WHITE)
                self.screen.blit(qs, (px + 30, py + 65))
                for btn in self.puzzle_buttons:
                    btn.draw(self.screen, self.font_small)
            elif puzzle["type"] == "true_false":
                q = pm.get_tf_question()
                if q:
                    prog = f"({pm.tf_index + 1}/{len(puzzle['questions'])})"
                    qs = self.font_small.render(q["question"], True, WHITE)
                    self.screen.blit(qs, (px + 30, py + 82))
                    ps = self.font_tiny.render(prog, True, LIGHT_BLUE)
                    self.screen.blit(ps, (px + 30, py + 57))
                    for btn in self.puzzle_buttons:
                        btn.draw(self.screen, self.font_small)
        else:
            rc = UI_GREEN if getattr(self, 'puzzle_result', False) else UI_RED
            rt = "\u2713 回答正确！" if getattr(self, 'puzzle_result',
                                                  False) else "\u2717 回答错误！"
            rs = self.font_medium.render(rt, True, rc)
            self.screen.blit(rs,
                             (px + (pw - rs.get_width()) // 2, py + 155))
            for btn in self.puzzle_buttons:
                btn.draw(self.screen, self.font_small)

        esc = self.font_tiny.render("按 ESC 关闭", True, (120, 120, 150))
        self.screen.blit(esc, (px + pw - esc.get_width() - 15, py + ph - 25))

    def _draw_travel(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        pw, ph = 400, 480
        px = (WINDOW_WIDTH - pw) // 2
        py = (WINDOW_HEIGHT - ph) // 2
        pygame.draw.rect(self.screen, (30, 30, 60), (px, py, pw, ph),
                         border_radius=12)
        pygame.draw.rect(self.screen, LIGHT_BLUE, (px, py, pw, ph), 3,
                         border_radius=12)

        title = self.font_medium.render("大地图概览", True, GOLD)
        self.screen.blit(title, (px + (pw - title.get_width()) // 2, py + 20))

        cur = "本部校园" if self.current_map == "main" else "南湖区域"
        cs = self.font_small.render(f"当前位置：{cur}", True, WHITE)
        self.screen.blit(cs, (px + 30, py + 65))

        hint = self.font_tiny.render("按 ESC 或 T 返回游戏", True, (120, 120, 150))
        self.screen.blit(hint, (px + pw - hint.get_width() - 15, py + ph - 25))

    def _draw_transition(self):
        if self.current_map == "main":
            self.map_surface.fill((0, 0, 0))
            self.main_world.draw(self.map_surface, self.font_small,
                                 self.camera.x, self.camera.y)
            self.player.draw(self.map_surface, self.camera.x, self.camera.y)
            self.screen.blit(self.map_surface, (0, 0))
        else:
            self.nanhu_surface.fill((0, 0, 0))
            self.nanhu_world.draw(self.nanhu_surface, self.font_small)
            self.player.draw(self.nanhu_surface)
            self.screen.blit(self.nanhu_surface, (0, 0))

        alpha = min(255, int(self.transition_alpha))
        fade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        fade.fill((0, 0, 0, alpha))
        self.screen.blit(fade, (0, 0))

        txt = "正在前往..." if self.transition_target == "nanhu" else "正在返回..."
        ts = self.font_medium.render(txt, True, WHITE)
        self.screen.blit(ts,
                           (WINDOW_WIDTH // 2 - ts.get_width() // 2,
                            WINDOW_HEIGHT // 2))

    def _draw_win(self):
        for y in range(WINDOW_HEIGHT):
            t = y / WINDOW_HEIGHT
            r = int(8 + t * 12)
            g = int(4 + t * 8)
            b = int(25 + t * 20)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))

        t = self.win_anim_timer
        if t > 0.4:
            ts = self.font_large.render("恭 喜 通 关", True, UI_GOLD)
            self.screen.blit(ts,
                             (WINDOW_WIDTH // 2 - ts.get_width() // 2, 127))
            sub = self.font_medium.render("桂子山校园秘境 · 完美通关",
                                         True, UI_ACCENT)
            self.screen.blit(sub,
                             (WINDOW_WIDTH // 2 - sub.get_width() // 2, 175))

        if t > 1.3:
            lines = [
                ("你成功探索了桂子山的所有秘境！", WHITE),
                (f"最终积分：{self.score_system.score}", UI_GOLD),
                (f"收集道具：{self.score_system.items_collected} 件",
                 (180, 230, 120)),
                (f"解锁区域：{self.score_system.areas_unlocked} / 8",
                 UI_ACCENT),
                ("桂子山桂花飘香，华师学子永远前行！", UI_GOLD),
            ]
            sy = 240
            for ln, lc in lines:
                s = self.font_small.render(ln, True, lc)
                self.screen.blit(s, (WINDOW_WIDTH // 2 - s.get_width() // 2, sy))
                sy += 30

        if t > 2.0:
            ht = self.font_tiny.render("点击任意键返回主菜单", True, (160, 165, 195))
            self.screen.blit(ht,
                             (WINDOW_WIDTH // 2 - ht.get_width() // 2,
                              WINDOW_HEIGHT - 38))

        for i in range(min(25, int(t * 6))):
            px = random.randint(40, WINDOW_WIDTH - 40)
            py = random.randint(40, WINDOW_HEIGHT - 40)
            sz = random.randint(2, 5)
            c = random.choice([UI_GOLD, (255, 120, 100),
                                (100, 255, 140), UI_ACCENT])
            pygame.draw.circle(self.screen, c, (px, py), sz)


if __name__ == "__main__":
    game = Game()
    game.run()
