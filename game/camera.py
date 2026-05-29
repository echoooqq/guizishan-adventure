import pygame
from config import INTERNAL_WIDTH, INTERNAL_HEIGHT, TILE_SIZE


class Camera:
    def __init__(self, map_width_tiles, map_height_tiles):
        self.x = 0.0
        self.y = 0.0
        self.map_pixel_width = map_width_tiles * TILE_SIZE
        self.map_pixel_height = map_height_tiles * TILE_SIZE

    def update(self, target_x, target_y):
        self.x = target_x - INTERNAL_WIDTH / 2
        self.y = target_y - INTERNAL_HEIGHT / 2
        max_x = max(0, self.map_pixel_width - INTERNAL_WIDTH)
        max_y = max(0, self.map_pixel_height - INTERNAL_HEIGHT)
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def apply(self, world_x, world_y):
        return world_x - self.x, world_y - self.y

    @property
    def visible_tile_range(self):
        start_col = max(0, int(self.x // TILE_SIZE))
        start_row = max(0, int(self.y // TILE_SIZE))
        end_col = min(
            self.map_pixel_width // TILE_SIZE,
            int((self.x + INTERNAL_WIDTH) // TILE_SIZE) + 1,
        )
        end_row = min(
            self.map_pixel_height // TILE_SIZE,
            int((self.y + INTERNAL_HEIGHT) // TILE_SIZE) + 1,
        )
        return start_row, end_row, start_col, end_col
