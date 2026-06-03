"""HUD抬头显示 — 体力条、徽章进度、游戏时间

阶段1实现：矩形体力条+文字徽章进度+文字时间
阶段2替换：桂花形体力图标+桂花形徽章图标+像素风字体+太阳/月亮图标
"""

import os
import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    MAX_STAMINA,
    COLOR_WHITE,
    COLOR_BLACK,
)


# 体力条颜色
STAMINA_COLOR_HIGH = (80, 200, 80)      # 体力充足：绿色
STAMINA_COLOR_MID = (220, 200, 60)      # 体力中等：黄色
STAMINA_COLOR_LOW = (220, 60, 60)       # 体力不足：红色
STAMINA_BG_COLOR = (40, 40, 50, 180)    # 体力条背景

# HUD整体背景
HUD_BG_COLOR = (0, 0, 0, 100)

# 徽章图标颜色
BADGE_FILLED_COLOR = (255, 215, 0)      # 已获得：金色
BADGE_EMPTY_COLOR = (80, 80, 100)       # 未获得：灰色

# HUD布局参数
HUD_MARGIN = 4
HUD_PADDING = 4
STAMINA_BAR_WIDTH = 60
STAMINA_BAR_HEIGHT = 6
BADGE_ICON_SIZE = 6
BADGE_ICON_GAP = 2


class HUD:
    """HUD抬头显示"""

    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self._small_font = pygame.font.Font(FONT_PATH, 8)

        # 尝试加载HUD精灵图
        self._stamina_sprites = {}
        self._badge_sprites = {}
        self._load_sprites()

    def _load_sprites(self):
        """加载HUD相关精灵图（阶段2素材，可能不存在）"""
        sprites_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "ui", "sprites",
        )
        # 体力条图标
        for name in ("hud_stamina_full", "hud_stamina_half", "hud_stamina_low"):
            path = os.path.join(sprites_dir, f"{name}.png")
            if os.path.exists(path):
                try:
                    self._stamina_sprites[name] = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    pass

        # 徽章图标
        for name in ("badge_filled", "badge_empty"):
            path = os.path.join(sprites_dir, f"{name}.png")
            if os.path.exists(path):
                try:
                    self._badge_sprites[name] = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    pass

    def draw(self, surface, player, puzzle_manager, game_clock):
        """绘制HUD

        布局：左上角
        ┌──────────────────────────────────┐
        │ 体力 85/100  徽章 3/7  第1天 14:30│
        └──────────────────────────────────┘
        """
        stamina = player.stamina
        badge_count = puzzle_manager.get_badge_count(player.inventory)
        day_count = game_clock.day_count
        time_str = game_clock.get_time_string()
        period_name = game_clock.get_period_name()

        x = HUD_MARGIN + HUD_PADDING
        y = HUD_MARGIN + HUD_PADDING

        # 先绘制各元素到临时Surface以测量总宽度
        temp_surf = pygame.Surface((INTERNAL_WIDTH, 30), pygame.SRCALPHA)
        end_x = self._draw_all(temp_surf, x, y, stamina, badge_count, day_count, time_str, period_name)

        # 绘制半透明背景遮罩（问题7修复）
        bg_width = end_x - x + HUD_PADDING * 2
        bg_height = 14 + HUD_PADDING * 2
        bg_rect = pygame.Rect(HUD_MARGIN, HUD_MARGIN, bg_width, bg_height)
        bg_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 100))
        surface.blit(bg_surf, bg_rect.topleft)

        # 在游戏画面上绘制HUD元素
        self._draw_all(surface, x, y, stamina, badge_count, day_count, time_str, period_name)

    def _draw_all(self, surface, x, y, stamina, badge_count, day_count, time_str, period_name):
        """绘制所有HUD元素，返回结束x坐标"""
        x = self._draw_stamina(surface, x, y, stamina)
        x += 8
        x = self._draw_badges(surface, x, y, badge_count)
        x += 8
        x = self._draw_time(surface, x, y, day_count, time_str, period_name)
        return x

    def _draw_stamina(self, surface, x, y, stamina):
        """绘制体力条"""
        # 标签
        label = self.font.render("体力", True, COLOR_WHITE)
        surface.blit(label, (x, y))
        x += label.get_width() + 2

        # 体力条背景
        bar_x = x
        bar_y = y + 2
        bar_bg = pygame.Surface((STAMINA_BAR_WIDTH, STAMINA_BAR_HEIGHT), pygame.SRCALPHA)
        bar_bg.fill(STAMINA_BG_COLOR)
        surface.blit(bar_bg, (bar_x, bar_y))

        # 体力条填充
        fill_ratio = max(0, min(1, stamina / MAX_STAMINA))
        fill_width = int(STAMINA_BAR_WIDTH * fill_ratio)
        if fill_width > 0:
            if fill_ratio > 0.5:
                color = STAMINA_COLOR_HIGH
            elif fill_ratio > 0.25:
                color = STAMINA_COLOR_MID
            else:
                color = STAMINA_COLOR_LOW
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, STAMINA_BAR_HEIGHT)
            pygame.draw.rect(surface, color, fill_rect)

        # 体力条边框
        pygame.draw.rect(
            surface, (100, 100, 120),
            (bar_x, bar_y, STAMINA_BAR_WIDTH, STAMINA_BAR_HEIGHT), 1,
        )

        x += STAMINA_BAR_WIDTH + 2

        # 数值
        value_text = self._small_font.render(
            f"{int(stamina)}/{MAX_STAMINA}", True, COLOR_WHITE
        )
        surface.blit(value_text, (x, y + 1))
        x += value_text.get_width()

        return x

    def _draw_badges(self, surface, x, y, badge_count):
        """绘制徽章进度"""
        # 标签
        label = self.font.render("徽章", True, COLOR_WHITE)
        surface.blit(label, (x, y))
        x += label.get_width() + 2

        # 如果有精灵图，使用精灵图绘制7个徽章图标
        if "badge_filled" in self._badge_sprites and "badge_empty" in self._badge_sprites:
            filled_img = self._badge_sprites["badge_filled"]
            empty_img = self._badge_sprites["badge_empty"]
            icon_w = BADGE_ICON_SIZE
            icon_h = BADGE_ICON_SIZE
            for i in range(7):
                img = filled_img if i < badge_count else empty_img
                scaled = pygame.transform.scale(img, (icon_w, icon_h))
                surface.blit(scaled, (x, y + 2))
                x += icon_w + BADGE_ICON_GAP
        else:
            # 阶段1：文字显示
            badge_text = self.font.render(
                f"{badge_count}/7", True, BADGE_FILLED_COLOR
            )
            surface.blit(badge_text, (x, y))
            x += badge_text.get_width()

        return x

    def _draw_time(self, surface, x, y, day_count, time_str, period_name):
        """绘制游戏时间"""
        day_text = self.font.render(f"第{day_count}天", True, COLOR_WHITE)
        surface.blit(day_text, (x, y))
        x += day_text.get_width() + 4

        time_text = self.font.render(time_str, True, COLOR_WHITE)
        surface.blit(time_text, (x, y))
        x += time_text.get_width() + 4

        # 时段小标签
        period_colors = {
            "白天": (255, 220, 100),
            "黄昏": (255, 150, 80),
            "夜晚": (120, 140, 220),
        }
        period_color = period_colors.get(period_name, COLOR_WHITE)
        period_text = self._small_font.render(period_name, True, period_color)
        surface.blit(period_text, (x, y + 2))
        x += period_text.get_width()

        return x
