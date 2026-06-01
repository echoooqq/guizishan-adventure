import os
import sys
import random
import pygame
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TILE_SIZE

MAP_WIDTH = 40
MAP_HEIGHT = 30

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

SOLID_GIDS = {
    GID_WALL_BRICK, GID_WALL_BRICK_TOP, GID_WALL_GRAY,
    GID_WALL_GRAY_WINDOW, GID_BUILDING_ROOF, GID_WATER,
    GID_TREE_OSMANTHUS, GID_TREE_GREEN, GID_BUSH,
    GID_FLOWER_BED, GID_LAMP, GID_BENCH, GID_FENCE,
    GID_FOUNTAIN_BASE, GID_FOUNTAIN_WATER, GID_SCULPTURE,
    GID_BUS_STOP, GID_HEDGE, GID_COLLISION,
    GID_FLOWER_GARDEN, GID_TREE_CLUSTER,
}


def _fill_layer(layer, w, h, gid):
    return [[gid] * w for _ in range(h)]


def _fill_rect(layer, x, y, w, h, gid):
    for row in range(y, y + h):
        for col in range(x, x + w):
            if 0 <= row < len(layer) and 0 <= col < len(layer[0]):
                layer[row][col] = gid


def _fill_border(layer, w, h, gid):
    for x in range(w):
        layer[0][x] = gid
        layer[h - 1][x] = gid
    for y in range(h):
        layer[y][0] = gid
        layer[y][w - 1] = gid


def _add_exit_trigger(triggers, x, y, w, h, target_map, spawn_point,
                      transition_type="indoor_exit"):
    triggers.append({
        "x": x * TILE_SIZE, "y": y * TILE_SIZE,
        "width": w * TILE_SIZE, "height": h * TILE_SIZE,
        "type": "door_exit",
        "properties": {
            "target_map": target_map,
            "spawn_point": spawn_point,
            "auto_trigger": True,
            "transition_type": transition_type,
        }
    })


def _add_spawn(trigger_objects, spawn_id, x, y):
    trigger_objects.append({
        "x": x * TILE_SIZE, "y": y * TILE_SIZE,
        "width": 2 * TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "spawn",
        "properties": {"spawn_id": spawn_id}
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


def design_nanhu_campus():
    random.seed(88)

    ground = [[GID_GRASS] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    terrain = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    structures = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    decorations = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    collision = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]

    interactive_objects = []
    trigger_objects = []

    _place_nanhu_borders(structures, collision)
    _place_nanhu_road(ground, structures, decorations, collision, interactive_objects)
    _place_nanhulou(ground, structures, collision, interactive_objects, trigger_objects)
    _place_nanhu_shuttle(ground, structures, decorations, collision, interactive_objects, trigger_objects)
    _place_nanhu_lake(ground, structures, decorations, collision, interactive_objects)
    _place_nanhu_garden(ground, structures, decorations, collision, interactive_objects)
    _place_nanhu_nature(ground, structures, decorations, collision, interactive_objects)
    _add_grass_variation(ground)
    _add_nanhu_spawn(trigger_objects)

    return ground, terrain, structures, decorations, collision, interactive_objects, trigger_objects


def _place_nanhu_borders(structures, collision):
    for x in range(MAP_WIDTH):
        for row in [0, 1, MAP_HEIGHT - 2, MAP_HEIGHT - 1]:
            structures[row][x] = GID_TREE_GREEN
            collision[row][x] = GID_COLLISION
    for y in range(MAP_HEIGHT):
        for col in [0, 1, MAP_WIDTH - 2, MAP_WIDTH - 1]:
            structures[y][col] = GID_TREE_GREEN
            collision[y][col] = GID_COLLISION


def _place_nanhu_road(ground, structures, decorations, collision, interactive_objects):
    road_y_start = 13
    road_y_end = 16
    road_x_start = 3
    road_x_end = 36

    for y in range(road_y_start, road_y_end + 1):
        for x in range(road_x_start, road_x_end + 1):
            ground[y][x] = GID_PATH_STONE

    for x in range(road_x_start, road_x_end + 1, 2):
        ground[14][x] = GID_PATH_DIRT
        ground[15][x] = GID_PATH_DIRT

    for x in range(road_x_start + 3, road_x_end, 6):
        structures[road_y_start - 1][x] = GID_TREE_OSMANTHUS
        collision[road_y_start - 1][x] = GID_COLLISION
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": (road_y_start - 1) * TILE_SIZE,
            "width": TILE_SIZE, "height": TILE_SIZE,
            "type": "osmanthus_tree",
            "properties": {"interactive_type": "examine", "display_name": "桂花树",
                           "desc": "南湖校区的桂花树，同样散发着幽幽花香"}
        })

    for x in range(road_x_start + 5, road_x_end, 6):
        structures[road_y_end + 1][x] = GID_TREE_OSMANTHUS
        collision[road_y_end + 1][x] = GID_COLLISION

    for x in range(road_x_start + 8, road_x_end, 10):
        decorations[road_y_start - 1][x] = GID_LAMP
        collision[road_y_start - 1][x] = GID_COLLISION
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": (road_y_start - 1) * TILE_SIZE,
            "width": TILE_SIZE, "height": TILE_SIZE,
            "type": "lamp",
            "properties": {"interactive_type": "examine", "display_name": "路灯",
                           "desc": "南湖校区的路灯"}
        })

    for x in range(road_x_start + 12, road_x_end, 12):
        decorations[road_y_start][x] = GID_BENCH
        collision[road_y_start][x] = GID_COLLISION
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": road_y_start * TILE_SIZE,
            "width": TILE_SIZE, "height": TILE_SIZE,
            "type": "bench",
            "properties": {"interactive_type": "examine", "display_name": "长椅",
                           "desc": "南湖校区的休息长椅"}
        })

    for y in range(3, road_y_start):
        if ground[y][20] == GID_GRASS:
            ground[y][20] = GID_PATH_DIRT
        if ground[y][21] == GID_GRASS:
            ground[y][21] = GID_PATH_DIRT

    for y in range(road_y_end + 1, MAP_HEIGHT - 3):
        if ground[y][20] == GID_GRASS:
            ground[y][20] = GID_PATH_DIRT
        if ground[y][21] == GID_GRASS:
            ground[y][21] = GID_PATH_DIRT


