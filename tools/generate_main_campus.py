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
GID_GATE_PILLAR = 28
GID_GATE_BEAM = 29
GID_GATE_SIGN = 30
# 图书馆专属 tile
GID_LIB_WALL = 31
GID_LIB_WINDOW = 32
GID_LIB_ROOF = 33
GID_LIB_DOOR = 34
GID_LIB_PILLAR = 35
GID_LIB_AWNING = 36
GID_LIB_SIGN = 37
GID_LIB_SIGN_SIDE = 38
# 体育馆专属 tile
GID_GYM_WALL = 39
GID_GYM_WINDOW = 40
GID_GYM_ROOF_CENTER = 41
GID_GYM_ROOF_SIDE = 42
GID_GYM_DOOR_MAIN = 43
GID_GYM_DOOR_SIDE = 44
GID_GYM_VENT = 45
GID_GYM_SIGN = 46
# 食堂专属 tile
GID_DINING_WALL = 47
GID_DINING_WINDOW = 48
GID_DINING_ROOF = 49
GID_DINING_DOOR = 50
GID_DINING_AWNING = 51
GID_DINING_CHIMNEY = 52
GID_DINING_SIGN = 53
GID_DINING_MENU = 54
# 南湖综合楼专属 tile
GID_NANHU_WALL = 55
GID_NANHU_GLASS = 56
GID_NANHU_ROOF = 57
GID_NANHU_ROOF_RAIL = 58
GID_NANHU_DOOR = 59
GID_NANHU_SIGN = 60
GID_NANHU_AC = 61
GID_NANHU_LOBBY_LIGHT = 62
# 喷泉底座凹槽 tile（7个凹槽分布在6×6网格的不同位置）
GID_FOUNTAIN_SLOT_0 = 63  # 顶部凹槽 - tile(3,0)
GID_FOUNTAIN_SLOT_1 = 64  # 右上凹槽 - tile(4,1)
GID_FOUNTAIN_SLOT_2 = 65  # 右侧凹槽 - tile(5,3)
GID_FOUNTAIN_SLOT_3 = 66  # 右下凹槽 - tile(4,4)
GID_FOUNTAIN_SLOT_4 = 67  # 左下凹槽 - tile(1,4)
GID_FOUNTAIN_SLOT_5 = 68  # 左侧凹槽 - tile(0,3)
GID_FOUNTAIN_SLOT_6 = 69  # 左上凹槽 - tile(1,1)

TILE_COUNT = 69

SOLID_GIDS = {
    GID_WALL_BRICK, GID_WALL_BRICK_TOP, GID_WALL_GRAY,
    GID_WALL_GRAY_WINDOW, GID_BUILDING_ROOF, GID_WATER,
    GID_TREE_OSMANTHUS, GID_TREE_GREEN, GID_BUSH,
    GID_FLOWER_BED, GID_LAMP, GID_BENCH, GID_FENCE,
    GID_FOUNTAIN_BASE, GID_FOUNTAIN_WATER, GID_SCULPTURE,
    GID_BUS_STOP, GID_HEDGE, GID_COLLISION,
    GID_FLOWER_GARDEN, GID_TREE_CLUSTER,
    GID_GATE_PILLAR, GID_GATE_BEAM, GID_GATE_SIGN,
    GID_LIB_WALL, GID_LIB_WINDOW, GID_LIB_ROOF, GID_LIB_PILLAR, GID_LIB_AWNING, GID_LIB_SIGN, GID_LIB_SIGN_SIDE,
    GID_GYM_WALL, GID_GYM_WINDOW, GID_GYM_ROOF_CENTER, GID_GYM_ROOF_SIDE, GID_GYM_VENT, GID_GYM_SIGN,
    GID_DINING_WALL, GID_DINING_WINDOW, GID_DINING_ROOF, GID_DINING_AWNING, GID_DINING_CHIMNEY, GID_DINING_SIGN, GID_DINING_MENU,
    GID_NANHU_WALL, GID_NANHU_GLASS, GID_NANHU_ROOF, GID_NANHU_ROOF_RAIL, GID_NANHU_AC, GID_NANHU_SIGN,
    GID_FOUNTAIN_SLOT_0, GID_FOUNTAIN_SLOT_1, GID_FOUNTAIN_SLOT_2, GID_FOUNTAIN_SLOT_3,
    GID_FOUNTAIN_SLOT_4, GID_FOUNTAIN_SLOT_5, GID_FOUNTAIN_SLOT_6,
}


def _draw_fountain_base_tile(surface, x, rect):
    """绘制喷泉底座 tile 的基础外观（不含凹槽）"""
    surface.fill((0, 0, 0, 0), rect)
    pygame.draw.ellipse(surface, (120, 118, 115), (x + 0, 1, 16, 14))
    pygame.draw.ellipse(surface, (160, 158, 155), (x + 1, 2, 14, 12))
    pygame.draw.ellipse(surface, (145, 143, 140), (x + 2, 3, 12, 10))
    pygame.draw.ellipse(surface, (130, 128, 125), (x + 3, 4, 10, 8))
    for tx, ty in [(x+3,5),(x+6,4),(x+10,6),(x+12,8),(x+5,10),(x+9,11),(x+2,8)]:
        surface.set_at((tx, ty), (140, 138, 135))
    for tx, ty in [(x+4,6),(x+8,5),(x+11,9),(x+7,10),(x+3,9)]:
        surface.set_at((tx, ty), (170, 168, 165))
    pygame.draw.ellipse(surface, (50, 100, 200), (x + 4, 5, 8, 6))
    pygame.draw.arc(surface, (80, 140, 220), (x + 5, 6, 5, 3), 0.2, 2.9, 1)
    pygame.draw.arc(surface, (70, 130, 215), (x + 6, 7, 4, 2), 0.5, 2.5, 1)
    surface.set_at((x + 6, 6), (120, 180, 245))
    surface.set_at((x + 9, 8), (100, 165, 235))


def _draw_slot_marker(surface, sx, sy):
    """在指定位置绘制凹槽标记（3×3深色凹陷+金色边框）"""
    # 凹槽凹陷（深色）
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            px, py = sx + dx, sy + dy
            if 0 <= px < surface.get_width() and 0 <= py < TILE_SIZE:
                surface.set_at((px, py), (60, 55, 50))
    # 凹槽中心（更暗）
    if 0 <= sx < surface.get_width() and 0 <= sy < TILE_SIZE:
        surface.set_at((sx, sy), (40, 35, 30))
    # 金色边框高光（右上角）
    if sx + 1 < surface.get_width() and sy - 1 >= 0:
        surface.set_at((sx + 1, sy - 1), (200, 170, 60))
    if sx - 1 >= 0 and sy + 1 < TILE_SIZE:
        surface.set_at((sx - 1, sy + 1), (160, 130, 40))


