import os
import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    COLOR_DIALOG_BG,
    COLOR_DIALOG_BORDER,
    COLOR_DIALOG_TEXT,
    COLOR_DIALOG_NAME,
    COLOR_CHOICE_HIGHLIGHT,
    COLOR_BLACK,
    COLOR_WHITE,
)
from ui.dialog_box import create_border_surface, draw_nine_slice


CATEGORY_COLORS = {
    "key_item": (255, 200, 50),
    "tool": (100, 180, 255),
    "clue": (180, 140, 255),
    "consumable": (100, 220, 100),
    "material": (220, 160, 100),
}

CATEGORY_NAMES = {
    "key_item": "关键道具",
    "tool": "工具",
    "clue": "线索",
    "consumable": "消耗品",
    "material": "材料",
}

GRID_COLS = 5
GRID_ROWS = 4
SLOT_SIZE = 32
SLOT_GAP = 4
ICON_SIZE = 32

_icon_font = None
_count_font = None
_icon_cache = {}


def _get_icon_fonts():
    global _icon_font, _count_font
    if _icon_font is None:
        _icon_font = pygame.font.Font(FONT_PATH, 10)
        _count_font = pygame.font.Font(FONT_PATH, 8)
    return _icon_font, _count_font


def _draw_item_icon(surface, item, x, y):
    sprite_name = item.sprite
    if sprite_name not in _icon_cache:
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "ui", "sprites", f"{sprite_name}.png",
        )
        if os.path.exists(icon_path):
            try:
                icon_surf = pygame.image.load(icon_path).convert_alpha()
                icon_surf = pygame.transform.scale(icon_surf, (ICON_SIZE, ICON_SIZE))
                _icon_cache[sprite_name] = icon_surf
            except pygame.error:
                _icon_cache[sprite_name] = None
        else:
            _icon_cache[sprite_name] = None

    cached = _icon_cache.get(sprite_name)
    if cached is not None:
        surface.blit(cached, (x, y))
        if item.count > 1:
            _, count_font = _get_icon_fonts()
            count_surf = count_font.render(str(item.count), True, COLOR_WHITE)
            surface.blit(count_surf, (x + ICON_SIZE - count_surf.get_width() - 2, y + ICON_SIZE - count_surf.get_height()))
        return

    cat_color = CATEGORY_COLORS.get(item.category, (180, 180, 180))
    pygame.draw.rect(surface, cat_color, (x + 2, y + 2, ICON_SIZE - 4, ICON_SIZE - 4))
    darker = tuple(max(0, c - 60) for c in cat_color)
    pygame.draw.rect(surface, darker, (x + 2, y + 2, ICON_SIZE - 4, ICON_SIZE - 4), 1)
    icon_font, count_font = _get_icon_fonts()
    char = item.name[0] if item.name else "?"
    char_surf = icon_font.render(char, True, COLOR_BLACK)
    char_rect = char_surf.get_rect(centerx=x + ICON_SIZE // 2, centery=y + ICON_SIZE // 2)
    surface.blit(char_surf, char_rect)
    if item.count > 1:
        count_surf = count_font.render(str(item.count), True, COLOR_WHITE)
        surface.blit(count_surf, (x + ICON_SIZE - count_surf.get_width() - 2, y + ICON_SIZE - count_surf.get_height()))


class InventoryUI:
    PANEL_MARGIN = 10
    TITLE_HEIGHT = 18
    DETAIL_MIN_WIDTH = 180
    BUTTON_HEIGHT = 16
    BUTTON_GAP = 4

    def __init__(self):
        self.active = False
        self.inventory = None
        self.selected_index = 0
        self.combine_mode = False
        self.combine_first_id = ""
        self.message = ""
        self.message_timer = 0.0

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.small_font = pygame.font.Font(FONT_PATH, 10)
        self.title_font = pygame.font.Font(FONT_PATH, 14)

        self.border_image = create_border_surface(
            size=24, border_width=3,
            border_color=COLOR_DIALOG_BORDER,
            bg_color=COLOR_DIALOG_BG,
        )
        self.slot_border_image = create_border_surface(
            size=SLOT_SIZE, border_width=2,
            border_color=(80, 80, 110),
            bg_color=(40, 40, 60, 200),
        )

        self._layout()

    def _layout(self):
        grid_w = GRID_COLS * (SLOT_SIZE + SLOT_GAP) - SLOT_GAP
        grid_h = GRID_ROWS * (SLOT_SIZE + SLOT_GAP) - SLOT_GAP
        detail_w = self.DETAIL_MIN_WIDTH
        content_w = grid_w + SLOT_GAP * 2 + detail_w
        content_h = self.TITLE_HEIGHT + grid_h + self.BUTTON_HEIGHT + SLOT_GAP * 3
        panel_w = content_w + self.PANEL_MARGIN * 2
        panel_h = content_h + self.PANEL_MARGIN * 2
        self.panel_x = (INTERNAL_WIDTH - panel_w) // 2
        self.panel_y = (INTERNAL_HEIGHT - panel_h) // 2
        self.panel_w = panel_w
        self.panel_h = panel_h

        self.grid_x = self.panel_x + self.PANEL_MARGIN
        self.grid_y = self.panel_y + self.PANEL_MARGIN + self.TITLE_HEIGHT + SLOT_GAP

        self.detail_x = self.grid_x + grid_w + SLOT_GAP * 2
        self.detail_y = self.grid_y
        self.detail_w = detail_w
        self.detail_h = grid_h

        self.button_y = self.grid_y + grid_h + SLOT_GAP

    def open(self, inventory, player=None):
        self.active = True
        self.inventory = inventory
        self.player = player
        self.selected_index = 0
        self.combine_mode = False
        self.combine_first_id = ""
        self.message = ""
        self.message_timer = 0.0

    def close(self):
        self.active = False
        self.inventory = None
        self.combine_mode = False
        self.combine_first_id = ""

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type != pygame.KEYDOWN:
            return True

        if event.key in (pygame.K_TAB, pygame.K_i, pygame.K_ESCAPE):
            if self.combine_mode:
                self.combine_mode = False
                self.combine_first_id = ""
                self.message = ""
            else:
                self.close()
            return True

        if event.key == pygame.K_UP:
            self._move_selection(0, -1)
        elif event.key == pygame.K_DOWN:
            self._move_selection(0, 1)
        elif event.key == pygame.K_LEFT:
            self._move_selection(-1, 0)
        elif event.key == pygame.K_RIGHT:
            self._move_selection(1, 0)
        elif event.key == pygame.K_f or event.key == pygame.K_RETURN:
            self._action_use()
        elif event.key == pygame.K_c:
            self._action_combine()
        elif event.key == pygame.K_d:
            self._action_drop()

        return True

    def _move_selection(self, dx, dy):
        if not self.inventory or len(self.inventory.items) == 0:
            return
        col = self.selected_index % GRID_COLS
        row = self.selected_index // GRID_COLS
        col = (col + dx) % GRID_COLS
        row = (row + dy) % GRID_ROWS
        new_index = row * GRID_COLS + col
        max_index = len(self.inventory.items)
        if new_index < max_index:
            self.selected_index = new_index
        elif dx != 0:
            col = 0 if dx > 0 else GRID_COLS - 1
            new_index = row * GRID_COLS + col
            if new_index < max_index:
                self.selected_index = new_index
        elif dy != 0:
            row_end = min((row + 1) * GRID_COLS, max_index) - 1
            if row_end >= row * GRID_COLS:
                self.selected_index = row_end
            else:
                last_row = (max_index - 1) // GRID_COLS
                last_row_end = max_index - 1
                if last_row >= 0:
                    self.selected_index = last_row_end

    def _action_use(self):
        if not self.inventory:
            return
        if self.selected_index >= len(self.inventory.items):
            return
        item = self.inventory.items[self.selected_index]
        item_name = item.name
        result = self.inventory.use_item(item.id)
        self.message = result.get("message", "")
        self.message_timer = 2.0
        effect = result.get("effect")
        if effect and self.player:
            if effect.get("type") == "stamina_restore":
                from config import MAX_STAMINA
                old_stamina = self.player.stamina
                self.player.stamina = min(MAX_STAMINA, self.player.stamina + effect.get("value", 0))
                restored = int(self.player.stamina - old_stamina)
                self.message = f"使用了{item_name}，恢复了{restored}点体力！"
        if self.selected_index >= len(self.inventory.items) and self.selected_index > 0:
            self.selected_index = len(self.inventory.items) - 1

    def _action_combine(self):
        if not self.inventory:
            return
        if self.selected_index >= len(self.inventory.items):
            return
        item = self.inventory.items[self.selected_index]
        if not self.combine_mode:
            combinable = self.inventory.get_combinable_items(item.id)
            if combinable:
                self.combine_mode = True
                self.combine_first_id = item.id
                self.message = f"选择与{item.name}组合的道具"
                self.message_timer = 5.0
            else:
                self.message = f"{item.name}无法与其他道具组合"
                self.message_timer = 2.0
        else:
            if item.id == self.combine_first_id:
                self.combine_mode = False
                self.combine_first_id = ""
                self.message = "取消组合"
                self.message_timer = 2.0
                return
            first_item = self.inventory.get_item(self.combine_first_id)
            if not first_item:
                self.combine_mode = False
                self.combine_first_id = ""
                return
            result_id = self.inventory.combine(first_item.id, item.id)
            if result_id:
                result_data = self.inventory.get_item(result_id)
                result_name = result_data.name if result_data else result_id
                self.message = f"组合成功！获得{result_name}"
                self.message_timer = 3.0
            else:
                self.message = "这两个道具无法组合"
                self.message_timer = 2.0
            self.combine_mode = False
            self.combine_first_id = ""
            if self.selected_index >= len(self.inventory.items) and self.selected_index > 0:
                self.selected_index = len(self.inventory.items) - 1

    def _action_drop(self):
        if not self.inventory:
            return
        if self.selected_index >= len(self.inventory.items):
            return
        item = self.inventory.items[self.selected_index]
        if not item.droppable:
            self.message = f"{item.name}是关键道具，无法丢弃"
            self.message_timer = 2.0
            return
        name = item.name
        self.inventory.remove_item(item.id)
        self.message = f"丢弃了{name}"
        self.message_timer = 2.0
        if self.selected_index >= len(self.inventory.items) and self.selected_index > 0:
            self.selected_index = len(self.inventory.items) - 1

    def update(self, dt):
        if not self.active:
            return
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def draw(self, surface):
        if not self.active:
            return

        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        surface.blit(overlay, (0, 0))

        draw_nine_slice(
            surface, self.border_image,
            (self.panel_x, self.panel_y, self.panel_w, self.panel_h),
        )

        title_surf = self.title_font.render("背包", True, COLOR_DIALOG_NAME)
        surface.blit(title_surf, (self.panel_x + self.PANEL_MARGIN, self.panel_y + self.PANEL_MARGIN))

        close_text = "关闭(Tab)"
        close_surf = self.small_font.render(close_text, True, COLOR_DIALOG_TEXT)
        surface.blit(close_surf, (self.panel_x + self.panel_w - self.PANEL_MARGIN - close_surf.get_width(), self.panel_y + self.PANEL_MARGIN + 2))

        self._draw_grid(surface)
        self._draw_detail(surface)
        self._draw_buttons(surface)

        if self.message:
            msg_surf = self.font.render(self.message, True, COLOR_CHOICE_HIGHLIGHT)
            msg_x = self.panel_x + (self.panel_w - msg_surf.get_width()) // 2
            msg_y = self.panel_y + self.panel_h - self.PANEL_MARGIN - 14
            bg_rect = msg_surf.get_rect(topleft=(msg_x, msg_y))
            bg_surf = pygame.Surface((bg_rect.width + 6, bg_rect.height + 4), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 180))
            surface.blit(bg_surf, (bg_rect.x - 3, bg_rect.y - 2))
            surface.blit(msg_surf, (msg_x, msg_y))

    def _draw_grid(self, surface):
        if not self.inventory:
            return
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                idx = row * GRID_COLS + col
                sx = self.grid_x + col * (SLOT_SIZE + SLOT_GAP)
                sy = self.grid_y + row * (SLOT_SIZE + SLOT_GAP)

                is_selected = idx == self.selected_index
                is_combine_first = self.combine_mode and idx < len(self.inventory.items) and self.inventory.items[idx].id == self.combine_first_id

                if is_selected:
                    highlight = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
                    highlight.fill((255, 215, 0, 60))
                    surface.blit(highlight, (sx, sy))
                    pygame.draw.rect(surface, COLOR_CHOICE_HIGHLIGHT, (sx, sy, SLOT_SIZE, SLOT_SIZE), 2)
                elif is_combine_first:
                    highlight = pygame.Surface((SLOT_SIZE, SLOT_SIZE), pygame.SRCALPHA)
                    highlight.fill((100, 255, 100, 60))
                    surface.blit(highlight, (sx, sy))
                    pygame.draw.rect(surface, (100, 255, 100), (sx, sy, SLOT_SIZE, SLOT_SIZE), 2)
                else:
                    draw_nine_slice(
                        surface, self.slot_border_image,
                        (sx, sy, SLOT_SIZE, SLOT_SIZE),
                    )

                if idx < len(self.inventory.items):
                    item = self.inventory.items[idx]
                    _draw_item_icon(surface, item, sx, sy)
                else:
                    empty_surf = self.small_font.render("空", True, (80, 80, 100))
                    empty_rect = empty_surf.get_rect(centerx=sx + SLOT_SIZE // 2, centery=sy + SLOT_SIZE // 2)
                    surface.blit(empty_surf, empty_rect)

    def _draw_detail(self, surface):
        draw_nine_slice(
            surface, self.border_image,
            (self.detail_x, self.detail_y, self.detail_w, self.detail_h),
        )

        if not self.inventory or self.selected_index >= len(self.inventory.items):
            hint_surf = self.small_font.render("选择道具查看详情", True, (120, 120, 140))
            hint_rect = hint_surf.get_rect(
                centerx=self.detail_x + self.detail_w // 2,
                centery=self.detail_y + self.detail_h // 2,
            )
            surface.blit(hint_surf, hint_rect)
            return

        item = self.inventory.items[self.selected_index]
        tx = self.detail_x + 6
        ty = self.detail_y + 6
        max_w = self.detail_w - 12

        name_surf = self.font.render(item.name, True, COLOR_DIALOG_NAME)
        surface.blit(name_surf, (tx, ty))
        ty += self.font.get_linesize() + 2

        cat_name = CATEGORY_NAMES.get(item.category, item.category)
        cat_color = CATEGORY_COLORS.get(item.category, COLOR_DIALOG_TEXT)
        cat_surf = self.small_font.render(f"类别: {cat_name}", True, cat_color)
        surface.blit(cat_surf, (tx, ty))
        ty += self.small_font.get_linesize() + 2

        if item.count > 1:
            count_surf = self.small_font.render(f"数量: {item.count}", True, COLOR_DIALOG_TEXT)
            surface.blit(count_surf, (tx, ty))
            ty += self.small_font.get_linesize() + 2

        pygame.draw.line(surface, (80, 80, 110), (tx, ty), (tx + max_w - 12, ty))
        ty += 4

        desc = item.description
        line = ""
        for ch in desc:
            test = line + ch
            if self.small_font.size(test)[0] > max_w:
                desc_surf = self.small_font.render(line, True, COLOR_DIALOG_TEXT)
                surface.blit(desc_surf, (tx, ty))
                ty += self.small_font.get_linesize()
                line = ch
            else:
                line = test
        if line:
            desc_surf = self.small_font.render(line, True, COLOR_DIALOG_TEXT)
            surface.blit(desc_surf, (tx, ty))
            ty += self.small_font.get_linesize()

        if item.combinable_with:
            ty += 4
            combine_surf = self.small_font.render("可组合", True, (100, 255, 100))
            surface.blit(combine_surf, (tx, ty))

    def _draw_buttons(self, surface):
        buttons = [
            ("使用(F)", "use"),
            ("组合(C)", "combine"),
            ("丢弃(D)", "drop"),
        ]
        bx = self.grid_x
        by = self.button_y
        btn_w = 52
        for label, action in buttons:
            is_active = False
            if action == "combine" and self.combine_mode:
                is_active = True
            rect = pygame.Rect(bx, by, btn_w, self.BUTTON_HEIGHT)
            if is_active:
                pygame.draw.rect(surface, (80, 120, 80), rect)
                pygame.draw.rect(surface, (100, 255, 100), rect, 1)
            else:
                pygame.draw.rect(surface, (50, 50, 70), rect)
                pygame.draw.rect(surface, (80, 80, 110), rect, 1)
            btn_surf = self.small_font.render(label, True, COLOR_DIALOG_TEXT)
            btn_rect = btn_surf.get_rect(center=rect.center)
            surface.blit(btn_surf, btn_rect)
            bx += btn_w + self.BUTTON_GAP
