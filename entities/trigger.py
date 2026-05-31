import pygame
from config import INTERACTION_RANGE


class Trigger:
    def __init__(self, x, y, width, height, trigger_type, properties=None):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.trigger_type = trigger_type
        self.properties = properties or {}
        self.auto_trigger = self.properties.get("auto_trigger", False)
        self.on_trigger = None
        self.target_map = self.properties.get("target_map")
        self.spawn_point = self.properties.get("spawn_point")
        self.interaction_range = self.properties.get(
            "interaction_range", INTERACTION_RANGE
        )

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    def contains_point(self, px, py):
        return self.rect.collidepoint(px, py)

    def overlaps_rect(self, other_rect):
        return self.rect.colliderect(other_rect)

    def is_player_nearby(self, player_x, player_y):
        if self.auto_trigger:
            return False
        dx = player_x - self.center_x
        dy = player_y - self.center_y
        return dx * dx + dy * dy <= self.interaction_range * self.interaction_range

    def interact(self):
        if self.on_trigger:
            return self.on_trigger(self)
        return {
            "type": "enter",
            "object": self,
            "target_map": self.target_map,
            "spawn_point": self.spawn_point,
        }

    def draw_prompt(self, surface, camera, font):
        sx, sy = camera.apply(self.center_x, self.y - 4)
        transition_type_str = self.properties.get("transition_type", "indoor_enter")
        if transition_type_str == "floor_change":
            prompt = "按 F 切换楼层"
        elif transition_type_str == "campus_bus":
            prompt = "按 F 乘校车"
        else:
            prompt = "按 F 进入"
        text_surf = font.render(prompt, True, (255, 255, 255))
        text_rect = text_surf.get_rect(centerx=int(sx), bottom=int(sy))
        bg_rect = text_rect.inflate(6, 4)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 160))
        surface.blit(bg_surf, bg_rect.topleft)
        surface.blit(text_surf, text_rect)

    def activate(self):
        if self.on_trigger:
            return self.on_trigger(self)
        return {"type": self.trigger_type, "trigger": self}

    def draw(self, surface, camera, debug=False):
        if not debug:
            return
        sx, sy = camera.apply(self.x, self.y)
        debug_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        color = (255, 0, 0, 60) if self.auto_trigger else (0, 255, 0, 60)
        debug_surf.fill(color)
        surface.blit(debug_surf, (int(sx), int(sy)))
