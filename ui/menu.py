"""暂停菜单 — 继续游戏/背包/校园地图/存档/设置/返回标题

采用自定义渲染层绘制像素风菜单，pygame_gui处理交互逻辑。
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


# 菜单项定义
PAUSE_MENU_ITEMS = [
    ("continue", "继续游戏"),
    ("inventory", "背包"),
    ("map", "校园地图"),
    ("save", "存档"),
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

# 设置菜单项
SETTINGS_MENU_ITEMS = [
    ("volume", "音量调节"),
    ("window_size", "窗口大小"),
    ("controls", "操作说明"),
    ("back", "返回"),
]

# 颜色
MENU_BG_COLOR = (0, 0, 0, 160)
MENU_BORDER_COLOR = (100, 100, 140)
MENU_TITLE_COLOR = (255, 215, 0)
MENU_ITEM_COLOR = (220, 220, 220)
MENU_ITEM_HOVER_COLOR = (255, 255, 255)
MENU_ITEM_HOVER_BG = (60, 60, 90, 180)
SAVE_INFO_COLOR = (160, 160, 180)


class Menu:
    """暂停菜单系统"""

    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        self._small_font = pygame.font.Font(FONT_PATH, 8)

        self.active = False
        self.current_menu = "pause"  # pause / save / settings
        self.selected_index = 0
        self._save_infos = []
        self._save_message = ""
        self._save_message_timer = 0.0

        # 边框素材
        self._border_image = create_border_surface(
            size=24, border_width=3,
            border_color=MENU_BORDER_COLOR,
            bg_color=(20, 20, 40, 220),
        )

    def open(self, menu_type="pause"):
        """打开菜单"""
        self.active = True
        self.current_menu = menu_type
        self.selected_index = 0
        self._save_message = ""
        self._save_message_timer = 0.0

    def close(self):
        """关闭菜单"""
        self.active = False
        self.current_menu = "pause"
        self.selected_index = 0

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
            if event.key == pygame.K_ESCAPE:
                if self.current_menu == "pause":
                    return "continue"
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

        return None

    def _move_selection(self, direction):
        """移动选中项"""
        items = self._get_current_items()
        if not items:
            return
        self.selected_index = (self.selected_index + direction) % len(items)

    def _confirm_selection(self):
        """确认选中项，返回对应动作"""
        items = self._get_current_items()
        if not items or self.selected_index >= len(items):
            return None

        action = items[self.selected_index][0]

        if action == "back":
            self.current_menu = "pause"
            self.selected_index = 0
            return None

        if action == "save":
            self.current_menu = "save"
            self.selected_index = 0
            return "open_save"

        if action == "settings":
            self.current_menu = "settings"
            self.selected_index = 0
            return "open_settings"

        return action

    def _get_current_items(self):
        """获取当前菜单的项目列表"""
        if self.current_menu == "pause":
            return PAUSE_MENU_ITEMS
        elif self.current_menu == "save":
            return SAVE_MENU_ITEMS
        elif self.current_menu == "settings":
            return SETTINGS_MENU_ITEMS
        return []

    def set_save_infos(self, save_infos):
        """设置存档槽位信息（用于显示存档菜单）"""
        self._save_infos = save_infos

    def set_save_message(self, message):
        """设置存档操作提示消息"""
        self._save_message = message
        self._save_message_timer = 2.0

    def get_save_slot_id(self):
        """获取当前选中的存档槽位ID"""
        items = self._get_current_items()
        if self.selected_index < len(items):
            action = items[self.selected_index][0]
            if action in ("auto_save", "slot_1", "slot_2"):
                slot_map = {
                    "auto_save": "auto",
                    "slot_1": "slot_1",
                    "slot_2": "slot_2",
                }
                return slot_map.get(action)
        return None

    def draw(self, surface):
        """绘制菜单"""
        if not self.active:
            return

        # 半透明遮罩
        overlay = pygame.Surface(
            (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill(MENU_BG_COLOR)
        surface.blit(overlay, (0, 0))

        if self.current_menu == "pause":
            self._draw_pause_menu(surface)
        elif self.current_menu == "save":
            self._draw_save_menu(surface)
        elif self.current_menu == "settings":
            self._draw_settings_menu(surface)

    def _draw_pause_menu(self, surface):
        """绘制暂停主菜单"""
        # 标题
        title = self.title_font.render("暂停", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 60,
        )
        surface.blit(title, title_rect)

        # 菜单项
        items = PAUSE_MENU_ITEMS
        start_y = INTERNAL_HEIGHT // 2 - 30
        item_height = 16
        item_spacing = 2

        for i, (action, label) in enumerate(items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_index)

            # 选中项背景
            if is_selected:
                bg_rect = pygame.Rect(
                    INTERNAL_WIDTH // 2 - 50, y - 1,
                    100, item_height + 2,
                )
                bg_surf = pygame.Surface(
                    (bg_rect.width, bg_rect.height), pygame.SRCALPHA
                )
                bg_surf.fill(MENU_ITEM_HOVER_BG)
                surface.blit(bg_surf, bg_rect.topleft)

            # 选中指示器
            color = MENU_ITEM_HOVER_COLOR if is_selected else MENU_ITEM_COLOR
            if is_selected:
                indicator = self.font.render("▶", True, MENU_TITLE_COLOR)
                surface.blit(indicator, (INTERNAL_WIDTH // 2 - 56, y))

            # 文字
            text = self.font.render(label, True, color)
            text_rect = text.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=y + item_height // 2,
            )
            surface.blit(text, text_rect)

    def _draw_save_menu(self, surface):
        """绘制存档菜单"""
        # 标题
        title = self.title_font.render("存档", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 70,
        )
        surface.blit(title, title_rect)

        # 存档槽位
        items = SAVE_MENU_ITEMS
        start_y = INTERNAL_HEIGHT // 2 - 40
        item_height = 20
        item_spacing = 4

        for i, (action, label) in enumerate(items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_index)

            # 选中项背景
            if is_selected:
                bg_rect = pygame.Rect(
                    INTERNAL_WIDTH // 2 - 70, y - 1,
                    140, item_height + 2,
                )
                bg_surf = pygame.Surface(
                    (bg_rect.width, bg_rect.height), pygame.SRCALPHA
                )
                bg_surf.fill(MENU_ITEM_HOVER_BG)
                surface.blit(bg_surf, bg_rect.topleft)

            color = MENU_ITEM_HOVER_COLOR if is_selected else MENU_ITEM_COLOR

            # 选中指示器
            if is_selected:
                indicator = self.font.render("▶", True, MENU_TITLE_COLOR)
                surface.blit(indicator, (INTERNAL_WIDTH // 2 - 76, y))

            # 槽位名称
            text = self.font.render(label, True, color)
            text_rect = text.get_rect(
                centerx=INTERNAL_WIDTH // 2 - 20, centery=y + item_height // 2,
            )
            surface.blit(text, text_rect)

            # 存档信息
            if action != "back" and i < len(self._save_infos):
                info = self._save_infos[i]
                if not info.get("empty", True):
                    save_time = info.get("save_time", "")
                    badge_count = info.get("badge_count", 0)
                    info_text = self._small_font.render(
                        f"{save_time} 徽章:{badge_count}/7",
                        True, SAVE_INFO_COLOR,
                    )
                    surface.blit(info_text, (INTERNAL_WIDTH // 2 + 10, y + 4))

        # 存档提示消息
        if self._save_message:
            msg_text = self.font.render(
                self._save_message, True, (100, 255, 100)
            )
            msg_rect = msg_text.get_rect(
                centerx=INTERNAL_WIDTH // 2,
                centery=start_y + len(items) * (item_height + item_spacing) + 10,
            )
            surface.blit(msg_text, msg_rect)

    def _draw_settings_menu(self, surface):
        """绘制设置菜单"""
        # 标题
        title = self.title_font.render("设置", True, MENU_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 60,
        )
        surface.blit(title, title_rect)

        # 设置项
        items = SETTINGS_MENU_ITEMS
        start_y = INTERNAL_HEIGHT // 2 - 30
        item_height = 16
        item_spacing = 2

        for i, (action, label) in enumerate(items):
            y = start_y + i * (item_height + item_spacing)
            is_selected = (i == self.selected_index)

            if is_selected:
                bg_rect = pygame.Rect(
                    INTERNAL_WIDTH // 2 - 50, y - 1,
                    100, item_height + 2,
                )
                bg_surf = pygame.Surface(
                    (bg_rect.width, bg_rect.height), pygame.SRCALPHA
                )
                bg_surf.fill(MENU_ITEM_HOVER_BG)
                surface.blit(bg_surf, bg_rect.topleft)

            color = MENU_ITEM_HOVER_COLOR if is_selected else MENU_ITEM_COLOR

            if is_selected:
                indicator = self.font.render("▶", True, MENU_TITLE_COLOR)
                surface.blit(indicator, (INTERNAL_WIDTH // 2 - 56, y))

            text = self.font.render(label, True, color)
            text_rect = text.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=y + item_height // 2,
            )
            surface.blit(text, text_rect)

        # 操作说明
        if self.selected_index == 2:  # 操作说明
            controls = [
                "WASD/方向键：移动",
                "Shift：冲刺",
                "F/空格：互动",
                "Tab/I：背包",
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
