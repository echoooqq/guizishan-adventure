import pygame
from config import TILE_SIZE


class Entity:
    def __init__(self, x, y, width, height, hitbox_width=None, hitbox_height=None):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.hitbox_width = hitbox_width or width
        self.hitbox_height = hitbox_height or height
        self.direction = "down"
        self.is_moving = False
        self.animation_frame = 0
        self.animation_timer = 0.0

    def get_hitbox_rect(self):
        hb_x = self.x - self.hitbox_width / 2
        hb_y = self.y - self.hitbox_height
        return pygame.Rect(hb_x, hb_y, self.hitbox_width, self.hitbox_height)

    def check_tile_collision(self, x, y, collision_map, map_width, map_height):
        hb_x = x - self.hitbox_width / 2
        hb_y = y - self.hitbox_height
        corners = [
            (hb_x, hb_y),
            (hb_x + self.hitbox_width - 1, hb_y),
            (hb_x, hb_y + self.hitbox_height - 1),
            (hb_x + self.hitbox_width - 1, hb_y + self.hitbox_height - 1),
        ]
        for cx, cy in corners:
            tile_x = int(cx // TILE_SIZE)
            tile_y = int(cy // TILE_SIZE)
            if tile_x < 0 or tile_x >= map_width or tile_y < 0 or tile_y >= map_height:
                return True
            if collision_map[tile_y][tile_x]:
                return True
        return False

    def move_with_collision(self, dx, dy, speed, dt, collision_map, map_width, map_height):
        if dx != 0 and dy != 0:
            factor = 0.7071
            dx *= factor
            dy *= factor

        new_x = self.x + dx * speed * dt
        if not self.check_tile_collision(new_x, self.y, collision_map, map_width, map_height):
            self.x = new_x

        new_y = self.y + dy * speed * dt
        if not self.check_tile_collision(self.x, new_y, collision_map, map_width, map_height):
            self.y = new_y

    def update_animation(self, dt, frame_interval=0.15, max_frames=4):
        if self.is_moving:
            self.animation_timer += dt
            if self.animation_timer >= frame_interval:
                self.animation_timer -= frame_interval
                self.animation_frame = (self.animation_frame + 1) % max_frames
        else:
            self.animation_frame = 0
            self.animation_timer = 0.0

    def update(self, dt):
        pass

    def draw(self, surface, camera):
        pass
