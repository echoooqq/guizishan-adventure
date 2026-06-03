import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    COLOR_WHITE,
    COLOR_CHOICE_HIGHLIGHT,
)
from ui.dialog_box import create_border_surface, draw_nine_slice


class FountainPuzzle:
    CORRECT_ORDER = [
        "badge_1", "badge_2", "badge_3",
        "badge_4", "badge_5", "badge_6", "badge_7",
    ]
    BADGE_NUMERALS = {
        "badge_1": "壹", "badge_2": "贰", "badge_3": "叁",
        "badge_4": "肆", "badge_5": "伍", "badge_6": "陆",
        "badge_7": "柒",
    }
    BADGE_NAMES = {
        "badge_1": "桂花徽章碎片·壹", "badge_2": "桂花徽章碎片·贰",
        "badge_3": "桂花徽章碎片·叁", "badge_4": "桂花徽章碎片·肆",
        "badge_5": "桂花徽章碎片·伍", "badge_6": "桂花徽章碎片·陆",
        "badge_7": "桂花徽章碎片·柒",
    }
    SLOT_RADIUS = 14
    SLOT_GAP = 8
    SLOT_COUNT = 7

    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self.active = False
        self._solved = False
        self.on_complete = None

        self._slots = [None] * self.SLOT_COUNT
        self._selected_slot = 0
        self._selected_badge_index = 0
        self._available_badges = []
        self._message = ""
        self._message_timer = 0.0
        self._is_correct = False
        self._glow_timer = 0.0

        # 第七枚徽章显现动画状态
        self._seventh_anim_phase = 0  # 0=无动画, 1=光芒汇聚, 2=第七枚显现, 3=完成
        self._seventh_anim_timer = 0.0
        self._particles = []  # 粒子列表

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.title_font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE + 4)
        self.border_image = create_border_surface()

    @property
    def solved(self):
        return self._solved

    def start(self, on_complete=None):
        if self.puzzle_manager.get_state("fountain").value == "solved":
            return False
        self.active = True
        self._solved = False
        self.on_complete = on_complete
        self._slots = [None] * self.SLOT_COUNT
        self._selected_slot = 0
        self._selected_badge_index = 0
        self._message = ""
        self._message_timer = 0.0
        self._is_correct = False
        self._glow_timer = 0.0
        self._seventh_anim_phase = 0
        self._seventh_anim_timer = 0.0
        self._particles = []
        self._refresh_available_badges()
        self.puzzle_manager.start_puzzle("fountain")
        return True

    def _refresh_available_badges(self):
        self._available_badges = []
        for badge_id in self.CORRECT_ORDER[:6]:
            if self.inventory.has_item(badge_id) and badge_id not in self._slots:
                self._available_badges.append(badge_id)
        if self._selected_badge_index >= len(self._available_badges):
            self._selected_badge_index = max(0, len(self._available_badges) - 1)

    def handle_event(self, event):
        if not self.active:
            return
        if event.type != pygame.KEYDOWN:
            return

        # 第七枚动画期间，仅允许完成后按F继续
        if self._seventh_anim_phase > 0 and self._seventh_anim_phase < 4:
            if self._seventh_anim_phase == 3:
                if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                    self._seventh_anim_phase = 0
                    self._seventh_anim_timer = 0.0
                    self._finish()
            return

        if self._message:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                if self._is_correct:
                    self._message = ""
                    self._message_timer = 0.0
                    self._finish()
                else:
                    self._message = ""
                    self._message_timer = 0.0
            return

        if event.key == pygame.K_ESCAPE:
            self._finish()
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self._move_slot(-1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self._move_slot(1)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self._move_badge_selection(-1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._move_badge_selection(1)
        elif event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
            self._place_badge()

    def _move_slot(self, direction):
        self._selected_slot = (self._selected_slot + direction) % self.SLOT_COUNT

    def _move_badge_selection(self, direction):
        if not self._available_badges:
            return
        self._selected_badge_index = (self._selected_badge_index + direction) % len(self._available_badges)

    def _place_badge(self):
        if not self._available_badges:
            return
        if self._selected_badge_index >= len(self._available_badges):
            return

        badge_id = self._available_badges[self._selected_badge_index]
        slot_index = self._selected_slot

        if self._slots[slot_index] is not None:
            return

        correct_badge = self.CORRECT_ORDER[slot_index]

        if badge_id == correct_badge:
            self._slots[slot_index] = badge_id
            self.inventory.remove_item(badge_id)
            self._refresh_available_badges()

            filled_count = sum(1 for s in self._slots if s is not None)

            if filled_count == 6:
                # 前6枚归位，启动第七枚显现动画（而非直接放置）
                self._seventh_anim_phase = 1
                self._seventh_anim_timer = 0.0
            else:
                for i in range(self.SLOT_COUNT):
                    if self._slots[i] is None:
                        self._selected_slot = i
                        break
        else:
            self._is_correct = False
            self._message = "顺序似乎不对……"
            self._message_timer = 0.0
            for i, placed in enumerate(self._slots):
                if placed is not None:
                    self.inventory.add_item(placed)
                    self._slots[i] = None
            self._selected_slot = 0
            self._selected_badge_index = 0
            self._refresh_available_badges()

    def update(self, dt):
        if not self.active:
            return

        self._glow_timer += dt

        if self._message:
            self._message_timer += dt

        # 第七枚徽章显现动画更新
        if self._seventh_anim_phase == 1:
            # 阶段1：光芒汇聚（2秒）
            self._seventh_anim_timer += dt
            self._update_particles(dt)
            if self._seventh_anim_timer >= 2.0:
                self._seventh_anim_phase = 2
                self._seventh_anim_timer = 0.0
        elif self._seventh_anim_phase == 2:
            # 阶段2：第七枚从光芒中显现（2秒）
            self._seventh_anim_timer += dt
            self._update_particles(dt)
            if self._seventh_anim_timer >= 2.0:
                self._slots[6] = "badge_7"
                self._is_correct = True
                self._solved = True
                self._seventh_anim_phase = 3
                self._seventh_anim_timer = 0.0
                self._particles = []
                self.puzzle_manager.solve("fountain", self.inventory)

    def _finish(self):
        if not self._solved:
            for i, placed in enumerate(self._slots):
                if placed is not None:
                    self.inventory.add_item(placed)
                    self._slots[i] = None
        self.active = False
        if self.on_complete:
            callback = self.on_complete
            self.on_complete = None
            callback()

    def draw(self, surface):
        if not self.active:
            return

        panel_w, panel_h = 340, 210
        panel_x = (INTERNAL_WIDTH - panel_w) // 2
        panel_y = (INTERNAL_HEIGHT - panel_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (panel_x, panel_y, panel_w, panel_h),
        )

        title = self.title_font.render("七徽归位", True, COLOR_CHOICE_HIGHLIGHT)
        title_rect = title.get_rect(centerx=INTERNAL_WIDTH // 2, top=panel_y + 8)
        surface.blit(title, title_rect)

        self._draw_slots(surface, panel_x, panel_y)

        # 第七枚动画期间隐藏徽章列表和操作提示
        if self._seventh_anim_phase == 0:
            self._draw_badge_list(surface, panel_x, panel_y, panel_w)
            hint = self.font.render("←→选槽 ↑↓选徽章 F放置 Esc退出", True, (180, 180, 180))
            hint_rect = hint.get_rect(centerx=INTERNAL_WIDTH // 2, top=panel_y + panel_h - 18)
            surface.blit(hint, hint_rect)

        # 第七枚徽章显现动画
        if self._seventh_anim_phase > 0:
            self._draw_seventh_anim(surface, panel_x, panel_y, panel_w, panel_h)

        if self._message:
            self._draw_message(surface)

    def _draw_slots(self, surface, panel_x, panel_y):
        total_w = self.SLOT_COUNT * (self.SLOT_RADIUS * 2) + (self.SLOT_COUNT - 1) * self.SLOT_GAP
        start_x = panel_x + (340 - total_w) // 2
        slot_y = panel_y + 32

        for i in range(self.SLOT_COUNT):
            cx = start_x + i * (self.SLOT_RADIUS * 2 + self.SLOT_GAP) + self.SLOT_RADIUS
            cy = slot_y + self.SLOT_RADIUS

            if self._slots[i] is not None:
                glow = int(180 + 60 * abs((self._glow_timer * 2 + i * 0.3) % 2 - 1))
                pygame.draw.circle(surface, (glow, int(glow * 0.84), 0), (cx, cy), self.SLOT_RADIUS)
                pygame.draw.circle(surface, COLOR_CHOICE_HIGHLIGHT, (cx, cy), self.SLOT_RADIUS, 2)
                numeral = self.BADGE_NUMERALS.get(self._slots[i], "?")
                num_surf = self.font.render(numeral, True, COLOR_WHITE)
                num_rect = num_surf.get_rect(center=(cx, cy))
                surface.blit(num_surf, num_rect)
            else:
                pygame.draw.circle(surface, (40, 40, 60), (cx, cy), self.SLOT_RADIUS)
                pygame.draw.circle(surface, (80, 80, 100), (cx, cy), self.SLOT_RADIUS, 2)

            if i == self._selected_slot:
                pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), self.SLOT_RADIUS + 2, 2)

    def _draw_badge_list(self, surface, panel_x, panel_y, panel_w):
        list_y = panel_y + 68
        list_x = panel_x + 12
        max_w = panel_w - 24

        if not self._available_badges:
            empty_text = self.font.render("背包中没有可放置的徽章碎片", True, (120, 120, 120))
            empty_rect = empty_text.get_rect(centerx=INTERNAL_WIDTH // 2, top=list_y)
            surface.blit(empty_text, empty_rect)
            return

        for i, badge_id in enumerate(self._available_badges):
            name = self.BADGE_NAMES.get(badge_id, badge_id)
            is_selected = (i == self._selected_badge_index)

            item_rect = pygame.Rect(list_x, list_y + i * 18, max_w, 16)

            if is_selected:
                pygame.draw.rect(surface, (60, 50, 20), item_rect)
                pygame.draw.rect(surface, COLOR_CHOICE_HIGHLIGHT, item_rect, 1)
                prefix = "▶ "
                color = COLOR_CHOICE_HIGHLIGHT
            else:
                prefix = "  "
                color = COLOR_WHITE

            text = f"{prefix}{name}"
            text_surf = self.font.render(text, True, color)
            surface.blit(text_surf, (list_x + 2, list_y + i * 18 + 1))

    def _draw_message(self, surface):
        msg_w = 280
        lines = self._wrap_text(self._message, msg_w - 20)
        line_height = self.font.get_linesize()
        msg_h = max(50, len(lines) * line_height + 28)
        msg_x = (INTERNAL_WIDTH - msg_w) // 2
        msg_y = (INTERNAL_HEIGHT + 60) // 2

        draw_nine_slice(
            surface, self.border_image,
            (msg_x, msg_y, msg_w, msg_h),
        )

        color = COLOR_CHOICE_HIGHLIGHT if self._is_correct else (255, 100, 100)
        text_y = msg_y + 8
        for line in lines:
            line_surf = self.font.render(line, True, color)
            line_rect = line_surf.get_rect(centerx=msg_x + msg_w // 2, top=text_y)
            surface.blit(line_surf, line_rect)
            text_y += line_height

        cont = self.font.render("按 F 继续", True, COLOR_WHITE)
        cont_rect = cont.get_rect(centerx=msg_x + msg_w // 2, top=text_y + 2)
        surface.blit(cont, cont_rect)

    def _wrap_text(self, text, max_width):
        if not text:
            return [""]
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            if self.font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        return lines

    def _update_particles(self, dt):
        """更新粒子状态并生成新粒子"""
        import math
        import random

        # 计算第7个槽位的中心坐标（粒子目标）
        total_w = self.SLOT_COUNT * (self.SLOT_RADIUS * 2) + (self.SLOT_COUNT - 1) * self.SLOT_GAP
        start_x = (INTERNAL_WIDTH - 340) // 2 + (340 - total_w) // 2
        slot_y = (INTERNAL_HEIGHT - 210) // 2 + 32
        target_cx = start_x + 6 * (self.SLOT_RADIUS * 2 + self.SLOT_GAP) + self.SLOT_RADIUS
        target_cy = slot_y + self.SLOT_RADIUS

        # 从每个已放置的徽章生成粒子
        for i in range(6):
            if self._slots[i] is None:
                continue
            cx = start_x + i * (self.SLOT_RADIUS * 2 + self.SLOT_GAP) + self.SLOT_RADIUS
            cy = slot_y + self.SLOT_RADIUS

            # 每帧每个徽章生成1-2个粒子
            for _ in range(random.randint(1, 2)):
                # 起始位置在徽章边缘随机位置
                angle = random.uniform(0, 2 * math.pi)
                px = cx + int(self.SLOT_RADIUS * 0.8 * math.cos(angle))
                py = cy + int(self.SLOT_RADIUS * 0.8 * math.sin(angle))

                # 计算到目标的方向
                dx = target_cx - px
                dy = target_cy - py
                dist = max(1, math.sqrt(dx * dx + dy * dy))
                speed = random.uniform(40, 80)

                # 弧线偏移：垂直于运动方向的随机偏移
                perp_x = -dy / dist
                perp_y = dx / dist
                curve_offset = random.uniform(-15, 15)

                particle = {
                    'x': float(px),
                    'y': float(py),
                    'vx': dx / dist * speed + perp_x * curve_offset,
                    'vy': dy / dist * speed + perp_y * curve_offset,
                    'target_x': target_cx,
                    'target_y': target_cy,
                    'life': random.uniform(0.8, 1.5),
                    'max_life': 1.5,
                    'size': random.uniform(1.0, 3.0),
                    'brightness': random.uniform(0.6, 1.0),
                    'glow_size': random.uniform(4, 8),
                }
                self._particles.append(particle)

        # 更新现有粒子
        alive = []
        for p in self._particles:
            p['life'] -= dt
            if p['life'] <= 0:
                continue

            # 向目标方向加速
            dx = p['target_x'] - p['x']
            dy = p['target_y'] - p['y']
            dist = max(1, math.sqrt(dx * dx + dy * dy))

            # 接近目标时加速
            accel = 120 if dist < 30 else 60
            p['vx'] += dx / dist * accel * dt
            p['vy'] += dy / dist * accel * dt

            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt

            # 到达目标附近则消亡
            if dist < 8:
                continue

            alive.append(p)

        self._particles = alive[-200:]  # 限制最大粒子数

    def _draw_seventh_anim(self, surface, panel_x, panel_y, panel_w, panel_h):
        """绘制第七枚徽章显现动画（粒子流光+光晕）"""
        import math

        # 计算槽位中心坐标
        total_w = self.SLOT_COUNT * (self.SLOT_RADIUS * 2) + (self.SLOT_COUNT - 1) * self.SLOT_GAP
        start_x = panel_x + (340 - total_w) // 2
        slot_y = panel_y + 32
        target_cx = start_x + 6 * (self.SLOT_RADIUS * 2 + self.SLOT_GAP) + self.SLOT_RADIUS
        target_cy = slot_y + self.SLOT_RADIUS

        if self._seventh_anim_phase == 1:
            # 阶段1：粒子从6枚徽章汇聚到第7槽位
            progress = min(1.0, self._seventh_anim_timer / 2.0)

            # 绘制粒子
            for p in self._particles:
                life_ratio = max(0, p['life'] / p['max_life'])
                alpha = int(255 * life_ratio * p['brightness'])
                size = max(1, int(p['size'] * life_ratio))

                # 粒子光晕（自然柔和的发光效果）
                glow_size = int(p['glow_size'] * life_ratio)
                if glow_size > 1:
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    glow_alpha = int(alpha * 0.3)
                    pygame.draw.circle(glow_surf, (255, 230, 120, glow_alpha),
                                       (glow_size, glow_size), glow_size)
                    surface.blit(glow_surf, (int(p['x']) - glow_size, int(p['y']) - glow_size))

                # 粒子核心
                px, py = int(p['x']), int(p['y'])
                core_color = (
                    min(255, int(255 * p['brightness'])),
                    min(255, int(220 * p['brightness'])),
                    min(255, int(80 + 120 * (1 - life_ratio))),
                )
                pygame.draw.circle(surface, core_color, (px, py), size)

            # 6枚徽章发光增强
            for i in range(6):
                if self._slots[i] is None:
                    continue
                cx = start_x + i * (self.SLOT_RADIUS * 2 + self.SLOT_GAP) + self.SLOT_RADIUS
                cy = slot_y + self.SLOT_RADIUS
                glow_surf = pygame.Surface((self.SLOT_RADIUS * 4, self.SLOT_RADIUS * 4), pygame.SRCALPHA)
                glow_alpha = int((100 + 155 * progress) * 0.4)
                pygame.draw.circle(glow_surf, (255, 220, 100, glow_alpha),
                                   (self.SLOT_RADIUS * 2, self.SLOT_RADIUS * 2),
                                   self.SLOT_RADIUS + int(4 * progress))
                surface.blit(glow_surf, (cx - self.SLOT_RADIUS * 2, cy - self.SLOT_RADIUS * 2))

            # 第7槽位处光晕脉动
            pulse = 0.7 + 0.3 * math.sin(self._seventh_anim_timer * 4)
            glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            glow_alpha = int(180 * progress * pulse)
            pygame.draw.circle(glow_surf, (255, 240, 150, glow_alpha), (30, 30), int(10 + 10 * progress))
            # 外层柔光
            outer_alpha = int(80 * progress * pulse)
            pygame.draw.circle(glow_surf, (255, 230, 120, outer_alpha), (30, 30), int(18 + 8 * progress))
            surface.blit(glow_surf, (target_cx - 30, target_cy - 30))

            # 提示文字
            if progress > 0.3:
                text_alpha = min(255, int((progress - 0.3) * 300))
                hint_text = self.font.render("六枚徽章的光芒正在汇聚……", True, (255, 220, 100))
                hint_text.set_alpha(text_alpha)
                hint_rect = hint_text.get_rect(centerx=INTERNAL_WIDTH // 2, top=panel_y + panel_h - 30)
                surface.blit(hint_text, hint_rect)

        elif self._seventh_anim_phase == 2:
            # 阶段2：第七枚从光芒中显现
            progress = min(1.0, self._seventh_anim_timer / 2.0)

            # 持续的粒子流（减少数量）
            for p in self._particles:
                life_ratio = max(0, p['life'] / p['max_life'])
                alpha = int(255 * life_ratio * p['brightness'])
                size = max(1, int(p['size'] * life_ratio))

                glow_size = int(p['glow_size'] * life_ratio)
                if glow_size > 1:
                    glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    glow_alpha = int(alpha * 0.3)
                    pygame.draw.circle(glow_surf, (255, 230, 120, glow_alpha),
                                       (glow_size, glow_size), glow_size)
                    surface.blit(glow_surf, (int(p['x']) - glow_size, int(p['y']) - glow_size))

                px, py = int(p['x']), int(p['y'])
                core_color = (
                    min(255, int(255 * p['brightness'])),
                    min(255, int(220 * p['brightness'])),
                    min(255, int(80 + 120 * (1 - life_ratio))),
                )
                pygame.draw.circle(surface, core_color, (px, py), size)

            # 第7槽位处强烈光芒+光晕
            pulse = 0.8 + 0.2 * math.sin(self._seventh_anim_timer * 6)
            glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            glow_alpha = int(255 * pulse)
            # 外层柔光
            pygame.draw.circle(glow_surf, (255, 230, 120, int(glow_alpha * 0.3)), (40, 40), 30)
            # 中层光晕
            pygame.draw.circle(glow_surf, (255, 240, 150, glow_alpha), (40, 40), 20)
            # 内层亮核
            pygame.draw.circle(glow_surf, (255, 255, 220, min(255, glow_alpha + 30)), (40, 40), 12)
            surface.blit(glow_surf, (target_cx - 40, target_cy - 40))

            # 第七枚徽章逐渐显现（从透明到实体）
            badge_alpha = int(255 * progress)
            badge_surf = pygame.Surface((self.SLOT_RADIUS * 2 + 4, self.SLOT_RADIUS * 2 + 4), pygame.SRCALPHA)
            b_cx, b_cy = self.SLOT_RADIUS + 2, self.SLOT_RADIUS + 2
            pygame.draw.circle(badge_surf, (255, 200, 50, badge_alpha), (b_cx, b_cy), self.SLOT_RADIUS)
            pygame.draw.circle(badge_surf, (255, 220, 100, badge_alpha), (b_cx, b_cy), self.SLOT_RADIUS, 2)
            num_surf = self.font.render("柒", True, (255, 255, 255))
            num_surf.set_alpha(badge_alpha)
            num_rect = num_surf.get_rect(center=(b_cx, b_cy))
            badge_surf.blit(num_surf, num_rect)
            surface.blit(badge_surf, (target_cx - self.SLOT_RADIUS - 2, target_cy - self.SLOT_RADIUS - 2))

            # 提示文字
            if progress > 0.5:
                text_alpha = min(255, int((progress - 0.5) * 400))
                hint_text = self.font.render("第七枚徽章碎片从光芒中显现！", True, (255, 220, 100))
                hint_text.set_alpha(text_alpha)
                hint_rect = hint_text.get_rect(centerx=INTERNAL_WIDTH // 2, top=panel_y + panel_h - 30)
                surface.blit(hint_text, hint_rect)

        elif self._seventh_anim_phase == 3:
            # 阶段3：完成，显示成功消息
            fade = max(0, 1.0 - self._seventh_anim_timer / 1.0)

            # 残余光晕消散
            if fade > 0:
                glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                glow_alpha = int(200 * fade)
                pygame.draw.circle(glow_surf, (255, 240, 150, glow_alpha), (40, 40), 20)
                surface.blit(glow_surf, (target_cx - 40, target_cy - 40))

            # 显示成功消息
            msg_w = 280
            msg_text = "七徽归位！封印解除！"
            lines = self._wrap_text(msg_text, msg_w - 20)
            line_height = self.font.get_linesize()
            msg_h = max(50, len(lines) * line_height + 28)
            msg_x = (INTERNAL_WIDTH - msg_w) // 2
            msg_y = (INTERNAL_HEIGHT + 60) // 2

            draw_nine_slice(
                surface, self.border_image,
                (msg_x, msg_y, msg_w, msg_h),
            )

            color = COLOR_CHOICE_HIGHLIGHT
            text_y = msg_y + 8
            for line in lines:
                line_surf = self.font.render(line, True, color)
                line_rect = line_surf.get_rect(centerx=msg_x + msg_w // 2, top=text_y)
                surface.blit(line_surf, line_rect)
                text_y += line_height

            cont = self.font.render("按 F 继续", True, COLOR_WHITE)
            cont_rect = cont.get_rect(centerx=msg_x + msg_w // 2, top=text_y + 2)
            surface.blit(cont, cont_rect)
