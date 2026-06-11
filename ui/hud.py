"""HUD抬头显示 — 体力条、徽章进度、游戏时间

阶段1实现：矩形体力条+文字徽章进度+文字时间
阶段2替换：桂花形体力图标+桂花形徽章图标+像素风字体+太阳/月亮图标
阶段3打磨：平滑动画+低体力脉冲+昼夜色调
"""

import os
import math
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

# 昼夜色调叠加
HUD_TINT_DAY = (255, 240, 200, 15)      # 白天：暖色调
HUD_TINT_DUSK = (255, 180, 100, 20)     # 黄昏：橙色调
HUD_TINT_NIGHT = (100, 120, 200, 20)    # 夜晚：冷蓝色调

# 体力条动画参数
STAMINA_LERP_SPEED = 5.0                # 体力条平滑过渡速度
STAMINA_LOW_THRESHOLD = 0.25            # 低体力脉冲阈值（25%）
STAMINA_PULSE_SPEED = 3.0               # 低体力脉冲速度
STAMINA_PULSE_MIN_ALPHA = 0.3           # 低体力脉冲最小透明度


class HUD:
    """HUD抬头显示"""

    def __init__(self):
        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self._small_font = pygame.font.Font(FONT_PATH, 8)

        # 尝试加载HUD精灵图
        self._stamina_sprites = {}
        self._badge_sprites = {}
        self._icon_sprites = {}
        self._load_sprites()

        # 平滑动画：显示用体力值（向实际值渐变）
        self._displayed_stamina = float(MAX_STAMINA)
        # 低体力脉冲计时器
        self._pulse_timer = 0.0

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
        for name in ("badge_filled", "badge_empty", "hud_badge_icon"):
            path = os.path.join(sprites_dir, f"{name}.png")
            if os.path.exists(path):
                try:
                    self._badge_sprites[name] = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    pass

        # 太阳/月亮图标
        for name in ("hud_sun_icon", "hud_moon_icon"):
            path = os.path.join(sprites_dir, f"{name}.png")
            if os.path.exists(path):
                try:
                    self._icon_sprites[name] = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    pass

    def update(self, dt):
        """更新HUD动画状态

        每帧调用，用于平滑体力条过渡和低体力脉冲效果。
        """
        # 平滑过渡：显示值向实际值渐变
        diff = self._displayed_stamina - self._target_stamina
        if abs(diff) < 0.5:
            self._displayed_stamina = self._target_stamina
        else:
            self._displayed_stamina -= diff * STAMINA_LERP_SPEED * dt

        # 低体力脉冲计时
        self._pulse_timer += dt

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

        # 记录目标体力值（供update渐变使用）
        self._target_stamina = float(stamina)

        x = HUD_MARGIN + HUD_PADDING
        y = HUD_MARGIN + HUD_PADDING

        # 先绘制各元素到临时Surface以测量总宽度
        temp_surf = pygame.Surface((INTERNAL_WIDTH, 30), pygame.SRCALPHA)
        end_x = self._draw_all(temp_surf, x, y, stamina, badge_count, day_count, time_str, period_name)

        # 绘制半透明背景遮罩
        bg_width = end_x - x + HUD_PADDING * 2
        bg_height = 14 + HUD_PADDING * 2
        bg_rect = pygame.Rect(HUD_MARGIN, HUD_MARGIN, bg_width, bg_height)
        bg_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 100))

        # 昼夜色调叠加到背景
        tint = self._get_period_tint(period_name)
        if tint is not None:
            tint_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            tint_surf.fill(tint)
            bg_surf.blit(tint_surf, (0, 0))

        surface.blit(bg_surf, bg_rect.topleft)

        # 在游戏画面上绘制HUD元素
        self._draw_all(surface, x, y, stamina, badge_count, day_count, time_str, period_name)

    def _get_period_tint(self, period_name):
        """根据时段返回HUD背景色调"""
        if period_name == "白天":
            return HUD_TINT_DAY
        elif period_name == "黄昏":
            return HUD_TINT_DUSK
        elif period_name == "夜晚":
            return HUD_TINT_NIGHT
        return None

    def _get_stamina_color(self, ratio):
        """根据体力比例返回颜色"""
        if ratio > 0.5:
            return STAMINA_COLOR_HIGH
        elif ratio > 0.25:
            return STAMINA_COLOR_MID
        else:
            return STAMINA_COLOR_LOW

    def _get_stamina_sprite_key(self, ratio):
        """根据体力比例返回对应精灵图键名"""
        if ratio > 0.5:
            return "hud_stamina_full"
        elif ratio > 0.25:
            return "hud_stamina_half"
        else:
            return "hud_stamina_low"

    def _draw_all(self, surface, x, y, stamina, badge_count, day_count, time_str, period_name):
        """绘制所有HUD元素，返回结束x坐标"""
        x = self._draw_stamina(surface, x, y, stamina)
        x += 8
        x = self._draw_badges(surface, x, y, badge_count)
        x += 8
        x = self._draw_time(surface, x, y, day_count, time_str, period_name)
        return x

    def _draw_stamina(self, surface, x, y, stamina):
        """绘制体力条（桂花主题，带平滑动画和低体力脉冲）"""
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

        # 使用显示用体力值（平滑动画）
        display_ratio = max(0, min(1, self._displayed_stamina / MAX_STAMINA))
        fill_width = int(STAMINA_BAR_WIDTH * display_ratio)

        if fill_width > 0:
            color = self._get_stamina_color(display_ratio)
            sprite_key = self._get_stamina_sprite_key(display_ratio)

            # 尝试使用桂花精灵图作为填充纹理
            if sprite_key in self._stamina_sprites:
                sprite = self._stamina_sprites[sprite_key]
                # 缩放精灵图到体力条高度
                sprite_h = STAMINA_BAR_HEIGHT
                sprite_w = sprite.get_width()
                scaled_sprite = pygame.transform.scale(sprite, (sprite_w, sprite_h))

                # 裁剪精灵图到填充宽度
                fill_surf = pygame.Surface((fill_width, sprite_h), pygame.SRCALPHA)
                # 平铺精灵图填充
                offset = 0
                while offset < fill_width:
                    clip_w = min(sprite_w, fill_width - offset)
                    fill_surf.blit(scaled_sprite, (offset, 0), (0, 0, clip_w, sprite_h))
                    offset += sprite_w

                # 低体力脉冲效果
                if display_ratio <= STAMINA_LOW_THRESHOLD:
                    pulse = (math.sin(self._pulse_timer * STAMINA_PULSE_SPEED) + 1) / 2
                    pulse_alpha = int(255 * (STAMINA_PULSE_MIN_ALPHA + (1 - STAMINA_PULSE_MIN_ALPHA) * pulse))
                    fill_surf.set_alpha(pulse_alpha)

                surface.blit(fill_surf, (bar_x, bar_y))
            else:
                # 无精灵图时使用纯色填充
                fill_rect = pygame.Rect(bar_x, bar_y, fill_width, STAMINA_BAR_HEIGHT)
                pygame.draw.rect(surface, color, fill_rect)

                # 低体力脉冲效果（纯色模式）
                if display_ratio <= STAMINA_LOW_THRESHOLD:
                    pulse = (math.sin(self._pulse_timer * STAMINA_PULSE_SPEED) + 1) / 2
                    pulse_alpha = int(255 * (STAMINA_PULSE_MIN_ALPHA + (1 - STAMINA_PULSE_MIN_ALPHA) * pulse))
                    pulse_surf = pygame.Surface((fill_width, STAMINA_BAR_HEIGHT), pygame.SRCALPHA)
                    pulse_surf.fill((*color, pulse_alpha))
                    surface.blit(pulse_surf, (bar_x, bar_y))

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
        """绘制徽章进度（使用桂花徽章图标）"""
        # 如果有hud_badge_icon精灵图，使用它作为标签图标
        if "hud_badge_icon" in self._badge_sprites:
            icon = self._badge_sprites["hud_badge_icon"]
            icon_size = 10
            scaled_icon = pygame.transform.scale(icon, (icon_size, icon_size))
            surface.blit(scaled_icon, (x, y))
            x += icon_size + 2
        else:
            # 降级：文字标签
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
        """绘制游戏时间（带太阳/月亮图标）"""
        # 太阳/月亮图标
        icon_key = None
        if period_name == "白天":
            icon_key = "hud_sun_icon"
        elif period_name == "夜晚":
            icon_key = "hud_moon_icon"
        # 黄昏不显示图标

        if icon_key is not None and icon_key in self._icon_sprites:
            icon = self._icon_sprites[icon_key]
            icon_size = 10
            scaled_icon = pygame.transform.scale(icon, (icon_size, icon_size))
            surface.blit(scaled_icon, (x, y))
            x += icon_size + 2

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
