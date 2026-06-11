import os
import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    DIALOG_CHAR_DELAY,
    COLOR_DIALOG_BG,
    COLOR_DIALOG_BORDER,
    COLOR_DIALOG_TEXT,
    COLOR_DIALOG_NAME,
    COLOR_CHOICE_HIGHLIGHT,
)

# 角色头像映射：说话者名称 -> 头像文件名
PORTRAIT_MAP = {
    "神秘学长": "portrait_senior_student.png",
    "图书管理员": "portrait_librarian.png",
    "广场舞阿姨": "portrait_dancing_auntie.png",
    "体育老师": "portrait_pe_teacher.png",
    "食堂阿姨": "portrait_cafeteria_auntie.png",
    "秘境守护者": "portrait_guardian.png",
}

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PORTRAIT_DIR = os.path.join(_PROJECT_ROOT, "assets", "ui", "sprites")
_portrait_cache = {}


def _load_portrait(speaker_name):
    """加载角色头像（带缓存）"""
    if speaker_name in _portrait_cache:
        return _portrait_cache[speaker_name]
    filename = PORTRAIT_MAP.get(speaker_name)
    if filename:
        path = os.path.join(_PORTRAIT_DIR, filename)
        if os.path.exists(path):
            portrait = pygame.image.load(path).convert_alpha()
            _portrait_cache[speaker_name] = portrait
            return portrait
    _portrait_cache[speaker_name] = None
    return None


def create_border_surface(size=24, border_width=3, border_color=COLOR_DIALOG_BORDER, bg_color=COLOR_DIALOG_BG):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill(bg_color)
    pygame.draw.rect(surf, border_color, (0, 0, size, size), border_width)
    inner_highlight = tuple(min(255, c + 40) for c in border_color[:3])
    pygame.draw.line(surf, inner_highlight, (border_width, border_width), (size - border_width - 1, border_width))
    pygame.draw.line(surf, inner_highlight, (border_width, border_width), (border_width, size - border_width - 1))
    return surf


def draw_nine_slice(surface, border_image, rect, border_size=3):
    x, y, w, h = rect
    bw = border_size
    img_w = border_image.get_width()
    img_h = border_image.get_height()

    min_size = 2 * bw + 1
    if w < min_size or h < min_size:
        scaled = pygame.transform.scale(border_image, (max(1, w), max(1, h)))
        surface.blit(scaled, (x, y))
        return

    corners_src = [
        (0, 0, bw, bw),
        (img_w - bw, 0, bw, bw),
        (0, img_h - bw, bw, bw),
        (img_w - bw, img_h - bw, bw, bw),
    ]
    corners_dst = [
        (x, y),
        (x + w - bw, y),
        (x, y + h - bw),
        (x + w - bw, y + h - bw),
    ]
    for src, dst in zip(corners_src, corners_dst):
        sub = border_image.subsurface(src)
        surface.blit(sub, dst)

    edges_src = [
        (bw, 0, img_w - 2 * bw, bw),
        (bw, img_h - bw, img_w - 2 * bw, bw),
        (0, bw, bw, img_h - 2 * bw),
        (img_w - bw, bw, bw, img_h - 2 * bw),
    ]
    edges_dst = [
        (x + bw, y, w - 2 * bw, bw),
        (x + bw, y + h - bw, w - 2 * bw, bw),
        (x, y + bw, bw, h - 2 * bw),
        (x + w - bw, y + bw, bw, h - 2 * bw),
    ]
    for src, dst in zip(edges_src, edges_dst):
        sub = border_image.subsurface(src)
        scaled = pygame.transform.scale(sub, (dst[2], dst[3]))
        surface.blit(scaled, (dst[0], dst[1]))

    center_src = (bw, bw, img_w - 2 * bw, img_h - 2 * bw)
    center_dst = (x + bw, y + bw, w - 2 * bw, h - 2 * bw)
    if center_dst[2] > 0 and center_dst[3] > 0:
        sub = border_image.subsurface(center_src)
        scaled = pygame.transform.scale(sub, (center_dst[2], center_dst[3]))
        surface.blit(scaled, (center_dst[0], center_dst[1]))


