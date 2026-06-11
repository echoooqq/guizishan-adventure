"""暂停菜单 — 继续游戏/背包/校园地图/存档/读档/设置/返回标题

采用自定义渲染层绘制像素风菜单。
阶段1：纯色背景+文字按钮
阶段2：9-slice像素风边框+像素风按钮
"""

import os
import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    FONT_TITLE_SIZE,
    COLOR_WHITE,
    COLOR_BLACK,
)
from ui.dialog_box import create_border_surface, draw_nine_slice

# 从quest_log导入共享颜色
QUEST_SOLVED_COLOR = (100, 220, 100)


# 菜单项定义
PAUSE_MENU_ITEMS = [
    ("continue", "继续游戏"),
    ("inventory", "背包"),
    ("quest_log", "任务日志"),
    ("map", "校园地图"),
    ("save", "存档"),
    ("load", "读档"),
    ("settings", "设置"),
    ("quit_title", "返回标题"),
]

# 存档菜单项
SAVE_MENU_ITEMS = [
    ("auto_save", "自动存档"),
    ("slot_1", "存档槽 1"),
    ("slot_2", "存档槽 2"),
    ("back", "返回"),
]

# 读档菜单项（与存档菜单结构相同，但行为不同）
LOAD_MENU_ITEMS = [
    ("load_auto", "自动存档"),
    ("load_slot_1", "存档槽 1"),
    ("load_slot_2", "存档槽 2"),
    ("back", "返回"),
]

# 设置菜单项
SETTINGS_MENU_ITEMS = [
    ("volume", "音量调节"),
    ("window_size", "窗口大小"),
    ("controls", "操作说明"),
    ("back", "返回"),
]

# 音量调节子菜单项
VOLUME_MENU_ITEMS = [
    ("master_volume", "主音量"),
    ("bgm_volume", "背景音乐"),
    ("sfx_volume", "音效"),
    ("back", "返回"),
]

# 窗口大小选项
WINDOW_SIZE_OPTIONS = [
    (960, 540, "960×540（默认）"),
    (1280, 720, "1280×720"),
    (1440, 810, "1440×810"),
    (1920, 1080, "1920×1080"),
]

# 标题画面读档菜单项
TITLE_LOAD_MENU_ITEMS = [
    ("load_auto", "自动存档"),
    ("load_slot_1", "存档槽 1"),
    ("load_slot_2", "存档槽 2"),
    ("back", "返回"),
]

# 颜色
MENU_BG_COLOR = (0, 0, 0, 160)
MENU_BORDER_COLOR = (100, 100, 140)
MENU_TITLE_COLOR = (255, 215, 0)
MENU_ITEM_COLOR = (220, 220, 220)
MENU_ITEM_HOVER_COLOR = (255, 255, 255)
MENU_ITEM_HOVER_BG = (60, 60, 90, 180)
MENU_ITEM_DISABLED_COLOR = (80, 80, 100)
SAVE_INFO_COLOR = (160, 160, 180)
CONFIRM_COLOR = (255, 200, 100)
EMPTY_SLOT_TEXT = "— 空 —"


