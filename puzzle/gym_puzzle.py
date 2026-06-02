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


class GymPuzzle:
    CORRECT_CODE = [1, 9, 0, 3]

    _SHOOTING = "shooting"
    _SCOREBOARD = "scoreboard"

    _BAR_WIDTH = 240
    _BAR_HEIGHT = 16
    _GREEN_ZONE_RATIO = 0.2
    _INDICATOR_SPEED = 200
    _MAX_ATTEMPTS = 3
    _REQUIRED_HITS = 2
    _FEEDBACK_DURATION = 1.0

    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self.active = False
        self.on_complete = None

        self._phase = None
        self._shooting_passed = False
        self._scoreboard_opened = False

        self._indicator_pos = 0.0
        self._indicator_dir = 1
        self._attempts = 0
        self._hits = 0
        self._feedback_text = ""
        self._feedback_timer = 0.0
        self._showing_result = False
        self._result_text = ""
        self._bar_locked = False

        self._digits = [0, 0, 0, 0]
        self._selected_digit = 0
        self._message = ""
        self._message_timer = 0.0
        self._is_correct = False

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.title_font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE + 4)
        self.digit_font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE + 8)
        self.border_image = create_border_surface()

    @property
    def shooting_passed(self):
        return self._shooting_passed

    @property
    def scoreboard_opened(self):
        return self._scoreboard_opened

    def start_shooting(self, on_complete=None):
        if self._shooting_passed:
            return False
        self.active = True
        self.on_complete = on_complete
        self._phase = self._SHOOTING
        self._indicator_pos = 0.0
        self._indicator_dir = 1
        self._attempts = 0
        self._hits = 0
        self._feedback_text = ""
        self._feedback_timer = 0.0
        self._showing_result = False
        self._result_text = ""
        self._bar_locked = False
        self.puzzle_manager.start_puzzle("gym")
        return True

    def start_scoreboard(self, on_complete=None):
        if self._scoreboard_opened:
            return False
        self.active = True
        self.on_complete = on_complete
        self._phase = self._SCOREBOARD
        self._digits = [0, 0, 0, 0]
        self._selected_digit = 0
        self._message = ""
        self._message_timer = 0.0
        self._is_correct = False
        return True

    def handle_event(self, event):
        if not self.active:
            return
        if event.type != pygame.KEYDOWN:
            return

        if self._phase == self._SHOOTING:
            self._handle_shooting_event(event)
        elif self._phase == self._SCOREBOARD:
            self._handle_scoreboard_event(event)

    def _handle_shooting_event(self, event):
        if self._showing_result:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._finish()
            return

        if self._feedback_text:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._feedback_text = ""
                self._feedback_timer = 0.0
                if self._attempts >= self._MAX_ATTEMPTS:
                    self._showing_result = True
                    if self._hits >= self._REQUIRED_HITS:
                        self._result_text = "挑战成功！获得了器材室钥匙！"
                    else:
                        self._result_text = "挑战失败……可以重新挑战。"
                else:
                    self._indicator_pos = 0.0
                    self._indicator_dir = 1
                    self._bar_locked = False
            return

        if event.key in (pygame.K_f, pygame.K_SPACE):
            self._bar_locked = True
            self._attempts += 1
            green_start = (1.0 - self._GREEN_ZONE_RATIO) / 2.0
            green_end = green_start + self._GREEN_ZONE_RATIO
            if green_start <= self._indicator_pos <= green_end:
                self._hits += 1
                self._feedback_text = "命中！"
            else:
                self._feedback_text = "未命中！"
            self._feedback_timer = 0.0

        if event.key == pygame.K_ESCAPE:
            self._finish()

    def _handle_scoreboard_event(self, event):
        if self._message:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                if self._is_correct:
                    self._message = ""
                    self._message_timer = 0.0
                    self._finish()
                else:
                    self._message = ""
                    self._message_timer = 0.0
                    self._digits = [0, 0, 0, 0]
                    self._selected_digit = 0
            return

        if event.key == pygame.K_ESCAPE:
            self._finish()
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            if self._selected_digit > 0:
                self._selected_digit -= 1
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            if self._selected_digit < 3:
                self._selected_digit += 1
        elif event.key in (pygame.K_UP, pygame.K_w):
            self._digits[self._selected_digit] = (self._digits[self._selected_digit] + 1) % 10
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._digits[self._selected_digit] = (self._digits[self._selected_digit] - 1) % 10
        elif event.key in (pygame.K_f, pygame.K_RETURN, pygame.K_SPACE):
            self._submit_code()

    def _submit_code(self):
        if self._digits == self.CORRECT_CODE:
            self._is_correct = True
            self._message = "数字正确！暗门缓缓开启……"
            self._message_timer = 0.0
            self._scoreboard_opened = True
        else:
            self._is_correct = False
            self._message = "数字不对……再看看记分牌便条吧。"
            self._message_timer = 0.0

    def update(self, dt):
        if not self.active:
            return

        if self._phase == self._SHOOTING:
            self._update_shooting(dt)
        elif self._phase == self._SCOREBOARD:
            self._update_scoreboard(dt)

    def _update_shooting(self, dt):
        if self._feedback_text:
            self._feedback_timer += dt
            return

        if self._bar_locked or self._showing_result:
            return

        self._indicator_pos += self._indicator_dir * (self._INDICATOR_SPEED / self._BAR_WIDTH) * dt
        if self._indicator_pos >= 1.0:
            self._indicator_pos = 1.0
            self._indicator_dir = -1
        elif self._indicator_pos <= 0.0:
            self._indicator_pos = 0.0
            self._indicator_dir = 1

    def _update_scoreboard(self, dt):
        if self._message:
            self._message_timer += dt

    def _finish(self):
        if self._phase == self._SHOOTING and self._hits >= self._REQUIRED_HITS:
            self._shooting_passed = True
        self.active = False
        if self.on_complete:
            callback = self.on_complete
            self.on_complete = None
            callback()

    def draw(self, surface):
        if not self.active:
            return

        if self._phase == self._SHOOTING:
            self._draw_shooting(surface)
        elif self._phase == self._SCOREBOARD:
            self._draw_scoreboard(surface)

    def _draw_shooting(self, surface):
        panel_w, panel_h = 300, 180
        panel_x = (INTERNAL_WIDTH - panel_w) // 2
        panel_y = (INTERNAL_HEIGHT - panel_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (panel_x, panel_y, panel_w, panel_h),
        )

        title = self.title_font.render("投篮挑战", True, COLOR_CHOICE_HIGHLIGHT)
        title_rect = title.get_rect(centerx=INTERNAL_WIDTH // 2, top=panel_y + 10)
        surface.blit(title, title_rect)

        bar_x = (INTERNAL_WIDTH - self._BAR_WIDTH) // 2
        bar_y = panel_y + 40

        green_width = int(self._BAR_WIDTH * self._GREEN_ZONE_RATIO)
        green_x = bar_x + (self._BAR_WIDTH - green_width) // 2

        red_left_rect = pygame.Rect(bar_x, bar_y, green_x - bar_x, self._BAR_HEIGHT)
        pygame.draw.rect(surface, (180, 50, 50), red_left_rect)

        green_rect = pygame.Rect(green_x, bar_y, green_width, self._BAR_HEIGHT)
        pygame.draw.rect(surface, (50, 180, 50), green_rect)

        red_right_start = green_x + green_width
        red_right_width = (bar_x + self._BAR_WIDTH) - red_right_start
        red_right_rect = pygame.Rect(red_right_start, bar_y, red_right_width, self._BAR_HEIGHT)
        pygame.draw.rect(surface, (180, 50, 50), red_right_rect)

        pygame.draw.rect(surface, COLOR_WHITE, (bar_x, bar_y, self._BAR_WIDTH, self._BAR_HEIGHT), 1)

        if not self._bar_locked and not self._showing_result and not self._feedback_text:
            indicator_x = bar_x + int(self._indicator_pos * (self._BAR_WIDTH - 2)) + 1
            pygame.draw.line(
                surface, COLOR_WHITE,
                (indicator_x, bar_y), (indicator_x, bar_y + self._BAR_HEIGHT), 2,
            )
        else:
            indicator_x = bar_x + int(self._indicator_pos * (self._BAR_WIDTH - 2)) + 1
            pygame.draw.line(
                surface, (255, 255, 100),
                (indicator_x, bar_y), (indicator_x, bar_y + self._BAR_HEIGHT), 2,
            )

        score_y = bar_y + self._BAR_HEIGHT + 10
        score_text = self.font.render(f"命中: {self._hits}/{self._MAX_ATTEMPTS}", True, COLOR_WHITE)
        surface.blit(score_text, (panel_x + 20, score_y))

        attempt_text = self.font.render(f"第{min(self._attempts + 1, self._MAX_ATTEMPTS)}次投篮", True, COLOR_WHITE)
        attempt_rect = attempt_text.get_rect(right=panel_x + panel_w - 20, top=score_y)
        surface.blit(attempt_text, attempt_rect)

        feedback_y = score_y + 20
        if self._feedback_text:
            color = (100, 255, 100) if self._feedback_text == "命中！" else (255, 100, 100)
            fb_surf = self.title_font.render(self._feedback_text, True, color)
            fb_rect = fb_surf.get_rect(centerx=INTERNAL_WIDTH // 2, top=feedback_y)
            surface.blit(fb_surf, fb_rect)

            hint = self.font.render("按 F 继续", True, COLOR_WHITE)
            hint_rect = hint.get_rect(centerx=INTERNAL_WIDTH // 2, top=feedback_y + 22)
            surface.blit(hint, hint_rect)

        if self._showing_result:
            result_color = (100, 255, 100) if self._hits >= self._REQUIRED_HITS else (255, 100, 100)
            result_surf = self.title_font.render(self._result_text, True, result_color)
            result_rect = result_surf.get_rect(centerx=INTERNAL_WIDTH // 2, top=feedback_y)
            surface.blit(result_surf, result_rect)

            cont = self.font.render("按 F 继续", True, COLOR_WHITE)
            cont_rect = cont.get_rect(centerx=INTERNAL_WIDTH // 2, top=feedback_y + 22)
            surface.blit(cont, cont_rect)

        if not self._feedback_text and not self._showing_result and not self._bar_locked:
            hint = self.font.render("按 F 投篮 | Esc退出", True, (180, 180, 180))
            hint_rect = hint.get_rect(centerx=INTERNAL_WIDTH // 2, bottom=panel_y + panel_h - 6)
            surface.blit(hint, hint_rect)

    def _draw_scoreboard(self, surface):
        panel_w, panel_h = 280, 160
        panel_x = (INTERNAL_WIDTH - panel_w) // 2
        panel_y = (INTERNAL_HEIGHT - panel_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (panel_x, panel_y, panel_w, panel_h),
        )

        bg_rect = pygame.Rect(panel_x + 6, panel_y + 6, panel_w - 12, panel_h - 12)
        pygame.draw.rect(surface, (40, 30, 20), bg_rect)

        title = self.title_font.render("记分牌", True, (220, 200, 160))
        title_rect = title.get_rect(centerx=INTERNAL_WIDTH // 2, top=panel_y + 10)
        surface.blit(title, title_rect)

        digit_area_y = panel_y + 36
        digit_w = 36
        digit_h = 44
        digit_gap = 12
        total_w = 4 * digit_w + 3 * digit_gap
        start_x = (INTERNAL_WIDTH - total_w) // 2

        for i in range(4):
            dx = start_x + i * (digit_w + digit_gap)
            dy = digit_area_y

            card_rect = pygame.Rect(dx, dy, digit_w, digit_h)
            if i == self._selected_digit:
                pygame.draw.rect(surface, (80, 60, 30), card_rect)
                pygame.draw.rect(surface, COLOR_CHOICE_HIGHLIGHT, card_rect, 2)
            else:
                pygame.draw.rect(surface, (60, 45, 25), card_rect)
                pygame.draw.rect(surface, (120, 100, 60), card_rect, 1)

            digit_surf = self.digit_font.render(str(self._digits[i]), True, COLOR_WHITE)
            digit_rect = digit_surf.get_rect(centerx=dx + digit_w // 2, centery=dy + digit_h // 2)
            surface.blit(digit_surf, digit_rect)

            if i == self._selected_digit:
                up_x = dx + digit_w // 2
                up_y = dy - 6
                pygame.draw.polygon(surface, COLOR_CHOICE_HIGHLIGHT, [
                    (up_x, up_y - 5), (up_x - 4, up_y + 3), (up_x + 4, up_y + 3)
                ])
                down_y = dy + digit_h + 6
                pygame.draw.polygon(surface, COLOR_CHOICE_HIGHLIGHT, [
                    (up_x, down_y + 5), (up_x - 4, down_y - 3), (up_x + 4, down_y - 3)
                ])

        hint_y = panel_y + panel_h - 40
        hint = self.font.render("←→选位 ↑↓翻牌 F确认 Esc退出", True, (160, 140, 100))
        hint_rect = hint.get_rect(centerx=INTERNAL_WIDTH // 2, top=hint_y)
        surface.blit(hint, hint_rect)

        if self.inventory.has_item("scoreboard_note"):
            clue = self.font.render("提示：记分牌便条上的数字……", True, (180, 180, 0))
            clue_rect = clue.get_rect(centerx=INTERNAL_WIDTH // 2, top=hint_y + 14)
            surface.blit(clue, clue_rect)

        if self._message:
            self._draw_message(surface)

    def _draw_message(self, surface):
        msg_w = 280
        lines = self._wrap_text(self._message, msg_w - 20)
        line_height = self.font.get_linesize()
        msg_h = max(50, len(lines) * line_height + 28)
        msg_x = (INTERNAL_WIDTH - msg_w) // 2
        msg_y = (INTERNAL_HEIGHT + 80) // 2

        draw_nine_slice(
            surface, self.border_image,
            (msg_x, msg_y, msg_w, msg_h),
        )

        color = (100, 255, 100) if self._is_correct else (255, 100, 100)
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