def create_tileset(output_path):
    pygame.init()
    surface = pygame.Surface((TILE_COUNT * TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

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
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x + 6, 10, 4, 6))
        pygame.draw.circle(surface, (34, 139, 34), (x + 8, 6), 7)
        pygame.draw.circle(surface, (44, 155, 44), (x + 5, 4), 5)
        pygame.draw.circle(surface, (44, 155, 44), (x + 11, 5), 4)
        pygame.draw.circle(surface, (0, 100, 0), (x + 3, 3), 3)
        for fx, fy in [(3, 1), (5, 2), (7, 1), (9, 2), (11, 1), (13, 3),
                       (4, 4), (6, 5), (8, 4), (10, 5), (12, 4),
                       (3, 6), (7, 7), (11, 6)]:
            surface.set_at((x + fx, fy), (255, 200, 0))
        for fx, fy in [(4, 2), (8, 2), (12, 3), (5, 5), (9, 5), (6, 7), (10, 7), (3, 4)]:
            surface.set_at((x + fx, fy), (255, 230, 100))
        for fx, fy in [(2, 0), (6, 0), (10, 0), (14, 2),
                       (1, 3), (13, 5), (2, 7), (12, 7)]:
            surface.set_at((x + fx, fy), (255, 240, 150))
    elif gid == GID_TREE_GREEN:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x + 6, 9, 4, 7))
        pygame.draw.circle(surface, (34, 139, 34), (x + 8, 6), 6)
        pygame.draw.circle(surface, (0, 100, 0), (x + 5, 4), 3)
        pygame.draw.circle(surface, (50, 160, 50), (x + 10, 5), 2)
    elif gid == GID_BUSH:
        surface.fill((0, 0, 0, 0), rect)
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
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (80, 80, 80), (x + 7, 4, 2, 10))
        pygame.draw.circle(surface, (255, 255, 150), (x + 8, 3), 3)
        pygame.draw.circle(surface, (255, 255, 200), (x + 8, 3), 2)
        pygame.draw.rect(surface, (60, 60, 60), (x + 6, 13, 4, 2))
    elif gid == GID_BENCH:
        # 加长版长椅：坐板和靠背延伸到14px宽
        surface.fill((0, 0, 0, 0), rect)
        # 坐板
        pygame.draw.rect(surface, (139, 90, 43), (x + 1, 6, 14, 3))
        # 靠背
        pygame.draw.rect(surface, (120, 75, 35), (x + 1, 4, 14, 2))
        # 四条腿
        pygame.draw.rect(surface, (101, 67, 33), (x + 1, 9, 2, 5))
        pygame.draw.rect(surface, (101, 67, 33), (x + 13, 9, 2, 5))
        # 靠背支撑柱
        pygame.draw.rect(surface, (101, 67, 33), (x + 1, 3, 2, 2))
        pygame.draw.rect(surface, (101, 67, 33), (x + 13, 3, 2, 2))
    elif gid == GID_FENCE:
        surface.fill((0, 0, 0, 0), rect)
        for fx in range(0, TILE_SIZE, 4):
            pygame.draw.rect(surface, (80, 80, 80), (x + fx + 1, 3, 2, 10))
        pygame.draw.rect(surface, (100, 100, 100), (x, 5, TILE_SIZE, 2))
        pygame.draw.rect(surface, (100, 100, 100), (x, 10, TILE_SIZE, 2))
    elif gid == GID_FOUNTAIN_BASE:
        surface.fill((0, 0, 0, 0), rect)
        # 多层石质底座（外深内浅渐变，营造立体感）
        pygame.draw.ellipse(surface, (120, 118, 115), (x + 0, 1, 16, 14))  # 最外层阴影
        pygame.draw.ellipse(surface, (160, 158, 155), (x + 1, 2, 14, 12))  # 底座主体
        pygame.draw.ellipse(surface, (145, 143, 140), (x + 2, 3, 12, 10))  # 内层暗面
        pygame.draw.ellipse(surface, (130, 128, 125), (x + 3, 4, 10, 8))   # 内圈
        # 石纹纹理（深浅交替像素点）
        for tx, ty in [(x+3,5),(x+6,4),(x+10,6),(x+12,8),(x+5,10),(x+9,11),(x+2,8)]:
            surface.set_at((tx, ty), (140, 138, 135))
        for tx, ty in [(x+4,6),(x+8,5),(x+11,9),(x+7,10),(x+3,9)]:
            surface.set_at((tx, ty), (170, 168, 165))
        # 水面
        pygame.draw.ellipse(surface, (50, 100, 200), (x + 4, 5, 8, 6))
        # 水面波纹
        pygame.draw.arc(surface, (80, 140, 220), (x + 5, 6, 5, 3), 0.2, 2.9, 1)
        pygame.draw.arc(surface, (70, 130, 215), (x + 6, 7, 4, 2), 0.5, 2.5, 1)
        # 水面高光
        surface.set_at((x + 6, 6), (120, 180, 245))
        surface.set_at((x + 9, 8), (100, 165, 235))
    elif gid == GID_FOUNTAIN_WATER:
        surface.fill((0, 0, 0, 0), rect)
        # 底座（同 BASE）
        pygame.draw.ellipse(surface, (120, 118, 115), (x + 0, 1, 16, 14))
        pygame.draw.ellipse(surface, (160, 158, 155), (x + 1, 2, 14, 12))
        pygame.draw.ellipse(surface, (145, 143, 140), (x + 2, 3, 12, 10))
        pygame.draw.ellipse(surface, (130, 128, 125), (x + 3, 4, 10, 8))
        for tx, ty in [(x+3,5),(x+6,4),(x+10,6),(x+12,8),(x+5,10),(x+9,11),(x+2,8)]:
            surface.set_at((tx, ty), (140, 138, 135))
        for tx, ty in [(x+4,6),(x+8,5),(x+11,9),(x+7,10),(x+3,9)]:
            surface.set_at((tx, ty), (170, 168, 165))
        # 水面
        pygame.draw.ellipse(surface, (50, 100, 200), (x + 4, 5, 8, 6))
        pygame.draw.arc(surface, (80, 140, 220), (x + 5, 6, 5, 3), 0.2, 2.9, 1)
        pygame.draw.arc(surface, (70, 130, 215), (x + 6, 7, 4, 2), 0.5, 2.5, 1)
        surface.set_at((x + 6, 6), (120, 180, 245))
        surface.set_at((x + 9, 8), (100, 165, 235))
        # 中心柱（加粗，带石质纹理）
        pygame.draw.rect(surface, (130, 128, 125), (x + 6, 0, 4, 6))
        pygame.draw.rect(surface, (155, 153, 150), (x + 7, 0, 2, 6))
        # 顶部碗状结构（更立体）
        pygame.draw.rect(surface, (140, 138, 135), (x + 4, 0, 8, 2))
        pygame.draw.rect(surface, (160, 158, 155), (x + 5, 1, 6, 1))
        # 水花（多层水滴弧线）
        surface.set_at((x + 7, 14), (120, 185, 250))  # 向上水柱
        surface.set_at((x + 8, 14), (120, 185, 250))
        surface.set_at((x + 6, 13), (100, 165, 235))
        surface.set_at((x + 9, 13), (100, 165, 235))
        surface.set_at((x + 5, 12), (80, 145, 220))
        surface.set_at((x + 10, 12), (80, 145, 220))
        # 水滴飞溅
        surface.set_at((x + 4, 11), (90, 155, 225))
        surface.set_at((x + 11, 11), (90, 155, 225))
        surface.set_at((x + 3, 10), (70, 135, 210))
        surface.set_at((x + 12, 10), (70, 135, 210))
    # 喷泉底座凹槽 tile：底座外观 + 凹槽标记
    # 每个凹槽在 tile 内的相对位置不同，根据6×6网格中的位置精确绘制
    elif gid == GID_FOUNTAIN_SLOT_0:
        # 顶部凹槽 - tile(3,0)，凹槽在 tile 内 (0, 14)
        _draw_fountain_base_tile(surface, x, rect)
        _draw_slot_marker(surface, x + 0, 14)
    elif gid == GID_FOUNTAIN_SLOT_1:
        # 右上凹槽 - tile(4,1)，凹槽在 tile 内 (14, 11)
        _draw_fountain_base_tile(surface, x, rect)
        _draw_slot_marker(surface, x + 14, 11)
    elif gid == GID_FOUNTAIN_SLOT_2:
        # 右侧凹槽 - tile(5,3)，凹槽在 tile 内 (5, 8)
        _draw_fountain_base_tile(surface, x, rect)
        _draw_slot_marker(surface, x + 5, 8)
    elif gid == GID_FOUNTAIN_SLOT_3:
        # 右下凹槽 - tile(4,4)，凹槽在 tile 内 (0, 15)
        _draw_fountain_base_tile(surface, x, rect)
        _draw_slot_marker(surface, x + 0, 15)
    elif gid == GID_FOUNTAIN_SLOT_4:
        # 左下凹槽 - tile(1,4)，凹槽在 tile 内 (16, 15)
        _draw_fountain_base_tile(surface, x, rect)
        _draw_slot_marker(surface, x + 15, 15)
    elif gid == GID_FOUNTAIN_SLOT_5:
        # 左侧凹槽 - tile(0,3)，凹槽在 tile 内 (11, 8)
        _draw_fountain_base_tile(surface, x, rect)
        _draw_slot_marker(surface, x + 11, 8)
    elif gid == GID_FOUNTAIN_SLOT_6:
        # 左上凹槽 - tile(1,1)，凹槽在 tile 内 (2, 11)
        _draw_fountain_base_tile(surface, x, rect)
        _draw_slot_marker(surface, x + 2, 11)
    elif gid == GID_SCULPTURE:
        surface.fill((0, 0, 0, 0), rect)
        # 底座（3层石阶，由下到上逐渐收窄）
        pygame.draw.rect(surface, (130, 125, 120), (x + 1, 13, 14, 3))  # 最下层
        pygame.draw.rect(surface, (150, 145, 140), (x + 2, 12, 12, 1))  # 中层
        pygame.draw.rect(surface, (160, 155, 150), (x + 3, 11, 10, 1))  # 上层
        # 底座高光与阴影
        pygame.draw.line(surface, (170, 165, 160), (x + 2, 13), (x + 14, 13))
        pygame.draw.line(surface, (110, 105, 100), (x + 1, 15), (x + 14, 15))
        # 柱身（从底座向上延伸）
        pygame.draw.rect(surface, (170, 165, 160), (x + 5, 5, 6, 6))
        pygame.draw.rect(surface, (180, 175, 170), (x + 6, 5, 4, 6))
        # 柱身纹理
        pygame.draw.line(surface, (155, 150, 145), (x + 5, 7), (x + 10, 7))
        pygame.draw.line(surface, (155, 150, 145), (x + 5, 9), (x + 10, 9))
        # 顶部装饰（球形）
        pygame.draw.circle(surface, (190, 185, 180), (x + 8, 4), 3)
        pygame.draw.circle(surface, (200, 195, 190), (x + 7, 3), 2)
        # 球体高光
        surface.set_at((x + 7, 2), (220, 215, 210))
        # 顶部尖端
        surface.set_at((x + 8, 1), (210, 205, 200))
    elif gid == GID_BUS_STOP:
        # 放大版站台：更粗的站牌杆、更大的站牌、候车棚
        surface.fill((0, 0, 0, 0), rect)
        # 站牌杆（加粗到3px）
        pygame.draw.rect(surface, (80, 80, 80), (x + 6, 4, 3, 10))
        # 站牌（放大到12x7）
        pygame.draw.rect(surface, (0, 100, 180), (x + 2, 0, 12, 7))
        pygame.draw.rect(surface, (255, 255, 255), (x + 3, 1, 10, 5))
        pygame.draw.rect(surface, (0, 100, 180), (x + 2, 0, 12, 7), 1)
        # 候车棚顶
        pygame.draw.rect(surface, (100, 100, 110), (x, 8, TILE_SIZE, 2))
        # 棚柱
        pygame.draw.rect(surface, (80, 80, 90), (x + 1, 10, 2, 5))
        pygame.draw.rect(surface, (80, 80, 90), (x + 13, 10, 2, 5))
        # 座椅
        pygame.draw.rect(surface, (139, 90, 43), (x + 4, 12, 8, 2))
    elif gid == GID_HEDGE:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (34, 120, 0), (x, 2, TILE_SIZE, 12))
        pygame.draw.rect(surface, (50, 140, 20), (x, 3, TILE_SIZE, 10))
        for hx in range(0, TILE_SIZE, 3):
            pygame.draw.rect(surface, (40, 130, 10), (x + hx, 2, 2, 1))
    elif gid == GID_COLLISION:
        surface.fill((0, 0, 0, 0), rect)
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
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (80, 55, 25), (x + 2, 8, 3, 7))
        pygame.draw.rect(surface, (80, 55, 25), (x + 11, 9, 3, 6))
        pygame.draw.circle(surface, (34, 139, 34), (x + 3, 5), 4)
        pygame.draw.circle(surface, (0, 100, 0), (x + 2, 4), 2)
        pygame.draw.circle(surface, (34, 139, 34), (x + 12, 6), 4)
        pygame.draw.circle(surface, (50, 160, 50), (x + 13, 5), 2)
        pygame.draw.circle(surface, (40, 120, 20), (x + 8, 4), 5)
        pygame.draw.circle(surface, (30, 110, 15), (x + 7, 3), 3)
    elif gid == GID_LAWN_ROCK:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.ellipse(surface, (140, 140, 130), (x + 3, 6, 10, 8))
        pygame.draw.ellipse(surface, (160, 160, 150), (x + 4, 7, 8, 5))
        pygame.draw.ellipse(surface, (120, 120, 110), (x + 5, 8, 4, 3))
        surface.set_at((x + 7, 7), (180, 180, 170))
    elif gid == GID_GATE_PILLAR:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (180, 175, 165), (x + 3, 0, 10, 16))
        pygame.draw.rect(surface, (200, 195, 185), (x + 4, 0, 4, 16))
        pygame.draw.rect(surface, (160, 155, 145), (x + 11, 0, 2, 16))
        pygame.draw.rect(surface, (150, 145, 135), (x + 3, 0, 10, 2))
        pygame.draw.rect(surface, (150, 145, 135), (x + 3, 14, 10, 2))
        pygame.draw.rect(surface, (190, 185, 175), (x + 2, 0, 1, 16))
        pygame.draw.rect(surface, (190, 185, 175), (x + 13, 0, 1, 16))
        pygame.draw.rect(surface, (140, 135, 125), (x + 2, 0, 12, 1))
        pygame.draw.rect(surface, (140, 135, 125), (x + 2, 15, 12, 1))
    elif gid == GID_GATE_BEAM:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (140, 30, 25), (x, 4, 16, 8))
        pygame.draw.rect(surface, (160, 40, 35), (x, 4, 16, 2))
        pygame.draw.rect(surface, (120, 25, 20), (x, 10, 16, 2))
        pygame.draw.rect(surface, (100, 20, 15), (x, 4, 16, 1))
        pygame.draw.rect(surface, (100, 20, 15), (x, 11, 16, 1))
        pygame.draw.rect(surface, (180, 160, 60), (x + 2, 6, 12, 1))
        pygame.draw.rect(surface, (180, 160, 60), (x + 2, 9, 12, 1))
        pygame.draw.rect(surface, (170, 150, 50), (x + 6, 6, 1, 4))
        pygame.draw.rect(surface, (170, 150, 50), (x + 9, 6, 1, 4))
    elif gid == GID_GATE_SIGN:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (140, 30, 25), (x, 2, 16, 12))
        pygame.draw.rect(surface, (160, 40, 35), (x, 2, 16, 2))
        pygame.draw.rect(surface, (120, 25, 20), (x, 12, 16, 2))
        pygame.draw.rect(surface, (180, 160, 60), (x + 1, 3, 14, 10), 1)
        pygame.draw.rect(surface, (200, 180, 70), (x + 2, 4, 12, 8))
        for cx, cy in [(4, 6), (7, 6), (10, 6), (4, 9), (7, 9), (10, 9)]:
            pygame.draw.rect(surface, (140, 30, 25), (x + cx, cy, 2, 3))
    # ---- 图书馆专属 tile ----
    elif gid == GID_LIB_WALL:
        surface.fill((210, 195, 150), rect)
        for yy in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (180, 165, 120), (x, yy), (x + TILE_SIZE, yy))
        pygame.draw.line(surface, (190, 175, 130), (x + 8, 0), (x + 8, TILE_SIZE))
    elif gid == GID_LIB_WINDOW:
        surface.fill((210, 195, 150), rect)
        for yy in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (180, 165, 120), (x, yy), (x + TILE_SIZE, yy))
        pygame.draw.rect(surface, (100, 140, 180), (x + 2, 1, 12, 7))
        pygame.draw.rect(surface, (80, 60, 30), (x + 2, 1, 12, 7), 1)
        pygame.draw.line(surface, (80, 60, 30), (x + 8, 1), (x + 8, 8))
        pygame.draw.line(surface, (80, 60, 30), (x + 2, 4), (x + 14, 4))
    elif gid == GID_LIB_ROOF:
        surface.fill((70, 80, 95), rect)
        for yy in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (60, 70, 85), (x, yy), (x + TILE_SIZE, yy))
        pygame.draw.line(surface, (90, 90, 90), (x + 12, 0), (x + 12, 4))
    elif gid == GID_LIB_DOOR:
        surface.fill((210, 195, 150), rect)
        pygame.draw.rect(surface, (160, 190, 210), (x + 3, 1, 10, 14))
        pygame.draw.rect(surface, (120, 120, 130), (x + 3, 1, 10, 14), 1)
        pygame.draw.line(surface, (120, 120, 130), (x + 8, 1), (x + 8, 15))
        surface.set_at((x + 11, 8), (180, 180, 190))
    elif gid == GID_LIB_PILLAR:
        surface.fill((210, 195, 150), rect)
        pygame.draw.rect(surface, (200, 185, 140), (x + 5, 0, 6, 16))
        pygame.draw.rect(surface, (180, 165, 120), (x + 4, 0, 8, 2))
        pygame.draw.rect(surface, (180, 165, 120), (x + 4, 14, 8, 2))
        pygame.draw.line(surface, (190, 175, 130), (x + 8, 0), (x + 8, 16))
    elif gid == GID_LIB_AWNING:
        surface.fill((210, 195, 150), rect)
        for yy in range(0, 6, 4):
            pygame.draw.line(surface, (180, 165, 120), (x, yy), (x + TILE_SIZE, yy))
        pygame.draw.rect(surface, (120, 80, 40), (x + 1, 6, 14, 4))
        pygame.draw.line(surface, (100, 65, 30), (x + 1, 10), (x + 15, 10))
        pygame.draw.line(surface, (120, 80, 40), (x + 4, 10), (x + 4, 12))
        pygame.draw.line(surface, (120, 80, 40), (x + 11, 10), (x + 11, 12))
    elif gid == GID_LIB_SIGN:
        surface.fill((210, 195, 150), rect)
        pygame.draw.rect(surface, (140, 30, 25), (x + 1, 2, 14, 8))
        pygame.draw.rect(surface, (200, 180, 60), (x + 1, 2, 14, 8), 1)
        pygame.draw.rect(surface, (220, 200, 80), (x + 2, 3, 12, 6))
        for sx, sy in [(4, 5), (7, 5), (10, 5), (4, 7), (7, 7)]:
            surface.set_at((x + sx, sy), (140, 30, 25))
    elif gid == GID_LIB_SIGN_SIDE:
        surface.fill((210, 195, 150), rect)
        pygame.draw.rect(surface, (140, 30, 25), (x + 1, 2, 14, 8))
        pygame.draw.rect(surface, (200, 180, 60), (x + 1, 2, 14, 8), 1)
        pygame.draw.rect(surface, (180, 160, 60), (x + 2, 3, 12, 6))
    # ---- 体育馆专属 tile ----
    elif gid == GID_GYM_WALL:
        surface.fill((160, 170, 185), rect)
        for bx in [4, 8, 12]:
            pygame.draw.line(surface, (140, 150, 165), (x + bx, 0), (x + bx, TILE_SIZE))
        pygame.draw.line(surface, (145, 155, 170), (x, 8), (x + TILE_SIZE, 8))
    elif gid == GID_GYM_WINDOW:
        surface.fill((160, 170, 185), rect)
        for bx in [4, 8, 12]:
            pygame.draw.line(surface, (140, 150, 165), (x + bx, 0), (x + bx, TILE_SIZE))
        pygame.draw.rect(surface, (180, 210, 230), (x + 1, 2, 14, 4))
        pygame.draw.rect(surface, (240, 240, 240), (x + 1, 2, 14, 4), 1)
    elif gid == GID_GYM_ROOF_CENTER:
        surface.fill((150, 155, 165), rect)
        pygame.draw.rect(surface, (150, 155, 165), (x, 0, TILE_SIZE, 4))
        pygame.draw.rect(surface, (140, 145, 155), (x, 4, TILE_SIZE, 4))
        pygame.draw.rect(surface, (160, 170, 185), (x, 8, TILE_SIZE, 8))
    elif gid == GID_GYM_ROOF_SIDE:
        surface.fill((150, 155, 165), rect)
        pygame.draw.rect(surface, (140, 145, 155), (x, 0, 8, 8))
        pygame.draw.rect(surface, (160, 170, 185), (x, 8, TILE_SIZE, 8))
    elif gid == GID_GYM_DOOR_MAIN:
        surface.fill((160, 170, 185), rect)
        pygame.draw.rect(surface, (180, 185, 195), (x + 1, 1, 14, 14))
        for yy in [4, 7, 10, 13]:
            pygame.draw.line(surface, (220, 140, 40), (x + 1, yy), (x + 15, yy))
        pygame.draw.rect(surface, (120, 125, 135), (x + 1, 1, 14, 14), 1)
    elif gid == GID_GYM_DOOR_SIDE:
        surface.fill((160, 170, 185), rect)
        pygame.draw.rect(surface, (160, 165, 175), (x + 4, 1, 8, 14))
        pygame.draw.rect(surface, (130, 135, 145), (x + 4, 1, 8, 14), 1)
        surface.set_at((x + 10, 8), (200, 200, 210))
    elif gid == GID_GYM_VENT:
        surface.fill((160, 170, 185), rect)
        pygame.draw.rect(surface, (130, 135, 145), (x + 3, 3, 10, 10))
        for yy in [5, 7, 9, 11]:
            pygame.draw.line(surface, (110, 115, 125), (x + 3, yy), (x + 13, yy))
        pygame.draw.rect(surface, (100, 105, 115), (x + 3, 3, 10, 10), 1)
    elif gid == GID_GYM_SIGN:
        surface.fill((160, 170, 185), rect)
        pygame.draw.rect(surface, (0, 80, 160), (x + 1, 2, 14, 8))
        pygame.draw.rect(surface, (255, 255, 255), (x + 1, 2, 14, 8), 1)
        pygame.draw.rect(surface, (20, 100, 180), (x + 2, 3, 12, 6))
        for sx, sy in [(4, 5), (7, 5), (10, 5), (4, 7), (7, 7)]:
            surface.set_at((x + sx, sy), (255, 255, 255))
    # ---- 食堂专属 tile ----
    elif gid == GID_DINING_WALL:
        surface.fill((200, 130, 80), rect)
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (180, 110, 60), (x, yy), (x + TILE_SIZE, yy))
        for bx in [4, 8, 12]:
            pygame.draw.line(surface, (180, 110, 60), (x + bx, 0), (x + bx, TILE_SIZE))
        for dx, dy in [(2, 2), (6, 6), (10, 10)]:
            surface.set_at((x + dx, dy), (215, 145, 95))
    elif gid == GID_DINING_WINDOW:
        surface.fill((200, 130, 80), rect)
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (180, 110, 60), (x, yy), (x + TILE_SIZE, yy))
        for bx in [4, 8, 12]:
            pygame.draw.line(surface, (180, 110, 60), (x + bx, 0), (x + bx, TILE_SIZE))
        pygame.draw.rect(surface, (240, 220, 150), (x + 2, 2, 12, 7))
        pygame.draw.rect(surface, (250, 250, 250), (x + 2, 2, 12, 7), 1)
        pygame.draw.line(surface, (250, 250, 250), (x + 8, 2), (x + 8, 9))
        pygame.draw.line(surface, (250, 250, 250), (x + 2, 5), (x + 14, 5))
    elif gid == GID_DINING_ROOF:
        surface.fill((130, 40, 25), rect)
        for yy in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (110, 30, 18), (x, yy), (x + TILE_SIZE, yy))
        for bx in range(0, TILE_SIZE, 8):
            pygame.draw.line(surface, (110, 30, 18), (x + bx, 0), (x + bx, TILE_SIZE))
    elif gid == GID_DINING_DOOR:
        surface.fill((200, 130, 80), rect)
        pygame.draw.rect(surface, (140, 90, 40), (x + 2, 1, 6, 14))
        pygame.draw.rect(surface, (200, 220, 200), (x + 8, 1, 6, 14))
        pygame.draw.rect(surface, (100, 65, 25), (x + 2, 1, 12, 14), 1)
        surface.set_at((x + 7, 8), (200, 180, 50))
        surface.set_at((x + 8, 8), (200, 180, 50))
    elif gid == GID_DINING_AWNING:
        surface.fill((200, 130, 80), rect)
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (180, 110, 60), (x, yy), (x + TILE_SIZE, yy))
        for col in range(0, TILE_SIZE, 4):
            color = (50, 150, 50) if (col // 4) % 2 == 0 else (70, 170, 70)
            pygame.draw.rect(surface, color, (x + col, 6, 4, 5))
        pygame.draw.line(surface, (40, 130, 40), (x, 11), (x + TILE_SIZE, 11))
    elif gid == GID_DINING_CHIMNEY:
        surface.fill((130, 40, 25), rect)
        for yy in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (110, 30, 18), (x, yy), (x + TILE_SIZE, yy))
        pygame.draw.rect(surface, (100, 80, 70), (x + 6, 0, 4, 10))
        pygame.draw.rect(surface, (80, 60, 50), (x + 5, 0, 6, 2))
        pygame.draw.circle(surface, (180, 180, 180), (x + 7, 0), 2)
        pygame.draw.circle(surface, (180, 180, 180), (x + 9, 0), 2)
    elif gid == GID_DINING_SIGN:
        surface.fill((200, 130, 80), rect)
        pygame.draw.rect(surface, (200, 100, 30), (x + 1, 2, 14, 8))
        pygame.draw.rect(surface, (255, 255, 255), (x + 1, 2, 14, 8), 1)
        pygame.draw.rect(surface, (230, 130, 50), (x + 2, 3, 12, 6))
        for sx, sy in [(4, 5), (7, 5), (10, 5), (4, 7)]:
            surface.set_at((x + sx, sy), (255, 255, 255))
    elif gid == GID_DINING_MENU:
        surface.fill((200, 130, 80), rect)
        pygame.draw.rect(surface, (240, 230, 200), (x + 3, 3, 10, 10))
        pygame.draw.rect(surface, (139, 90, 43), (x + 3, 3, 10, 10), 1)
        for yy in [5, 7, 9]:
            pygame.draw.line(surface, (80, 60, 30), (x + 5, yy), (x + 11, yy))
    # ---- 南湖综合楼专属 tile ----
    elif gid == GID_NANHU_WALL:
        surface.fill((230, 230, 235), rect)
        pygame.draw.line(surface, (210, 210, 215), (x, 5), (x + TILE_SIZE, 5))
        pygame.draw.line(surface, (210, 210, 215), (x, 10), (x + TILE_SIZE, 10))
        pygame.draw.line(surface, (220, 220, 225), (x + 8, 0), (x + 8, TILE_SIZE))
    elif gid == GID_NANHU_GLASS:
        surface.fill((140, 170, 210), rect)
        for bx in [4, 8, 12]:
            pygame.draw.line(surface, (40, 40, 50), (x + bx, 0), (x + bx, TILE_SIZE))
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (40, 40, 50), (x, yy), (x + TILE_SIZE, yy))
        for dx, dy in [(2, 2), (6, 6), (10, 10)]:
            surface.set_at((x + dx, dy), (170, 200, 240))
    elif gid == GID_NANHU_ROOF:
        surface.fill((80, 85, 90), rect)
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (70, 75, 80), (x, yy), (x + TILE_SIZE, yy))
        pygame.draw.rect(surface, (90, 95, 100), (x + 10, 2, 4, 4))
    elif gid == GID_NANHU_ROOF_RAIL:
        surface.fill((80, 85, 90), rect)
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (70, 75, 80), (x, yy), (x + TILE_SIZE, yy))
        pygame.draw.line(surface, (100, 105, 110), (x, 2), (x + TILE_SIZE, 2))
        pygame.draw.line(surface, (100, 105, 110), (x, 14), (x + TILE_SIZE, 14))
        for bx in [2, 6, 10, 14]:
            pygame.draw.line(surface, (90, 95, 100), (x + bx, 2), (x + bx, 14))
    elif gid == GID_NANHU_DOOR:
        surface.fill((230, 230, 235), rect)
        pygame.draw.rect(surface, (170, 200, 230), (x + 2, 1, 12, 14))
        pygame.draw.rect(surface, (150, 155, 165), (x + 2, 1, 12, 14), 1)
        pygame.draw.rect(surface, (0, 200, 0), (x + 7, 2, 2, 1))
        pygame.draw.rect(surface, (180, 180, 190), (x + 5, 14, 6, 1))
    elif gid == GID_NANHU_SIGN:
        surface.fill((230, 230, 235), rect)
        pygame.draw.rect(surface, (30, 60, 120), (x + 1, 2, 14, 8))
        pygame.draw.rect(surface, (255, 255, 255), (x + 1, 2, 14, 8), 1)
        pygame.draw.rect(surface, (50, 80, 140), (x + 2, 3, 12, 6))
        for sx, sy in [(4, 5), (7, 5), (10, 5), (4, 7), (7, 7)]:
            surface.set_at((x + sx, sy), (255, 255, 255))
    elif gid == GID_NANHU_AC:
        surface.fill((230, 230, 235), rect)
        pygame.draw.rect(surface, (190, 195, 200), (x + 10, 4, 5, 8))
        for yy in [6, 8, 10]:
            pygame.draw.line(surface, (170, 175, 180), (x + 10, yy), (x + 15, yy))
        pygame.draw.rect(surface, (150, 155, 160), (x + 10, 3, 5, 1))
    elif gid == GID_NANHU_LOBBY_LIGHT:
        surface.fill((230, 230, 235), rect)
        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.ellipse(overlay, (255, 240, 180, 80), (4, 4, 8, 8))
        surface.blit(overlay, (x, 0))
        pygame.draw.circle(surface, (255, 250, 200), (x + 7, 7), 2)


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
    _place_school_gate(ground, structures, collision, interactive_objects, trigger_objects)
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
    gate_x_start = 57
    gate_x_end = 62
    for x in range(MAP_WIDTH):
        for row in [0, 1, MAP_HEIGHT - 2, MAP_HEIGHT - 1]:
            if row >= MAP_HEIGHT - 4 and gate_x_start <= x <= gate_x_end:
                continue
            structures[row][x] = GID_TREE_GREEN
            collision[row][x] = GID_COLLISION
    for y in range(MAP_HEIGHT):
        for col in [0, 1, MAP_WIDTH - 2, MAP_WIDTH - 1]:
            structures[y][col] = GID_TREE_GREEN
            collision[y][col] = GID_COLLISION
    for x in range(2, MAP_WIDTH - 2, 3):
        if not (gate_x_start <= x <= gate_x_end):
            structures[MAP_HEIGHT - 3][x] = GID_TREE_GREEN
            collision[MAP_HEIGHT - 3][x] = GID_COLLISION
        structures[2][x] = GID_TREE_GREEN
        collision[2][x] = GID_COLLISION
    for y in range(2, MAP_HEIGHT - 2, 3):
        structures[y][2] = GID_TREE_GREEN
        collision[y][2] = GID_COLLISION
        structures[y][MAP_WIDTH - 3] = GID_TREE_GREEN
        collision[y][MAP_WIDTH - 3] = GID_COLLISION


