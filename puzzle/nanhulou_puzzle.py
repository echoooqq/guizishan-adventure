import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_DIALOG_BG,
    COLOR_DIALOG_BORDER,
    COLOR_DIALOG_TEXT,
    COLOR_CHOICE_HIGHLIGHT,
)
from ui.dialog_box import create_border_surface, draw_nine_slice


class NanhulouPuzzle:
    CORRECT_CODE = "1903"

    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self.active = False
        self.on_complete = None

        self._input_buffer = ""
        self._max_input_length = 4
        self._cursor_blink_timer = 0.0
        self._show_cursor = True
        self._message = ""
        self._message_timer = 0.0
        self._message_duration = 2.0
        self._is_correct = False
        self._show_result = False
        self._result_timer = 0.0
        self._result_duration = 2.5
        self._secret_room_open = False

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.title_font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE + 4)
        self.border_image = create_border_surface()

    def start(self, on_complete=None):
        if self.puzzle_manager.get_state("nanhulou").value == "solved":
            return False
        self.active = True
        self.on_complete = on_complete
        self._input_buffer = ""
        self._message = ""
        self._message_timer = 0.0
        self._is_correct = False
        self._show_result = False
        self._result_timer = 0.0
        self._secret_room_open = False
        self.puzzle_manager.start_puzzle("nanhulou")
        return True

    @property
    def has_bulletin_scrap(self):
        return self.inventory.has_item("bulletin_scrap")

    @property
    def secret_room_open(self):
        return self._secret_room_open

    def handle_event(self, event):
        if not self.active:
            return
        if event.type != pygame.KEYDOWN:
            return

        if self._show_result:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._finish()
            return

        if self._message:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._message = ""
                self._message_timer = 0.0
                if not self._is_correct:
                    self._input_buffer = ""
            return

        if event.key == pygame.K_ESCAPE:
            self._finish()
        elif event.key == pygame.K_RETURN or event.key == pygame.K_f:
            self._submit_code()
        elif event.key == pygame.K_BACKSPACE:
            if self._input_buffer:
                self._input_buffer = self._input_buffer[:-1]
        elif event.key in (pygame.K_0, pygame.K_KP0):
            self._append_digit("0")
        elif event.key in (pygame.K_1, pygame.K_KP1):
            self._append_digit("1")
        elif event.key in (pygame.K_2, pygame.K_KP2):
            self._append_digit("2")
        elif event.key in (pygame.K_3, pygame.K_KP3):
            self._append_digit("3")
        elif event.key in (pygame.K_4, pygame.K_KP4):
            self._append_digit("4")
        elif event.key in (pygame.K_5, pygame.K_KP5):
            self._append_digit("5")
        elif event.key in (pygame.K_6, pygame.K_KP6):
            self._append_digit("6")
        elif event.key in (pygame.K_7, pygame.K_KP7):
            self._append_digit("7")
        elif event.key in (pygame.K_8, pygame.K_KP8):
            self._append_digit("8")
        elif event.key in (pygame.K_9, pygame.K_KP9):
            self._append_digit("9")

    def _append_digit(self, digit):
        if len(self._input_buffer) < self._max_input_length:
            self._input_buffer += digit

    def _submit_code(self):
        if len(self._input_buffer) < 4:
            self._message = "请输入4位数字密码。"
            self._message_timer = 0.0
            return

        if self._input_buffer == self.CORRECT_CODE:
            self._is_correct = True
            self._message = "密码正确！密室通道已开启！"
            self._message_timer = 0.0
            self._secret_room_open = True
        else:
            self._is_correct = False
            self._message = "密码错误……再仔细看看公告栏吧。"
            self._message_timer = 0.0

    def update(self, dt):
        if not self.active:
            return

        self._cursor_blink_timer += dt
        if self._cursor_blink_timer >= 0.5:
            self._cursor_blink_timer -= 0.5
            self._show_cursor = not self._show_cursor

        if self._message:
            self._message_timer += dt

        if self._show_result:
            self._result_timer += dt

    def trigger_badge_pickup(self):
        self._show_result = True
        self._result_timer = 0.0
        self.puzzle_manager.solve("nanhulou", self.inventory)

    def _finish(self):
        self.active = False
        if self.on_complete:
            callback = self.on_complete
            self.on_complete = None
            callback()

    def draw(self, surface):
        if not self.active:
            return

        self._draw_terminal(surface)

        if self._message:
            self._draw_message(surface)

        if self._show_result:
            self._draw_result_overlay(surface)

    def _draw_terminal(self, surface):
        term_w, term_h = 260, 140
        term_x = (INTERNAL_WIDTH - term_w) // 2
        term_y = (INTERNAL_HEIGHT - term_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (term_x, term_y, term_w, term_h),
        )

        screen_rect = pygame.Rect(
            term_x + 6, term_y + 6,
            term_w - 12, term_h - 12,
        )
        pygame.draw.rect(surface, (10, 20, 10), screen_rect)

        title = self.title_font.render("电脑终端", True, (0, 200, 0))
        surface.blit(title, (term_x + 10, term_y + 10))

        prompt = self.font.render("请输入4位密码：", True, (0, 180, 0))
        surface.blit(prompt, (term_x + 10, term_y + 32))

        input_x = term_x + 10
        input_y = term_y + 50
        input_rect = pygame.Rect(input_x, input_y, term_w - 20, 20)
        pygame.draw.rect(surface, (20, 40, 20), input_rect)
        pygame.draw.rect(surface, (0, 150, 0), input_rect, 1)

        display_text = self._input_buffer
        if self._show_cursor:
            display_text += "_"
        input_surf = self.title_font.render(display_text, True, (0, 255, 0))
        surface.blit(input_surf, (input_x + 4, input_y + 3))

        hint_y = term_y + term_h - 36
        hint = self.font.render("数字键输入 | 回车确认 | Esc退出", True, (0, 120, 0))
        surface.blit(hint, (term_x + 10, hint_y))

        if self.has_bulletin_scrap:
            clue = self.font.render("提示：公告栏残页上的年份……", True, (180, 180, 0))
            surface.blit(clue, (term_x + 10, hint_y + 14))

    def _draw_message(self, surface):
        msg_w, msg_h = 240, 40
        msg_x = (INTERNAL_WIDTH - msg_w) // 2
        msg_y = (INTERNAL_HEIGHT + 80) // 2

        draw_nine_slice(
            surface, self.border_image,
            (msg_x, msg_y, msg_w, msg_h),
        )

        color = (0, 255, 0) if self._is_correct else (255, 100, 100)
        msg_surf = self.font.render(self._message, True, color)
        msg_rect = msg_surf.get_rect(centerx=msg_x + msg_w // 2, centery=msg_y + msg_h // 2 - 4)
        surface.blit(msg_surf, msg_rect)

        cont = self.font.render("按 F 继续", True, COLOR_WHITE)
        cont_rect = cont.get_rect(centerx=msg_x + msg_w // 2, centery=msg_y + msg_h // 2 + 10)
        surface.blit(cont, cont_rect)

    def _draw_result_overlay(self, surface):
        box_w, box_h = 240, 50
        box_x = (INTERNAL_WIDTH - box_w) // 2
        box_y = (INTERNAL_HEIGHT - box_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (box_x, box_y, box_w, box_h),
        )

        text = self.font.render("获得了桂花徽章碎片·贰！", True, (255, 215, 0))
        text_rect = text.get_rect(centerx=box_x + box_w // 2, centery=box_y + box_h // 2 - 6)
        surface.blit(text, text_rect)

        hint = self.font.render("按 F 继续", True, COLOR_WHITE)
        hint_rect = hint.get_rect(centerx=box_x + box_w // 2, centery=box_y + box_h // 2 + 10)
        surface.blit(hint, hint_rect)