def _place_nanhulou(ground, structures, collision, interactive_objects, trigger_objects):
    bx, by, bw, bh = 14, 4, 14, 8

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

    door_x = bx + 6
    door_y = by + bh - 1
    structures[door_y][door_x] = GID_BUILDING_DOOR
    collision[door_y][door_x] = GID_EMPTY
    structures[door_y][door_x + 1] = GID_BUILDING_DOOR
    collision[door_y][door_x + 1] = GID_EMPTY

    interactive_objects.append({
        "x": door_x * TILE_SIZE,
        "y": door_y * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": TILE_SIZE,
        "type": "building_entrance",
        "properties": {
            "interactive_type": "enter",
            "display_name": "南湖综合楼入口",
            "target_map": "nanhulou_f1",
            "spawn_point": "nanhulou_entrance",
            "transition_type": "indoor_enter",
        }
    })

    trigger_objects.append({
        "x": door_x * TILE_SIZE,
        "y": door_y * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": TILE_SIZE,
        "type": "door_trigger",
        "properties": {
            "target_map": "nanhulou_f1",
            "spawn_point": "nanhulou_entrance",
        }
    })

    for x in range(bx - 1, bx + bw + 1):
        ground[by + bh][x] = GID_PATH_STONE
        ground[by + bh + 1][x] = GID_PATH_STONE

    for y in range(by + bh + 1, 13):
        for x in range(door_x, door_x + 2):
            if ground[y][x] == GID_GRASS:
                ground[y][x] = GID_PATH_STONE

    _add_exit_spawn(trigger_objects, "nanhulou_exit", door_x, by + bh + 1)


