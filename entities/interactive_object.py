import pygame
from config import INTERACTION_RANGE, TILE_SIZE


class InteractiveObject:
    def __init__(self, x, y, width, height, interactive_type, properties=None):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.interactive_type = interactive_type
        self.properties = properties or {}
        self.interaction_range = self.properties.get("interaction_range", INTERACTION_RANGE)
        self.prompt_text = self.properties.get("prompt_text", self._default_prompt())
        self.interacted = False
        self.on_interact = None
        self.color = self.properties.get("color", (120, 100, 80))
        self.item_id = self.properties.get("item_id", "")

    def _default_prompt(self):
        prompts = {
            "dialog": "对话",
            "examine": "查看",
            "pickup": "拾取",
            "use": "使用",
            "mechanism": "操作",
        }
        return prompts.get(self.interactive_type, "互动")

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    def is_player_nearby(self, player_x, player_y):
        if self.interactive_type == "pickup" and self.interacted:
            return False
        dx = player_x - self.center_x
        dy = player_y - self.center_y
        return dx * dx + dy * dy <= self.interaction_range * self.interaction_range

    def interact(self):
        if self.interactive_type == "pickup" and self.interacted:
            return None
        if self.on_interact:
            return self.on_interact(self)
        result = {"type": self.interactive_type, "object": self}
        if self.interactive_type == "dialog":
            result["dialogue_id"] = self.properties.get("dialogue_id", "")
        return result

    def draw(self, surface, camera):
        if self.interactive_type == "pickup" and self.interacted:
            return
        sx, sy = camera.apply(self.x, self.y)
        ix, iy = int(sx), int(sy)
        rect = pygame.Rect(ix, iy, self.width, self.height)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (200, 200, 200), rect, 1)

    def draw_prompt(self, surface, camera, font):
        sx, sy = camera.apply(self.center_x, self.y - 4)
        text_surf = font.render(f"[F] {self.prompt_text}", True, (255, 255, 255))
        text_rect = text_surf.get_rect(centerx=int(sx), bottom=int(sy))
        bg_rect = text_rect.inflate(6, 4)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 160))
        surface.blit(bg_surf, bg_rect.topleft)
        surface.blit(text_surf, text_rect)
