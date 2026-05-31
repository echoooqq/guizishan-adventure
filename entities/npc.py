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

    def is_player_nearby(self, player_x, player_y):
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
        draw_x, draw_y = camera.apply(
            self.x - self.width / 2,
            self.y - self.height,
        )
        ix, iy = int(draw_x), int(draw_y) - self._idle_offset

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
        sx, sy = camera.apply(self.x, self.y - self.height - 4)
        text_surf = font.render(f"[F] {self.prompt_text}", True, (255, 255, 255))
        text_rect = text_surf.get_rect(centerx=int(sx), bottom=int(sy))
        bg_rect = text_rect.inflate(6, 4)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 160))
        surface.blit(bg_surf, bg_rect.topleft)
        surface.blit(text_surf, text_rect)