def _place_nanhu_shuttle(ground, structures, decorations, collision, interactive_objects, trigger_objects):
    sx, sy, sw, sh = 14, 23, 12, 5

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
            "prompt_text": "乘校车",
            "desc": "返回本部校区的校车",
            "target_map": "main_campus",
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
            "target_map": "main_campus",
            "spawn_point": "shuttle_return",
            "transition_type": "campus_bus",
        }
    })

    for y in range(sy - 1, sy + sh + 1):
        structures[y][sx - 1] = GID_HEDGE
        collision[y][sx - 1] = GID_COLLISION
        structures[y][sx + sw] = GID_HEDGE
        collision[y][sx + sw] = GID_COLLISION

    for y in range(17, sy):
        for x in range(sx + sw // 2 - 1, sx + sw // 2 + 1):
            if ground[y][x] == GID_GRASS:
                ground[y][x] = GID_PATH_STONE

    for dx in [3, 8]:
        decorations[sy + sh - 2][sx + dx] = GID_BENCH
        collision[sy + sh - 2][sx + dx] = GID_COLLISION


def _place_nanhu_lake(ground, structures, decorations, collision, interactive_objects):
    lake_x, lake_y, lake_w, lake_h = 26, 4, 10, 7

    for y in range(lake_y, lake_y + lake_h):
        for x in range(lake_x, lake_x + lake_w):
            if 0 <= y < MAP_HEIGHT and 0 <= x < MAP_WIDTH:
                ground[y][x] = GID_WATER
                collision[y][x] = GID_COLLISION

    for y in range(lake_y - 1, lake_y + lake_h + 1):
        for x in [lake_x - 1, lake_x + lake_w]:
            if 0 <= y < MAP_HEIGHT and 0 <= x < MAP_WIDTH:
                if structures[y][x] == GID_EMPTY and decorations[y][x] == GID_EMPTY:
                    decorations[y][x] = GID_BUSH
                    collision[y][x] = GID_COLLISION

    for x in range(lake_x - 1, lake_x + lake_w + 1):
        for y in [lake_y - 1, lake_y + lake_h]:
            if 0 <= y < MAP_HEIGHT and 0 <= x < MAP_WIDTH:
                if structures[y][x] == GID_EMPTY and decorations[y][x] == GID_EMPTY:
                    decorations[y][x] = GID_BUSH
                    collision[y][x] = GID_COLLISION

    interactive_objects.append({
        "x": (lake_x + lake_w // 2 - 1) * TILE_SIZE,
        "y": (lake_y + lake_h // 2 - 1) * TILE_SIZE,
        "width": 2 * TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "lake_view",
        "properties": {
            "interactive_type": "examine",
            "display_name": "南湖",
            "desc": "波光粼粼的南湖，湖面上映着天空的倒影……"
        }
    })


def _place_nanhu_garden(ground, structures, decorations, collision, interactive_objects):
    gx, gy, gw, gh = 4, 18, 8, 8

    for y in range(gy, gy + gh):
        for x in range(gx, gx + gw):
            if ground[y][x] == GID_GRASS:
                ground[y][x] = GID_PATH_DIRT

    for y in range(gy, gy + gh):
        ground[y][gx] = GID_FLOWER_GARDEN
        collision[y][gx] = GID_COLLISION
        ground[y][gx + gw - 1] = GID_FLOWER_GARDEN
        collision[y][gx + gw - 1] = GID_COLLISION
    for x in range(gx, gx + gw):
        ground[gy][x] = GID_FLOWER_GARDEN
        collision[gy][x] = GID_COLLISION
        ground[gy + gh - 1][x] = GID_FLOWER_GARDEN
        collision[gy + gh - 1][x] = GID_COLLISION

    for dx in [2, 5]:
        decorations[gy + 2][gx + dx] = GID_FLOWER_BED
        collision[gy + 2][gx + dx] = GID_COLLISION
        decorations[gy + gh - 3][gx + dx] = GID_FLOWER_BED
        collision[gy + gh - 3][gx + dx] = GID_COLLISION

    structures[gy + gh // 2][gx + gw // 2] = GID_SCULPTURE
    collision[gy + gh // 2][gx + gw // 2] = GID_COLLISION
    interactive_objects.append({
        "x": (gx + gw // 2) * TILE_SIZE,
        "y": (gy + gh // 2) * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "sculpture",
        "properties": {
            "interactive_type": "examine",
            "display_name": "南湖雕塑",
            "desc": "南湖校区的小型雕塑，底座上刻着'求实创新'……"
        }
    })

    decorations[gy + 1][gx + gw // 2] = GID_LAMP
    collision[gy + 1][gx + gw // 2] = GID_COLLISION


def _place_nanhu_nature(ground, structures, decorations, collision, interactive_objects):
    random.seed(256)

    tree_positions = []
    for _ in range(25):
        tx = random.randint(3, MAP_WIDTH - 4)
        ty = random.randint(3, MAP_HEIGHT - 4)
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
                               "desc": "南湖校区的桂花树"}
            })
        else:
            structures[ty][tx] = GID_TREE_GREEN
        collision[ty][tx] = GID_COLLISION

    for _ in range(20):
        bx = random.randint(3, MAP_WIDTH - 4)
        by = random.randint(3, MAP_HEIGHT - 4)
        if ground[by][bx] != GID_GRASS:
            continue
        if structures[by][bx] != GID_EMPTY:
            continue
        if decorations[by][bx] != GID_EMPTY:
            continue
        if collision[by][bx] != GID_EMPTY:
            continue
        decorations[by][bx] = GID_BUSH
        collision[by][bx] = GID_COLLISION

    for _ in range(8):
        rx = random.randint(3, MAP_WIDTH - 4)
        ry = random.randint(3, MAP_HEIGHT - 4)
        if ground[ry][rx] == GID_GRASS and structures[ry][rx] == GID_EMPTY and decorations[ry][rx] == GID_EMPTY and collision[ry][rx] == GID_EMPTY:
            decorations[ry][rx] = GID_LAWN_ROCK

    for fx in range(3, MAP_WIDTH - 3, 6):
        if structures[2][fx] == GID_EMPTY and decorations[2][fx] == GID_EMPTY and collision[2][fx] == GID_EMPTY:
            structures[2][fx] = GID_FENCE
            collision[2][fx] = GID_COLLISION


def _add_grass_variation(ground):
    random.seed(999)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if ground[y][x] != GID_GRASS:
                continue
            if random.random() < 0.06:
                ground[y][x] = GID_GRASS_DARK


def _add_nanhu_spawn(trigger_objects):
    trigger_objects.append({
        "x": 20 * TILE_SIZE,
        "y": 12 * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": 2 * TILE_SIZE,
        "type": "spawn",
        "properties": {
            "spawn_id": "nanhu_entrance",
        }
    })
    trigger_objects.append({
        "x": 20 * TILE_SIZE,
        "y": 25 * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": 2 * TILE_SIZE,
        "type": "spawn",
        "properties": {
            "spawn_id": "shuttle_return",
        }
    })


GID_EMPTY_I = 0
GID_WOOD_FLOOR = 1
GID_WOOD_FLOOR2 = 2
GID_TILE_FLOOR = 3
GID_CARPET_RED = 4
GID_INDOOR_WALL = 5
GID_INDOOR_WALL_TOP = 6
GID_BOOKSHELF = 7
GID_BOOKSHELF_TOP = 8
GID_TABLE = 9
GID_CHAIR = 10
GID_COUNTER = 11
GID_FRIDGE = 12
GID_STAIRS_DOWN = 13
GID_STAIRS_UP = 14
GID_COURT_FLOOR = 15
GID_HOOP = 16
GID_SCOREBOARD = 17
GID_COMPUTER = 18
GID_DOOR_INDOOR = 19
GID_COLLISION_I = 20
GID_KITCHEN_FLOOR = 21
GID_RUG = 22
GID_BLACKBOARD = 23
GID_PLANT_INDOOR = 24

TILE_COUNT_I = 24

SOLID_GIDS_I = {
    GID_INDOOR_WALL, GID_INDOOR_WALL_TOP, GID_BOOKSHELF, GID_BOOKSHELF_TOP,
    GID_TABLE, GID_CHAIR, GID_COUNTER, GID_FRIDGE,
    GID_HOOP, GID_SCOREBOARD, GID_COMPUTER,
    GID_BLACKBOARD, GID_PLANT_INDOOR, GID_COLLISION_I,
}


def design_nanhulou_f1():
    W, H = 20, 15
    ground = _fill_layer(None, W, H, GID_TILE_FLOOR)
    structures = _fill_layer(None, W, H, GID_EMPTY_I)
    decorations = _fill_layer(None, W, H, GID_EMPTY_I)
    collision = _fill_layer(None, W, H, GID_EMPTY_I)
    interactive_objects = []
    trigger_objects = []

    _fill_border(structures, W, H, GID_INDOOR_WALL_TOP)
    for y in range(2, H - 1):
        structures[y][0] = GID_INDOOR_WALL
        structures[y][W - 1] = GID_INDOOR_WALL

    for x in range(2, 7):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION_I
        collision[2][x] = GID_COLLISION_I

    for x in range(13, 18):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION_I
        collision[2][x] = GID_COLLISION_I

    structures[5][4] = GID_TABLE
    structures[5][5] = GID_TABLE
    collision[5][4] = GID_COLLISION_I
    collision[5][5] = GID_COLLISION_I
    structures[4][4] = GID_CHAIR
    structures[4][5] = GID_CHAIR
    collision[4][4] = GID_COLLISION_I
    collision[4][5] = GID_COLLISION_I

    structures[5][14] = GID_TABLE
    structures[5][15] = GID_TABLE
    collision[5][14] = GID_COLLISION_I
    collision[5][15] = GID_COLLISION_I
    structures[4][14] = GID_CHAIR
    structures[4][15] = GID_CHAIR
    collision[4][14] = GID_COLLISION_I
    collision[4][15] = GID_COLLISION_I

    structures[8][9] = GID_COUNTER
    structures[8][10] = GID_COUNTER
    collision[8][9] = GID_COLLISION_I
    collision[8][10] = GID_COLLISION_I

    structures[10][2] = GID_BLACKBOARD
    collision[10][2] = GID_COLLISION_I

    structures[10][17] = GID_COMPUTER
    collision[10][17] = GID_COLLISION_I

    structures[3][9] = GID_PLANT_INDOOR
    collision[3][9] = GID_COLLISION_I

    ground[7][9] = GID_CARPET_RED
    ground[7][10] = GID_CARPET_RED
    ground[8][9] = GID_CARPET_RED
    ground[8][10] = GID_CARPET_RED

    structures[1][17] = GID_STAIRS_UP
    collision[1][17] = GID_EMPTY_I
    for sy in range(1, 3):
        for sx in range(16, 19):
            if sy == 1 and sx == 17:
                continue
            structures[sy][sx] = GID_EMPTY_I
            collision[sy][sx] = GID_EMPTY_I

    interactive_objects.append({
        "x": 17 * TILE_SIZE, "y": 1 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "stairs_up",
        "properties": {
            "interactive_type": "enter",
            "prompt_text": "上楼",
            "target_map": "nanhulou_f2",
            "spawn_point": "nanhulou_f2_stairs",
            "transition_type": "floor_change",
        }
    })

    interactive_objects.append({
        "x": 2 * TILE_SIZE, "y": 10 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "blackboard",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看公告栏",
            "display_name": "公告栏",
        }
    })

    interactive_objects.append({
        "x": 17 * TILE_SIZE, "y": 10 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "computer",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看电脑",
            "display_name": "查询终端",
        }
    })

    for x in range(2, 7):
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": 1 * TILE_SIZE,
            "width": TILE_SIZE, "height": 2 * TILE_SIZE,
            "type": "bookshelf",
            "properties": {
                "interactive_type": "examine",
                "prompt_text": "查看书架",
                "display_name": "书架",
            }
        })

    structures[H - 2][9] = GID_DOOR_INDOOR
    structures[H - 2][10] = GID_DOOR_INDOOR
    collision[H - 2][9] = GID_EMPTY_I
    collision[H - 2][10] = GID_EMPTY_I

    _add_exit_trigger(trigger_objects, 9, H - 2, 2, 1,
                      "nanhu_campus", "nanhulou_exit")
    _add_spawn(trigger_objects, "nanhulou_entrance", 9, H - 4)
    _add_spawn(trigger_objects, "nanhulou_f1_stairs", 16, 2)

    return W, H, ground, structures, decorations, collision, interactive_objects, trigger_objects


def design_nanhulou_f2():
    W, H = 20, 15
    ground = _fill_layer(None, W, H, GID_WOOD_FLOOR)
    structures = _fill_layer(None, W, H, GID_EMPTY_I)
    decorations = _fill_layer(None, W, H, GID_EMPTY_I)
    collision = _fill_layer(None, W, H, GID_EMPTY_I)
    interactive_objects = []
    trigger_objects = []

    _fill_border(structures, W, H, GID_INDOOR_WALL_TOP)
    for y in range(2, H - 1):
        structures[y][0] = GID_INDOOR_WALL
        structures[y][W - 1] = GID_INDOOR_WALL

    for x in range(2, 6):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION_I
        collision[2][x] = GID_COLLISION_I

    for x in range(14, 18):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION_I
        collision[2][x] = GID_COLLISION_I

    structures[5][4] = GID_TABLE
    structures[5][5] = GID_TABLE
    collision[5][4] = GID_COLLISION_I
    collision[5][5] = GID_COLLISION_I
    structures[4][4] = GID_CHAIR
    structures[4][5] = GID_CHAIR
    collision[4][4] = GID_COLLISION_I
    collision[4][5] = GID_COLLISION_I

    structures[5][14] = GID_TABLE
    structures[5][15] = GID_TABLE
    collision[5][14] = GID_COLLISION_I
    collision[5][15] = GID_COLLISION_I

    structures[8][3] = GID_COMPUTER
    collision[8][3] = GID_COLLISION_I
    structures[8][7] = GID_COMPUTER
    collision[8][7] = GID_COLLISION_I
    structures[8][12] = GID_COMPUTER
    collision[8][12] = GID_COLLISION_I
    structures[8][16] = GID_COMPUTER
    collision[8][16] = GID_COLLISION_I

    structures[11][9] = GID_COMPUTER
    collision[11][9] = GID_COLLISION_I
    structures[11][10] = GID_COMPUTER
    collision[11][10] = GID_COLLISION_I

    ground[7][9] = GID_RUG
    ground[7][10] = GID_RUG
    ground[8][9] = GID_RUG
    ground[8][10] = GID_RUG

    structures[3][9] = GID_PLANT_INDOOR
    collision[3][9] = GID_COLLISION_I

    structures[1][2] = GID_STAIRS_DOWN
    collision[1][2] = GID_EMPTY_I
    for sy in range(1, 3):
        for sx in range(2, 5):
            if sy == 1 and sx == 2:
                continue
            structures[sy][sx] = GID_EMPTY_I
            collision[sy][sx] = GID_EMPTY_I

    interactive_objects.append({
        "x": 2 * TILE_SIZE, "y": 1 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "stairs_down",
        "properties": {
            "interactive_type": "enter",
            "prompt_text": "下楼",
            "target_map": "nanhulou_f1",
            "spawn_point": "nanhulou_f1_stairs",
            "transition_type": "floor_change",
        }
    })

    interactive_objects.append({
        "x": 3 * TILE_SIZE, "y": 8 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "computer",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看电脑",
            "display_name": "电脑终端A",
        }
    })

    interactive_objects.append({
        "x": 7 * TILE_SIZE, "y": 8 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "computer",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看电脑",
            "display_name": "电脑终端B",
        }
    })

    interactive_objects.append({
        "x": 12 * TILE_SIZE, "y": 8 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "computer",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看电脑",
            "display_name": "电脑终端C",
        }
    })

    interactive_objects.append({
        "x": 16 * TILE_SIZE, "y": 8 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "computer",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看电脑",
            "display_name": "电脑终端D",
        }
    })

    interactive_objects.append({
        "x": 9 * TILE_SIZE, "y": 11 * TILE_SIZE,
        "width": 2 * TILE_SIZE, "height": TILE_SIZE,
        "type": "computer",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看主终端",
            "display_name": "主控电脑",
        }
    })

    _add_spawn(trigger_objects, "nanhulou_f2_stairs", 3, 2)

    return W, H, ground, structures, decorations, collision, interactive_objects, trigger_objects