class DialogBox:
    BOX_MARGIN = 8
    BOX_HEIGHT = 80
    PORTRAIT_SIZE = 28
    PORTRAIT_MARGIN = 6
    TEXT_LEFT_MARGIN = 8
    TEXT_TOP_PADDING = 10
    TEXT_RIGHT_PADDING = 10
    CHOICE_INDENT = 12
    CHOICE_SPACING = 4
    LINE_SPACING = 3

    def __init__(self):
        self.active = False
        self.dialogue_data = None
        self.current_key = None
        self.current_lines = []
        self.current_index = 0
        self.displayed_text = ""
        self.full_text = ""
        self.char_timer = 0.0
        self.text_complete = False
        self.choices = None
        self.selected_choice = 0
        self.speaker = ""
        self.on_complete = None
        self.speaker_color = COLOR_DIALOG_NAME
        self.portrait_color = None
        self.game_state = {}

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.border_image = create_border_surface()

        self._box_x = self.BOX_MARGIN
        self._box_y = INTERNAL_HEIGHT - self.BOX_HEIGHT - self.BOX_MARGIN
        self._box_w = INTERNAL_WIDTH - 2 * self.BOX_MARGIN
        self._box_h = self.BOX_HEIGHT

        self._portrait_x = self._box_x + self.PORTRAIT_MARGIN
        self._portrait_y = self._box_y + self.PORTRAIT_MARGIN
        self._text_x = self._portrait_x + self.PORTRAIT_SIZE + self.TEXT_LEFT_MARGIN
        self._text_y = self._box_y + self.TEXT_TOP_PADDING
        self._text_max_width = self._box_x + self._box_w - self._text_x - self.TEXT_RIGHT_PADDING

    def start(self, dialogue_data, start_key="default", on_complete=None, speaker_color=None, portrait_color=None, game_state=None):
        self.active = True
        self.dialogue_data = dialogue_data
        self.on_complete = on_complete
        self.speaker_color = speaker_color or COLOR_DIALOG_NAME
        self.portrait_color = portrait_color or (180, 80, 80)
        self.game_state = game_state or {}
        self._load_key(start_key)

    def _load_key(self, key):
        self.current_key = key
        self.current_lines = self.dialogue_data.get(key, [])
        self.current_index = 0
        self._setup_line()

    def _setup_line(self):
        if self.current_index >= len(self.current_lines):
            self._end_dialogue()
            return

        line = self.current_lines[self.current_index]

        condition = line.get("condition")
        if condition and not self._check_condition(condition):
            self.current_index += 1
            self._setup_line()
            return

        if line.get("type") == "choice":
            filtered = []
            for opt in line.get("options", []):
                opt_cond = opt.get("condition")
                if opt_cond and not self._check_condition(opt_cond):
                    continue
                filtered.append(opt)
            self.choices = filtered if filtered else None
            if self.choices is None:
                self.current_index += 1
                self._setup_line()
                return
            self.selected_choice = 0
            self.displayed_text = ""
            self.full_text = ""
            self.text_complete = True
            self.speaker = ""
            self.char_timer = 0.0
        else:
            self.speaker = line.get("speaker", "")
            self.full_text = line.get("text", "")
            self.displayed_text = ""
            self.text_complete = False
            self.char_timer = 0.0
            self.choices = None

    def _check_condition(self, condition):
        if isinstance(condition, str):
            return self.game_state.get(condition, False)
        if isinstance(condition, dict):
            cond_type = condition.get("type", "")
            if cond_type == "has_item":
                item_id = condition.get("item_id", "")
                inventory_items = self.game_state.get("inventory", [])
                return item_id in inventory_items
            key = condition.get("key", "")
            value = condition.get("value")
            current = self._resolve_key(key)
            if value is not None:
                return current == value
            return bool(current)
        return True

    def _resolve_key(self, key):
        parts = key.split(".")
        current = self.game_state
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def _advance(self):
        if not self.text_complete:
            self.displayed_text = self.full_text
            self.text_complete = True
        else:
            self.current_index += 1
            self._setup_line()

    def _select_choice(self):
        if self.choices is None:
            return
        choice = self.choices[self.selected_choice]
        next_key = choice.get("next")
        if next_key:
            self._load_key(next_key)
        else:
            self._end_dialogue()

    def _end_dialogue(self):
        self.active = False
        self.dialogue_data = None
        self.current_lines = []
        self.choices = None
        self.displayed_text = ""
        self.full_text = ""
        self.speaker = ""
        self.text_complete = False
        self.char_timer = 0.0
        self.current_index = 0
        if self.on_complete:
            callback = self.on_complete
            self.on_complete = None
            callback()

    def update(self, dt):
        if not self.active or self.text_complete:
            return
        self.char_timer += dt
        chars_to_show = int(self.char_timer / DIALOG_CHAR_DELAY)
        if chars_to_show >= len(self.full_text):
            self.displayed_text = self.full_text
            self.text_complete = True
        else:
            self.displayed_text = self.full_text[:chars_to_show]

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type != pygame.KEYDOWN:
            return True

        if self.choices is not None:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected_choice = (self.selected_choice - 1) % len(self.choices)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected_choice = (self.selected_choice + 1) % len(self.choices)
            elif event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._select_choice()
        else:
            if event.key in (pygame.K_f, pygame.K_SPACE, pygame.K_RETURN):
                self._advance()
        return True

    def draw(self, surface):
        if not self.active:
            return

        draw_nine_slice(
            surface, self.border_image,
            (self._box_x, self._box_y, self._box_w, self._box_h),
        )

        portrait_rect = pygame.Rect(
            self._portrait_x, self._portrait_y,
            self.PORTRAIT_SIZE, self.PORTRAIT_SIZE,
        )
        # 尝试加载角色头像精灵
        portrait_sprite = _load_portrait(self.speaker) if self.speaker else None
        if portrait_sprite is not None:
            # 缩放头像到肖像框大小
            scaled = pygame.transform.scale(portrait_sprite, (self.PORTRAIT_SIZE, self.PORTRAIT_SIZE))
            surface.blit(scaled, (self._portrait_x, self._portrait_y))
            pygame.draw.rect(surface, COLOR_DIALOG_BORDER, portrait_rect, 1)
        else:
            # 降级：使用颜色矩形+简笔脸
            pygame.draw.rect(surface, self.portrait_color, portrait_rect)
            pygame.draw.rect(surface, COLOR_DIALOG_BORDER, portrait_rect, 1)
            face_cx = self._portrait_x + self.PORTRAIT_SIZE // 2
            face_cy = self._portrait_y + self.PORTRAIT_SIZE // 2
            pygame.draw.rect(surface, (0, 0, 0), (face_cx - 4, face_cy - 2, 3, 3))
            pygame.draw.rect(surface, (0, 0, 0), (face_cx + 2, face_cy - 2, 3, 3))
            pygame.draw.rect(surface, (0, 0, 0), (face_cx - 2, face_cy + 3, 4, 2))

        if self.speaker:
            name_surf = self.font.render(self.speaker, True, self.speaker_color)
            surface.blit(name_surf, (self._text_x, self._text_y))

        text_y = self._text_y
        if self.speaker:
            text_y += self.font.get_linesize() + 2

        max_y = self._box_y + self._box_h - 6

        if self.displayed_text:
            words = self.displayed_text
            line = ""
            line_y = text_y
            for ch in words:
                test = line + ch
                if self.font.size(test)[0] > self._text_max_width:
                    if line_y + self.font.get_linesize() > max_y:
                        break
                    text_surf = self.font.render(line, True, COLOR_DIALOG_TEXT)
                    surface.blit(text_surf, (self._text_x, line_y))
                    line_y += self.font.get_linesize() + self.LINE_SPACING
                    line = ch
                else:
                    line = test
            if line and line_y + self.font.get_linesize() <= max_y:
                text_surf = self.font.render(line, True, COLOR_DIALOG_TEXT)
                surface.blit(text_surf, (self._text_x, line_y))

        if self.choices is not None:
            choice_y = text_y
            if self.displayed_text:
                choice_y += self.font.get_linesize() + self.CHOICE_SPACING
            for i, choice in enumerate(self.choices):
                if choice_y + self.font.get_linesize() > max_y:
                    break
                # 选中指示器用三角形绘制（避免Zpix不支持▶）
                if i == self.selected_choice:
                    ind_x = self._text_x + self.CHOICE_INDENT - 6
                    ind_y = choice_y + self.font.get_linesize() // 2
                    pygame.draw.polygon(surface, COLOR_CHOICE_HIGHLIGHT, [
                        (ind_x, ind_y - 3),
                        (ind_x + 4, ind_y),
                        (ind_x, ind_y + 3),
                    ])
                choice_text = choice.get('text', '')
                color = COLOR_CHOICE_HIGHLIGHT if i == self.selected_choice else COLOR_DIALOG_TEXT
                choice_surf = self.font.render(choice_text, True, color)
                surface.blit(choice_surf, (self._text_x + self.CHOICE_INDENT, choice_y))
                choice_y += self.font.get_linesize()

        if self.text_complete and self.choices is None and self.current_index < len(self.current_lines):
            indicator_x = self._box_x + self._box_w - 14
            indicator_y = self._box_y + self._box_h - 12
            points = [
                (indicator_x, indicator_y),
                (indicator_x + 6, indicator_y),
                (indicator_x + 3, indicator_y + 4),
            ]
            pygame.draw.polygon(surface, COLOR_DIALOG_TEXT, points)
