"""任务日志UI — 线索卡片式布局+小图标，谜题进度、已获线索汇总

按J键或从暂停菜单进入，显示当前谜题进度和已获取的线索道具。
采用卡片式布局，每条线索带小图标。
"""

import os
import json
import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    FONT_TITLE_SIZE,
    COLOR_WHITE,
    COLOR_BLACK,
)
from ui.dialog_box import create_border_surface, draw_nine_slice

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 颜色定义
QUEST_BG_COLOR = (0, 0, 0, 180)
QUEST_TITLE_COLOR = (255, 215, 0)
QUEST_CARD_BG = (30, 30, 50, 200)
QUEST_CARD_BORDER = (80, 80, 120)
QUEST_CARD_SELECTED_BG = (40, 40, 70, 220)
QUEST_TEXT_COLOR = (220, 220, 220)
QUEST_DESC_COLOR = (160, 160, 180)
QUEST_SOLVED_COLOR = (100, 220, 100)
QUEST_UNDISCOVERED_COLOR = (80, 80, 100)
QUEST_IN_PROGRESS_COLOR = (255, 200, 80)
QUEST_CLUE_ICON_COLOR = (255, 215, 0)
QUEST_PUZZLE_ICON_COLOR = (120, 180, 255)
QUEST_BADGE_ICON_COLOR = (255, 180, 50)

# 谜题进度描述
PUZZLE_PROGRESS_TEXT = {
    "undiscovered": "未发现",
    "discovered": "已发现",
    "in_progress": "进行中",
    "solved": "已完成",
}

# 谜题图标颜色（按难度）
DIFFICULTY_COLORS = {
    1: (100, 200, 100),   # 简单：绿色
    2: (255, 200, 80),    # 中等：黄色
    3: (220, 80, 80),    # 困难：红色
}