def _place_school_gate(ground, structures, collision, interactive_objects, trigger_objects):
    gx = 57
    gy = 76

    structures[gy + 3][gx] = GID_GATE_PILLAR
    collision[gy + 3][gx] = GID_COLLISION
    structures[gy + 3][gx + 5] = GID_GATE_PILLAR
    collision[gy + 3][gx + 5] = GID_COLLISION
    structures[gy + 2][gx] = GID_GATE_PILLAR
    collision[gy + 2][gx] = GID_COLLISION
    structures[gy + 2][gx + 5] = GID_GATE_PILLAR
    collision[gy + 2][gx + 5] = GID_COLLISION

    structures[gy + 1][gx] = GID_GATE_BEAM
    collision[gy + 1][gx] = GID_COLLISION
    structures[gy + 1][gx + 5] = GID_GATE_BEAM
    collision[gy + 1][gx + 5] = GID_COLLISION
    structures[gy + 1][gx + 1] = GID_GATE_SIGN
    structures[gy + 1][gx + 2] = GID_GATE_SIGN
    structures[gy + 1][gx + 3] = GID_GATE_SIGN
    structures[gy + 1][gx + 4] = GID_GATE_SIGN

    for y in range(gy, gy + 4):
        for x in range(gx + 1, gx + 5):
            ground[y][x] = GID_PATH_STONE

    for y in range(gy - 1, gy + 4):
        for x in range(gx - 2, gx):
            if structures[y][x] == GID_EMPTY and collision[y][x] == GID_EMPTY:
                structures[y][x] = GID_TREE_GREEN
                collision[y][x] = GID_COLLISION
        for x in range(gx + 6, gx + 8):
            if structures[y][x] == GID_EMPTY and collision[y][x] == GID_EMPTY:
                structures[y][x] = GID_TREE_GREEN
                collision[y][x] = GID_COLLISION

    interactive_objects.append({
        "x": (gx + 1) * TILE_SIZE,
        "y": (gy + 1) * TILE_SIZE,
        "width": 4 * TILE_SIZE,
        "height": TILE_SIZE,
        "type": "school_gate",
        "properties": {
            "interactive_type": "examine",
            "display_name": "校门牌匾",
            "desc": "华中师范大学——桂子山校区"
        }
    })

    trigger_objects.append({
        "x": (gx + 1) * TILE_SIZE,
        "y": (gy - 1) * TILE_SIZE,
        "width": 4 * TILE_SIZE,
        "height": 1 * TILE_SIZE,
        "type": "spawn",
        "properties": {
            "spawn_id": "gate",
        }
    })

    for y in range(gy - 1, 42, -1):
        for x in range(gx + 1, gx + 5):
            if ground[y][x] == GID_GRASS:
                ground[y][x] = GID_PATH_STONE


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
            "transition_type": "indoor_enter",
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

    # 填充图书馆墙壁
    for y in range(by, by + bh):
        for x in range(bx, bx + bw):
            structures[y][x] = GID_LIB_WALL
            collision[y][x] = GID_COLLISION

    # 平顶屋顶（2行）
    for x in range(bx, bx + bw):
        structures[by][x] = GID_LIB_ROOF
        if by + 1 < by + bh:
            structures[by + 1][x] = GID_LIB_ROOF

    # 大落地窗布局：从第3行开始，每2行一组窗户，每3列一个窗
    for y in range(by + 2, by + bh - 1):
        for x in range(bx + 1, bx + bw - 1):
            if (y - by) % 2 == 0 and (x - bx) % 3 == 1:
                structures[y][x] = GID_LIB_WINDOW
            else:
                structures[y][x] = GID_LIB_WALL

    # 入口立柱（门两侧）
    door_x = bx + 6
    door_y = by + bh - 1
    structures[door_y][door_x - 1] = GID_LIB_PILLAR
    structures[door_y][door_x + 2] = GID_LIB_PILLAR

    # 雨棚（门上方1行）
    if door_y - 1 > by + 1:
        structures[door_y - 1][door_x] = GID_LIB_AWNING
        structures[door_y - 1][door_x + 1] = GID_LIB_AWNING

    # 牌匾（屋顶下方第3行，居中3格）
    sign_y = by + 2
    sign_center = bx + bw // 2
    structures[sign_y][sign_center - 1] = GID_LIB_SIGN_SIDE
    structures[sign_y][sign_center] = GID_LIB_SIGN
    structures[sign_y][sign_center + 1] = GID_LIB_SIGN_SIDE

    # 玻璃门
    structures[door_y][door_x] = GID_LIB_DOOR
    collision[door_y][door_x] = GID_EMPTY
    structures[door_y][door_x + 1] = GID_LIB_DOOR
    collision[door_y][door_x + 1] = GID_EMPTY

    # 门前石板路
    for y in range(by + bh, 36):
        for x in range(bx + 6, bx + 8):
            ground[y][x] = GID_PATH_STONE
    for x in range(bx - 1, bx + bw + 1):
        ground[by + bh][x] = GID_PATH_STONE
        ground[by + bh + 1][x] = GID_PATH_STONE

    # 互动对象和触发区
    interactive_objects.append({
        "x": door_x * TILE_SIZE,
        "y": door_y * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": TILE_SIZE,
        "type": "building_entrance",
        "properties": {
            "interactive_type": "enter",
            "display_name": "图书馆入口",
            "target_map": "library_f1",
            "spawn_point": "library_entrance",
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
            "target_map": "library_f1",
            "spawn_point": "library_entrance",
        }
    })
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

    # 填充体育馆墙壁
    for y in range(by, by + bh):
        for x in range(bx, bx + bw):
            structures[y][x] = GID_GYM_WALL
            collision[y][x] = GID_COLLISION

    # 弧形屋顶：中间2行高，两侧1行
    for x in range(bx, bx + bw):
        structures[by][x] = GID_GYM_ROOF_SIDE
    # 中间部分用中心屋顶
    for x in range(bx + 2, bx + bw - 2):
        if by + 1 < by + bh:
            structures[by + 1][x] = GID_GYM_ROOF_CENTER
    # 两侧保持侧面屋顶
    structures[by + 1][bx] = GID_GYM_ROOF_SIDE
    structures[by + 1][bx + 1] = GID_GYM_ROOF_SIDE
    structures[by + 1][bx + bw - 2] = GID_GYM_ROOF_SIDE
    structures[by + 1][bx + bw - 1] = GID_GYM_ROOF_SIDE

    # 窄长横窗：墙面上部每隔2列
    for y in range(by + 2, by + 4):
        for x in range(bx + 1, bx + bw - 1):
            if (x - bx) % 2 == 1:
                structures[y][x] = GID_GYM_WINDOW
            else:
                structures[y][x] = GID_GYM_WALL

    # 通风口（屋顶下方两侧）
    structures[by + 2][bx + 1] = GID_GYM_VENT
    structures[by + 2][bx + bw - 2] = GID_GYM_VENT

    # 牌匾
    sign_y = by + 4
    sign_center = bx + bw // 2
    structures[sign_y][sign_center - 1] = GID_GYM_SIGN
    structures[sign_y][sign_center] = GID_GYM_SIGN
    structures[sign_y][sign_center + 1] = GID_GYM_SIGN

    # 主入口（3格宽）
    door_y = by + bh - 1
    door_center = bx + bw // 2
    structures[door_y][door_center - 1] = GID_GYM_DOOR_SIDE
    structures[door_y][door_center] = GID_GYM_DOOR_MAIN
    structures[door_y][door_center + 1] = GID_GYM_DOOR_SIDE
    collision[door_y][door_center - 1] = GID_EMPTY
    collision[door_y][door_center] = GID_EMPTY
    collision[door_y][door_center + 1] = GID_EMPTY

    # 门前路
    for y in range(42, by):
        for x in range(bx + 7, bx + 9):
            ground[y][x] = GID_PATH_STONE
    for x in range(bx - 1, bx + bw + 1):
        ground[by - 1][x] = GID_PATH_STONE
        ground[by - 2][x] = GID_PATH_STONE

    # 互动对象和触发区
    interactive_objects.append({
        "x": (door_center - 1) * TILE_SIZE,
        "y": door_y * TILE_SIZE,
        "width": 3 * TILE_SIZE,
        "height": TILE_SIZE,
        "type": "building_entrance",
        "properties": {
            "interactive_type": "enter",
            "display_name": "佑铭体育馆入口",
            "target_map": "gym",
            "spawn_point": "gym_entrance",
            "transition_type": "indoor_enter",
        }
    })
    trigger_objects.append({
        "x": (door_center - 1) * TILE_SIZE,
        "y": door_y * TILE_SIZE,
        "width": 3 * TILE_SIZE,
        "height": TILE_SIZE,
        "type": "door_trigger",
        "properties": {
            "target_map": "gym",
            "spawn_point": "gym_entrance",
        }
    })
    _add_exit_spawn(trigger_objects, "gym_exit", bx + 7, by + bh + 1)