class Menu:
    """暂停菜单系统"""

    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        self._small_font = pygame.font.Font(FONT_PATH, 8)

        self.active = False
        self.current_menu = "pause"  # pause / save / load / settings / title_load / confirm_load / volume / window_size
        self.selected_index = 0
        self._save_infos = []
        self._save_message = ""
        self._save_message_timer = 0.0
        self._pending_load_slot = None  # 等待确认读档的槽位ID
        self._confirm_choice = 0     # 确认对话框选项：0=确认, 1=取消

        # 音量设置（0.0-1.0）
        self._master_volume = 1.0
        self._bgm_volume = 0.5
        self._sfx_volume = 0.7
        self._adjusting_slider = False  # 是否正在拖动滑块

        # 窗口大小选择
        self._window_size_index = 0  # 当前选中的窗口大小索引
        self._current_window_size = (960, 540)  # 当前窗口大小

        # 昼夜时段（影响遮罩色调）
        self._period_name = "白天"

        # 按钮精灵图
        self._btn_normal = None
        self._btn_hover = None
        self._btn_pressed = None
        self._load_button_sprites()

        # 边框素材
        self._border_image = create_border_surface(
            size=24, border_width=3,
            border_color=MENU_BORDER_COLOR,
            bg_color=(20, 20, 40, 220),
        )

    def _load_button_sprites(self):
        """加载按钮精灵图，加载失败则降级为纯色"""
        try:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "ui", "sprites")
            normal_path = os.path.join(base_dir, "button_normal.png")
            hover_path = os.path.join(base_dir, "button_hover.png")
            pressed_path = os.path.join(base_dir, "button_pressed.png")
            if os.path.exists(normal_path):
                self._btn_normal = pygame.image.load(normal_path).convert_alpha()
            if os.path.exists(hover_path):
                self._btn_hover = pygame.image.load(hover_path).convert_alpha()
            if os.path.exists(pressed_path):
                self._btn_pressed = pygame.image.load(pressed_path).convert_alpha()
        except Exception:
            # 加载失败，降级为纯色绘制
            self._btn_normal = None
            self._btn_hover = None
            self._btn_pressed = None

    def set_period(self, period_name):
        """设置当前昼夜时段，影响菜单遮罩色调"""
        self._period_name = period_name

    def _get_overlay_color(self):
        """根据昼夜时段返回遮罩颜色"""
        if self._period_name == "黄昏":
            return (30, 10, 0, 170)
        elif self._period_name == "夜晚":
            return (0, 5, 20, 180)
        else:
            return MENU_BG_COLOR  # 白天: (0, 0, 0, 160)

    def _draw_button_bg(self, surface, rect, is_selected):
        """绘制菜单项背景，优先使用精灵图，降级为纯色"""
        if is_selected and self._btn_hover:
            scaled = pygame.transform.scale(self._btn_hover, (rect.width, rect.height))
            surface.blit(scaled, rect.topleft)
        elif not is_selected and self._btn_normal:
            scaled = pygame.transform.scale(self._btn_normal, (rect.width, rect.height))
            surface.blit(scaled, rect.topleft)
        else:
            # 降级：纯色背景
            bg_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            bg_surf.fill(MENU_ITEM_HOVER_BG if is_selected else (0, 0, 0, 0))
            surface.blit(bg_surf, rect.topleft)

    def open(self, menu_type="pause"):
        """打开菜单"""
        self.active = True
        self.current_menu = menu_type
        self.selected_index = 0
        self._save_message = ""
        self._save_message_timer = 0.0
        self._pending_load_slot = None
        self._confirm_choice = 0

    def close(self):
        """关闭菜单"""
        self.active = False
        self.current_menu = "pause"
        self.selected_index = 0
        self._pending_load_slot = None

    def update(self, dt):
        """更新菜单状态"""
        if self._save_message_timer > 0:
            self._save_message_timer -= dt
            if self._save_message_timer <= 0:
                self._save_message = ""

    def handle_event(self, event):
        """处理菜单输入事件，返回菜单动作"""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            # 确认读档对话框
            if self.current_menu == "confirm_load":
                return self._handle_confirm_event(event)

            if event.key == pygame.K_ESCAPE:
                if self.current_menu == "pause":
                    return "continue"
                elif self.current_menu == "title_load":
                    return "cancel_title_load"
                elif self.current_menu in ("volume", "window_size"):
                    self.current_menu = "settings"
                    self.selected_index = 0
                    return None
                else:
                    self.current_menu = "pause"
                    self.selected_index = 0
                    return None

            if event.key == pygame.K_UP:
                self._move_selection(-1)
            elif event.key == pygame.K_DOWN:
                self._move_selection(1)
            elif event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                return self._confirm_selection()
            elif event.key == pygame.K_LEFT:
                # 音量调节：减小音量
                if self.current_menu == "volume":
                    return self._adjust_volume(-0.05)
                # 窗口大小：上一个选项
                elif self.current_menu == "window_size":
                    return self._change_window_size(-1)
            elif event.key == pygame.K_RIGHT:
                # 音量调节：增大音量
                if self.current_menu == "volume":
                    return self._adjust_volume(0.05)
                # 窗口大小：下一个选项
                elif self.current_menu == "window_size":
                    return self._change_window_size(1)

        return None

    def _handle_confirm_event(self, event):
        """处理确认读档对话框事件"""
        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self._confirm_choice = 1 - self._confirm_choice
        elif event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
            if self._confirm_choice == 0:
                # 确认读档
                slot = self._pending_load_slot
                self._pending_load_slot = None
                self.close()
                return ("load_confirm", slot)
            else:
                # 取消
                self._pending_load_slot = None
                self.current_menu = "load"
                self.selected_index = 0
        elif event.key == pygame.K_ESCAPE:
            self._pending_load_slot = None
            self.current_menu = "load"
            self.selected_index = 0
        return None

    def _move_selection(self, direction):
        """移动选中项"""
        items = self._get_current_items()
        if not items:
            return

        # 跳过空存档槽位（读档菜单中）
        if self.current_menu in ("load", "title_load"):
            for _ in range(len(items)):
                self.selected_index = (self.selected_index + direction) % len(items)
                if self.selected_index < len(items):
                    action = items[self.selected_index][0]
                    if action == "back":
                        break
                    # 检查该槽位是否有存档
                    slot_id = self._action_to_slot_id(action)
                    if slot_id and self._is_slot_empty(slot_id):
                        continue  # 跳过空槽位
                    break
        else:
            self.selected_index = (self.selected_index + direction) % len(items)

    def _is_slot_empty(self, slot_id):
        """检查存档槽位是否为空"""
        for info in self._save_infos:
            if info.get("slot_id") == slot_id:
                return info.get("empty", True)
        return True

    def _get_slot_info(self, slot_id):
        """获取存档槽位信息"""
        for info in self._save_infos:
            if info.get("slot_id") == slot_id:
                return info
        return None

    def _confirm_selection(self):
        """确认选中项，返回对应动作"""
        items = self._get_current_items()
        if not items or self.selected_index >= len(items):
            return None

        action = items[self.selected_index][0]

        if action == "back":
            if self.current_menu == "title_load":
                return "cancel_title_load"
            self.current_menu = "pause"
            self.selected_index = 0
            return None

        if action == "save":
            self.current_menu = "save"
            self.selected_index = 0
            return "open_save"

        if action == "load":
            self.current_menu = "load"
            self.selected_index = 0
            return "open_load"

        if action == "settings":
            self.current_menu = "settings"
            self.selected_index = 0
            return "open_settings"

        if action == "volume":
            self.current_menu = "volume"
            self.selected_index = 0
            return "open_volume"

        if action == "window_size":
            self.current_menu = "window_size"
            self.selected_index = 0
            return "open_window_size"

        # 读档菜单中的槽位选择
        if action.startswith("load_"):
            slot_id = self._action_to_slot_id(action)
            if slot_id and not self._is_slot_empty(slot_id):
                self._pending_load_slot = slot_id
                self.current_menu = "confirm_load"
                self._confirm_choice = 0
                return None  # 进入确认对话框

        # 窗口大小选择
        if action.startswith("size_"):
            idx = int(action.split("_")[1])
            if idx < len(WINDOW_SIZE_OPTIONS):
                w, h, _ = WINDOW_SIZE_OPTIONS[idx]
                self._window_size_index = idx
                self._current_window_size = (w, h)
                return ("window_size_change", w, h)

        return action

    def _action_to_slot_id(self, action):
        """将菜单action转换为存档槽位ID"""
        mapping = {
            "auto_save": "auto",
            "slot_1": "slot_1",
            "slot_2": "slot_2",
            "load_auto": "auto",
            "load_slot_1": "slot_1",
            "load_slot_2": "slot_2",
        }
        return mapping.get(action)

    def _get_current_items(self):
        """获取当前菜单的项目列表"""
        if self.current_menu == "pause":
            return PAUSE_MENU_ITEMS
        elif self.current_menu == "save":
            return SAVE_MENU_ITEMS
        elif self.current_menu == "load":
            return LOAD_MENU_ITEMS
        elif self.current_menu == "title_load":
            return TITLE_LOAD_MENU_ITEMS
        elif self.current_menu == "settings":
            return SETTINGS_MENU_ITEMS
        elif self.current_menu == "volume":
            return VOLUME_MENU_ITEMS
        elif self.current_menu == "window_size":
            # 窗口大小菜单项动态生成
            return [(f"size_{i}", opt[2]) for i, opt in enumerate(WINDOW_SIZE_OPTIONS)] + [("back", "返回")]
        return []

    def set_save_infos(self, save_infos):
        """设置存档槽位信息（用于显示存档/读档菜单）"""
        self._save_infos = save_infos

    def set_save_message(self, message):
        """设置存档操作提示消息"""
        self._save_message = message
        self._save_message_timer = 2.0

    def set_volumes(self, master, bgm, sfx):
        """设置音量值（从音频管理器同步）"""
        self._master_volume = master
        self._bgm_volume = bgm
        self._sfx_volume = sfx

    def get_volumes(self):
        """获取音量值"""
        return self._master_volume, self._bgm_volume, self._sfx_volume

    def set_window_size(self, width, height):
        """设置当前窗口大小"""
        self._current_window_size = (width, height)
        # 查找匹配的索引
        for i, (w, h, _) in enumerate(WINDOW_SIZE_OPTIONS):
            if w == width and h == height:
                self._window_size_index = i
                break

    def _adjust_volume(self, delta):
        """调整音量，返回音量变更动作"""
        items = VOLUME_MENU_ITEMS
        if self.selected_index < len(items):
            action = items[self.selected_index][0]
            if action == "master_volume":
                self._master_volume = max(0.0, min(1.0, self._master_volume + delta))
                return ("volume_change", "master", self._master_volume)
            elif action == "bgm_volume":
                self._bgm_volume = max(0.0, min(1.0, self._bgm_volume + delta))
                return ("volume_change", "bgm", self._bgm_volume)
            elif action == "sfx_volume":
                self._sfx_volume = max(0.0, min(1.0, self._sfx_volume + delta))
                return ("volume_change", "sfx", self._sfx_volume)
        return None

    def _change_window_size(self, direction):
        """切换窗口大小选项"""
        new_index = self._window_size_index + direction
        new_index = max(0, min(len(WINDOW_SIZE_OPTIONS) - 1, new_index))
        if new_index != self._window_size_index:
            self._window_size_index = new_index
            w, h, _ = WINDOW_SIZE_OPTIONS[new_index]
            self._current_window_size = (w, h)
            return ("window_size_change", w, h)
        return None

    def get_save_slot_id(self):
        """获取当前选中的存档槽位ID（存档菜单用）"""
        items = self._get_current_items()
        if self.selected_index < len(items):
            action = items[self.selected_index][0]
            return self._action_to_slot_id(action)
        return None

    def draw(self, surface):
        """绘制菜单"""
        if not self.active:
            return

        # 半透明遮罩（根据昼夜时段调整色调）
        overlay = pygame.Surface(
            (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill(self._get_overlay_color())
        surface.blit(overlay, (0, 0))

        if self.current_menu == "pause":
            self._draw_pause_menu(surface)
        elif self.current_menu == "save":
            self._draw_save_menu(surface, "存档")
        elif self.current_menu == "load":
            self._draw_load_menu(surface, "读档")
        elif self.current_menu == "title_load":
            self._draw_load_menu(surface, "继续游戏")
        elif self.current_menu == "settings":
            self._draw_settings_menu(surface)
        elif self.current_menu == "volume":
            self._draw_volume_menu(surface)
        elif self.current_menu == "window_size":
            self._draw_window_size_menu(surface)
        elif self.current_menu == "confirm_load":
            self._draw_confirm_load(surface)

    def _draw_indicator(self, surface, x, y, color):
        """绘制选中指示器（右指三角形），替代不兼容的▶字符"""
        # 绘制5x7像素的右指三角形
        points = [(x, y), (x, y + 7), (x + 5, y + 3)]
        pygame.draw.polygon(surface, color, points)

    def _draw_pause_menu(self, surface):
        """绘制暂停主菜单"""
        title = self.title_font.render("暂停", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 70,
        )
        surface.blit(title, title_rect)

        items = PAUSE_MENU_ITEMS
        start_y = INTERNAL_HEIGHT // 2 - 45
        item_height = 14
        item_spacing = 2

        for i, (action, label) in enumerate(items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_index)

            bg_rect = pygame.Rect(
                INTERNAL_WIDTH // 2 - 50, y - 1,
                100, item_height + 2,
            )
            self._draw_button_bg(surface, bg_rect, is_selected)

            color = MENU_ITEM_HOVER_COLOR if is_selected else MENU_ITEM_COLOR
            if is_selected:
                self._draw_indicator(surface, INTERNAL_WIDTH // 2 - 56, y, MENU_TITLE_COLOR)

            text = self.font.render(label, True, color)
            text_rect = text.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=y + item_height // 2,
            )
            surface.blit(text, text_rect)

    def _draw_save_menu(self, surface, title_text):
        """绘制存档菜单"""
        title = self.title_font.render(title_text, True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 70,
        )
        surface.blit(title, title_rect)

        items = SAVE_MENU_ITEMS
        start_y = INTERNAL_HEIGHT // 2 - 40
        item_height = 20
        item_spacing = 4

        for i, (action, label) in enumerate(items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_index)

            bg_rect = pygame.Rect(
                INTERNAL_WIDTH // 2 - 70, y - 1,
                140, item_height + 2,
            )
            self._draw_button_bg(surface, bg_rect, is_selected)

            color = MENU_ITEM_HOVER_COLOR if is_selected else MENU_ITEM_COLOR
            if is_selected:
                self._draw_indicator(surface, INTERNAL_WIDTH // 2 - 76, y, MENU_TITLE_COLOR)

            text = self.font.render(label, True, color)
            text_rect = text.get_rect(
                centerx=INTERNAL_WIDTH // 2 - 20, centery=y + item_height // 2,
            )
            surface.blit(text, text_rect)

            # 存档信息（通过slot_id查找，而非索引）
            if action != "back":
                slot_id = self._action_to_slot_id(action)
                info = self._get_slot_info(slot_id) if slot_id else None
                if info and not info.get("empty", True):
                    save_time = info.get("save_time", "")
                    badge_count = info.get("badge_count", 0)
                    info_text = self._small_font.render(
                        f"{save_time} 徽章:{badge_count}/7",
                        True, SAVE_INFO_COLOR,
                    )
                    surface.blit(info_text, (INTERNAL_WIDTH // 2 + 10, y + 4))
                else:
                    empty_text = self._small_font.render(EMPTY_SLOT_TEXT, True, MENU_ITEM_DISABLED_COLOR)
                    surface.blit(empty_text, (INTERNAL_WIDTH // 2 + 10, y + 4))

        if self._save_message:
            msg_text = self.font.render(
                self._save_message, True, (100, 255, 100)
            )
            msg_rect = msg_text.get_rect(
                centerx=INTERNAL_WIDTH // 2,
                centery=start_y + len(items) * (item_height + item_spacing) + 10,
            )
            surface.blit(msg_text, msg_rect)

    def _draw_load_menu(self, surface, title_text):
        """绘制读档菜单"""
        title = self.title_font.render(title_text, True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 70,
        )
        surface.blit(title, title_rect)

        items = self._get_current_items()
        start_y = INTERNAL_HEIGHT // 2 - 40
        item_height = 20
        item_spacing = 4

        for i, (action, label) in enumerate(items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_index)

            # 判断该槽位是否为空
            slot_id = self._action_to_slot_id(action)
            is_empty = slot_id and self._is_slot_empty(slot_id) if slot_id else False

            if is_selected and not is_empty:
                bg_rect = pygame.Rect(
                    INTERNAL_WIDTH // 2 - 70, y - 1,
                    140, item_height + 2,
                )
                self._draw_button_bg(surface, bg_rect, is_selected)
            elif is_selected:
                bg_rect = pygame.Rect(
                    INTERNAL_WIDTH // 2 - 70, y - 1,
                    140, item_height + 2,
                )
                self._draw_button_bg(surface, bg_rect, is_selected)

            # 颜色：空槽位灰显
            if is_empty:
                color = MENU_ITEM_DISABLED_COLOR
            elif is_selected:
                color = MENU_ITEM_HOVER_COLOR
            else:
                color = MENU_ITEM_COLOR

            if is_selected and not is_empty:
                self._draw_indicator(surface, INTERNAL_WIDTH // 2 - 76, y, MENU_TITLE_COLOR)

            text = self.font.render(label, True, color)
            text_rect = text.get_rect(
                centerx=INTERNAL_WIDTH // 2 - 20, centery=y + item_height // 2,
            )
            surface.blit(text, text_rect)

            # 存档信息（通过slot_id查找，而非索引）
            if action != "back":
                slot_id = self._action_to_slot_id(action)
                info = self._get_slot_info(slot_id) if slot_id else None
                if info and not info.get("empty", True):
                    save_time = info.get("save_time", "")
                    badge_count = info.get("badge_count", 0)
                    info_text = self._small_font.render(
                        f"{save_time} 徽章:{badge_count}/7",
                        True, SAVE_INFO_COLOR if not is_empty else MENU_ITEM_DISABLED_COLOR,
                    )
                    surface.blit(info_text, (INTERNAL_WIDTH // 2 + 10, y + 4))
                else:
                    empty_text = self._small_font.render(EMPTY_SLOT_TEXT, True, MENU_ITEM_DISABLED_COLOR)
                    surface.blit(empty_text, (INTERNAL_WIDTH // 2 + 10, y + 4))

    def _draw_confirm_load(self, surface):
        """绘制读档确认对话框"""
        # 对话框背景
        box_w, box_h = 200, 50
        box_x = (INTERNAL_WIDTH - box_w) // 2
        box_y = (INTERNAL_HEIGHT - box_h) // 2

        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((20, 20, 40, 230))
        pygame.draw.rect(box_surf, MENU_BORDER_COLOR, (0, 0, box_w, box_h), 1)
        surface.blit(box_surf, (box_x, box_y))

        # 提示文字
        warn_text = self._small_font.render("读档将丢失当前未保存的进度", True, CONFIRM_COLOR)
        warn_rect = warn_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=box_y + 14,
        )
        surface.blit(warn_text, warn_rect)

        confirm_text = self._small_font.render("确认读档？", True, CONFIRM_COLOR)
        confirm_rect = confirm_text.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=box_y + 26,
        )
        surface.blit(confirm_text, confirm_rect)

        # 确认/取消按钮
        btn_y = box_y + 36
        confirm_btn = self.font.render("确认", True,
            MENU_ITEM_HOVER_COLOR if self._confirm_choice == 0 else MENU_ITEM_COLOR)
        cancel_btn = self.font.render("取消", True,
            MENU_ITEM_HOVER_COLOR if self._confirm_choice == 1 else MENU_ITEM_COLOR)

        surface.blit(confirm_btn, (INTERNAL_WIDTH // 2 - 30, btn_y))
        surface.blit(cancel_btn, (INTERNAL_WIDTH // 2 + 10, btn_y))

        # 选中指示器
        if self._confirm_choice == 0:
            self._draw_indicator(surface, INTERNAL_WIDTH // 2 - 40, btn_y, MENU_TITLE_COLOR)
        else:
            self._draw_indicator(surface, INTERNAL_WIDTH // 2 + 2, btn_y, MENU_TITLE_COLOR)

    def _draw_settings_menu(self, surface):
        """绘制设置菜单"""
        title = self.title_font.render("设置", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 60,
        )
        surface.blit(title, title_rect)

        items = SETTINGS_MENU_ITEMS
        start_y = INTERNAL_HEIGHT // 2 - 30
        item_height = 16
        item_spacing = 2

        for i, (action, label) in enumerate(items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_index)

            bg_rect = pygame.Rect(
                INTERNAL_WIDTH // 2 - 50, y - 1,
                100, item_height + 2,
            )
            self._draw_button_bg(surface, bg_rect, is_selected)

            color = MENU_ITEM_HOVER_COLOR if is_selected else MENU_ITEM_COLOR

            if is_selected:
                self._draw_indicator(surface, INTERNAL_WIDTH // 2 - 56, y, MENU_TITLE_COLOR)

            text = self.font.render(label, True, color)
            text_rect = text.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=y + item_height // 2,
            )
            surface.blit(text, text_rect)

        if self.selected_index == 2:
            controls = [
                "WASD/方向键：移动",
                "Shift：冲刺",
                "F/空格：互动",
                "Tab/I：背包",
                "J：任务日志",
                "M：地图",
                "Esc：菜单",
            ]
            cy = start_y + len(items) * (item_height + item_spacing) + 8
            for line in controls:
                ctrl_text = self._small_font.render(line, True, SAVE_INFO_COLOR)
                ctrl_rect = ctrl_text.get_rect(
                    centerx=INTERNAL_WIDTH // 2, centery=cy,
                )
                surface.blit(ctrl_text, ctrl_rect)
                cy += 10

    def _draw_volume_menu(self, surface):
        """绘制音量调节菜单"""
        title = self.title_font.render("音量调节", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 70,
        )
        surface.blit(title, title_rect)

        items = VOLUME_MENU_ITEMS
        start_y = INTERNAL_HEIGHT // 2 - 40
        item_height = 20
        item_spacing = 6

        volumes = {
            "master_volume": self._master_volume,
            "bgm_volume": self._bgm_volume,
            "sfx_volume": self._sfx_volume,
        }

        for i, (action, label) in enumerate(items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_index)

            bg_rect = pygame.Rect(
                INTERNAL_WIDTH // 2 - 80, y - 1,
                160, item_height + 2,
            )
            self._draw_button_bg(surface, bg_rect, is_selected)

            if is_selected:
                self._draw_indicator(surface, INTERNAL_WIDTH // 2 - 86, y, MENU_TITLE_COLOR)

            # 标签
            color = MENU_ITEM_HOVER_COLOR if is_selected else MENU_ITEM_COLOR
            text = self.font.render(label, True, color)
            surface.blit(text, (INTERNAL_WIDTH // 2 - 70, y + 2))

            # 滑块（仅音量项）
            if action in volumes:
                volume = volumes[action]
                slider_x = INTERNAL_WIDTH // 2 - 10
                slider_y = y + 8
                slider_w = 70
                slider_h = 4

                # 滑块背景
                slider_bg = pygame.Surface((slider_w, slider_h), pygame.SRCALPHA)
                slider_bg.fill((40, 40, 60))
                surface.blit(slider_bg, (slider_x, slider_y))

                # 滑块填充
                fill_w = int(slider_w * volume)
                if fill_w > 0:
                    fill_color = (100, 200, 100) if volume > 0.3 else (220, 60, 60)
                    pygame.draw.rect(surface, fill_color, (slider_x, slider_y, fill_w, slider_h))

                # 滑块边框
                pygame.draw.rect(surface, (80, 80, 120), (slider_x, slider_y, slider_w, slider_h), 1)

                # 滑块手柄
                handle_x = slider_x + fill_w
                pygame.draw.rect(surface, MENU_TITLE_COLOR, (handle_x - 2, slider_y - 2, 5, slider_h + 4))

                # 百分比文字
                pct_text = self._small_font.render(f"{int(volume * 100)}%", True, SAVE_INFO_COLOR)
                surface.blit(pct_text, (slider_x + slider_w + 4, y + 4))

            # 操作提示
            if is_selected and action in volumes:
                hint = self._small_font.render("←→调节", True, (120, 120, 150))
                surface.blit(hint, (INTERNAL_WIDTH // 2 - 70, y + 14))

    def _draw_window_size_menu(self, surface):
        """绘制窗口大小选择菜单"""
        title = self.title_font.render("窗口大小", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 70,
        )
        surface.blit(title, title_rect)

        items = self._get_current_items()
        start_y = INTERNAL_HEIGHT // 2 - 40
        item_height = 16
        item_spacing = 2

        for i, (action, label) in enumerate(items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_index)

            # 检查是否为当前窗口大小
            is_current = False
            if action.startswith("size_"):
                idx = int(action.split("_")[1])
                if idx < len(WINDOW_SIZE_OPTIONS):
                    w, h, _ = WINDOW_SIZE_OPTIONS[idx]
                    is_current = (w == self._current_window_size[0] and h == self._current_window_size[1])

            if is_selected:
                bg_rect = pygame.Rect(
                    INTERNAL_WIDTH // 2 - 70, y - 1,
                    140, item_height + 2,
                )
                self._draw_button_bg(surface, bg_rect, is_selected)

            if is_selected:
                self._draw_indicator(surface, INTERNAL_WIDTH // 2 - 76, y, MENU_TITLE_COLOR)

            # 标签
            color = MENU_ITEM_HOVER_COLOR if is_selected else MENU_ITEM_COLOR
            text = self.font.render(label, True, color)
            text_rect = text.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=y + item_height // 2,
            )
            surface.blit(text, text_rect)

            # 当前选中标记（程序化绘制勾号，避免字体不支持✓）
            if is_current:
                cx = INTERNAL_WIDTH // 2 + 62
                cy = y + 5
                pygame.draw.lines(surface, QUEST_SOLVED_COLOR, False, [
                    (cx, cy + 3), (cx + 2, cy + 5), (cx + 6, cy),
                ], 1)

        # 操作提示
        hint = self._small_font.render("←→切换  F/回车确认", True, (120, 120, 150))
        hint_rect = hint.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=start_y + len(items) * (item_height + item_spacing) + 10,
        )
        surface.blit(hint, hint_rect)
