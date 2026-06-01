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
        self.active = False
        self.on_complete = None

        self._card_table_index = random.randint(0, self.TABLE_COUNT - 1)
        self._searched_tables = set()
        self._card_found = False
        self._card_returned = False
        self._kitchen_open = False
        self._badge_obtained = False

        self._searching = False
        self._search_timer = 0.0
        self._search_duration = 0.6
        self._search_table_index = -1

        self._show_message = False
        self._message_text = ""
        self._message_timer = 0.0
        self._message_duration = 2.0

        self._show_result = False
        self._result_timer = 0.0
        self._result_duration = 2.5

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.border_image = create_border_surface()

    def start(self, on_complete=None):
        if self.puzzle_manager.get_state("dining_hall").value == "solved":
            return False
        self.active = True
        self.on_complete = on_complete
        self._searched_tables = set()
        self._card_found = False
        self._card_returned = False
        self._kitchen_open = False
        self._badge_obtained = False
        self._searching = False
        self._show_message = False
        self._show_result = False
        self._card_table_index = random.randint(0, self.TABLE_COUNT - 1)
        self.puzzle_manager.start_puzzle("dining_hall")
        return True

    @property
    def card_found(self):
        return self._card_found

    @property
    def card_returned(self):
        return self._card_returned

    @property
    def kitchen_open(self):
        return self._kitchen_open

    def return_card(self):
        if not self._card_found or self._card_returned:
            return
        self._card_returned = True
        self._kitchen_open = True
        self.inventory.remove_item("meal_card")

    def search_table(self, table_index):
        if table_index < 0 or table_index >= self.TABLE_COUNT:
            return
        if table_index in self._searched_tables:
            self._show_message_text("已经搜索过这张桌子了。")
            return

        self._searching = True
        self._search_timer = 0.0
        self._search_table_index = table_index

    def pickup_badge(self):
        if self._badge_obtained:
            return
        self._badge_obtained = True
        self.puzzle_manager.solve("dining_hall", self.inventory)

    def _show_message_text(self, text):
        self._show_message = True
        self._message_text = text
        self._message_timer = 0.0

    def _finish(self):
        self.active = False
        if self.on_complete:
            callback = self.on_complete
            self.on_complete = None
            callback()

    def handle_event(self, event):
        if not self.active:
            return
        if event.type != pygame.KEYDOWN:
            return

        if self._show_result:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._finish()
            return

        if self._show_message:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._show_message = False
            return

        if self._searching:
            return

        if event.key == pygame.K_ESCAPE:
            self._finish()

    def update(self, dt):
        if not self.active:
            return

        if self._searching:
            self._search_timer += dt
            if self._search_timer >= self._search_duration:
                self._searching = False
                idx = self._search_table_index
                self._searched_tables.add(idx)
                if idx == self._card_table_index:
                    self._card_found = True
                    self.inventory.add_item("meal_card")
                    self._show_message_text("找到了饭卡！赶紧还给食堂阿姨吧！")
                else:
                    self._show_message_text("这里没有……试试其他桌子吧。")

        if self._show_message:
            self._message_timer += dt

        if self._show_result:
            self._result_timer += dt

    def trigger_badge_pickup(self):
        self._show_result = True
        self._result_timer = 0.0
        self.pickup_badge()

    def draw(self, surface):
        if not self.active:
            return

        panel_w, panel_h = 280, 160
        panel_x = (INTERNAL_WIDTH - panel_w) // 2
        panel_y = (INTERNAL_HEIGHT - panel_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (panel_x, panel_y, panel_w, panel_h),
        )

        title = self.font.render("学子食堂·饭卡迷踪", True, (255, 215, 0))
        surface.blit(title, (panel_x + 10, panel_y + 8))

        status_y = panel_y + 28
        if self._card_found and self._card_returned:
            status = self.font.render("饭卡已归还，后厨已开启！", True, (100, 255, 100))
        elif self._card_found:
            status = self.font.render("已找到饭卡，快去还给阿姨！", True, (255, 255, 100))
        else:
            searched = len(self._searched_tables)
            status = self.font.render(f"搜索餐桌中……（已查{searched}/{self.TABLE_COUNT}）", True, COLOR_WHITE)
        surface.blit(status, (panel_x + 10, status_y))

        table_y = panel_y + 50
        table_spacing = 80
        table_start_x = panel_x + 20

        for i in range(self.TABLE_COUNT):
            tx = table_start_x + i * table_spacing
            ty = table_y

            is_searched = i in self._searched_tables
            is_searching = self._searching and i == self._search_table_index
            has_card = (i == self._card_table_index) and self._card_found

            if is_searching:
                progress = self._search_timer / self._search_duration
                bar_w = 60
                bar_h = 6
                pygame.draw.rect(surface, (60, 60, 60), (tx, ty + 30, bar_w, bar_h))
                pygame.draw.rect(surface, (100, 200, 255), (tx, ty + 30, int(bar_w * progress), bar_h))
                label = self.font.render("搜索中……", True, (100, 200, 255))
                surface.blit(label, (tx, ty + 10))
            elif is_searched:
                if has_card:
                    pygame.draw.rect(surface, (80, 180, 80), (tx, ty, 60, 30))
                    label = self.font.render("找到饭卡！", True, (80, 255, 80))
                else:
                    pygame.draw.rect(surface, (100, 80, 80), (tx, ty, 60, 30))
                    label = self.font.render("没有", True, (180, 100, 100))
                surface.blit(label, (tx, ty + 10))
            else:
                pygame.draw.rect(surface, (120, 100, 80), (tx, ty, 60, 30))
                pygame.draw.rect(surface, (180, 160, 120), (tx, ty, 60, 30), 1)
                label = self.font.render(f"餐桌{i + 1}", True, COLOR_WHITE)
                surface.blit(label, (tx + 8, ty + 10))

        hint_y = panel_y + panel_h - 30
        if not self._card_found:
            hint = self.font.render("靠近餐桌按 F 搜索 | Esc退出", True, (180, 180, 180))
        elif not self._card_returned:
            hint = self.font.render("去1楼找食堂阿姨归还饭卡 | Esc退出", True, (180, 180, 180))
        else:
            hint = self.font.render("后厨已开启，去冰箱看看吧！", True, (100, 255, 100))
        surface.blit(hint, (panel_x + 10, hint_y))

        if self._show_message:
            self._draw_message(surface)

        if self._show_result:
            self._draw_result_overlay(surface)

    def _draw_message(self, surface):
        msg_w, msg_h = 220, 36
        msg_x = (INTERNAL_WIDTH - msg_w) // 2
        msg_y = INTERNAL_HEIGHT // 2 + 60

        draw_nine_slice(
            surface, self.border_image,
            (msg_x, msg_y, msg_w, msg_h),
        )

        msg_surf = self.font.render(self._message_text, True, COLOR_WHITE)
        msg_rect = msg_surf.get_rect(centerx=msg_x + msg_w // 2, centery=msg_y + msg_h // 2)
        surface.blit(msg_surf, msg_rect)

    def _draw_result_overlay(self, surface):
        box_w, box_h = 240, 50
        box_x = (INTERNAL_WIDTH - box_w) // 2
        box_y = (INTERNAL_HEIGHT - box_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (box_x, box_y, box_w, box_h),
        )

        text = self.font.render("获得了桂花徽章碎片·陆！", True, (255, 215, 0))
        text_rect = text.get_rect(centerx=box_x + box_w // 2, centery=box_y + box_h // 2 - 6)
        surface.blit(text, text_rect)

        hint = self.font.render("按 F 继续", True, COLOR_WHITE)
        hint_rect = hint.get_rect(centerx=box_x + box_w // 2, centery=box_y + box_h // 2 + 10)
        surface.blit(hint, hint_rect)
