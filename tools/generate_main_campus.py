import os
import sys
import random
import pygame
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TILE_SIZE

MAP_WIDTH = 120
MAP_HEIGHT = 80

GID_EMPTY = 0
GID_GRASS = 1
GID_GRASS_DARK = 2
GID_PATH_STONE = 3
GID_PATH_DIRT = 4
GID_WALL_BRICK = 5
GID_WALL_BRICK_TOP = 6
GID_WALL_GRAY = 7
GID_WALL_GRAY_WINDOW = 8
GID_BUILDING_DOOR = 9
GID_BUILDING_ROOF = 10
GID_WATER = 11
GID_TREE_OSMANTHUS = 12
GID_TREE_GREEN = 13
GID_BUSH = 14
GID_FLOWER_BED = 15
GID_LAMP = 16
GID_BENCH = 17
GID_FENCE = 18
GID_FOUNTAIN_BASE = 19
GID_FOUNTAIN_WATER = 20
GID_SCULPTURE = 21
GID_BUS_STOP = 22
GID_HEDGE = 23
GID_COLLISION = 24
GID_FLOWER_GARDEN = 25
GID_TREE_CLUSTER = 26
GID_LAWN_ROCK = 27

TILE_COUNT = 27

SOLID_GIDS = {
    GID_WALL_BRICK, GID_WALL_BRICK_TOP, GID_WALL_GRAY,
    GID_WALL_GRAY_WINDOW, GID_BUILDING_ROOF, GID_WATER,
    GID_TREE_OSMANTHUS, GID_TREE_GREEN, GID_BUSH,
    GID_FLOWER_BED, GID_LAMP, GID_BENCH, GID_FENCE,
    GID_FOUNTAIN_BASE, GID_FOUNTAIN_WATER, GID_SCULPTURE,
    GID_BUS_STOP, GID_HEDGE, GID_COLLISION,
    GID_FLOWER_GARDEN, GID_TREE_CLUSTER,
}


def create_tileset(output_path):
    pygame.init()
    surface = pygame.Surface((TILE_COUNT * TILE_SIZE, TILE_SIZE))

    for i in range(1, TILE_COUNT + 1):
        x = (i - 1) * TILE_SIZE
        _draw_tile(surface, i, x)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pygame.image.save(surface, output_path)
    pygame.quit()
    print(f"Tileset saved to {output_path}")


