import pygame
from config import (
    TILE_SIZE,
    TILE_GRASS,
    TILE_PATH,
    TILE_WALL,
    TILE_WATER,
    TILE_TREE,
    TILE_GRASS_DARK,
    TEST_MAP_WIDTH,
    TEST_MAP_HEIGHT,
    COLOR_GRASS,
    COLOR_GRASS_DARK,
    COLOR_PATH,
    COLOR_PATH_DARK,
    COLOR_WALL,
    COLOR_WALL_TOP,
    COLOR_WATER,
    COLOR_WATER_LIGHT,
    COLOR_TREE_TRUNK,
    COLOR_TREE_LEAF,
    COLOR_TREE_LEAF_DARK,
    TILE_SOLID,
)


class TestMap:
    def __init__(self):
        self.width = TEST_MAP_WIDTH
        self.height = TEST_MAP_HEIGHT
        self.tiles = [[TILE_GRASS] * self.width for _ in range(self.height)]
        self.collision_map = [[False] * self.width for _ in range(self.height)]
        self._generate()
        self._build_collision()
        self._tile_cache = {}
        self._prerender_tiles()

    def _generate(self):
        for x in range(self.width):
            self.tiles[0][x] = TILE_WALL
            self.tiles[self.height - 1][x] = TILE_WALL
        for y in range(self.height):
            self.tiles[y][0] = TILE_WALL
            self.tiles[y][self.width - 1] = TILE_WALL

        mid_y = self.height // 2
        for x in range(1, self.width - 1):
            self.tiles[mid_y][x] = TILE_PATH
            self.tiles[mid_y - 1][x] = TILE_PATH

        mid_x = self.width // 2
        for y in range(1, self.height - 1):
            self.tiles[y][mid_x] = TILE_PATH
            self.tiles[y][mid_x - 1] = TILE_PATH

        buildings = [
            (3, 2, 6, 4),
            (3, 14, 6, 4),
            (30, 2, 7, 5),
            (30, 14, 7, 5),
        ]
        for bx, by, bw, bh in buildings:
            for y in range(by, by + bh):
                for x in range(bx, bx + bw):
                    if 0 <= y < self.height and 0 <= x < self.width:
                        if y == by:
                            self.tiles[y][x] = TILE_WALL
                        elif x == bx or x == bx + bw - 1:
                            self.tiles[y][x] = TILE_WALL
                        else:
                            self.tiles[y][x] = TILE_PATH

        trees = [
            (10, 3), (11, 3), (10, 5), (11, 5),
            (15, 8), (16, 8), (15, 10), (16, 10),
            (25, 3), (26, 3), (25, 5), (26, 5),
            (25, 16), (26, 16), (25, 18), (26, 18),
            (10, 16), (11, 16), (10, 18), (11, 18),
            (20, 4), (20, 17),
        ]
        for tx, ty in trees:
            if 0 <= ty < self.height and 0 <= tx < self.width:
                self.tiles[ty][tx] = TILE_TREE

        pond_x, pond_y, pond_w, pond_h = 18, 9, 4, 3
        for y in range(pond_y, pond_y + pond_h):
            for x in range(pond_x, pond_x + pond_w):
                if 0 <= y < self.height and 0 <= x < self.width:
                    self.tiles[y][x] = TILE_WATER

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.tiles[y][x] == TILE_GRASS:
                    if (x + y) % 3 == 0:
                        self.tiles[y][x] = TILE_GRASS_DARK

    def _build_collision(self):
        for y in range(self.height):
            for x in range(self.width):
                self.collision_map[y][x] = self.tiles[y][x] in TILE_SOLID

    def _prerender_tiles(self):
        size = (TILE_SIZE, TILE_SIZE)
        self._tile_cache[TILE_GRASS] = self._make_tile(COLOR_GRASS, size)
        self._tile_cache[TILE_GRASS_DARK] = self._make_tile(COLOR_GRASS_DARK, size)
        self._tile_cache[TILE_PATH] = self._make_tile_path(size)
        self._tile_cache[TILE_WALL] = self._make_tile_wall(size)
        self._tile_cache[TILE_WATER] = self._make_tile_water(size)
        self._tile_cache[TILE_TREE] = self._make_tile_tree(size)

    def _make_tile(self, color, size):
        surf = pygame.Surface(size)
        surf.fill(color)
        return surf

    def _make_tile_path(self, size):
        surf = pygame.Surface(size)
        surf.fill(COLOR_PATH)
        pygame.draw.rect(surf, COLOR_PATH_DARK, (0, 0, TILE_SIZE, 1))
        pygame.draw.rect(surf, COLOR_PATH_DARK, (0, 0, 1, TILE_SIZE))
        return surf

    def _make_tile_wall(self, size):
        surf = pygame.Surface(size)
        surf.fill(COLOR_WALL)
        pygame.draw.rect(surf, COLOR_WALL_TOP, (0, 0, TILE_SIZE, 4))
        pygame.draw.line(surf, (90, 60, 30), (0, 4), (TILE_SIZE, 4))
        pygame.draw.line(surf, (90, 60, 30), (TILE_SIZE // 2, 0), (TILE_SIZE // 2, 4))
        return surf

    def _make_tile_water(self, size):
        surf = pygame.Surface(size)
        surf.fill(COLOR_WATER)
        pygame.draw.line(surf, COLOR_WATER_LIGHT, (2, 4), (6, 4))
        pygame.draw.line(surf, COLOR_WATER_LIGHT, (9, 10), (13, 10))
        return surf

    def _make_tile_tree(self, size):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.rect(surf, COLOR_TREE_TRUNK, (6, 10, 4, 6))
        pygame.draw.circle(surf, COLOR_TREE_LEAF, (8, 6), 6)
        pygame.draw.circle(surf, COLOR_TREE_LEAF_DARK, (6, 5), 3)
        return surf

    def draw(self, surface, camera):
        start_row, end_row, start_col, end_col = camera.visible_tile_range
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_type = self.tiles[row][col]
                tile_surf = self._tile_cache.get(tile_type)
                if tile_surf:
                    sx, sy = camera.apply(col * TILE_SIZE, row * TILE_SIZE)
                    surface.blit(tile_surf, (int(sx), int(sy)))

    def get_spawn_position(self):
        return (self.width // 2) * TILE_SIZE + TILE_SIZE // 2, \
               (self.height // 2) * TILE_SIZE + TILE_SIZE // 2