def _place_dining_hall(ground, structures, collision, interactive_objects, trigger_objects):
    bx, by, bw, bh = 89, 49, 12, 10

    # 填充食堂墙壁
    for y in range(by, by + bh):
        for x in range(bx, bx + bw):
            structures[y][x] = GID_DINING_WALL
            collision[y][x] = GID_COLLISION

    # 深红色坡屋顶（2行）
    for x in range(bx, bx + bw):
        structures[by][x] = GID_DINING_ROOF
        if by + 1 < by + bh:
            structures[by + 1][x] = GID_DINING_ROOF

    # 烟囱（屋顶右侧）
    structures[by][bx + bw - 3] = GID_DINING_CHIMNEY

    # 方形大窗（暖黄光）
    for y in range(by + 2, by + bh - 1):
        for x in range(bx + 1, bx + bw - 1):
            if (y - by) % 3 == 0 and (x - bx) % 3 == 1:
                structures[y][x] = GID_DINING_WINDOW
            else:
                structures[y][x] = GID_DINING_WALL

    # 牌匾
    sign_y = by + 2
    sign_center = bx + bw // 2
    structures[sign_y][sign_center - 1] = GID_DINING_SIGN
    structures[sign_y][sign_center] = GID_DINING_SIGN
    structures[sign_y][sign_center + 1] = GID_DINING_SIGN

    # 菜单牌（门旁）
    door_x = bx + 5
    door_y = by + bh - 1
    structures[door_y][door_x + 2] = GID_DINING_MENU

    # 遮阳棚（门上方）
    if door_y - 1 > by + 1:
        for dx in range(4):
            if door_x + dx < bx + bw:
                structures[door_y - 1][door_x + dx] = GID_DINING_AWNING

    # 双开门
    structures[door_y][door_x] = GID_DINING_DOOR
    collision[door_y][door_x] = GID_EMPTY
    structures[door_y][door_x + 1] = GID_DINING_DOOR
    collision[door_y][door_x + 1] = GID_EMPTY

    # 门前路
    for y in range(42, by):
        for x in range(bx + 5, bx + 7):
            ground[y][x] = GID_PATH_STONE
    for x in range(bx - 1, bx + bw + 1):
        ground[by - 1][x] = GID_PATH_STONE
        ground[by - 2][x] = GID_PATH_STONE

    # 互动对象和触发区
    interactive_objects.append({
        "x": door_x * TILE_SIZE,
        "y": door_y * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": TILE_SIZE,
        "type": "building_entrance",
        "properties": {
            "interactive_type": "enter",
            "display_name": "学子食堂入口",
            "target_map": "dining_hall_f1",
            "spawn_point": "dining_entrance",
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
            "target_map": "dining_hall_f1",
            "spawn_point": "dining_entrance",
        }
    })
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
    # 喷泉区域：structures层设为空（喷泉外观由精灵渲染）
    for dy in range(6):
        for dx in range(6):
            structures[fy + dy][fx + dx] = GID_EMPTY
    # 碰撞区域：仅底座核心部分（4×3 tiles），留出外围1格供玩家靠近交互
    # 底座在精灵中偏下方，对应 tile 区域为 (fx+1, fy+2) 到 (fx+4, fy+4)
    for dy in range(2, 5):
        for dx in range(1, 5):
            collision[fy + dy][fx + dx] = GID_COLLISION

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
            "prompt_text": "乘校车",
            "desc": "前往南湖校区的校车",
            "target_map": "nanhu_campus",
            "spawn_point": "nanhu_entrance",
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
        "y": 75 * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": 1 * TILE_SIZE,
        "type": "spawn",
        "properties": {
            "spawn_id": "default",
        }
    })
    trigger_objects.append({
        "x": 58 * TILE_SIZE,
        "y": 68 * TILE_SIZE,
        "width": 2 * TILE_SIZE,
        "height": 2 * TILE_SIZE,
        "type": "spawn",
        "properties": {
            "spawn_id": "shuttle_return",
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

    # 为所有 tile 创建元素，确保 pytmx 正确分配 images 数组
    solid_local_ids = set(gid - 1 for gid in SOLID_GIDS)
    for local_id in range(TILE_COUNT):
        tile_elem = ET.SubElement(tileset, "tile")
        tile_elem.set("id", str(local_id))
        if local_id in solid_local_ids:
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