def _draw_tile(surface, gid, x):
    rect = pygame.Rect(x, 0, TILE_SIZE, TILE_SIZE)
    if gid == GID_GRASS:
        surface.fill((76, 153, 0), rect)
        for dx, dy in [(3, 5), (10, 3), (7, 12), (13, 9), (1, 10)]:
            surface.set_at((x + dx, dy), (60, 130, 0))
    elif gid == GID_GRASS_DARK:
        surface.fill((56, 120, 0), rect)
        for dx, dy in [(2, 4), (9, 7), (5, 13), (12, 2), (14, 11)]:
            surface.set_at((x + dx, dy), (46, 100, 0))
    elif gid == GID_PATH_STONE:
        surface.fill((180, 160, 120), rect)
        pygame.draw.line(surface, (150, 130, 100), (x, 0), (x + TILE_SIZE, 0))
        pygame.draw.line(surface, (150, 130, 100), (x, 0), (x, TILE_SIZE))
        pygame.draw.line(surface, (160, 140, 110), (x + 8, 0), (x + 8, 8))
        pygame.draw.line(surface, (160, 140, 110), (x, 8), (x + 8, 8))
        pygame.draw.line(surface, (160, 140, 110), (x + 4, 8), (x + 4, TILE_SIZE))
        pygame.draw.line(surface, (160, 140, 110), (x + 8, 8), (x + TILE_SIZE, 8))
        for dx, dy in [(2, 3), (11, 5), (6, 12), (14, 14)]:
            surface.set_at((x + dx, dy), (170, 150, 110))
    elif gid == GID_PATH_DIRT:
        surface.fill((139, 119, 101), rect)
        for dx, dy in [(2, 3), (7, 8), (12, 5), (5, 13), (10, 11), (14, 2)]:
            surface.set_at((x + dx, dy), (120, 100, 80))
    elif gid == GID_WALL_BRICK:
        surface.fill((120, 80, 50), rect)
        for row in range(4):
            yy = row * 4
            pygame.draw.line(surface, (90, 60, 30), (x, yy), (x + TILE_SIZE, yy))
            offset = 8 if row % 2 == 0 else 0
            for bx in range(offset, TILE_SIZE, 8):
                pygame.draw.line(surface, (90, 60, 30), (x + bx, yy), (x + bx, yy + 4))
    elif gid == GID_WALL_BRICK_TOP:
        surface.fill((140, 100, 60), rect)
        pygame.draw.line(surface, (100, 70, 40), (x, 3), (x + TILE_SIZE, 3))
        pygame.draw.line(surface, (100, 70, 40), (x, TILE_SIZE - 1), (x + TILE_SIZE, TILE_SIZE - 1))
        for bx in range(0, TILE_SIZE, 8):
            pygame.draw.line(surface, (100, 70, 40), (x + bx, 3), (x + bx, TILE_SIZE))
    elif gid == GID_WALL_GRAY:
        surface.fill((140, 140, 140), rect)
        pygame.draw.line(surface, (110, 110, 110), (x, 0), (x + TILE_SIZE, 0))
        pygame.draw.line(surface, (110, 110, 110), (x, 8), (x + TILE_SIZE, 8))
        for bx in [4, 12]:
            pygame.draw.line(surface, (110, 110, 110), (x + bx, 0), (x + bx, 8))
        for bx in [0, 8]:
            pygame.draw.line(surface, (110, 110, 110), (x + bx, 8), (x + bx, TILE_SIZE))
    elif gid == GID_WALL_GRAY_WINDOW:
        surface.fill((140, 140, 140), rect)
        pygame.draw.rect(surface, (100, 140, 180), (x + 3, 2, 10, 6))
        pygame.draw.rect(surface, (80, 80, 80), (x + 3, 2, 10, 6), 1)
        pygame.draw.line(surface, (80, 80, 80), (x + 8, 2), (x + 8, 8))
        pygame.draw.line(surface, (80, 80, 80), (x + 3, 5), (x + 13, 5))
        pygame.draw.line(surface, (110, 110, 110), (x, 9), (x + TILE_SIZE, 9))
        for bx in [4, 12]:
            pygame.draw.line(surface, (110, 110, 110), (x + bx, 9), (x + bx, TILE_SIZE))
    elif gid == GID_BUILDING_DOOR:
        surface.fill((140, 140, 140), rect)
        pygame.draw.rect(surface, (100, 60, 30), (x + 3, 1, 10, 14))
        pygame.draw.rect(surface, (80, 45, 20), (x + 3, 1, 10, 14), 1)
        pygame.draw.circle(surface, (200, 180, 50), (x + 11, 8), 1)
        pygame.draw.line(surface, (110, 110, 110), (x, 0), (x + TILE_SIZE, 0))
    elif gid == GID_BUILDING_ROOF:
        surface.fill((100, 50, 30), rect)
        for row in range(4):
            yy = row * 4
            pygame.draw.line(surface, (80, 40, 20), (x, yy), (x + TILE_SIZE, yy))
            offset = 4 if row % 2 == 0 else 0
            for bx in range(offset, TILE_SIZE, 8):
                pygame.draw.line(surface, (80, 40, 20), (x + bx, yy), (x + bx, yy + 4))
    elif gid == GID_WATER:
        surface.fill((65, 105, 225), rect)
        pygame.draw.line(surface, (100, 149, 237), (x + 2, 4), (x + 7, 4))
        pygame.draw.line(surface, (100, 149, 237), (x + 9, 10), (x + 14, 10))
        pygame.draw.line(surface, (80, 130, 210), (x + 4, 12), (x + 8, 12))
    elif gid == GID_TREE_OSMANTHUS:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x + 6, 9, 4, 7))
        pygame.draw.circle(surface, (34, 139, 34), (x + 8, 6), 6)
        pygame.draw.circle(surface, (0, 100, 0), (x + 5, 4), 3)
        for fx, fy in [(3, 2), (10, 3), (6, 7), (12, 6), (4, 5), (11, 4)]:
            surface.set_at((x + fx, fy), (255, 200, 0))
        for fx, fy in [(5, 3), (9, 5), (7, 2)]:
            surface.set_at((x + fx, fy), (255, 230, 100))
    elif gid == GID_TREE_GREEN:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x + 6, 9, 4, 7))
        pygame.draw.circle(surface, (34, 139, 34), (x + 8, 6), 6)
        pygame.draw.circle(surface, (0, 100, 0), (x + 5, 4), 3)
        pygame.draw.circle(surface, (50, 160, 50), (x + 10, 5), 2)
    elif gid == GID_BUSH:
        surface.fill((76, 153, 0), rect)
        pygame.draw.ellipse(surface, (34, 139, 34), (x + 1, 4, 14, 10))
        pygame.draw.ellipse(surface, (0, 100, 0), (x + 2, 5, 6, 5))
        pygame.draw.ellipse(surface, (50, 160, 50), (x + 8, 6, 5, 4))
    elif gid == GID_FLOWER_BED:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x + 1, 1, 14, 14), 1)
        for fx, fy, c in [(3, 4, (255, 50, 50)), (8, 3, (255, 200, 0)),
                          (12, 6, (200, 50, 200)), (5, 9, (255, 100, 50)),
                          (10, 10, (255, 255, 100)), (3, 12, (100, 100, 255))]:
            pygame.draw.circle(surface, c, (x + fx, fy), 2)
    elif gid == GID_LAMP:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (80, 80, 80), (x + 7, 4, 2, 10))
        pygame.draw.circle(surface, (255, 255, 150), (x + 8, 3), 3)
        pygame.draw.circle(surface, (255, 255, 200), (x + 8, 3), 2)
        pygame.draw.rect(surface, (60, 60, 60), (x + 6, 13, 4, 2))
    elif gid == GID_BENCH:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (139, 90, 43), (x + 2, 5, 12, 3))
        pygame.draw.rect(surface, (120, 75, 35), (x + 2, 4, 12, 2))
        pygame.draw.rect(surface, (101, 67, 33), (x + 2, 8, 2, 5))
        pygame.draw.rect(surface, (101, 67, 33), (x + 12, 8, 2, 5))
        pygame.draw.rect(surface, (101, 67, 33), (x + 2, 3, 2, 2))
        pygame.draw.rect(surface, (101, 67, 33), (x + 12, 3, 2, 2))
    elif gid == GID_FENCE:
        surface.fill((76, 153, 0), rect)
        for fx in range(0, TILE_SIZE, 4):
            pygame.draw.rect(surface, (80, 80, 80), (x + fx + 1, 3, 2, 10))
        pygame.draw.rect(surface, (100, 100, 100), (x, 5, TILE_SIZE, 2))
        pygame.draw.rect(surface, (100, 100, 100), (x, 10, TILE_SIZE, 2))
    elif gid == GID_FOUNTAIN_BASE:
        surface.fill((76, 153, 0), rect)
        pygame.draw.ellipse(surface, (160, 160, 160), (x + 1, 2, 14, 12))
        pygame.draw.ellipse(surface, (130, 130, 130), (x + 3, 4, 10, 8))
        pygame.draw.ellipse(surface, (65, 105, 225), (x + 4, 5, 8, 6))
    elif gid == GID_FOUNTAIN_WATER:
        surface.fill((76, 153, 0), rect)
        pygame.draw.ellipse(surface, (160, 160, 160), (x + 1, 2, 14, 12))
        pygame.draw.ellipse(surface, (130, 130, 130), (x + 3, 4, 10, 8))
        pygame.draw.ellipse(surface, (65, 105, 225), (x + 4, 5, 8, 6))
        pygame.draw.rect(surface, (160, 160, 160), (x + 7, 1, 2, 4))
        for dy in range(3):
            surface.set_at((x + 6, 1 + dy), (100, 149, 237))
            surface.set_at((x + 9, 1 + dy), (100, 149, 237))
        pygame.draw.circle(surface, (200, 220, 255), (x + 8, 1), 2)
    elif gid == GID_SCULPTURE:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (140, 140, 140), (x + 4, 10, 8, 5))
        pygame.draw.rect(surface, (160, 160, 160), (x + 3, 9, 10, 2))
        pygame.draw.polygon(surface, (180, 180, 180), [
            (x + 8, 2), (x + 5, 9), (x + 11, 9)
        ])
        pygame.draw.circle(surface, (200, 200, 200), (x + 8, 2), 2)
    elif gid == GID_BUS_STOP:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (80, 80, 80), (x + 7, 3, 2, 11))
        pygame.draw.rect(surface, (0, 100, 180), (x + 3, 1, 10, 5))
        pygame.draw.rect(surface, (255, 255, 255), (x + 4, 2, 8, 3))
        pygame.draw.rect(surface, (0, 100, 180), (x + 3, 1, 10, 5), 1)
    elif gid == GID_HEDGE:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (34, 120, 0), (x, 2, TILE_SIZE, 12))
        pygame.draw.rect(surface, (50, 140, 20), (x, 3, TILE_SIZE, 10))
        for hx in range(0, TILE_SIZE, 3):
            pygame.draw.rect(surface, (40, 130, 10), (x + hx, 2, 2, 1))
    elif gid == GID_COLLISION:
        surface.fill((76, 153, 0), rect)
        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 60))
        surface.blit(overlay, (x, 0))
    elif gid == GID_FLOWER_GARDEN:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x, 0, TILE_SIZE, TILE_SIZE), 1)
        pygame.draw.rect(surface, (60, 100, 20), (x + 1, 1, 14, 14))
        for fx, fy, c in [(3, 3, (255, 80, 80)), (7, 2, (255, 200, 50)),
                          (12, 4, (200, 80, 200)), (2, 8, (255, 150, 50)),
                          (8, 7, (255, 255, 100)), (13, 9, (100, 150, 255)),
                          (5, 12, (255, 100, 100)), (10, 12, (255, 220, 80)),
                          (1, 5, (180, 80, 180)), (14, 6, (255, 180, 60))]:
            pygame.draw.circle(surface, c, (x + fx, fy), 2)
        for fx, fy in [(4, 5), (9, 4), (6, 10), (11, 8)]:
            surface.set_at((x + fx, fy), (40, 80, 10))
    elif gid == GID_TREE_CLUSTER:
        surface.fill((76, 153, 0), rect)
        pygame.draw.rect(surface, (80, 55, 25), (x + 2, 8, 3, 7))
        pygame.draw.rect(surface, (80, 55, 25), (x + 11, 9, 3, 6))
        pygame.draw.circle(surface, (34, 139, 34), (x + 3, 5), 4)
        pygame.draw.circle(surface, (0, 100, 0), (x + 2, 4), 2)
        pygame.draw.circle(surface, (34, 139, 34), (x + 12, 6), 4)
        pygame.draw.circle(surface, (50, 160, 50), (x + 13, 5), 2)
        pygame.draw.circle(surface, (40, 120, 20), (x + 8, 4), 5)
        pygame.draw.circle(surface, (30, 110, 15), (x + 7, 3), 3)
    elif gid == GID_LAWN_ROCK:
        surface.fill((76, 153, 0), rect)
        pygame.draw.ellipse(surface, (140, 140, 130), (x + 3, 6, 10, 8))
        pygame.draw.ellipse(surface, (160, 160, 150), (x + 4, 7, 8, 5))
        pygame.draw.ellipse(surface, (120, 120, 110), (x + 5, 8, 4, 3))
        surface.set_at((x + 7, 7), (180, 180, 170))


