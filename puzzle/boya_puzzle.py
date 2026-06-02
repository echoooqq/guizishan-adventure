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


class BoyaPuzzle:
    TILE_LABELS = [
        "西北", "北", "东北",
        "西",   "中", "东",
        "西南", "南", "东南",
    ]
    CORRECT_ORDER = [5, 7, 3, 1, 4, 8, 0, 2, 6]
    HINT_ORDER_TEXT = "东→南→西→北→中→东南→西北→东北→西南"

    TILE_W = 60
    TILE_H = 40
    TILE_GAP = 8
    GRID_COLS = 3
    GRID_ROWS = 3

    COLOR_UNSTEPPED = (80, 80, 80)
    COLOR_STEPPED = (200, 180, 50)
    COLOR_CURSOR_BORDER = (255, 255, 255)

    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self.active = False
        self.solved = False
        self.on_complete = None

        self._current_step = 0
        self._stepped = [False] * 9
        self._cursor_row = 1
        self._cursor_col = 1
        self._message = ""
        self._message_timer = 0.0
        self._message_duration = 2.0
        self._is_correct = False

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.title_font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE + 4)
        self.border_image = create_border_surface()

    def start(self, on_complete=None):
        if self.puzzle_manager.get_state("boya").value == "solved":
            return False
        self.active = True
        self.solved = False
        self.on_complete = on_complete
        self._current_step = 0
        self._stepped = [False] * 9
        self._cursor_row = 1
        self._cursor_col = 1
        self._message = ""
        self._message_timer = 0.0
        self._is_correct = False
        self.puzzle_manager.start_puzzle("boya")
        return True

    @property
    def has_sculpture_rubbing(self):
        return self.inventory.has_item("sculpture_rubbing")

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
        elif event.key in (pygame.K_UP, pygame.K_w):
            self._cursor_row = (self._cursor_row - 1) % self.GRID_ROWS
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self._cursor_row = (self._cursor_row + 1) % self.GRID_ROWS
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self._cursor_col = (self._cursor_col - 1) % self.GRID_COLS
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self._cursor_col = (self._cursor_col + 1) % self.GRID_COLS
        elif event.key in (pygame.K_f, pygame.K_RETURN, pygame.K_SPACE):
            self._step_tile()

    def _step_tile(self):
        idx = self._cursor_row * self.GRID_COLS + self._cursor_col

        if self._stepped[idx]:
            return

        expected = self.CORRECT_ORDER[self._current_step]

        if idx == expected:
            self._stepped[idx] = True
            self._current_step += 1

            if self._current_step >= len(self.CORRECT_ORDER):
                self.solved = True
                self._is_correct = True
                self._message = "地砖阵法破解！雕塑缓缓移开了……"
                self._message_timer = 0.0
        else:
            self._is_correct = False
            self._message = "顺序不对，重新开始！"
            self._message_timer = 0.0
            self._current_step = 0
            self._stepped = [False] * 9

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

        panel_w = 280
        panel_h = 220
        panel_x = (INTERNAL_WIDTH - panel_w) // 2
        panel_y = (INTERNAL_HEIGHT - panel_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (panel_x, panel_y, panel_w, panel_h),
        )

        title = self.title_font.render("地砖阵法", True, COLOR_CHOICE_HIGHLIGHT)
        title_rect = title.get_rect(centerx=panel_x + panel_w // 2, top=panel_y + 8)
        surface.blit(title, title_rect)

        grid_total_w = self.GRID_COLS * self.TILE_W + (self.GRID_COLS - 1) * self.TILE_GAP
        grid_total_h = self.GRID_ROWS * self.TILE_H + (self.GRID_ROWS - 1) * self.TILE_GAP
        grid_x = panel_x + (panel_w - grid_total_w) // 2
        grid_y = panel_y + 28

        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                idx = row * self.GRID_COLS + col
                tx = grid_x + col * (self.TILE_W + self.TILE_GAP)
                ty = grid_y + row * (self.TILE_H + self.TILE_GAP)

                tile_rect = pygame.Rect(tx, ty, self.TILE_W, self.TILE_H)

                if self._stepped[idx]:
                    tile_color = self.COLOR_STEPPED
                else:
                    tile_color = self.COLOR_UNSTEPPED

                pygame.draw.rect(surface, tile_color, tile_rect)

                if row == self._cursor_row and col == self._cursor_col:
                    pygame.draw.rect(surface, self.COLOR_CURSOR_BORDER, tile_rect, 2)

                label = self.font.render(self.TILE_LABELS[idx], True, COLOR_WHITE)
                label_rect = label.get_rect(center=tile_rect.center)
                surface.blit(label, label_rect)

        step_text = f"第{self._current_step + 1}步/共9步" if self._current_step < 9 else "完成"
        step_surf = self.font.render(step_text, True, COLOR_WHITE)
        surface.blit(step_surf, (grid_x, grid_y + grid_total_h + 6))

        hint_y = grid_y + grid_total_h + 20
        if self.has_sculpture_rubbing:
            hint = self.font.render(f"提示：{self.HINT_ORDER_TEXT}", True, (180, 180, 0))
            surface.blit(hint, (grid_x, hint_y))

        controls = self.font.render("方向键移动 | F踩踏 | Esc退出", True, (160, 160, 160))
        controls_rect = controls.get_rect(centerx=panel_x + panel_w // 2, bottom=panel_y + panel_h - 4)
        surface.blit(controls, controls_rect)

        if self._message:
            self._draw_message(surface)

    def _draw_message(self, surface):
        msg_w = 260
        lines = self._wrap_text(self._message, msg_w - 20)
        line_height = self.font.get_linesize()
        msg_h = max(50, len(lines) * line_height + 28)
        msg_x = (INTERNAL_WIDTH - msg_w) // 2
        msg_y = (INTERNAL_HEIGHT + 60) // 2

        draw_nine_slice(
            surface, self.border_image,
            (msg_x, msg_y, msg_w, msg_h),
        )

        color = self.COLOR_STEPPED if self._is_correct else (255, 100, 100)
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
