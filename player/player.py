import pygame
from config import (
    TILE_SIZE,
    PLAYER_SPEED,
    SPRINT_SPEED,
    SPRINT_STAMINA_COST,
    STAMINA_REGEN,
    MAX_STAMINA,
    PLAYER_WIDTH,
    PLAYER_HEIGHT,
    PLAYER_HITBOX_WIDTH,
    PLAYER_HITBOX_HEIGHT,
    TILE_SOLID,
    COLOR_BLACK,
    COLOR_PLAYER_BODY,
    COLOR_PLAYER_HEAD,
    COLOR_PLAYER_HAIR,
)


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.direction = "down"
        self.stamina = MAX_STAMINA
        self.is_sprinting = False
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.is_moving = False

    def update(self, dt, keys, collision_map, map_width, map_height):
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1.0

        if dy < 0 and dx == 0:
            self.direction = "up"
        elif dy > 0 and dx == 0:
            self.direction = "down"
        elif dx < 0 and dy == 0:
            self.direction = "left"
        elif dx > 0 and dy == 0:
            self.direction = "right"

        self.is_moving = dx != 0 or dy != 0

        self.is_sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.is_moving and self.stamina > 0
        speed = SPRINT_SPEED * TILE_SIZE if self.is_sprinting else PLAYER_SPEED * TILE_SIZE

        if self.is_sprinting:
            self.stamina = max(0, self.stamina - SPRINT_STAMINA_COST * dt)
        elif not self.is_moving:
            self.stamina = min(MAX_STAMINA, self.stamina + STAMINA_REGEN * dt)

        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        new_x = self.x + dx * speed * dt
        if not self._check_collision(new_x, self.y, collision_map, map_width, map_height):
            self.x = new_x

        new_y = self.y + dy * speed * dt
        if not self._check_collision(self.x, new_y, collision_map, map_width, map_height):
            self.y = new_y

        if self.is_moving:
            self.animation_timer += dt
            if self.animation_timer >= 0.15:
                self.animation_timer -= 0.15
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_frame = 0
            self.animation_timer = 0.0

    def _check_collision(self, x, y, collision_map, map_width, map_height):
        hb_x = x - PLAYER_HITBOX_WIDTH / 2
        hb_y = y - PLAYER_HITBOX_HEIGHT
        hb_w = PLAYER_HITBOX_WIDTH
        hb_h = PLAYER_HITBOX_HEIGHT

        corners = [
            (hb_x, hb_y),
            (hb_x + hb_w - 1, hb_y),
            (hb_x, hb_y + hb_h - 1),
            (hb_x + hb_w - 1, hb_y + hb_h - 1),
        ]

        for cx, cy in corners:
            tile_x = int(cx // TILE_SIZE)
            tile_y = int(cy // TILE_SIZE)
            if tile_x < 0 or tile_x >= map_width or tile_y < 0 or tile_y >= map_height:
                return True
            if collision_map[tile_y][tile_x]:
                return True
        return False

    def draw(self, surface, camera):
        draw_x, draw_y = camera.apply(
            self.x - PLAYER_WIDTH / 2,
            self.y - PLAYER_HEIGHT,
        )
        ix, iy = int(draw_x), int(draw_y)

        body_rect = pygame.Rect(ix + 1, iy + 8, PLAYER_WIDTH - 2, PLAYER_HEIGHT - 8)
        pygame.draw.rect(surface, COLOR_PLAYER_BODY, body_rect)

        head_rect = pygame.Rect(ix + 2, iy + 1, PLAYER_WIDTH - 4, 8)
        pygame.draw.rect(surface, COLOR_PLAYER_HEAD, head_rect)

        hair_rect = pygame.Rect(ix + 2, iy, PLAYER_WIDTH - 4, 3)
        pygame.draw.rect(surface, COLOR_PLAYER_HAIR, hair_rect)

        if self.direction == "down":
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 4, iy + 4, 2, 2))
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 8, iy + 4, 2, 2))
        elif self.direction == "up":
            pass
        elif self.direction == "left":
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 3, iy + 4, 2, 2))
        elif self.direction == "right":
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 9, iy + 4, 2, 2))

        if self.is_moving and self.animation_frame in (1, 3):
            offset = 1 if self.animation_frame == 1 else -1
            leg_y = iy + PLAYER_HEIGHT - 3
            pygame.draw.rect(surface, COLOR_PLAYER_BODY, (ix + 3, leg_y + offset, 3, 3))
            pygame.draw.rect(surface, COLOR_PLAYER_BODY, (ix + 8, leg_y - offset, 3, 3))