def design_map():
    random.seed(42)

    ground = [[GID_GRASS] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    terrain = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    structures = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    decorations = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    collision = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]

    interactive_objects = []
    trigger_objects = []

    _place_borders(structures, collision)
    _place_guizhong_road(ground, structures, decorations, collision, interactive_objects)
    _place_library(ground, structures, collision, interactive_objects, trigger_objects)
    _place_boya_square(ground, structures, decorations, collision, interactive_objects, trigger_objects)
    _place_gym(ground, structures, collision, interactive_objects, trigger_objects)
    _place_dining_hall(ground, structures, collision, interactive_objects, trigger_objects)
    _place_fountain_square(ground, structures, decorations, collision, interactive_objects, trigger_objects)
    _place_shuttle_station(ground, structures, decorations, collision, interactive_objects, trigger_objects)
    _place_connecting_paths(ground)
    _place_nature_decor(ground, structures, decorations, collision, interactive_objects)
    _add_grass_variation(ground)
    _add_default_spawn(trigger_objects)

    return ground, terrain, structures, decorations, collision, interactive_objects, trigger_objects


def _place_borders(structures, collision):
    for x in range(MAP_WIDTH):
        for row in [0, 1, MAP_HEIGHT - 2, MAP_HEIGHT - 1]:
            structures[row][x] = GID_TREE_GREEN
            collision[row][x] = GID_COLLISION
    for y in range(MAP_HEIGHT):
        for col in [0, 1, MAP_WIDTH - 2, MAP_WIDTH - 1]:
            structures[y][col] = GID_TREE_GREEN
            collision[y][col] = GID_COLLISION
    for x in range(2, MAP_WIDTH - 2, 3):
        structures[2][x] = GID_TREE_GREEN
        collision[2][x] = GID_COLLISION
        structures[MAP_HEIGHT - 3][x] = GID_TREE_GREEN
        collision[MAP_HEIGHT - 3][x] = GID_COLLISION
    for y in range(2, MAP_HEIGHT - 2, 3):
        structures[y][2] = GID_TREE_GREEN
        collision[y][2] = GID_COLLISION
        structures[y][MAP_WIDTH - 3] = GID_TREE_GREEN
        collision[y][MAP_WIDTH - 3] = GID_COLLISION


