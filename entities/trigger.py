import pygame


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

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def contains_point(self, px, py):
        return self.rect.collidepoint(px, py)

    def overlaps_rect(self, other_rect):
        return self.rect.colliderect(other_rect)

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
