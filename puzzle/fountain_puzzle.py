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
                self._slots[6] = "badge_7"
                self._is_correct = True
                self._solved = True
                self._message = "七徽归位！封印解除！"
                self._message_timer = 0.0
                self.puzzle_manager.solve("fountain", self.inventory)
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

        self._draw_badge_list(surface, panel_x, panel_y, panel_w)

        hint = self.font.render("←→选槽 ↑↓选徽章 F放置 Esc退出", True, (180, 180, 180))
        hint_rect = hint.get_rect(centerx=INTERNAL_WIDTH // 2, top=panel_y + panel_h - 18)
        surface.blit(hint, hint_rect)

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
