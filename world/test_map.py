import pygame

from config import TILE_SIZE, GRASS_COLOR, PATH_COLOR, WALL_COLOR, WATER_COLOR


class TestMap:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.pixel_width = width * TILE_SIZE
        self.pixel_height = height * TILE_SIZE
        self.collision_map = [[False] * width for _ in range(height)]
        self.tile_data = [[0] * width for _ in range(height)]

        self._generate()

    def _generate(self):
        for row in range(self.height):
            for col in range(self.width):
                self.tile_data[row][col] = 0
                self.collision_map[row][col] = False

        for col in range(self.width):
            self.tile_data[0][col] = 2
            self.collision_map[0][col] = True
            self.tile_data[self.height - 1][col] = 2
            self.collision_map[self.height - 1][col] = True

        for row in range(self.height):
            self.tile_data[row][0] = 2
            self.collision_map[row][0] = True
            self.tile_data[row][self.width - 1] = 2
            self.collision_map[row][self.width - 1] = True

        self.tile_data[4][4] = 2
        self.collision_map[4][4] = True
        self.tile_data[4][5] = 2
        self.collision_map[4][5] = True

        self.tile_data[2][7] = 3
        self.collision_map[2][7] = True

        for col in range(3, 7):
            self.tile_data[6][col] = 1

        for row in range(2, 5):
            self.tile_data[row][2] = 1

    def draw(self, surface, camera):
        start_row, end_row, start_col, end_col = camera.get_visible_tile_range(TILE_SIZE)

        tile_colors = {
            0: GRASS_COLOR,
            1: PATH_COLOR,
            2: WALL_COLOR,
            3: WATER_COLOR,
        }

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_type = self.tile_data[row][col]
                color = tile_colors.get(tile_type, GRASS_COLOR)
                screen_x, screen_y = camera.apply(col * TILE_SIZE, row * TILE_SIZE)
                rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, color, rect)

                if tile_type == 2:
                    pygame.draw.rect(surface, (80, 50, 20), rect, 1)
                elif tile_type == 3:
                    highlight = pygame.Rect(screen_x + 2, screen_y + 2, TILE_SIZE - 4, 3)
                    pygame.draw.rect(surface, (100, 200, 255), highlight)
