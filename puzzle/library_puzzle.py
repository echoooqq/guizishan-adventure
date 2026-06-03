import json
import os
import random

import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    COLOR_WHITE,
    COLOR_BLACK,
    COLOR_CHOICE_HIGHLIGHT,
)
from ui.dialog_box import create_border_surface, draw_nine_slice


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_PATH = os.path.join(PROJECT_ROOT, "data", "library_questions.json")

QUIZ_QUESTION_COUNT = 3


class LibraryPuzzle:
    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self.active = False
        self.on_complete = None

        self._questions = []
        self._current_index = 0
        self._selected_option = 0
        self._correct_count = 0
        self._quiz_passed = False
        self._message = ""
        self._message_timer = 0.0
        self._showing_feedback = False
        self._feedback_correct = False

        self._all_questions = []
        self._load_questions()

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.title_font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE + 4)
        self.border_image = create_border_surface()

    def _load_questions(self):
        try:
            with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
                self._all_questions = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._all_questions = []

    @property
    def quiz_passed(self):
        return self._quiz_passed

    def start(self, on_complete=None):
        if self.puzzle_manager.get_state("library").value == "solved":
            return False
        self.active = True
        self.on_complete = on_complete
        self._quiz_passed = False
        self._message = ""
        self._message_timer = 0.0
        self._showing_feedback = False
        self._feedback_correct = False
        self._current_index = 0
        self._selected_option = 0
        self._correct_count = 0

        available = list(self._all_questions)
        if len(available) >= QUIZ_QUESTION_COUNT:
            self._questions = random.sample(available, QUIZ_QUESTION_COUNT)
        else:
            self._questions = available[:]

        self.puzzle_manager.start_puzzle("library")
        return True

    def handle_event(self, event):
        if not self.active:
            return
        if event.type != pygame.KEYDOWN:
            return

        if self._message:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                if self._quiz_passed:
                    self._message = ""
                    self._message_timer = 0.0
                    self._finish()
                else:
                    self._message = ""
                    self._message_timer = 0.0
                    self._showing_feedback = False
            return

        if self._showing_feedback:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._showing_feedback = False
                if self._feedback_correct:
                    self._current_index += 1
                    self._selected_option = 0
                    if self._current_index >= len(self._questions):
                        self._quiz_passed = True
                        self._message = "全部答对！获得了古旧典籍和索书号便签！"
                        self._message_timer = 0.0
                else:
                    self._message = "答错了！可以重新挑战。"
                    self._message_timer = 0.0
            return

        if event.key == pygame.K_ESCAPE:
            self._finish()
        elif event.key in (pygame.K_UP, pygame.K_w):
            self._selected_option = (self._selected_option - 1) % 4
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._selected_option = (self._selected_option + 1) % 4
        elif event.key in (pygame.K_f, pygame.K_RETURN, pygame.K_SPACE):
            self._submit_answer()

    def _submit_answer(self):
        if self._current_index >= len(self._questions):
            return
        question = self._questions[self._current_index]
        correct_answer = question.get("answer", 0)
        if self._selected_option == correct_answer:
            self._correct_count += 1
            self._feedback_correct = True
            self._showing_feedback = True
        else:
            self._feedback_correct = False
            self._showing_feedback = True

    def update(self, dt):
        if not self.active:
            return

        if self._message:
            self._message_timer += dt

    def _finish(self):
        self.active = False
        if self.on_complete:
            callback = self.on_complete
            self.on_complete = None
            callback()

    def draw(self, surface):
        if not self.active:
            return

        if self._message:
            self._draw_message(surface)
            return

        if self._showing_feedback:
            self._draw_feedback(surface)
            return

        self._draw_quiz(surface)

    def _draw_quiz(self, surface):
        panel_w, panel_h = 300, 220
        panel_x = (INTERNAL_WIDTH - panel_w) // 2
        panel_y = (INTERNAL_HEIGHT - panel_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (panel_x, panel_y, panel_w, panel_h),
        )

        title = self.title_font.render("书海寻踪", True, COLOR_CHOICE_HIGHLIGHT)
        title_rect = title.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + 6)
        surface.blit(title, title_rect)

        indicator = self.font.render(
            f"第{self._current_index + 1}题/共{len(self._questions)}题",
            True, COLOR_WHITE,
        )
        indicator_rect = indicator.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + 22)
        surface.blit(indicator, indicator_rect)

        if self._current_index < len(self._questions):
            question = self._questions[self._current_index]
            question_text = question.get("question", "")
            lines = self._wrap_text(question_text, panel_w - 24)
            line_height = self.font.get_linesize()
            text_y = panel_y + 38
            for line in lines:
                line_surf = self.font.render(line, True, COLOR_WHITE)
                line_rect = line_surf.get_rect(left=panel_x + 12, top=text_y)
                surface.blit(line_surf, line_rect)
                text_y += line_height

            options = question.get("options", [])
            option_y = text_y + 6
            for i, option in enumerate(options):
                # 选中指示器用三角形绘制
                if i == self._selected_option:
                    ind_x = panel_x + 14
                    ind_y = option_y + line_height // 2
                    pygame.draw.polygon(surface, COLOR_CHOICE_HIGHLIGHT, [
                        (ind_x, ind_y - 3),
                        (ind_x + 4, ind_y),
                        (ind_x, ind_y + 3),
                    ])
                color = COLOR_CHOICE_HIGHLIGHT if i == self._selected_option else COLOR_WHITE
                option_surf = self.font.render(option, True, color)
                surface.blit(option_surf, (panel_x + 22, option_y))
                option_y += line_height + 2

        hint = self.font.render("↑↓选择 | F确认 | Esc退出", True, (150, 150, 150))
        hint_rect = hint.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + panel_h - 16)
        surface.blit(hint, hint_rect)

    def _draw_feedback(self, surface):
        panel_w, panel_h = 300, 220
        panel_x = (INTERNAL_WIDTH - panel_w) // 2
        panel_y = (INTERNAL_HEIGHT - panel_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (panel_x, panel_y, panel_w, panel_h),
        )

        title = self.title_font.render("书海寻踪", True, COLOR_CHOICE_HIGHLIGHT)
        title_rect = title.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + 6)
        surface.blit(title, title_rect)

        if self._current_index < len(self._questions):
            question = self._questions[self._current_index]
            question_text = question.get("question", "")
            lines = self._wrap_text(question_text, panel_w - 24)
            line_height = self.font.get_linesize()
            text_y = panel_y + 38
            for line in lines:
                line_surf = self.font.render(line, True, COLOR_WHITE)
                line_rect = line_surf.get_rect(left=panel_x + 12, top=text_y)
                surface.blit(line_surf, line_rect)
                text_y += line_height

            options = question.get("options", [])
            correct_answer = question.get("answer", 0)
            option_y = text_y + 6
            for i, option in enumerate(options):
                # 选中指示器用三角形绘制
                if i == self._selected_option:
                    ind_x = panel_x + 14
                    ind_y = option_y + line_height // 2
                    pygame.draw.polygon(surface, COLOR_CHOICE_HIGHLIGHT, [
                        (ind_x, ind_y - 3),
                        (ind_x + 4, ind_y),
                        (ind_x, ind_y + 3),
                    ])
                if i == correct_answer:
                    color = (100, 255, 100)
                elif i == self._selected_option and i != correct_answer:
                    color = (255, 100, 100)
                else:
                    color = COLOR_WHITE
                option_surf = self.font.render(option, True, color)
                surface.blit(option_surf, (panel_x + 22, option_y))
                option_y += line_height + 2

        if self._feedback_correct:
            fb_text = "正确！"
            fb_color = (100, 255, 100)
        else:
            fb_text = "错误！"
            fb_color = (255, 100, 100)
        fb_surf = self.title_font.render(fb_text, True, fb_color)
        fb_rect = fb_surf.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + panel_h - 30)
        surface.blit(fb_surf, fb_rect)

        cont = self.font.render("按 F 继续", True, COLOR_WHITE)
        cont_rect = cont.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + panel_h - 16)
        surface.blit(cont, cont_rect)

    def _draw_message(self, surface):
        msg_w = 300
        lines = self._wrap_text(self._message, msg_w - 20)
        line_height = self.font.get_linesize()
        msg_h = max(50, len(lines) * line_height + 36)
        msg_x = (INTERNAL_WIDTH - msg_w) // 2
        msg_y = (INTERNAL_HEIGHT - msg_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (msg_x, msg_y, msg_w, msg_h),
        )

        color = (100, 255, 100) if self._quiz_passed else (255, 100, 100)
        text_y = msg_y + 10
        for line in lines:
            line_surf = self.font.render(line, True, color)
            line_rect = line_surf.get_rect(centerx=msg_x + msg_w // 2, top=text_y)
            surface.blit(line_surf, line_rect)
            text_y += line_height

        cont = self.font.render("按 F 继续", True, COLOR_WHITE)
        cont_rect = cont.get_rect(centerx=msg_x + msg_w // 2, top=text_y + 4)
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
