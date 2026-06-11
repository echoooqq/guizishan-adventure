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
STAMINA_BG_COLOR = (30, 30, 40, 200)    # 体力条背景（深色凹陷感）
STAMINA_BAR_RADIUS = 2                  # 体力条圆角

# HUD槽位样式
SLOT_BG_COLOR = (20, 32, 20, 170)       # 槽位背景：深墨绿
SLOT_BORDER_COLOR = (55, 80, 55, 210)   # 槽位描边
SLOT_INNER_GLOW_COLOR = (45, 65, 45, 50) # 槽位内发光（凹陷感）
SLOT_HIGHLIGHT_COLOR = (85, 115, 85, 70) # 顶部内高光
SLOT_SHADOW_COLOR = (8, 12, 8, 90)      # 底部内阴影
SLOT_BORDER_RADIUS = 3                  # 圆角半径（像素）
SLOT_GAP = 3                            # 槽位间距

# 徽章图标颜色
BADGE_FILLED_COLOR = (255, 215, 0)      # 已获得：金色
BADGE_EMPTY_COLOR = (80, 80, 100)       # 未获得：灰色

# HUD布局参数
HUD_MARGIN = 4
HUD_PADDING = 4
STAMINA_BAR_WIDTH = 60
STAMINA_BAR_HEIGHT = 6
BADGE_ICON_SIZE = 6
BADGE_ICON_GAP = 3

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
        self._target_stamina = float(MAX_STAMINA)
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
        """绘制HUD（三槽分离式布局）

        布局：左上角
        ┌─────────┐  ┌──────┐  ┌──────────┐
        │体力 85% │  │徽章3/7│  │第1天 14:30│
        └─────────┘  └──────┘  └──────────┘
        """
        stamina = player.stamina
        badge_count = puzzle_manager.get_badge_count(player.inventory)
        day_count = game_clock.day_count
        time_str = game_clock.get_time_string()
        period_name = game_clock.get_period_name()

        # 记录目标体力值（供update渐变使用）
        self._target_stamina = float(stamina)

        # 昼夜色调
        tint = self._get_period_tint(period_name)

        # 逐槽绘制
        x = HUD_MARGIN
        y = HUD_MARGIN

        x = self._draw_stamina_slot(surface, x, y, stamina, tint)
        x += SLOT_GAP
        x = self._draw_badge_slot(surface, x, y, badge_count, tint)
        x += SLOT_GAP
        x = self._draw_time_slot(surface, x, y, day_count, time_str, period_name, tint)

    def _draw_slot_bg(self, surface, x, y, width, height, tint=None):
        """绘制单个槽位背景（圆角+描边+内发光+高光+阴影）"""
        bg_surf = pygame.Surface((width, height), pygame.SRCALPHA)

        # 圆角半透明背景
        pygame.draw.rect(bg_surf, SLOT_BG_COLOR, (0, 0, width, height),
                         border_radius=SLOT_BORDER_RADIUS)
        # 内发光（凹陷感：比背景稍亮的内边）
        inner_rect = (1, 1, width - 2, height - 2)
        pygame.draw.rect(bg_surf, SLOT_INNER_GLOW_COLOR, inner_rect, 1,
                         border_radius=max(1, SLOT_BORDER_RADIUS - 1))
        # 外描边
        pygame.draw.rect(bg_surf, SLOT_BORDER_COLOR, (0, 0, width, height), 1,
                         border_radius=SLOT_BORDER_RADIUS)
        # 顶部内高光
        pygame.draw.line(
            bg_surf, SLOT_HIGHLIGHT_COLOR,
            (SLOT_BORDER_RADIUS + 1, 1), (width - SLOT_BORDER_RADIUS - 2, 1)
        )
        # 底部内阴影
        pygame.draw.line(
            bg_surf, SLOT_SHADOW_COLOR,
            (SLOT_BORDER_RADIUS + 1, height - 2), (width - SLOT_BORDER_RADIUS - 2, height - 2)
        )

        # 昼夜色调叠加
        if tint is not None:
            tint_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(tint_surf, tint, (0, 0, width, height),
                             border_radius=SLOT_BORDER_RADIUS)
            bg_surf.blit(tint_surf, (0, 0))

        surface.blit(bg_surf, (x, y))

    def _measure_stamina_slot(self, stamina):
        """测量体力槽内容宽度"""
        x = 0
        label = self.font.render("体力", True, COLOR_WHITE)
        x += label.get_width() + 2
        x += STAMINA_BAR_WIDTH + 2
        value_text = self._small_font.render(f"{int(stamina)}/{MAX_STAMINA}", True, COLOR_WHITE)
        x += value_text.get_width()
        return x

    def _draw_stamina_bar(self, surface, bar_x, bar_y, display_ratio):
        """绘制圆角体力条（带高光线+低体力闪烁）"""
        # 圆角背景（凹陷槽）
        bar_bg = pygame.Surface((STAMINA_BAR_WIDTH, STAMINA_BAR_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(bar_bg, STAMINA_BG_COLOR,
                         (0, 0, STAMINA_BAR_WIDTH, STAMINA_BAR_HEIGHT),
                         border_radius=STAMINA_BAR_RADIUS)
        surface.blit(bar_bg, (bar_x, bar_y))

        # 填充
        fill_width = int(STAMINA_BAR_WIDTH * display_ratio)
        if fill_width <= 0:
            return

        color = self._get_stamina_color(display_ratio)
        sprite_key = self._get_stamina_sprite_key(display_ratio)

        # 低体力闪烁计算
        pulse_alpha = 255
        is_low = display_ratio <= STAMINA_LOW_THRESHOLD
        if is_low:
            pulse = (math.sin(self._pulse_timer * STAMINA_PULSE_SPEED) + 1) / 2
            pulse_alpha = int(255 * (STAMINA_PULSE_MIN_ALPHA + (1 - STAMINA_PULSE_MIN_ALPHA) * pulse))

        # 尝试使用桂花精灵图作为填充纹理
        if sprite_key in self._stamina_sprites:
            sprite = self._stamina_sprites[sprite_key]
            sprite_h = STAMINA_BAR_HEIGHT
            sprite_w = sprite.get_width()
            scaled_sprite = pygame.transform.scale(sprite, (sprite_w, sprite_h))

            fill_surf = pygame.Surface((fill_width, sprite_h), pygame.SRCALPHA)
            offset = 0
            while offset < fill_width:
                clip_w = min(sprite_w, fill_width - offset)
                fill_surf.blit(scaled_sprite, (offset, 0), (0, 0, clip_w, sprite_h))
                offset += sprite_w

            if is_low:
                fill_surf.set_alpha(pulse_alpha)

            surface.blit(fill_surf, (bar_x, bar_y))
        else:
            # 纯色圆角填充
            fill_surf = pygame.Surface((fill_width, STAMINA_BAR_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(fill_surf, (*color, pulse_alpha),
                             (0, 0, fill_width, STAMINA_BAR_HEIGHT),
                             border_radius=STAMINA_BAR_RADIUS)
            surface.blit(fill_surf, (bar_x, bar_y))

            # 顶部高光线（1px更亮的色线，模拟光泽）
            highlight_color = tuple(min(255, c + 60) for c in color)
            hl_y = bar_y + 1
            hl_x_start = bar_x + 1
            hl_x_end = bar_x + fill_width - 2
            if hl_x_end > hl_x_start:
                hl_surf = pygame.Surface((hl_x_end - hl_x_start, 1), pygame.SRCALPHA)
                hl_alpha = pulse_alpha if is_low else 120
                hl_surf.fill((*highlight_color, hl_alpha))
                surface.blit(hl_surf, (hl_x_start, hl_y))

    def _draw_stamina_slot(self, surface, x, y, stamina, tint):
        """绘制体力槽（独立圆角面板）"""
        content_w = self._measure_stamina_slot(stamina)
        slot_w = content_w + HUD_PADDING * 2
        slot_h = 14 + HUD_PADDING * 2  # 适配6px体力条

        # 绘制槽位背景
        self._draw_slot_bg(surface, x, y, slot_w, slot_h, tint)

        # 绘制内容
        cx = x + HUD_PADDING
        cy = y + HUD_PADDING

        # 标签
        label = self.font.render("体力", True, COLOR_WHITE)
        surface.blit(label, (cx, cy))
        cx += label.get_width() + 2

        # 体力条（在槽位内容区中垂直居中，内容区高14px，条高6px）
        bar_x = cx
        bar_y = cy + 4
        display_ratio = max(0, min(1, self._displayed_stamina / MAX_STAMINA))
        self._draw_stamina_bar(surface, bar_x, bar_y, display_ratio)

        # 体力条外框（圆角描边）
        pygame.draw.rect(
            surface, (80, 80, 100),
            (bar_x, bar_y, STAMINA_BAR_WIDTH, STAMINA_BAR_HEIGHT), 1,
            border_radius=STAMINA_BAR_RADIUS,
        )

        cx += STAMINA_BAR_WIDTH + 2

        # 数值
        value_text = self._small_font.render(
            f"{int(stamina)}/{MAX_STAMINA}", True, COLOR_WHITE
        )
        surface.blit(value_text, (cx, cy + 2))

        return x + slot_w

    def _measure_badge_slot(self, badge_count):
        """测量徽章槽内容宽度"""
        x = 0
        if "hud_badge_icon" in self._badge_sprites:
            x += 10 + 2
        else:
            label = self.font.render("徽章", True, COLOR_WHITE)
            x += label.get_width() + 2

        if "badge_filled" in self._badge_sprites and "badge_empty" in self._badge_sprites:
            x += 7 * BADGE_ICON_SIZE + 6 * BADGE_ICON_GAP
        else:
            badge_text = self.font.render(f"{badge_count}/7", True, BADGE_FILLED_COLOR)
            x += badge_text.get_width()
        return x

    def _draw_badge_slot(self, surface, x, y, badge_count, tint):
        """绘制徽章槽（独立圆角面板）"""
        content_w = self._measure_badge_slot(badge_count)
        slot_w = content_w + HUD_PADDING * 2
        slot_h = 14 + HUD_PADDING * 2  # 与体力槽等高

        # 绘制槽位背景
        self._draw_slot_bg(surface, x, y, slot_w, slot_h, tint)

        # 绘制内容
        cx = x + HUD_PADDING
        cy = y + HUD_PADDING

        # 标签图标或文字
        if "hud_badge_icon" in self._badge_sprites:
            icon = self._badge_sprites["hud_badge_icon"]
            icon_size = 10
            scaled_icon = pygame.transform.scale(icon, (icon_size, icon_size))
            surface.blit(scaled_icon, (cx, cy))
            cx += icon_size + 2
        else:
            label = self.font.render("徽章", True, COLOR_WHITE)
            surface.blit(label, (cx, cy))
            cx += label.get_width() + 2

        # 徽章图标或文字
        if "badge_filled" in self._badge_sprites and "badge_empty" in self._badge_sprites:
            filled_img = self._badge_sprites["badge_filled"]
            empty_img = self._badge_sprites["badge_empty"]
            for i in range(7):
                img = filled_img if i < badge_count else empty_img
                scaled = pygame.transform.scale(img, (BADGE_ICON_SIZE, BADGE_ICON_SIZE))
                surface.blit(scaled, (cx, cy + 3))
                cx += BADGE_ICON_SIZE + BADGE_ICON_GAP
        else:
            badge_text = self.font.render(
                f"{badge_count}/7", True, BADGE_FILLED_COLOR
            )
            surface.blit(badge_text, (cx, cy))
            cx += badge_text.get_width()

        return x + slot_w

    def _measure_time_slot(self, day_count, time_str, period_name):
        """测量时间槽内容宽度"""
        x = 0
        icon_key = None
        if period_name == "白天":
            icon_key = "hud_sun_icon"
        elif period_name == "夜晚":
            icon_key = "hud_moon_icon"
        if icon_key is not None and icon_key in self._icon_sprites:
            x += 1 + 10 + 4  # 左侧留白1px + 图标宽度 + 右侧间距

        day_text = self.font.render(f"第{day_count}天", True, COLOR_WHITE)
        x += day_text.get_width() + 3
        time_text = self.font.render(time_str, True, COLOR_WHITE)
        x += time_text.get_width() + 3
        period_colors = {
            "白天": (255, 220, 100),
            "黄昏": (255, 150, 80),
            "夜晚": (120, 140, 220),
        }
        period_color = period_colors.get(period_name, COLOR_WHITE)
        period_text = self._small_font.render(period_name, True, period_color)
        x += period_text.get_width()
        return x

    def _draw_time_slot(self, surface, x, y, day_count, time_str, period_name, tint):
        """绘制时间槽（独立圆角面板）"""
        content_w = self._measure_time_slot(day_count, time_str, period_name)
        slot_w = content_w + HUD_PADDING * 2
        slot_h = 14 + HUD_PADDING * 2  # 与体力槽等高

        # 绘制槽位背景
        self._draw_slot_bg(surface, x, y, slot_w, slot_h, tint)

        # 绘制内容
        cx = x + HUD_PADDING
        cy = y + HUD_PADDING

        # 太阳/月亮图标（左侧多留1px空间）
        icon_key = None
        if period_name == "白天":
            icon_key = "hud_sun_icon"
        elif period_name == "夜晚":
            icon_key = "hud_moon_icon"

        if icon_key is not None and icon_key in self._icon_sprites:
            cx += 1  # 图标左侧额外留白
            icon = self._icon_sprites[icon_key]
            icon_size = 10
            scaled_icon = pygame.transform.scale(icon, (icon_size, icon_size))
            surface.blit(scaled_icon, (cx, cy))
            cx += icon_size + 4  # 图标右侧间距与测量一致

        day_text = self.font.render(f"第{day_count}天", True, COLOR_WHITE)
        surface.blit(day_text, (cx, cy))
        cx += day_text.get_width() + 3

        time_text = self.font.render(time_str, True, COLOR_WHITE)
        surface.blit(time_text, (cx, cy))
        cx += time_text.get_width() + 3

        # 时段小标签
        period_colors = {
            "白天": (255, 220, 100),
            "黄昏": (255, 150, 80),
            "夜晚": (120, 140, 220),
        }
        period_color = period_colors.get(period_name, COLOR_WHITE)
        period_text = self._small_font.render(period_name, True, period_color)
        surface.blit(period_text, (cx, cy + 2))

        return x + slot_w

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