class QuestLog:
    """任务日志界面

    布局：
    ┌─────────────────────────────────────────────┐
    │              任务日志                         │
    │                                             │
    │  ┌─ 谜题进度 ─────────────────────────┐     │
    │  │ [桂花密语] ★☆☆ 已完成 ✓          │     │
    │  │ [建校之钥] ★★☆ 进行中             │     │
    │  │ [书海寻踪] ★★★ 未发现             │     │
    │  │ ...                                │     │
    │  └────────────────────────────────────┘     │
    │                                             │
    │  ┌─ 已获线索 ─────────────────────────┐     │
    │  │ [📋] 公告栏残页 - 1903年...        │     │
    │  │ [📋] 索书号便签 - K291.5/Z3        │     │
    │  │ ...                                │     │
    │  └────────────────────────────────────┘     │
    │                                             │
    │  按 J 或 Esc 返回游戏                        │
    └─────────────────────────────────────────────┘
    """

    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        self._small_font = pygame.font.Font(FONT_PATH, 8)

        self.active = False
        self.scroll_offset = 0
        self._max_scroll = 0

        # 边框素材
        self._border_image = create_border_surface(
            size=24, border_width=3,
            border_color=QUEST_CARD_BORDER,
            bg_color=(20, 20, 40, 220),
        )

        # 加载道具数据
        self._items_data = self._load_items_data()
        self._puzzles_data = self._load_puzzles_data()

    def _load_items_data(self):
        """加载道具数据"""
        path = os.path.join(PROJECT_ROOT, "data", "items.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _load_puzzles_data(self):
        """加载谜题数据"""
        path = os.path.join(PROJECT_ROOT, "data", "puzzles.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def open(self):
        """打开任务日志"""
        self.active = True
        self.scroll_offset = 0

    def close(self):
        """关闭任务日志"""
        self.active = False
        self.scroll_offset = 0

    def handle_event(self, event):
        """处理输入事件"""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_j, pygame.K_ESCAPE, pygame.K_TAB):
                return "close"
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 10)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self._max_scroll, self.scroll_offset + 10)

        # 鼠标滚轮
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(
                self._max_scroll,
                self.scroll_offset - event.y * 10,
            ))

        return None

    def update(self, dt):
        """更新状态"""
        pass

    def draw(self, surface, puzzle_manager, inventory):
        """绘制任务日志

        Args:
            surface: 内部分辨率Surface
            puzzle_manager: 谜题管理器
            inventory: 玩家背包
        """
        if not self.active:
            return

        # 半透明背景
        overlay = pygame.Surface(
            (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill(QUEST_BG_COLOR)
        surface.blit(overlay, (0, 0))

        # 标题
        title = self.title_font.render("任务日志", True, QUEST_TITLE_COLOR)
        title_rect = title.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=16,
        )
        surface.blit(title, title_rect)

        # 创建裁剪区域（内容区域）
        content_y_start = 30
        content_y_end = INTERNAL_HEIGHT - 16
        content_height = content_y_end - content_y_start

        # 绘制内容到临时Surface（支持滚动）
        content_surf = pygame.Surface(
            (INTERNAL_WIDTH, max(content_height, 300)), pygame.SRCALPHA
        )

        cy = 0
        cy = self._draw_puzzle_progress(content_surf, cy, puzzle_manager)
        cy += 6
        cy = self._draw_clue_section(content_surf, cy, inventory)

        # 更新最大滚动量
        self._max_scroll = max(0, cy - content_height)

        # 裁剪绘制
        src_rect = pygame.Rect(
            0, self.scroll_offset,
            INTERNAL_WIDTH, content_height,
        )
        # 确保不超出范围
        if src_rect.bottom > content_surf.get_height():
            src_rect.height = content_surf.get_height() - src_rect.top
        if src_rect.height > 0:
            surface.blit(content_surf, (0, content_y_start), src_rect)

        # 底部提示
        hint = self._small_font.render("按 J 或 Esc 返回游戏", True, (180, 180, 200))
        hint_rect = hint.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=INTERNAL_HEIGHT - 8,
        )
        surface.blit(hint, hint_rect)

        # 滚动条指示
        if self._max_scroll > 0:
            bar_height = max(10, int(content_height * content_height / cy))
            bar_y = content_y_start + int(
                self.scroll_offset / max(self._max_scroll, 1) * (content_height - bar_height)
            )
            bar_surf = pygame.Surface((3, bar_height), pygame.SRCALPHA)
            bar_surf.fill((100, 100, 140, 150))
            surface.blit(bar_surf, (INTERNAL_WIDTH - 5, bar_y))

    def _draw_puzzle_progress(self, surface, start_y, puzzle_manager):
        """绘制谜题进度区域

        Args:
            surface: 目标Surface
            start_y: 起始Y坐标
            puzzle_manager: 谜题管理器
        Returns:
            结束Y坐标
        """
        y = start_y

        # 区域标题
        section_title = self.font.render("— 谜题进度 —", True, QUEST_PUZZLE_ICON_COLOR)
        section_rect = section_title.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=y + 6,
        )
        surface.blit(section_title, section_rect)
        y += 16

        # 绘制每个谜题的进度卡片
        puzzle_ids = ["guizhong", "nanhulou", "library", "boya", "gym", "dining_hall", "fountain"]
        for puzzle_id in puzzle_ids:
            state = puzzle_manager.get_state(puzzle_id)
            puzzle_info = self._puzzles_data.get(puzzle_id, {})
            name = puzzle_info.get("name", puzzle_id)
            difficulty = puzzle_info.get("difficulty", 1)
            location = puzzle_info.get("location", "")
            night_only = puzzle_info.get("night_only", False)

            y = self._draw_puzzle_card(surface, y, puzzle_id, name, state, difficulty, location, night_only)
            y += 3

        return y

    def _draw_puzzle_card(self, surface, y, puzzle_id, name, state, difficulty, location, night_only):
        """绘制单个谜题进度卡片"""
        card_w = INTERNAL_WIDTH - 20
        card_h = 18
        card_x = 10

        # 卡片背景
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        if state.value == "solved":
            card_surf.fill((20, 40, 20, 180))
        else:
            card_surf.fill(QUEST_CARD_BG)
        surface.blit(card_surf, (card_x, y))

        # 卡片边框
        pygame.draw.rect(surface, QUEST_CARD_BORDER, (card_x, y, card_w, card_h), 1)

        # 谜题图标（小方块）
        icon_color = DIFFICULTY_COLORS.get(difficulty, (200, 200, 200))
        pygame.draw.rect(surface, icon_color, (card_x + 3, y + 3, 6, 6))

        # 谜题名称
        name_text = self.font.render(name, True, QUEST_TEXT_COLOR)
        surface.blit(name_text, (card_x + 14, y + 2))

        # 难度星星
        star_x = card_x + 14 + name_text.get_width() + 4
        for i in range(3):
            color = icon_color if i < difficulty else (60, 60, 80)
            self._draw_star(surface, star_x + i * 8, y + 5, 3, color)

        # 状态文字
        state_text = PUZZLE_PROGRESS_TEXT.get(state.value, state.value)
        if state.value == "solved":
            state_color = QUEST_SOLVED_COLOR
            state_text = "已完成"
        elif state.value == "in_progress":
            state_color = QUEST_IN_PROGRESS_COLOR
        elif state.value == "undiscovered":
            state_color = QUEST_UNDISCOVERED_COLOR
        else:
            state_color = QUEST_DESC_COLOR

        state_surf = self._small_font.render(state_text, True, state_color)
        surface.blit(state_surf, (card_x + card_w - state_surf.get_width() - 4, y + 4))

        # 夜晚限定标记
        if night_only:
            night_text = self._small_font.render("夜", True, (120, 140, 220))
            surface.blit(night_text, (card_x + card_w - state_surf.get_width() - 16, y + 4))

        return y + card_h

    def _draw_star(self, surface, x, y, size, color):
        """绘制小星星"""
        points = [
            (x, y - size),
            (x + size * 0.3, y - size * 0.3),
            (x + size, y - size * 0.3),
            (x + size * 0.5, y + size * 0.1),
            (x + size * 0.7, y + size),
            (x, y + size * 0.4),
            (x - size * 0.7, y + size),
            (x - size * 0.5, y + size * 0.1),
            (x - size, y - size * 0.3),
            (x - size * 0.3, y - size * 0.3),
        ]
        if len(points) >= 3:
            pygame.draw.polygon(surface, color, points)

    def _draw_clue_section(self, surface, start_y, inventory):
        """绘制已获线索区域

        Args:
            surface: 目标Surface
            start_y: 起始Y坐标
            inventory: 玩家背包
        Returns:
            结束Y坐标
        """
        y = start_y

        # 区域标题
        section_title = self.font.render("— 已获线索 —", True, QUEST_CLUE_ICON_COLOR)
        section_rect = section_title.get_rect(
            centerx=INTERNAL_WIDTH // 2, centery=y + 6,
        )
        surface.blit(section_title, section_rect)
        y += 16

        # 收集所有线索类道具
        clue_items = []
        for item in inventory.items:
            item_data = self._items_data.get(item.id, {})
            category = item_data.get("category", item.category if hasattr(item, 'category') else "")
            if category in ("clue", "key_item", "material"):
                clue_items.append((item, item_data))

        if not clue_items:
            # 无线索
            empty_text = self._small_font.render("暂无线索", True, QUEST_UNDISCOVERED_COLOR)
            empty_rect = empty_text.get_rect(
                centerx=INTERNAL_WIDTH // 2, centery=y + 8,
            )
            surface.blit(empty_text, empty_rect)
            y += 20
        else:
            for item, item_data in clue_items:
                y = self._draw_clue_card(surface, y, item, item_data)
                y += 2

        return y

    def _draw_clue_card(self, surface, y, item, item_data):
        """绘制单条线索卡片"""
        card_w = INTERNAL_WIDTH - 20
        card_h = 22
        card_x = 10

        # 卡片背景
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill(QUEST_CARD_BG)
        surface.blit(card_surf, (card_x, y))

        # 卡片边框
        pygame.draw.rect(surface, QUEST_CARD_BORDER, (card_x, y, card_w, card_h), 1)

        # 图标（根据类别不同颜色）
        category = item_data.get("category", "clue")
        if category == "key_item":
            icon_color = QUEST_BADGE_ICON_COLOR
            icon_char = "★"
        elif category == "material":
            icon_color = (150, 200, 150)
            icon_char = "◆"
        else:
            icon_color = QUEST_CLUE_ICON_COLOR
            icon_char = "●"

        # 绘制图标
        icon_text = self._small_font.render(icon_char, True, icon_color)
        surface.blit(icon_text, (card_x + 4, y + 3))

        # 道具名称
        name = item_data.get("name", item.id)
        name_text = self.font.render(name, True, QUEST_TEXT_COLOR)
        surface.blit(name_text, (card_x + 16, y + 1))

        # 简短描述（截断显示）
        description = item_data.get("description", "")
        # 截取前15个字符
        if len(description) > 15:
            description = description[:15] + "…"
        desc_text = self._small_font.render(description, True, QUEST_DESC_COLOR)
        surface.blit(desc_text, (card_x + 16, y + 13))

        return y + card_h
