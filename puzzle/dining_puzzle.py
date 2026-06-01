import random
import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    COLOR_WHITE,
    COLOR_BLACK,
    TILE_SIZE,
)
from ui.dialog_box import create_border_surface, draw_nine_slice


class DiningPuzzle:
    TABLE_COUNT = 3

    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self._card_table_index = random.randint(0, self.TABLE_COUNT - 1)
        self._searched_tables = set()
        self._card_found = False
        self._card_returned = False
        self._show_result = False
        self._result_timer = 0.0
        self.active = False
        self.on_complete = None
        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.border_image = create_border_surface()

    @property
    def card_found(self):
        return self._card_found

    @property
    def card_returned(self):
        return self._card_returned

    def search_table(self, table_index):
        if table_index < 0 or table_index >= self.TABLE_COUNT:
            return {"found": False, "already_searched": True}
        if table_index in self._searched_tables:
            return {"found": False, "already_searched": True}

        self._searched_tables.add(table_index)
        if table_index == self._card_table_index:
            self._card_found = True
            self.inventory.add_item("meal_card")
            return {"found": True, "already_searched": False}
        else:
            return {"found": False, "already_searched": False}

    def return_card(self):
        if not self._card_found or self._card_returned:
            return
        self._card_returned = True
        self.inventory.remove_item("meal_card")
        self.inventory.add_item("osmanthus_cake")

    def reveal_badge(self):
        if self.puzzle_manager.get_state("dining_hall").value == "solved":
            return
        self.puzzle_manager.solve("dining_hall", self.inventory)

    def handle_event(self, event):
        if not self.active:
            return
        if event.type != pygame.KEYDOWN:
            return
        if self._show_result:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._show_result = False
                self.active = False

    def update(self, dt):
        if not self.active:
            return
        if self._show_result:
            self._result_timer += dt

    def draw(self, surface):
        if not self.active or not self._show_result:
            return
        box_w, box_h = 260, 60
        box_x = (INTERNAL_WIDTH - box_w) // 2
        box_y = (INTERNAL_HEIGHT - box_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (box_x, box_y, box_w, box_h),
        )

        text = self.font.render("获得了阿姨特制的桂花糕！", True, (255, 215, 0))
        text_rect = text.get_rect(centerx=box_x + box_w // 2, centery=box_y + box_h // 2 - 10)
        surface.blit(text, text_rect)

        hint = self.font.render("入手的瞬间，你感到一阵不寻常的温热……", True, (200, 180, 100))
        hint_rect = hint.get_rect(centerx=box_x + box_w // 2, centery=box_y + box_h // 2 + 8)
        surface.blit(hint, hint_rect)

        cont = self.font.render("按 F 继续", True, COLOR_WHITE)
        cont_rect = cont.get_rect(centerx=box_x + box_w // 2, centery=box_y + box_h // 2 + 22)
        surface.blit(cont, cont_rect)