def _place_guizhong_road(ground, structures, decorations, collision, interactive_objects):
    road_y_start = 36
    road_y_end = 41
    road_x_start = 5
    road_x_end = 105

    for y in range(road_y_start, road_y_end + 1):
        for x in range(road_x_start, road_x_end + 1):
            ground[y][x] = GID_PATH_STONE

    for x in range(road_x_start, road_x_end + 1, 2):
        ground[38][x] = GID_PATH_DIRT
        ground[39][x] = GID_PATH_DIRT

    for x in range(road_x_start + 3, road_x_end, 5):
        structures[road_y_start - 1][x] = GID_TREE_OSMANTHUS
        collision[road_y_start - 1][x] = GID_COLLISION
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": (road_y_start - 1) * TILE_SIZE,
            "width": TILE_SIZE, "height": TILE_SIZE,
            "type": "osmanthus_tree",
            "properties": {"interactive_type": "examine", "display_name": "桂花树",
                           "desc": "一棵散发着淡淡桂花香的树"}
        })

    for x in range(road_x_start + 5, road_x_end, 5):
        structures[road_y_end + 1][x] = GID_TREE_OSMANTHUS
        collision[road_y_end + 1][x] = GID_COLLISION
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": (road_y_end + 1) * TILE_SIZE,
            "width": TILE_SIZE, "height": TILE_SIZE,
            "type": "osmanthus_tree",
            "properties": {"interactive_type": "examine", "display_name": "桂花树",
                           "desc": "一棵散发着淡淡桂花香的树"}
        })

    for x in range(road_x_start + 8, road_x_end, 10):
        decorations[road_y_start - 1][x] = GID_LAMP
        collision[road_y_start - 1][x] = GID_COLLISION
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": (road_y_start - 1) * TILE_SIZE,
            "width": TILE_SIZE, "height": TILE_SIZE,
            "type": "lamp",
            "properties": {"interactive_type": "examine", "display_name": "路灯",
                           "desc": "夜晚会亮起的校园路灯"}
        })

    for x in range(road_x_start + 10, road_x_end, 10):
        decorations[road_y_end + 1][x] = GID_LAMP
        collision[road_y_end + 1][x] = GID_COLLISION

    for x in range(road_x_start + 15, road_x_end, 15):
        decorations[road_y_start][x] = GID_BENCH
        collision[road_y_start][x] = GID_COLLISION
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": road_y_start * TILE_SIZE,
            "width": TILE_SIZE, "height": TILE_SIZE,
            "type": "bench",
            "properties": {"interactive_type": "examine", "display_name": "长椅",
                           "desc": "桂中路旁的休息长椅"}
        })


def _place_building(ground, structures, collision, bx, by, bw, bh,
                    door_side, door_offset, door_width,
                    interactive_objects, trigger_objects,
                    building_name, target_map, spawn_id):
    for y in range(by, by + bh):
        for x in range(bx, bx + bw):
            structures[y][x] = GID_WALL_GRAY
            collision[y][x] = GID_COLLISION

    for x in range(bx, bx + bw):
        structures[by][x] = GID_BUILDING_ROOF
        if by + 1 < by + bh:
            structures[by + 1][x] = GID_BUILDING_ROOF

    for y in range(by + 2, by + bh):
        for x in range(bx + 1, bx + bw - 1):
            if (y - by) % 3 == 0 and (x - bx) % 3 == 1:
                structures[y][x] = GID_WALL_GRAY_WINDOW
            else:
                structures[y][x] = GID_WALL_GRAY

    if door_side == "south":
        door_y = by + bh - 1
        for dx in range(door_offset, door_offset + door_width):
            door_x = bx + dx
            if 0 <= door_x < MAP_WIDTH:
                structures[door_y][door_x] = GID_BUILDING_DOOR
                collision[door_y][door_x] = GID_EMPTY
    elif door_side == "north":
        door_y = by
        for dx in range(door_offset, door_offset + door_width):
            door_x = bx + dx
            if 0 <= door_x < MAP_WIDTH:
                structures[door_y][door_x] = GID_BUILDING_DOOR
                collision[door_y][door_x] = GID_EMPTY
    elif door_side == "east":
        door_x = bx + bw - 1
        for dy in range(door_offset, door_offset + door_width):
            door_y = by + dy
            if 0 <= door_y < MAP_HEIGHT:
                structures[door_y][door_x] = GID_BUILDING_DOOR
                collision[door_y][door_x] = GID_EMPTY
    elif door_side == "west":
        door_x = bx
        for dy in range(door_offset, door_offset + door_width):
            door_y = by + dy
            if 0 <= door_y < MAP_HEIGHT:
                structures[door_y][door_x] = GID_BUILDING_DOOR
                collision[door_y][door_x] = GID_EMPTY

    if door_side == "south":
        obj_x = (bx + door_offset) * TILE_SIZE
        obj_y = (by + bh - 1) * TILE_SIZE
        obj_w = door_width * TILE_SIZE
        obj_h = TILE_SIZE
    elif door_side == "north":
        obj_x = (bx + door_offset) * TILE_SIZE
        obj_y = by * TILE_SIZE
        obj_w = door_width * TILE_SIZE
        obj_h = TILE_SIZE
    elif door_side == "east":
        obj_x = (bx + bw - 1) * TILE_SIZE
        obj_y = (by + door_offset) * TILE_SIZE
        obj_w = TILE_SIZE
        obj_h = door_width * TILE_SIZE
    elif door_side == "west":
        obj_x = bx * TILE_SIZE
        obj_y = (by + door_offset) * TILE_SIZE
        obj_w = TILE_SIZE
        obj_h = door_width * TILE_SIZE

    interactive_objects.append({
        "x": obj_x,
        "y": obj_y,
        "width": obj_w,
        "height": obj_h,
        "type": "building_entrance",
        "properties": {
            "interactive_type": "enter",
            "display_name": building_name + "入口",
            "target_map": target_map,
            "spawn_point": spawn_id,
        }
    })

    trigger_objects.append({
        "x": obj_x,
        "y": obj_y,
        "width": obj_w,
        "height": obj_h,
        "type": "door_trigger",
        "properties": {
            "target_map": target_map,
            "spawn_point": spawn_id,
        }
    })


def _place_library(ground, structures, collision, interactive_objects, trigger_objects):
    bx, by, bw, bh = 13, 7, 14, 10
    _place_building(ground, structures, collision, bx, by, bw, bh,
                    "south", 6, 2, interactive_objects, trigger_objects,
                    "图书馆", "library_f1", "library_entrance")

    for y in range(by + bh, 36):
        for x in range(bx + 6, bx + 8):
            ground[y][x] = GID_PATH_STONE

    for x in range(bx - 1, bx + bw + 1):
        ground[by + bh][x] = GID_PATH_STONE
        ground[by + bh + 1][x] = GID_PATH_STONE

    _add_exit_spawn(trigger_objects, "library_exit", bx + 6, by + bh + 1)


