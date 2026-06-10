"""NPC模块：非玩家角色逻辑、精灵渲染和互动"""
import os
import pygame
from config import (
    TILE_SIZE,
    INTERACTION_RANGE,
    NPC_WIDTH,
    NPC_HEIGHT,
    NPC_HITBOX_WIDTH,
    NPC_HITBOX_HEIGHT,
    COLOR_BLACK,
    COLOR_NPC_BODY,
    COLOR_NPC_HEAD,
    COLOR_NPC_HAIR,
)
from world.entity import Entity

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(PROJECT_ROOT, "assets", "sprites")

# NPC精灵表映射：npc_id -> 精灵文件名
NPC_SPRITE_MAP = {
    "senior_student": "senior_student_sheet.png",
    "librarian": "librarian_sheet.png",
    "dancing_auntie": "dancing_auntie_sheet.png",
    "pe_teacher": "pe_teacher_sheet.png",
    "cafeteria_auntie": "cafeteria_auntie_sheet.png",
    "guardian": "guardian_sheet.png",
    "passing_student": "passing_student_sheet.png",
    # 新增引导NPC
    "morning_student": "morning_student_sheet.png",
    "returning_student": "returning_student_sheet.png",
    "sketch_student": "sketch_student_sheet.png",
    "sport_student": "sport_student_sheet.png",
    "waiting_student": "waiting_student_sheet.png",
    "shuttle_student": "shuttle_student_sheet.png",
}

# 精灵表缓存
_sprite_cache = {}

SPRITE_FRAME_W = 16
SPRITE_FRAME_H = 24


def _load_npc_sprite(npc_id):
    """加载NPC精灵表（带缓存）"""
    if npc_id in _sprite_cache:
        return _sprite_cache[npc_id]
    filename = NPC_SPRITE_MAP.get(npc_id)
    if filename:
        path = os.path.join(SPRITES_DIR, filename)
        if os.path.exists(path):
            sheet = pygame.image.load(path).convert_alpha()
            _sprite_cache[npc_id] = sheet
            return sheet
    _sprite_cache[npc_id] = None
    return None


class NPC(Entity):
    def __init__(self, x, y, npc_id, dialogue_id, properties=None):
        super().__init__(
            x, y,
            width=NPC_WIDTH,
            height=NPC_HEIGHT,
            hitbox_width=NPC_HITBOX_WIDTH,
            hitbox_height=NPC_HITBOX_HEIGHT,
        )
        self.npc_id = npc_id
        self.dialogue_id = dialogue_id
        self.properties = properties or {}
        self.visible = True
        self.interaction_range = self.properties.get("interaction_range", INTERACTION_RANGE)
        self.prompt_text = self.properties.get("prompt_text", "对话")
        self.on_interact = None
        self.body_color = self.properties.get("body_color", COLOR_NPC_BODY)
        self.head_color = self.properties.get("head_color", COLOR_NPC_HEAD)
        self.hair_color = self.properties.get("hair_color", COLOR_NPC_HAIR)
        if "direction" in self.properties:
            self.direction = self.properties["direction"]
        self._idle_timer = 0.0
        self._idle_offset = 0
        self._sprite_sheet = None

    def _ensure_sprite_loaded(self):
        """延迟加载精灵表"""
        if self._sprite_sheet is None and self.npc_id in NPC_SPRITE_MAP:
            self._sprite_sheet = _load_npc_sprite(self.npc_id)

    def is_player_nearby(self, player_x, player_y):
        if not self.visible:
            return False
        dx = player_x - (self.x)
        dy = player_y - (self.y - self.height / 2)
        return dx * dx + dy * dy <= self.interaction_range * self.interaction_range

    def interact(self):
        if self.on_interact:
            return self.on_interact(self)
        return {"type": "dialog", "dialogue_id": self.dialogue_id, "npc": self}

    def update(self, dt):
        self._idle_timer += dt
        if self._idle_timer >= 0.6:
            self._idle_timer -= 0.6
            self._idle_offset = 1 if self._idle_offset == 0 else 0

    def draw(self, surface, camera):
        if not self.visible:
            return
        self._ensure_sprite_loaded()
        draw_x, draw_y = camera.apply(
            self.x - self.width / 2,
            self.y - self.height,
        )
        ix, iy = int(draw_x), int(draw_y) - self._idle_offset

        # 使用精灵表渲染
        if self._sprite_sheet is not None:
            col = self._idle_offset  # 0或1，对应待机动画帧
            src_rect = pygame.Rect(
                col * SPRITE_FRAME_W, 0,
                SPRITE_FRAME_W, SPRITE_FRAME_H,
            )
            offset_x = (NPC_WIDTH - SPRITE_FRAME_W) // 2
            offset_y = NPC_HEIGHT - SPRITE_FRAME_H
            surface.blit(self._sprite_sheet, (ix + offset_x, iy + offset_y), src_rect)
        else:
            # 降级：使用代码绘制
            self._draw_fallback(surface, ix, iy)

    def _draw_fallback(self, surface, ix, iy):
        """降级绘制：当精灵表不可用时使用代码绘制"""
        body_rect = pygame.Rect(ix + 1, iy + 8, self.width - 2, self.height - 8)
        pygame.draw.rect(surface, self.body_color, body_rect)

        head_rect = pygame.Rect(ix + 2, iy + 1, self.width - 4, 8)
        pygame.draw.rect(surface, self.head_color, head_rect)

        hair_rect = pygame.Rect(ix + 2, iy, self.width - 4, 3)
        pygame.draw.rect(surface, self.hair_color, hair_rect)

        if self.direction == "down":
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 4, iy + 4, 2, 2))
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 8, iy + 4, 2, 2))
        elif self.direction == "left":
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 3, iy + 4, 2, 2))
        elif self.direction == "right":
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 9, iy + 4, 2, 2))

    def draw_prompt(self, surface, camera, font):
        if not self.visible:
            return
        sx, sy = camera.apply(self.x, self.y - self.height - 4)
        text_surf = font.render(f"按 F {self.prompt_text}", True, (255, 255, 255))
        text_rect = text_surf.get_rect(centerx=int(sx), bottom=int(sy))
        bg_rect = text_rect.inflate(6, 4)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 160))
        surface.blit(bg_surf, bg_rect.topleft)
        surface.blit(text_surf, text_rect)