def layer_to_csv(layer_data):
    values = []
    for row in layer_data:
        values.extend(str(v) for v in row)
    return "\n" + ",".join(values) + "\n"


def create_tmx(W, H, ground, terrain, structures, decorations, collision,
               interactive_objects, trigger_objects,
               tileset_name, tileset_path, tile_count, solid_gids,
               output_path, has_terrain=False):
    root = ET.Element("map")
    root.set("version", "1.5")
    root.set("orientation", "orthogonal")
    root.set("renderorder", "right-down")
    root.set("width", str(W))
    root.set("height", str(H))
    root.set("tilewidth", str(TILE_SIZE))
    root.set("tileheight", str(TILE_SIZE))
    root.set("infinite", "0")
    root.set("nextobjectid", "1")

    tileset = ET.SubElement(root, "tileset")
    tileset.set("firstgid", "1")
    tileset.set("name", tileset_name)
    tileset.set("tilewidth", str(TILE_SIZE))
    tileset.set("tileheight", str(TILE_SIZE))
    tileset.set("tilecount", str(tile_count))
    tileset.set("columns", str(tile_count))

    image = ET.SubElement(tileset, "image")
    image.set("source", tileset_path)
    image.set("width", str(tile_count * TILE_SIZE))
    image.set("height", str(TILE_SIZE))

    for local_id in sorted(gid - 1 for gid in solid_gids):
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
    ground_layer.set("width", str(W))
    ground_layer.set("height", str(H))
    ground_data = ET.SubElement(ground_layer, "data")
    ground_data.set("encoding", "csv")
    ground_data.text = layer_to_csv(ground)
    layer_id += 1

    if has_terrain and terrain is not None:
        terrain_layer = ET.SubElement(root, "layer")
        terrain_layer.set("id", str(layer_id))
        terrain_layer.set("name", "terrain")
        terrain_layer.set("width", str(W))
        terrain_layer.set("height", str(H))
        terrain_data = ET.SubElement(terrain_layer, "data")
        terrain_data.set("encoding", "csv")
        terrain_data.text = layer_to_csv(terrain)
        layer_id += 1

    struct_layer = ET.SubElement(root, "layer")
    struct_layer.set("id", str(layer_id))
    struct_layer.set("name", "structures")
    struct_layer.set("width", str(W))
    struct_layer.set("height", str(H))
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
    coll_layer.set("width", str(W))
    coll_layer.set("height", str(H))
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
    deco_layer.set("width", str(W))
    deco_layer.set("height", str(H))
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
    print(f"  Map size: {W}x{H} tiles")
    print(f"  Interactive objects: {len(interactive_objects)}")
    print(f"  Trigger zones: {len(trigger_objects)}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    map_dir = os.path.join(base_dir, "world", "map_data")

    outdoor_tileset_path = os.path.join(base_dir, "assets", "tilesets", "main_campus_tileset.png")
    indoor_tileset_path = os.path.join(base_dir, "assets", "tilesets", "indoor_tileset.png")

    outdoor_tileset_rel = os.path.relpath(outdoor_tileset_path, map_dir).replace("\\", "/")
    indoor_tileset_rel = os.path.relpath(indoor_tileset_path, map_dir).replace("\\", "/")

    print("--- Nanhu Campus ---")
    ground, terrain, structures, decorations, collision, objs, triggers = design_nanhu_campus()
    create_tmx(MAP_WIDTH, MAP_HEIGHT, ground, terrain, structures, decorations, collision,
               objs, triggers,
               "main_campus_tileset", outdoor_tileset_rel, 27, SOLID_GIDS,
               os.path.join(map_dir, "nanhu_campus.tmx"), has_terrain=True)

    print("\n--- Nanhu Building F1 ---")
    W, H, ground, structures, decorations, collision, objs, triggers = design_nanhulou_f1()
    create_tmx(W, H, ground, None, structures, decorations, collision, objs, triggers,
               "indoor_tileset", indoor_tileset_rel, TILE_COUNT_I, SOLID_GIDS_I,
               os.path.join(map_dir, "nanhulou_f1.tmx"))

    print("\n--- Nanhu Building F2 ---")
    W, H, ground, structures, decorations, collision, objs, triggers = design_nanhulou_f2()
    create_tmx(W, H, ground, None, structures, decorations, collision, objs, triggers,
               "indoor_tileset", indoor_tileset_rel, TILE_COUNT_I, SOLID_GIDS_I,
               os.path.join(map_dir, "nanhulou_f2.tmx"))

    print("\nAll Nanhu maps generated successfully!")