def _place_boya_square(ground, structures, decorations, collision, interactive_objects, trigger_objects):
    sx, sy, sw, sh = 76, 6, 20, 16

    for y in range(sy, sy + sh):
        for x in range(sx, sx + sw):
            ground[y][x] = GID_PATH_STONE

    for y in range(sy, sy + sh):
        ground[y][sx] = GID_PATH_DIRT
        ground[y][sx + sw - 1] = GID_PATH_DIRT
    for x in range(sx, sx + sw):
        ground[sy][x] = GID_PATH_DIRT
        ground[sy + sh - 1][x] = GID_PATH_DIRT

    sc_x, sc_y = sx + sw // 2 - 1, sy + sh // 2 - 1
    structures[sc_y][sc_x] = GID_SCULPTURE
    structures[sc_y][sc_x + 1] = GID_SCULPTURE
    collision[sc_y][sc_x] = GID_COLLISION
    collision[sc_y][sc_x + 1] = GID_COLLISION

    interactive_objects.append({
        "x": sc_x * TILE_SIZE, "y": sc_y * TILE_SIZE,
        "width": TILE_SIZE * 2, "height": TILE_SIZE * 2,
        "type": "sculpture",
        "properties": {
            "interactive_type": "examine",
            "display_name": "博雅雕塑",
            "desc": "广场中央的雕塑，底座刻着古老的铭文……"
        }
    })

    for dx in [3, 8, 14]:
        decorations[sy + 2][sx + dx] = GID_FLOWER_BED
        collision[sy + 2][sx + dx] = GID_COLLISION
        decorations[sy + sh - 3][sx + dx] = GID_FLOWER_BED
        collision[sy + sh - 3][sx + dx] = GID_COLLISION

    for y in range(sy + sh, 36):
        for x in range(sx + sw // 2 - 1, sx + sw // 2 + 1):
            ground[y][x] = GID_PATH_STONE


def _place_gym(ground, structures, collision, interactive_objects, trigger_objects):
    bx, by, bw, bh = 11, 49, 16, 12
    _place_building(ground, structures, collision, bx, by, bw, bh,
                    "south", 7, 2, interactive_objects, trigger_objects,
                    "佑铭体育馆", "gym", "gym_entrance")

    for y in range(42, by):
        for x in range(bx + 7, bx + 9):
            ground[y][x] = GID_PATH_STONE

    for x in range(bx - 1, bx + bw + 1):
        ground[by - 1][x] = GID_PATH_STONE
        ground[by - 2][x] = GID_PATH_STONE

    _add_exit_spawn(trigger_objects, "gym_exit", bx + 7, by + bh + 1)


def _place_dining_hall(ground, structures, collision, interactive_objects, trigger_objects):
    bx, by, bw, bh = 89, 49, 12, 10
    _place_building(ground, structures, collision, bx, by, bw, bh,
                    "south", 5, 2, interactive_objects, trigger_objects,
                    "学子食堂", "dining_hall_f1", "dining_entrance")

    for y in range(42, by):
        for x in range(bx + 5, bx + 7):
            ground[y][x] = GID_PATH_STONE

    for x in range(bx - 1, bx + bw + 1):
        ground[by - 1][x] = GID_PATH_STONE
        ground[by - 2][x] = GID_PATH_STONE

    _add_exit_spawn(trigger_objects, "dining_exit", bx + 5, by + bh + 1)


def _place_fountain_square(ground, structures, decorations, collision, interactive_objects, trigger_objects):
    sx, sy, sw, sh = 51, 48, 18, 14

    for y in range(sy, sy + sh):
        for x in range(sx, sx + sw):
            ground[y][x] = GID_PATH_STONE

    for y in range(sy, sy + sh):
        ground[y][sx] = GID_PATH_DIRT
        ground[y][sx + sw - 1] = GID_PATH_DIRT
    for x in range(sx, sx + sw):
        ground[sy][x] = GID_PATH_DIRT
        ground[sy + sh - 1][x] = GID_PATH_DIRT

    fx, fy = sx + sw // 2 - 3, sy + sh // 2 - 3
    for dy in range(6):
        for dx in range(6):
            structures[fy + dy][fx + dx] = GID_FOUNTAIN_BASE
            collision[fy + dy][fx + dx] = GID_COLLISION
    structures[fy + 2][fx + 2] = GID_FOUNTAIN_WATER
    structures[fy + 2][fx + 3] = GID_FOUNTAIN_WATER
    structures[fy + 3][fx + 2] = GID_FOUNTAIN_WATER
    structures[fy + 3][fx + 3] = GID_FOUNTAIN_WATER

    interactive_objects.append({
        "x": fx * TILE_SIZE, "y": fy * TILE_SIZE,
        "width": 6 * TILE_SIZE, "height": 6 * TILE_SIZE,
        "type": "fountain",
        "properties": {
            "interactive_type": "examine",
            "display_name": "喷泉",
            "desc": "广场中央的古老喷泉，基座上有7个凹槽……"
        }
    })

    for dx in [2, 9, 14]:
        decorations[sy + 2][sx + dx] = GID_FLOWER_BED
        collision[sy + 2][sx + dx] = GID_COLLISION
        decorations[sy + sh - 3][sx + dx] = GID_FLOWER_BED
        collision[sy + sh - 3][sx + dx] = GID_COLLISION

    for y in range(42, sy):
        for x in range(sx + sw // 2 - 1, sx + sw // 2 + 1):
            ground[y][x] = GID_PATH_STONE


def _place_shuttle_station(ground, structures, decorations, collision, interactive_objects, trigger_objects):
    sx, sy, sw, sh = 54, 66, 12, 7

    for y in range(sy, sy + sh):
        for x in range(sx, sx + sw):
            ground[y][x] = GID_PATH_STONE

    for y in range(sy, sy + sh):
        ground[y][sx] = GID_PATH_DIRT
        ground[y][sx + sw - 1] = GID_PATH_DIRT
    for x in range(sx, sx + sw):
        ground[sy][x] = GID_PATH_DIRT
        ground[sy + sh - 1][x] = GID_PATH_DIRT

    bus_x = sx + sw // 2
    bus_y = sy + 1
    structures[bus_y][bus_x] = GID_BUS_STOP
    collision[bus_y][bus_x] = GID_COLLISION

    interactive_objects.append({
        "x": bus_x * TILE_SIZE, "y": bus_y * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "bus_stop",
        "properties": {
            "interactive_type": "enter",
            "display_name": "校区接驳站",
            "desc": "前往南湖校区的校车",
            "target_map": "nanhu_campus",
            "transition_type": "campus_bus",
        }
    })

    trigger_objects.append({
        "x": (sx + 2) * TILE_SIZE,
        "y": (sy + 2) * TILE_SIZE,
        "width": (sw - 4) * TILE_SIZE,
        "height": (sh - 4) * TILE_SIZE,
        "type": "shuttle_trigger",
        "properties": {
            "target_map": "nanhu_campus",
            "spawn_point": "nanhu_entrance",
            "transition_type": "campus_bus",
        }
    })

    for y in range(sy - 1, sy + sh + 1):
        structures[y][sx - 1] = GID_HEDGE
        collision[y][sx - 1] = GID_COLLISION
        structures[y][sx + sw] = GID_HEDGE
        collision[y][sx + sw] = GID_COLLISION

    for y in range(62, sy):
        for x in range(sx + sw // 2 - 1, sx + sw // 2 + 1):
            ground[y][x] = GID_PATH_STONE

    for dx in [3, 8]:
        decorations[sy + sh - 2][sx + dx] = GID_BENCH
        collision[sy + sh - 2][sx + dx] = GID_COLLISION


def _place_connecting_paths(ground):
    for x in range(5, 105):
        if ground[35][x] == GID_GRASS:
            ground[35][x] = GID_PATH_DIRT
        if ground[42][x] == GID_GRASS:
            ground[42][x] = GID_PATH_DIRT

    for y in range(3, 35):
        if ground[y][18] == GID_GRASS:
            ground[y][18] = GID_PATH_DIRT
        if ground[y][19] == GID_GRASS:
            ground[y][19] = GID_PATH_DIRT

    for y in range(3, 35):
        if ground[y][85] == GID_GRASS:
            ground[y][85] = GID_PATH_DIRT
        if ground[y][86] == GID_GRASS:
            ground[y][86] = GID_PATH_DIRT

    for y in range(43, 49):
        if ground[y][18] == GID_GRASS:
            ground[y][18] = GID_PATH_DIRT
        if ground[y][19] == GID_GRASS:
            ground[y][19] = GID_PATH_DIRT

    for y in range(43, 49):
        if ground[y][94] == GID_GRASS:
            ground[y][94] = GID_PATH_DIRT
        if ground[y][95] == GID_GRASS:
            ground[y][95] = GID_PATH_DIRT

    for y in range(43, 48):
        if ground[y][59] == GID_GRASS:
            ground[y][59] = GID_PATH_DIRT
        if ground[y][60] == GID_GRASS:
            ground[y][60] = GID_PATH_DIRT

    for x in range(25, 51):
        if ground[49][x] == GID_GRASS:
            ground[49][x] = GID_PATH_DIRT
        if ground[50][x] == GID_GRASS:
            ground[50][x] = GID_PATH_DIRT

    for x in range(69, 89):
        if ground[49][x] == GID_GRASS:
            ground[49][x] = GID_PATH_DIRT
        if ground[50][x] == GID_GRASS:
            ground[50][x] = GID_PATH_DIRT


def _place_nature_decor(ground, structures, decorations, collision, interactive_objects):
    random.seed(123)

    tree_positions = []
    for _ in range(70):
        tx = random.randint(4, MAP_WIDTH - 5)
        ty = random.randint(4, MAP_HEIGHT - 5)
        if ground[ty][tx] != GID_GRASS:
            continue
        if structures[ty][tx] != GID_EMPTY:
            continue
        if decorations[ty][tx] != GID_EMPTY:
            continue
        if collision[ty][tx] != GID_EMPTY:
            continue
        too_close = False
        for px, py in tree_positions:
            if abs(tx - px) < 3 and abs(ty - py) < 3:
                too_close = True
                break
        if too_close:
            continue
        tree_positions.append((tx, ty))

    for i, (tx, ty) in enumerate(tree_positions):
        if i % 3 == 0:
            structures[ty][tx] = GID_TREE_OSMANTHUS
            interactive_objects.append({
                "x": tx * TILE_SIZE, "y": ty * TILE_SIZE,
                "width": TILE_SIZE, "height": TILE_SIZE,
                "type": "osmanthus_tree",
                "properties": {"interactive_type": "examine", "display_name": "桂花树",
                               "desc": "校园里随处可见的桂花树"}
            })
        else:
            structures[ty][tx] = GID_TREE_GREEN
        collision[ty][tx] = GID_COLLISION

    bush_positions = []
    for _ in range(50):
        bx = random.randint(4, MAP_WIDTH - 5)
        by = random.randint(4, MAP_HEIGHT - 5)
        if ground[by][bx] != GID_GRASS:
            continue
        if structures[by][bx] != GID_EMPTY:
            continue
        if decorations[by][bx] != GID_EMPTY:
            continue
        if collision[by][bx] != GID_EMPTY:
            continue
        bush_positions.append((bx, by))

    for bx, by in bush_positions:
        decorations[by][bx] = GID_BUSH
        collision[by][bx] = GID_COLLISION

    flower_garden_positions = []
    for _ in range(10):
        gx = random.randint(5, MAP_WIDTH - 8)
        gy = random.randint(5, MAP_HEIGHT - 8)
        can_place = True
        for dy in range(3):
            for dx in range(3):
                ny, nx = gy + dy, gx + dx
                if not (0 <= ny < MAP_HEIGHT and 0 <= nx < MAP_WIDTH):
                    can_place = False
                    break
                if ground[ny][nx] != GID_GRASS or structures[ny][nx] != GID_EMPTY or decorations[ny][nx] != GID_EMPTY or collision[ny][nx] != GID_EMPTY:
                    can_place = False
                    break
            if not can_place:
                break
        if not can_place:
            continue
        for px, py in flower_garden_positions:
            if abs(gx - px) < 5 and abs(gy - py) < 5:
                can_place = False
                break
        if not can_place:
            continue
        flower_garden_positions.append((gx, gy))
        for dy in range(3):
            for dx in range(3):
                decorations[gy + dy][gx + dx] = GID_FLOWER_GARDEN
                collision[gy + dy][gx + dx] = GID_COLLISION

    tree_cluster_positions = []
    for _ in range(8):
        cx = random.randint(5, MAP_WIDTH - 7)
        cy = random.randint(5, MAP_HEIGHT - 7)
        can_place = True
        for dy in range(2):
            for dx in range(2):
                ny, nx = cy + dy, cx + dx
                if not (0 <= ny < MAP_HEIGHT and 0 <= nx < MAP_WIDTH):
                    can_place = False
                    break
                if ground[ny][nx] != GID_GRASS or structures[ny][nx] != GID_EMPTY or decorations[ny][nx] != GID_EMPTY or collision[ny][nx] != GID_EMPTY:
                    can_place = False
                    break
            if not can_place:
                break
        if not can_place:
            continue
        for px, py in tree_cluster_positions:
            if abs(cx - px) < 4 and abs(cy - py) < 4:
                can_place = False
                break
        if not can_place:
            continue
        tree_cluster_positions.append((cx, cy))
        for dy in range(2):
            for dx in range(2):
                structures[cy + dy][cx + dx] = GID_TREE_CLUSTER
                collision[cy + dy][cx + dx] = GID_COLLISION

    for _ in range(18):
        rx = random.randint(4, MAP_WIDTH - 5)
        ry = random.randint(4, MAP_HEIGHT - 5)
        if ground[ry][rx] == GID_GRASS and structures[ry][rx] == GID_EMPTY and decorations[ry][rx] == GID_EMPTY and collision[ry][rx] == GID_EMPTY:
            decorations[ry][rx] = GID_LAWN_ROCK

    building_doors = []
    for obj in interactive_objects:
        if obj.get("type") == "building_entrance":
            building_doors.append((obj["x"] // TILE_SIZE, obj["y"] // TILE_SIZE))
    for door_x, door_y in building_doors:
        for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            path_x = door_x + direction[0]
            path_y = door_y + direction[1]
            while 0 <= path_x < MAP_WIDTH and 0 <= path_y < MAP_HEIGHT:
                if ground[path_y][path_x] == GID_GRASS:
                    ground[path_y][path_x] = GID_PATH_DIRT
                    path_x += direction[0]
                    path_y += direction[1]
                else:
                    break

    pond_x, pond_y, pond_w, pond_h = 35, 20, 6, 4
    for y in range(pond_y, pond_y + pond_h):
        for x in range(pond_x, pond_x + pond_w):
            if 0 <= y < MAP_HEIGHT and 0 <= x < MAP_WIDTH:
                ground[y][x] = GID_WATER
                collision[y][x] = GID_COLLISION

    pond2_x, pond2_y, pond2_w, pond2_h = 40, 55, 5, 3
    for y in range(pond2_y, pond2_y + pond2_h):
        for x in range(pond2_x, pond2_x + pond2_w):
            if 0 <= y < MAP_HEIGHT and 0 <= x < MAP_WIDTH:
                ground[y][x] = GID_WATER
                collision[y][x] = GID_COLLISION

    for fx in range(3, MAP_WIDTH - 3, 8):
        if structures[3][fx] == GID_EMPTY and decorations[3][fx] == GID_EMPTY:
            structures[3][fx] = GID_FENCE
            collision[3][fx] = GID_COLLISION
        if structures[MAP_HEIGHT - 4][fx] == GID_EMPTY and decorations[MAP_HEIGHT - 4][fx] == GID_EMPTY:
            structures[MAP_HEIGHT - 4][fx] = GID_FENCE
            collision[MAP_HEIGHT - 4][fx] = GID_COLLISION

    bench_spots = [
        (30, 25), (70, 25), (45, 30), (95, 30),
        (30, 45), (75, 45), (100, 55), (35, 65),
    ]
    for bxx, byy in bench_spots:
        if 0 <= byy < MAP_HEIGHT and 0 <= bxx < MAP_WIDTH:
            if ground[byy][bxx] == GID_GRASS and structures[byy][bxx] == GID_EMPTY:
                decorations[byy][bxx] = GID_BENCH
                collision[byy][bxx] = GID_COLLISION
                interactive_objects.append({
                    "x": bxx * TILE_SIZE, "y": byy * TILE_SIZE,
                    "width": TILE_SIZE, "height": TILE_SIZE,
                    "type": "bench",
                    "properties": {"interactive_type": "examine", "display_name": "长椅",
                                   "desc": "校园里的休息长椅"}
                })

    flower_spots = [
        (15, 20), (25, 22), (65, 15), (90, 20),
        (20, 55), (80, 60), (45, 70), (100, 65),
    ]
    for fxx, fyy in flower_spots:
        if 0 <= fyy < MAP_HEIGHT and 0 <= fxx < MAP_WIDTH:
            if ground[fyy][fxx] == GID_GRASS and structures[fyy][fxx] == GID_EMPTY and decorations[fyy][fxx] == GID_EMPTY:
                decorations[fyy][fxx] = GID_FLOWER_BED
                collision[fyy][fxx] = GID_COLLISION


def _add_grass_variation(ground):
    random.seed(777)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if ground[y][x] != GID_GRASS:
                continue
            if random.random() < 0.06:
                ground[y][x] = GID_GRASS_DARK
            elif random.random() < 0.02:
                cluster_size = random.randint(1, 2)
                for dy in range(-cluster_size, cluster_size + 1):
                    for dx in range(-cluster_size, cluster_size + 1):
                        ny, nx = y + dy, x + dx
                        if (0 <= ny < MAP_HEIGHT and 0 <= nx < MAP_WIDTH
                                and ground[ny][nx] == GID_GRASS
                                and dx * dx + dy * dy <= cluster_size * cluster_size
                                and random.random() < 0.5):
                            ground[ny][nx] = GID_GRASS_DARK


def _add_default_spawn(trigger_objects):
    trigger_objects.append({
        "x": 59 * TILE_SIZE,
        "y": 38 * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": 3 * TILE_SIZE,
        "type": "spawn",
        "properties": {
            "spawn_id": "default",
        }
    })


def _add_exit_spawn(trigger_objects, spawn_id, tile_x, tile_y):
    trigger_objects.append({
        "x": tile_x * TILE_SIZE,
        "y": tile_y * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": 2 * TILE_SIZE,
        "type": "spawn",
        "properties": {
            "spawn_id": spawn_id,
        }
    })


def layer_to_csv(layer_data):
    values = []
    for row in layer_data:
        values.extend(str(v) for v in row)
    return "\n" + ",".join(values) + "\n"


def create_tmx(ground, terrain, structures, decorations, collision,
               interactive_objects, trigger_objects,
               tileset_path, output_path):
    root = ET.Element("map")
    root.set("version", "1.5")
    root.set("orientation", "orthogonal")
    root.set("renderorder", "right-down")
    root.set("width", str(MAP_WIDTH))
    root.set("height", str(MAP_HEIGHT))
    root.set("tilewidth", str(TILE_SIZE))
    root.set("tileheight", str(TILE_SIZE))
    root.set("infinite", "0")
    root.set("nextobjectid", "1")

    tileset = ET.SubElement(root, "tileset")
    tileset.set("firstgid", "1")
    tileset.set("name", "main_campus_tileset")
    tileset.set("tilewidth", str(TILE_SIZE))
    tileset.set("tileheight", str(TILE_SIZE))
    tileset.set("tilecount", str(TILE_COUNT))
    tileset.set("columns", str(TILE_COUNT))

    image = ET.SubElement(tileset, "image")
    image.set("source", tileset_path)
    image.set("width", str(TILE_COUNT * TILE_SIZE))
    image.set("height", str(TILE_SIZE))

    for local_id in sorted(gid - 1 for gid in SOLID_GIDS):
        tile_elem = ET.SubElement(tileset, "tile")
        tile_elem.set("id", str(local_id))
        props = ET.SubElement(tile_elem, "properties")
        prop = ET.SubElement(props, "property")
        prop.set("name", "solid")
        prop.set("type", "bool")
        prop.set("value", "true")

    layer_id = 1
    next_object_id = 1

    ground_layer = ET.SubElement(root, "layer")
    ground_layer.set("id", str(layer_id))
    ground_layer.set("name", "ground")
    ground_layer.set("width", str(MAP_WIDTH))
    ground_layer.set("height", str(MAP_HEIGHT))
    ground_data = ET.SubElement(ground_layer, "data")
    ground_data.set("encoding", "csv")
    ground_data.text = layer_to_csv(ground)
    layer_id += 1

    terrain_layer = ET.SubElement(root, "layer")
    terrain_layer.set("id", str(layer_id))
    terrain_layer.set("name", "terrain")
    terrain_layer.set("width", str(MAP_WIDTH))
    terrain_layer.set("height", str(MAP_HEIGHT))
    terrain_data = ET.SubElement(terrain_layer, "data")
    terrain_data.set("encoding", "csv")
    terrain_data.text = layer_to_csv(terrain)
    layer_id += 1

    struct_layer = ET.SubElement(root, "layer")
    struct_layer.set("id", str(layer_id))
    struct_layer.set("name", "structures")
    struct_layer.set("width", str(MAP_WIDTH))
    struct_layer.set("height", str(MAP_HEIGHT))
    struct_data = ET.SubElement(struct_layer, "data")
    struct_data.set("encoding", "csv")
    struct_data.text = layer_to_csv(structures)
    layer_id += 1

    objects_group = ET.SubElement(root, "objectgroup")
    objects_group.set("id", str(layer_id))
    objects_group.set("name", "objects")
    for obj in interactive_objects:
        obj_elem = ET.SubElement(objects_group, "object")
        obj_elem.set("id", str(next_object_id))
        next_object_id += 1
        obj_elem.set("x", str(obj["x"]))
        obj_elem.set("y", str(obj["y"]))
        obj_elem.set("width", str(obj["width"]))
        obj_elem.set("height", str(obj["height"]))
        if obj.get("type"):
            obj_elem.set("type", obj["type"])
        if obj.get("properties"):
            props_elem = ET.SubElement(obj_elem, "properties")
            for key, value in obj["properties"].items():
                prop = ET.SubElement(props_elem, "property")
                prop.set("name", key)
                if isinstance(value, bool):
                    prop.set("type", "bool")
                    prop.set("value", str(value).lower())
                else:
                    prop.set("value", str(value))
    layer_id += 1

    coll_layer = ET.SubElement(root, "layer")
    coll_layer.set("id", str(layer_id))
    coll_layer.set("name", "collision")
    coll_layer.set("width", str(MAP_WIDTH))
    coll_layer.set("height", str(MAP_HEIGHT))
    coll_layer.set("visible", "0")
    coll_data = ET.SubElement(coll_layer, "data")
    coll_data.set("encoding", "csv")
    coll_data.text = layer_to_csv(collision)
    layer_id += 1

    triggers_group = ET.SubElement(root, "objectgroup")
    triggers_group.set("id", str(layer_id))
    triggers_group.set("name", "triggers")
    for obj in trigger_objects:
        obj_elem = ET.SubElement(triggers_group, "object")
        obj_elem.set("id", str(next_object_id))
        next_object_id += 1
        obj_elem.set("x", str(obj["x"]))
        obj_elem.set("y", str(obj["y"]))
        obj_elem.set("width", str(obj["width"]))
        obj_elem.set("height", str(obj["height"]))
        if obj.get("type"):
            obj_elem.set("type", obj["type"])
        if obj.get("properties"):
            props_elem = ET.SubElement(obj_elem, "properties")
            for key, value in obj["properties"].items():
                prop = ET.SubElement(props_elem, "property")
                prop.set("name", key)
                if isinstance(value, bool):
                    prop.set("type", "bool")
                    prop.set("value", str(value).lower())
                else:
                    prop.set("value", str(value))
    layer_id += 1

    deco_layer = ET.SubElement(root, "layer")
    deco_layer.set("id", str(layer_id))
    deco_layer.set("name", "decorations")
    deco_layer.set("width", str(MAP_WIDTH))
    deco_layer.set("height", str(MAP_HEIGHT))
    deco_data = ET.SubElement(deco_layer, "data")
    deco_data.set("encoding", "csv")
    deco_data.text = layer_to_csv(decorations)
    layer_id += 1

    root.set("nextobjectid", str(next_object_id))
    root.set("nextlayerid", str(layer_id))

    tree = ET.ElementTree(root)
    ET.indent(tree, space=" ")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)
    print(f"TMX map saved to {output_path}")
    print(f"  Map size: {MAP_WIDTH}x{MAP_HEIGHT} tiles")
    print(f"  Interactive objects: {len(interactive_objects)}")
    print(f"  Trigger zones: {len(trigger_objects)}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    tileset_output = os.path.join(base_dir, "assets", "tilesets", "main_campus_tileset.png")
    tmx_output = os.path.join(base_dir, "world", "map_data", "main_campus.tmx")

    tileset_rel_path = os.path.relpath(tileset_output, os.path.dirname(tmx_output))
    tileset_rel_path = tileset_rel_path.replace("\\", "/")

    create_tileset(tileset_output)
    ground, terrain, structures, decorations, collision, interactive_objects, trigger_objects = design_map()
    create_tmx(ground, terrain, structures, decorations, collision,
               interactive_objects, trigger_objects,
               tileset_rel_path, tmx_output)
