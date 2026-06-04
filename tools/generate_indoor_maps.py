import os
import sys
import random
import pygame
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TILE_SIZE

GID_EMPTY = 0
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
GID_COLLISION = 20
GID_KITCHEN_FLOOR = 21
GID_RUG = 22
GID_BLACKBOARD = 23
GID_PLANT_INDOOR = 24
# 图书馆室内专属 tile
GID_LIB_WALL = 25        # 图书馆墙壁（暖黄+木纹护墙板）
GID_LIB_WALL_TOP = 26    # 图书馆墙壁顶部
GID_LIB_FLOOR = 27       # 图书馆深色木地板
GID_LIB_READING_LAMP = 28 # 图书馆阅读灯
# 体育馆室内专属 tile
GID_GYM_WALL = 29        # 体育馆墙壁（白色+蓝色条纹）
GID_GYM_WALL_TOP = 30    # 体育馆墙壁顶部
GID_GYM_LOCKER = 31      # 体育馆更衣柜
# 食堂室内专属 tile
GID_DINING_WALL = 32     # 食堂墙壁（白色+橙色腰线）
GID_DINING_WALL_TOP = 33 # 食堂墙壁顶部
GID_DINING_SERVING = 34  # 食堂取餐窗口
# 综合楼室内专属 tile
GID_NANHU_WALL = 35      # 综合楼墙壁（纯白+灰色踢脚线）
GID_NANHU_WALL_TOP = 36  # 综合楼墙壁顶部
GID_NANHU_FLOOR = 37     # 综合楼灰色大理石地面
GID_NANHU_ELEVATOR = 38  # 综合楼电梯门
# 密室专属 tile
GID_SECRET_WALL = 39     # 密室深色石墙
GID_SECRET_WALL_TOP = 40 # 密室墙壁顶部
GID_SECRET_FLOOR = 41    # 密室碎石地面
GID_SECRET_RUNE = 42     # 密室符文墙
GID_SECRET_TORCH = 43    # 密室火把
GID_OFFICE_DESK = 44     # 办公桌+电脑一体
GID_LARGE_DESK_L = 45   # 大办公桌左半（抽屉柜+桌面物品）
GID_LARGE_DESK_R = 46   # 大办公桌右半（显示器+键盘）

TILE_COUNT = 46

SOLID_GIDS = {
    GID_INDOOR_WALL, GID_INDOOR_WALL_TOP, GID_BOOKSHELF, GID_BOOKSHELF_TOP,
    GID_TABLE, GID_CHAIR, GID_COUNTER, GID_FRIDGE,
    GID_HOOP, GID_SCOREBOARD, GID_COMPUTER,
    GID_BLACKBOARD, GID_PLANT_INDOOR, GID_COLLISION,
    GID_LIB_WALL, GID_LIB_WALL_TOP, GID_LIB_READING_LAMP,
    GID_GYM_WALL, GID_GYM_WALL_TOP, GID_GYM_LOCKER,
    GID_DINING_WALL, GID_DINING_WALL_TOP, GID_DINING_SERVING,
    GID_NANHU_WALL, GID_NANHU_WALL_TOP, GID_NANHU_ELEVATOR,
    GID_SECRET_WALL, GID_SECRET_WALL_TOP, GID_SECRET_RUNE, GID_SECRET_TORCH,
    GID_OFFICE_DESK, GID_LARGE_DESK_L, GID_LARGE_DESK_R,
}


def create_tileset(output_path):
    pygame.init()
    surface = pygame.Surface((TILE_COUNT * TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)

    for i in range(1, TILE_COUNT + 1):
        x = (i - 1) * TILE_SIZE
        _draw_tile(surface, i, x)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pygame.image.save(surface, output_path)
    pygame.quit()
    print(f"Indoor tileset saved to {output_path}")


def _draw_tile(surface, gid, x):
    rect = pygame.Rect(x, 0, TILE_SIZE, TILE_SIZE)
    if gid == GID_WOOD_FLOOR:
        surface.fill((180, 140, 90), rect)
        for row in range(4):
            yy = row * 4
            pygame.draw.line(surface, (160, 120, 70), (x, yy), (x + TILE_SIZE, yy))
            offset = 8 if row % 2 == 0 else 0
            for bx in range(offset, TILE_SIZE, 8):
                pygame.draw.line(surface, (160, 120, 70), (x + bx, yy), (x + bx, yy + 4))
        for dx, dy in [(3, 2), (11, 6), (7, 11), (14, 14)]:
            surface.set_at((x + dx, dy), (170, 130, 80))
    elif gid == GID_WOOD_FLOOR2:
        surface.fill((175, 135, 85), rect)
        for row in range(4):
            yy = row * 4
            pygame.draw.line(surface, (155, 115, 65), (x, yy), (x + TILE_SIZE, yy))
            offset = 0 if row % 2 == 0 else 8
            for bx in range(offset, TILE_SIZE, 8):
                pygame.draw.line(surface, (155, 115, 65), (x + bx, yy), (x + bx, yy + 4))
    elif gid == GID_TILE_FLOOR:
        surface.fill((200, 200, 200), rect)
        pygame.draw.line(surface, (180, 180, 180), (x, 0), (x + TILE_SIZE, 0))
        pygame.draw.line(surface, (180, 180, 180), (x, 8), (x + TILE_SIZE, 8))
        pygame.draw.line(surface, (180, 180, 180), (x, 0), (x, TILE_SIZE))
        pygame.draw.line(surface, (180, 180, 180), (x + 8, 0), (x + 8, TILE_SIZE))
        for dx, dy in [(2, 3), (10, 5), (5, 12), (13, 11)]:
            surface.set_at((x + dx, dy), (190, 190, 190))
    elif gid == GID_CARPET_RED:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (140, 30, 30), (x + 1, 1, 14, 14))
        pygame.draw.rect(surface, (160, 40, 40), (x + 2, 2, 12, 12))
        pygame.draw.rect(surface, (180, 50, 50), (x + 3, 3, 10, 10))
        pygame.draw.rect(surface, (140, 30, 30), (x + 5, 5, 6, 6))
    elif gid == GID_INDOOR_WALL:
        surface.fill((220, 210, 190), rect)
        pygame.draw.line(surface, (190, 180, 160), (x, TILE_SIZE - 1), (x + TILE_SIZE, TILE_SIZE - 1))
        for bx in range(0, TILE_SIZE, 8):
            pygame.draw.line(surface, (200, 190, 170), (x + bx, 0), (x + bx, TILE_SIZE))
    elif gid == GID_INDOOR_WALL_TOP:
        surface.fill((220, 210, 190), rect)
        pygame.draw.rect(surface, (200, 190, 170), (x, 0, TILE_SIZE, 3))
        pygame.draw.line(surface, (190, 180, 160), (x, TILE_SIZE - 1), (x + TILE_SIZE, TILE_SIZE - 1))
    elif gid == GID_BOOKSHELF:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x + 1, 0, 14, TILE_SIZE))
        for row in range(4):
            yy = row * 4
            pygame.draw.line(surface, (80, 50, 25), (x + 1, yy), (x + 15, yy))
            colors = [(180, 50, 50), (50, 50, 180), (50, 140, 50), (180, 140, 50)]
            for bx in range(2, 14, 3):
                c = colors[(bx + row) % 4]
                pygame.draw.rect(surface, c, (x + bx, yy + 1, 2, 3))
    elif gid == GID_BOOKSHELF_TOP:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x + 1, 0, 14, 6))
        pygame.draw.rect(surface, (120, 80, 40), (x + 1, 6, 14, 3))
        pygame.draw.line(surface, (80, 50, 25), (x + 1, 0), (x + 15, 0))
        pygame.draw.line(surface, (80, 50, 25), (x + 1, 6), (x + 15, 6))
        pygame.draw.line(surface, (80, 50, 25), (x + 1, 9), (x + 15, 9))
    elif gid == GID_TABLE:
        surface.fill((180, 140, 90), rect)
        # 桌面（与 dining_table 精灵配色一致）
        pygame.draw.rect(surface, (160, 110, 60), (x + 2, 4, 12, 4))
        pygame.draw.rect(surface, (180, 130, 70), (x + 3, 4, 10, 3))
        # 桌面高光线
        pygame.draw.line(surface, (200, 150, 80), (x + 4, 5), (x + 12, 5))
        # 桌腿
        pygame.draw.rect(surface, (130, 90, 45), (x + 3, 8, 2, 7))
        pygame.draw.rect(surface, (130, 90, 45), (x + 11, 8, 2, 7))
        # 桌腿内侧高光
        surface.set_at((x + 4, 9), (150, 105, 55))
        surface.set_at((x + 12, 9), (150, 105, 55))
        # 桌上餐具：盘子
        surface.set_at((x + 6, 5), (200, 200, 200))
        surface.set_at((x + 7, 5), (200, 200, 200))
        surface.set_at((x + 6, 4), (220, 220, 220))
        # 桌上餐具：杯子
        surface.set_at((x + 10, 5), (180, 180, 180))
        surface.set_at((x + 10, 4), (200, 200, 220))
    elif gid == GID_CHAIR:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (120, 80, 40), (x + 4, 6, 8, 6))
        pygame.draw.rect(surface, (100, 65, 30), (x + 4, 4, 8, 3))
        pygame.draw.rect(surface, (100, 65, 30), (x + 5, 12, 2, 3))
        pygame.draw.rect(surface, (100, 65, 30), (x + 9, 12, 2, 3))
    elif gid == GID_COUNTER:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (160, 160, 160), (x, 4, TILE_SIZE, 8))
        pygame.draw.rect(surface, (140, 140, 140), (x, 3, TILE_SIZE, 2))
        pygame.draw.rect(surface, (130, 130, 130), (x, 12, TILE_SIZE, 2))
        pygame.draw.rect(surface, (100, 100, 100), (x + 1, 5, 3, 5))
        pygame.draw.rect(surface, (100, 100, 100), (x + 12, 5, 3, 5))
    elif gid == GID_FRIDGE:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (200, 200, 210), (x + 2, 1, 12, 14))
        pygame.draw.rect(surface, (180, 180, 190), (x + 2, 1, 12, 14), 1)
        pygame.draw.line(surface, (160, 160, 170), (x + 2, 8), (x + 14, 8))
        pygame.draw.rect(surface, (150, 150, 160), (x + 12, 3, 1, 3))
        pygame.draw.rect(surface, (150, 150, 160), (x + 12, 10, 1, 3))
    elif gid == GID_STAIRS_DOWN:
        surface.fill((180, 140, 90), rect)
        for i in range(4):
            step_y = i * 4
            step_w = TILE_SIZE - i * 4
            pygame.draw.rect(surface, (160, 120, 70), (x, step_y, step_w, 4))
            pygame.draw.line(surface, (140, 100, 55), (x, step_y + 3), (x + step_w, step_y + 3))
        pygame.draw.rect(surface, (120, 80, 40), (x, 0, TILE_SIZE, TILE_SIZE), 1)
    elif gid == GID_STAIRS_UP:
        surface.fill((180, 140, 90), rect)
        for i in range(4):
            step_y = TILE_SIZE - (i + 1) * 4
            step_w = TILE_SIZE - i * 4
            pygame.draw.rect(surface, (160, 120, 70), (x, step_y, step_w, 4))
            pygame.draw.line(surface, (140, 100, 55), (x, step_y + 3), (x + step_w, step_y + 3))
        pygame.draw.rect(surface, (120, 80, 40), (x, 0, TILE_SIZE, TILE_SIZE), 1)
    elif gid == GID_COURT_FLOOR:
        surface.fill((200, 160, 100), rect)
        pygame.draw.line(surface, (180, 140, 80), (x, 0), (x + TILE_SIZE, 0))
        pygame.draw.line(surface, (180, 140, 80), (x, TILE_SIZE - 1), (x + TILE_SIZE, TILE_SIZE - 1))
        pygame.draw.line(surface, (220, 180, 120), (x + 8, 0), (x + 8, TILE_SIZE))
        pygame.draw.arc(surface, (220, 180, 120), (x, 0, TILE_SIZE, TILE_SIZE), 0, 3.14, 1)
    elif gid == GID_HOOP:
        # 篮球框：篮板+篮筐+篮网
        surface.fill((0, 0, 0, 0), rect)
        # 篮板（白色矩形）
        pygame.draw.rect(surface, (240, 240, 245), (x + 3, 0, 10, 8))
        pygame.draw.rect(surface, (200, 200, 210), (x + 3, 0, 10, 8), 1)
        # 篮筐（红色圆环）
        pygame.draw.rect(surface, (200, 60, 30), (x + 4, 8, 8, 2))
        # 篮网（白色线条）
        for nx in range(5, 11, 2):
            pygame.draw.line(surface, (230, 230, 230), (x + nx, 10), (x + nx, 14))
        pygame.draw.line(surface, (230, 230, 230), (x + 5, 14), (x + 9, 14))
    elif gid == GID_SCOREBOARD:
        # 使用墙壁背景色，让精灵覆盖显示
        surface.fill((240, 240, 245), rect)
        pygame.draw.rect(surface, (220, 220, 225), (x, 0, TILE_SIZE, 3))
        pygame.draw.rect(surface, (40, 80, 160), (x, 5, TILE_SIZE, 2))
    elif gid == GID_COMPUTER:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (60, 60, 60), (x + 2, 1, 12, 9))
        pygame.draw.rect(surface, (80, 120, 180), (x + 3, 2, 10, 7))
        pygame.draw.rect(surface, (60, 60, 60), (x + 6, 10, 4, 2))
        pygame.draw.rect(surface, (80, 80, 80), (x + 4, 12, 8, 2))
        for dx, dy in [(5, 4), (8, 3), (11, 5)]:
            surface.set_at((x + dx, dy), (150, 200, 255))
    elif gid == GID_DOOR_INDOOR:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x + 3, 1, 10, 14))
        pygame.draw.rect(surface, (80, 50, 25), (x + 3, 1, 10, 14), 1)
        pygame.draw.circle(surface, (200, 180, 50), (x + 11, 8), 1)
    elif gid == GID_COLLISION:
        surface.fill((180, 140, 90), rect)
        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 60))
        surface.blit(overlay, (x, 0))
    elif gid == GID_KITCHEN_FLOOR:
        surface.fill((210, 210, 200), rect)
        for row in range(4):
            for col in range(4):
                if (row + col) % 2 == 0:
                    pygame.draw.rect(surface, (190, 190, 180), (x + col * 4, row * 4, 4, 4))
        pygame.draw.line(surface, (170, 170, 160), (x, 0), (x + TILE_SIZE, 0))
        pygame.draw.line(surface, (170, 170, 160), (x, 0), (x, TILE_SIZE))
    elif gid == GID_RUG:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (100, 60, 30), (x + 1, 1, 14, 14))
        pygame.draw.rect(surface, (130, 80, 40), (x + 2, 2, 12, 12))
        pygame.draw.rect(surface, (160, 100, 50), (x + 4, 4, 8, 8))
        for dx, dy in [(5, 5), (9, 5), (5, 9), (9, 9)]:
            surface.set_at((x + dx, dy), (180, 120, 60))
    elif gid == GID_BLACKBOARD:
        surface.fill((180, 140, 90), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x, 0, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, (30, 80, 30), (x + 1, 1, 14, 12))
        pygame.draw.rect(surface, (101, 67, 33), (x, 13, TILE_SIZE, 3))
        for dx, dy in [(3, 4), (7, 6), (11, 3), (5, 9)]:
            surface.set_at((x + dx, dy), (200, 200, 200))
    elif gid == GID_PLANT_INDOOR:
        # 透明背景，适配任何地面颜色
        surface.fill((0, 0, 0, 0), rect)
        # 花盆
        pygame.draw.rect(surface, (160, 100, 50), (x + 5, 10, 6, 5))
        # 植物冠
        pygame.draw.circle(surface, (34, 139, 34), (x + 8, 7), 5)
        pygame.draw.circle(surface, (50, 160, 50), (x + 6, 6), 3)
        pygame.draw.circle(surface, (0, 120, 0), (x + 10, 8), 2)
    # 图书馆室内专属 tile
    elif gid == GID_LIB_WALL:
        surface.fill((220, 200, 160), rect)
        pygame.draw.line(surface, (180, 150, 100), (x, 10), (x + TILE_SIZE, 10))
        for yy in range(10, TILE_SIZE):
            for xx in range(TILE_SIZE):
                surface.set_at((x + xx, yy), (200, 180, 140))
        for bx in [4, 8, 12]:
            pygame.draw.line(surface, (190, 170, 130), (x + bx, 10), (x + bx, TILE_SIZE))
    elif gid == GID_LIB_WALL_TOP:
        surface.fill((220, 200, 160), rect)
        pygame.draw.rect(surface, (190, 170, 130), (x, 0, TILE_SIZE, 3))
        pygame.draw.line(surface, (180, 150, 100), (x, 15), (x + TILE_SIZE, 15))
    elif gid == GID_LIB_FLOOR:
        surface.fill((120, 80, 45), rect)
        for yy in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (100, 65, 35), (x, yy), (x + TILE_SIZE, yy))
        offset = 0
        for yy in range(0, TILE_SIZE, 4):
            for bx in range(offset, TILE_SIZE, 8):
                pygame.draw.line(surface, (105, 70, 38), (x + bx, yy), (x + bx, yy + 4))
            offset = 8 if offset == 0 else 0
        for dx, dy in [(3, 3), (11, 7), (7, 13)]:
            surface.set_at((x + dx, dy), (110, 75, 40))
    elif gid == GID_LIB_READING_LAMP:
        surface.fill((120, 80, 45), rect)
        # 灯柱
        pygame.draw.rect(surface, (80, 80, 80), (x + 7, 6, 2, 8))
        # 灯罩（三角形）
        pygame.draw.polygon(surface, (200, 180, 50),
                            [(x + 5, 3), (x + 10, 3), (x + 7, 1)])
        # 暖光光晕
        glow = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 180, 80), (3, 3), 3)
        surface.blit(glow, (x + 5, 5))
    # 体育馆室内专属 tile
    elif gid == GID_GYM_WALL:
        surface.fill((240, 240, 245), rect)
        pygame.draw.rect(surface, (40, 80, 160), (x, 5, TILE_SIZE, 2))
        pygame.draw.rect(surface, (40, 80, 160), (x, 12, TILE_SIZE, 2))
        pygame.draw.line(surface, (230, 230, 235), (x + 8, 0), (x + 8, TILE_SIZE))
    elif gid == GID_GYM_WALL_TOP:
        surface.fill((240, 240, 245), rect)
        pygame.draw.rect(surface, (220, 220, 225), (x, 0, TILE_SIZE, 3))
        pygame.draw.rect(surface, (40, 80, 160), (x, 5, TILE_SIZE, 2))
    elif gid == GID_GYM_LOCKER:
        surface.fill((240, 240, 245), rect)
        # 更衣柜主体
        pygame.draw.rect(surface, (180, 180, 190), (x + 2, 1, 12, 14))
        # 三扇柜门
        pygame.draw.rect(surface, (160, 160, 170), (x + 2, 1, 3, 13))
        pygame.draw.rect(surface, (160, 160, 170), (x + 6, 1, 4, 13))
        pygame.draw.rect(surface, (160, 160, 170), (x + 11, 1, 3, 13))
        # 把手
        for hx in [x + 4, x + 9, x + 13]:
            surface.set_at((hx, 7), (200, 200, 210))
            surface.set_at((hx, 8), (200, 200, 210))
        # 通风槽
        for vy in [3, 5]:
            for vx in range(x + 3, x + 14):
                if vx % 2 == 0:
                    surface.set_at((vx, vy), (150, 150, 160))
    # 食堂室内专属 tile
    elif gid == GID_DINING_WALL:
        surface.fill((245, 245, 245), rect)
        pygame.draw.rect(surface, (230, 130, 50), (x, 8, TILE_SIZE, 2))
        pygame.draw.line(surface, (235, 235, 235), (x + 8, 0), (x + 8, TILE_SIZE))
    elif gid == GID_DINING_WALL_TOP:
        surface.fill((245, 245, 245), rect)
        pygame.draw.rect(surface, (225, 225, 225), (x, 0, TILE_SIZE, 3))
        pygame.draw.rect(surface, (230, 130, 50), (x, 8, TILE_SIZE, 2))
    elif gid == GID_DINING_SERVING:
        surface.fill((245, 245, 245), rect)
        # 取餐窗口开口
        pygame.draw.rect(surface, (240, 230, 200), (x + 1, 2, 14, 8))
        # 不锈钢边框
        pygame.draw.rect(surface, (180, 180, 190), (x + 1, 2, 14, 8), 1)
        # 台面
        pygame.draw.rect(surface, (200, 200, 210), (x + 1, 10, 14, 3))
        # 餐盘痕迹
        for dx in [3, 7, 11]:
            pygame.draw.rect(surface, (220, 200, 160), (x + dx, 5, 2, 2))
    # 综合楼室内专属 tile
    elif gid == GID_NANHU_WALL:
        surface.fill((240, 240, 242), rect)
        pygame.draw.rect(surface, (180, 180, 185), (x, 13, TILE_SIZE, 3))
        pygame.draw.line(surface, (235, 235, 237), (x + 8, 0), (x + 8, TILE_SIZE))
    elif gid == GID_NANHU_WALL_TOP:
        surface.fill((240, 240, 242), rect)
        pygame.draw.rect(surface, (225, 225, 228), (x, 0, TILE_SIZE, 3))
        pygame.draw.rect(surface, (180, 180, 185), (x, 13, TILE_SIZE, 3))
    elif gid == GID_NANHU_FLOOR:
        surface.fill((195, 195, 200), rect)
        # 大理石纹路
        pygame.draw.line(surface, (185, 185, 190), (x + 2, 2), (x + 8, 8))
        pygame.draw.line(surface, (185, 185, 190), (x + 10, 4), (x + 14, 12))
        pygame.draw.line(surface, (190, 190, 195), (x + 8, 0), (x + 8, TILE_SIZE))
        pygame.draw.line(surface, (190, 190, 195), (x, 8), (x + TILE_SIZE, 8))
    elif gid == GID_NANHU_ELEVATOR:
        surface.fill((240, 240, 242), rect)
        # 电梯门
        pygame.draw.rect(surface, (200, 200, 205), (x + 2, 1, 12, 14))
        # 中缝
        pygame.draw.line(surface, (170, 170, 175), (x + 8, 1), (x + 8, 15))
        # 指示灯
        pygame.draw.rect(surface, (0, 180, 0), (x + 7, 2, 2, 2))
        # 按钮面板
        pygame.draw.rect(surface, (160, 160, 165), (x + 13, 6, 1, 3))
        # 门框
        pygame.draw.rect(surface, (170, 170, 175), (x + 2, 1, 12, 14), 1)
    # 密室专属 tile
    elif gid == GID_SECRET_WALL:
        surface.fill((70, 65, 60), rect)
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (55, 50, 45), (x, yy), (x + TILE_SIZE, yy))
        for bx in [4, 12]:
            pygame.draw.line(surface, (55, 50, 45), (x + bx, 0), (x + bx, 4))
        for bx in [8]:
            pygame.draw.line(surface, (55, 50, 45), (x + bx, 4), (x + bx, 8))
        for bx in [4, 12]:
            pygame.draw.line(surface, (55, 50, 45), (x + bx, 8), (x + bx, 12))
        # 裂缝
        pygame.draw.line(surface, (60, 55, 50), (x + 5, 6), (x + 7, 9))
    elif gid == GID_SECRET_WALL_TOP:
        surface.fill((70, 65, 60), rect)
        pygame.draw.rect(surface, (55, 50, 45), (x, 0, TILE_SIZE, 3))
        for yy in [4, 8]:
            pygame.draw.line(surface, (55, 50, 45), (x, yy), (x + TILE_SIZE, yy))
    elif gid == GID_SECRET_FLOOR:
        surface.fill((110, 100, 85), rect)
        # 散落碎石
        for dx, dy in [(2, 3), (7, 1), (12, 5), (4, 9), (10, 11), (14, 13), (1, 13)]:
            surface.set_at((x + dx, dy), (95, 85, 70))
        for dx, dy in [(5, 6), (9, 8), (13, 3), (3, 12)]:
            surface.set_at((x + dx, dy), (120, 110, 95))
        for dx, dy in [(6, 4), (11, 10), (2, 8)]:
            surface.set_at((x + dx, dy), (100, 90, 75))
    elif gid == GID_SECRET_RUNE:
        surface.fill((70, 65, 60), rect)
        # 砖缝
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (55, 50, 45), (x, yy), (x + TILE_SIZE, yy))
        # 发光符文
        glow = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(glow, (50, 180, 80, 60), (8, 8), 4)
        surface.blit(glow, (x, 0))
        pygame.draw.circle(surface, (50, 180, 80), (x + 8, 8), 4, 1)
        # 内部图案
        pygame.draw.line(surface, (80, 220, 100), (x + 6, 6), (x + 10, 6))
        pygame.draw.line(surface, (80, 220, 100), (x + 8, 4), (x + 8, 12))
    elif gid == GID_SECRET_TORCH:
        surface.fill((70, 65, 60), rect)
        # 砖缝
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (55, 50, 45), (x, yy), (x + TILE_SIZE, yy))
        # 火把支架
        pygame.draw.rect(surface, (100, 80, 60), (x + 7, 4, 2, 4))
        # 火焰外层
        pygame.draw.circle(surface, (255, 150, 30), (x + 8, 3), 2)
        # 火焰内层
        pygame.draw.circle(surface, (255, 220, 80), (x + 8, 3), 1)
        # 暖光光晕
        warm_glow = pygame.Surface((6, 6), pygame.SRCALPHA)
        warm_glow.fill((255, 200, 50, 40))
        surface.blit(warm_glow, (x + 5, 0))
    elif gid == GID_OFFICE_DESK:
        # 办公桌+电脑一体：L型桌面+抽屉柜+显示器+键盘
        surface.fill((0, 0, 0, 0), rect)
        # 桌面（L型）
        pygame.draw.rect(surface, (110, 75, 40), (x + 1, 5, 14, 3))
        pygame.draw.rect(surface, (110, 75, 40), (x + 1, 5, 4, 8))
        # 桌面高光
        pygame.draw.rect(surface, (130, 90, 50), (x + 2, 6, 12, 1))
        # 抽屉柜（左侧）
        pygame.draw.rect(surface, (90, 60, 30), (x + 2, 8, 3, 5))
        pygame.draw.rect(surface, (80, 50, 25), (x + 2, 8, 3, 5), 1)
        # 抽屉拉手
        pygame.draw.rect(surface, (160, 140, 100), (x + 3, 9, 1, 1))
        pygame.draw.rect(surface, (160, 140, 100), (x + 3, 11, 1, 1))
        # 显示器底座
        pygame.draw.rect(surface, (60, 60, 70), (x + 8, 6, 4, 1))
        # 显示器支架
        pygame.draw.rect(surface, (60, 60, 70), (x + 9, 3, 2, 3))
        # 显示器屏幕
        pygame.draw.rect(surface, (40, 40, 50), (x + 7, 0, 6, 4))
        pygame.draw.rect(surface, (100, 140, 200), (x + 8, 1, 4, 2))
        # 键盘
        pygame.draw.rect(surface, (80, 80, 90), (x + 8, 7, 4, 1))
    elif gid == GID_LARGE_DESK_L:
        # 大办公桌左半：桌面+抽屉柜+桌面物品
        surface.fill((0, 0, 0, 0), rect)
        # 桌面顶部（浅木色，延伸到右边缘与右半无缝衔接）
        pygame.draw.rect(surface, (139, 90, 43), (x + 1, 4, 15, 3))
        # 桌面高光
        pygame.draw.rect(surface, (160, 110, 55), (x + 2, 5, 13, 1))
        # 桌面前面板（中木色）
        pygame.draw.rect(surface, (120, 75, 35), (x + 1, 7, 15, 6))
        # 前面板暗线
        pygame.draw.rect(surface, (110, 68, 30), (x + 1, 10, 15, 1))
        # 左侧边缘（深木色）
        pygame.draw.rect(surface, (90, 55, 25), (x, 4, 1, 9))
        # 抽屉柜（左侧，3层）
        pygame.draw.rect(surface, (100, 65, 30), (x + 2, 8, 4, 5))
        pygame.draw.rect(surface, (85, 50, 22), (x + 2, 8, 4, 5), 1)
        # 抽屉分隔线
        pygame.draw.line(surface, (80, 48, 20), (x + 2, 9), (x + 5, 9))
        pygame.draw.line(surface, (80, 48, 20), (x + 2, 11), (x + 5, 11))
        # 抽屉拉手
        pygame.draw.rect(surface, (180, 155, 100), (x + 3, 8, 2, 1))
        pygame.draw.rect(surface, (180, 155, 100), (x + 3, 10, 2, 1))
        pygame.draw.rect(surface, (180, 155, 100), (x + 3, 12, 2, 1))
        # 桌面物品：笔筒
        pygame.draw.rect(surface, (70, 70, 80), (x + 10, 2, 3, 2))
        pygame.draw.rect(surface, (90, 90, 100), (x + 10, 2, 3, 1))
        # 笔（红色+蓝色）
        surface.set_at((x + 11, 1), (200, 60, 60))
        surface.set_at((x + 12, 2), (60, 100, 200))
        # 桌面物品：文件堆
        pygame.draw.rect(surface, (230, 225, 215), (x + 7, 4, 3, 2))
        pygame.draw.rect(surface, (210, 205, 195), (x + 8, 4, 2, 2))
        # 桌面阴影
        pygame.draw.rect(surface, (100, 62, 28), (x + 1, 13, 15, 1))
    elif gid == GID_LARGE_DESK_R:
        # 大办公桌右半：桌面+显示器+键盘+鼠标
        surface.fill((0, 0, 0, 0), rect)
        # 桌面顶部（浅木色，从左边缘开始与左半无缝衔接）
        pygame.draw.rect(surface, (139, 90, 43), (x, 4, 15, 3))
        # 桌面高光
        pygame.draw.rect(surface, (160, 110, 55), (x + 1, 5, 13, 1))
        # 桌面前面板（中木色）
        pygame.draw.rect(surface, (120, 75, 35), (x, 7, 15, 6))
        # 前面板暗线
        pygame.draw.rect(surface, (110, 68, 30), (x, 10, 15, 1))
        # 右侧边缘（深木色）
        pygame.draw.rect(surface, (90, 55, 25), (x + 15, 4, 1, 9))
        # 右侧小柜门
        pygame.draw.rect(surface, (105, 68, 32), (x + 10, 8, 4, 5))
        pygame.draw.rect(surface, (85, 50, 22), (x + 10, 8, 4, 5), 1)
        # 柜门拉手
        pygame.draw.rect(surface, (180, 155, 100), (x + 13, 10, 1, 2))
        # 显示器底座
        pygame.draw.rect(surface, (55, 55, 65), (x + 5, 6, 4, 1))
        # 显示器支架
        pygame.draw.rect(surface, (55, 55, 65), (x + 6, 3, 2, 3))
        # 显示器屏幕外框
        pygame.draw.rect(surface, (35, 35, 45), (x + 3, 0, 8, 4))
        # 显示器屏幕
        pygame.draw.rect(surface, (70, 110, 170), (x + 4, 1, 6, 2))
        # 屏幕上的文字行
        surface.set_at((x + 5, 1), (90, 130, 190))
        surface.set_at((x + 7, 1), (90, 130, 190))
        surface.set_at((x + 6, 2), (90, 130, 190))
        surface.set_at((x + 8, 2), (90, 130, 190))
        # 键盘
        pygame.draw.rect(surface, (75, 75, 85), (x + 4, 7, 5, 1))
        # 鼠标
        pygame.draw.rect(surface, (75, 75, 85), (x + 10, 7, 2, 1))
        # 桌面阴影
        pygame.draw.rect(surface, (100, 62, 28), (x, 13, 15, 1))


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


def _add_exit_trigger(triggers, x, y, w, h, target_map, spawn_point):
    triggers.append({
        "x": x * TILE_SIZE, "y": y * TILE_SIZE,
        "width": w * TILE_SIZE, "height": h * TILE_SIZE,
        "type": "door_exit",
        "properties": {
            "target_map": target_map,
            "spawn_point": spawn_point,
            "auto_trigger": True,
            "transition_type": "indoor_exit",
        }
    })


def _add_stairs_trigger(triggers, x, y, w, h, target_map, spawn_point):
    triggers.append({
        "x": x * TILE_SIZE, "y": y * TILE_SIZE,
        "width": w * TILE_SIZE, "height": h * TILE_SIZE,
        "type": "stairs",
        "properties": {
            "target_map": target_map,
            "spawn_point": spawn_point,
            "transition_type": "floor_change",
        }
    })


def _add_spawn(trigger_objects, spawn_id, x, y):
    trigger_objects.append({
        "x": x * TILE_SIZE, "y": y * TILE_SIZE,
        "width": 2 * TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "spawn",
        "properties": {"spawn_id": spawn_id}
    })


def design_library_f1():
    W, H = 24, 18
    ground = _fill_layer(None, W, H, GID_LIB_FLOOR)
    structures = _fill_layer(None, W, H, GID_EMPTY)
    decorations = _fill_layer(None, W, H, GID_EMPTY)
    collision = _fill_layer(None, W, H, GID_EMPTY)
    interactive_objects = []
    trigger_objects = []

    _fill_border(structures, W, H, GID_LIB_WALL_TOP)
    for y in range(2, H - 1):
        structures[y][0] = GID_LIB_WALL
        structures[y][W - 1] = GID_LIB_WALL

    for x in range(2, 8):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        structures[3][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    for x in range(10, 14):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        structures[3][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    for x in range(16, 22):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        structures[3][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    for x in range(2, 8):
        structures[6][x] = GID_BOOKSHELF
        structures[7][x] = GID_BOOKSHELF
        collision[6][x] = GID_COLLISION
        collision[7][x] = GID_COLLISION

    for x in range(16, 22):
        structures[6][x] = GID_BOOKSHELF
        structures[7][x] = GID_BOOKSHELF
        collision[6][x] = GID_COLLISION
        collision[7][x] = GID_COLLISION

    structures[5][11] = GID_TABLE
    structures[5][12] = GID_TABLE
    collision[5][11] = GID_COLLISION
    collision[5][12] = GID_COLLISION
    structures[4][11] = GID_CHAIR
    structures[4][12] = GID_CHAIR
    collision[4][11] = GID_COLLISION
    collision[4][12] = GID_COLLISION

    structures[9][11] = GID_TABLE
    structures[9][12] = GID_TABLE
    collision[9][11] = GID_COLLISION
    collision[9][12] = GID_COLLISION

    # 阅读灯
    structures[4][10] = GID_LIB_READING_LAMP
    collision[4][10] = GID_COLLISION
    structures[4][13] = GID_LIB_READING_LAMP
    collision[4][13] = GID_COLLISION

    structures[10][2] = GID_COMPUTER
    collision[10][2] = GID_COLLISION

    structures[10][21] = GID_COMPUTER
    collision[10][21] = GID_COLLISION

    ground[9][11] = GID_CARPET_RED
    ground[9][12] = GID_CARPET_RED
    ground[10][11] = GID_CARPET_RED
    ground[10][12] = GID_CARPET_RED

    structures[H - 2][11] = GID_DOOR_INDOOR
    structures[H - 2][12] = GID_DOOR_INDOOR
    collision[H - 2][11] = GID_EMPTY
    collision[H - 2][12] = GID_EMPTY

    structures[1][21] = GID_STAIRS_UP
    collision[1][21] = GID_EMPTY

    for sy in range(1, 4):
        for sx in range(20, 22):
            if sy == 1 and sx == 21:
                continue
            structures[sy][sx] = GID_EMPTY
            collision[sy][sx] = GID_EMPTY

    interactive_objects.append({
        "x": 21 * TILE_SIZE, "y": 1 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "stairs_up",
        "properties": {
            "interactive_type": "enter",
            "prompt_text": "上楼",
            "target_map": "library_f2",
            "spawn_point": "library_f2_stairs",
            "transition_type": "floor_change",
        }
    })

    interactive_objects.append({
        "x": 2 * TILE_SIZE, "y": 10 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "computer",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看电脑",
            "display_name": "查询终端",
        }
    })

    interactive_objects.append({
        "x": 21 * TILE_SIZE, "y": 10 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "computer",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看电脑",
            "display_name": "查询终端",
        }
    })

    for x in range(2, 8):
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": 1 * TILE_SIZE,
            "width": TILE_SIZE, "height": 3 * TILE_SIZE,
            "type": "bookshelf",
            "properties": {
                "interactive_type": "examine",
                "prompt_text": "查看书架",
                "display_name": "书架A",
            }
        })

    _add_exit_trigger(trigger_objects, 11, H - 2, 2, 1,
                      "main_campus", "library_exit")
    _add_spawn(trigger_objects, "library_entrance", 11, H - 4)
    _add_spawn(trigger_objects, "library_f1_stairs", 20, 2)

    return W, H, ground, structures, decorations, collision, interactive_objects, trigger_objects


def design_library_f2():
    W, H = 24, 18
    ground = _fill_layer(None, W, H, GID_LIB_FLOOR)
    structures = _fill_layer(None, W, H, GID_EMPTY)
    decorations = _fill_layer(None, W, H, GID_EMPTY)
    collision = _fill_layer(None, W, H, GID_EMPTY)
    interactive_objects = []
    trigger_objects = []

    _fill_border(structures, W, H, GID_LIB_WALL_TOP)
    for y in range(2, H - 1):
        structures[y][0] = GID_LIB_WALL
        structures[y][W - 1] = GID_LIB_WALL

    for x in range(2, 7):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        structures[3][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    for x in range(9, 15):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        structures[3][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    for x in range(17, 22):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        structures[3][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    for x in range(2, 7):
        structures[7][x] = GID_BOOKSHELF
        structures[8][x] = GID_BOOKSHELF
        collision[7][x] = GID_COLLISION
        collision[8][x] = GID_COLLISION

    for x in range(17, 22):
        structures[7][x] = GID_BOOKSHELF
        structures[8][x] = GID_BOOKSHELF
        collision[7][x] = GID_COLLISION
        collision[8][x] = GID_COLLISION

    structures[5][11] = GID_TABLE
    structures[5][12] = GID_TABLE
    collision[5][11] = GID_COLLISION
    collision[5][12] = GID_COLLISION

    structures[6][11] = GID_CHAIR
    structures[6][12] = GID_CHAIR
    collision[6][11] = GID_COLLISION
    collision[6][12] = GID_COLLISION

    structures[10][11] = GID_TABLE
    structures[10][12] = GID_TABLE
    collision[10][11] = GID_COLLISION
    collision[10][12] = GID_COLLISION

    ground[10][11] = GID_RUG
    ground[10][12] = GID_RUG
    ground[11][11] = GID_RUG
    ground[11][12] = GID_RUG

    structures[H - 3][5] = GID_BLACKBOARD
    collision[H - 3][5] = GID_COLLISION

    structures[1][2] = GID_STAIRS_DOWN
    collision[1][2] = GID_EMPTY

    for sy in range(1, 4):
        for sx in range(2, 5):
            if sy == 1 and sx == 2:
                continue
            structures[sy][sx] = GID_EMPTY
            collision[sy][sx] = GID_EMPTY

    interactive_objects.append({
        "x": 2 * TILE_SIZE, "y": 1 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "stairs_down",
        "properties": {
            "interactive_type": "enter",
            "prompt_text": "下楼",
            "target_map": "library_f1",
            "spawn_point": "library_f1_stairs",
            "transition_type": "floor_change",
        }
    })

    interactive_objects.append({
        "x": 5 * TILE_SIZE, "y": (H - 3) * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "blackboard",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看黑板",
            "display_name": "黑板",
        }
    })

    for x in range(5, 7):
        interactive_objects.append({
            "x": x * TILE_SIZE, "y": 1 * TILE_SIZE,
            "width": TILE_SIZE, "height": 3 * TILE_SIZE,
            "type": "bookshelf",
            "properties": {
                "interactive_type": "examine",
                "prompt_text": "查看书架",
                "display_name": "书架B",
            }
        })

    _add_spawn(trigger_objects, "library_f2_stairs", 3, 2)

    return W, H, ground, structures, decorations, collision, interactive_objects, trigger_objects


def design_gym():
    W, H = 30, 20
    ground = _fill_layer(None, W, H, GID_COURT_FLOOR)
    structures = _fill_layer(None, W, H, GID_EMPTY)
    decorations = _fill_layer(None, W, H, GID_EMPTY)
    collision = _fill_layer(None, W, H, GID_EMPTY)
    interactive_objects = []
    trigger_objects = []

    _fill_border(structures, W, H, GID_GYM_WALL_TOP)
    for y in range(2, H - 1):
        structures[y][0] = GID_GYM_WALL
        structures[y][W - 1] = GID_GYM_WALL

    for x in range(3, 7):
        structures[1][x] = GID_SCOREBOARD
        collision[1][x] = GID_COLLISION

    structures[1][W - 2] = GID_HOOP
    collision[1][W - 2] = GID_COLLISION
    structures[1][1] = GID_HOOP
    collision[1][1] = GID_COLLISION

    # 更衣柜
    structures[4][1] = GID_GYM_LOCKER
    collision[4][1] = GID_COLLISION
    structures[5][1] = GID_GYM_LOCKER
    collision[5][1] = GID_COLLISION
    structures[6][1] = GID_GYM_LOCKER
    collision[6][1] = GID_COLLISION

    for y in range(4, 8):
        structures[y][2] = GID_CHAIR
        collision[y][2] = GID_COLLISION
        structures[y][3] = GID_CHAIR
        collision[y][3] = GID_COLLISION

    for y in range(4, 8):
        structures[y][W - 3] = GID_CHAIR
        collision[y][W - 3] = GID_COLLISION
        structures[y][W - 4] = GID_CHAIR
        collision[y][W - 4] = GID_COLLISION

    structures[4][5] = GID_TABLE
    structures[4][6] = GID_TABLE
    collision[4][5] = GID_COLLISION
    collision[4][6] = GID_COLLISION

    structures[H - 3][5] = GID_FRIDGE
    collision[H - 3][5] = GID_COLLISION

    structures[H - 3][8] = GID_COUNTER
    structures[H - 3][9] = GID_COUNTER
    collision[H - 3][8] = GID_COLLISION
    collision[H - 3][9] = GID_COLLISION

    structures[H - 2][14] = GID_DOOR_INDOOR
    structures[H - 2][15] = GID_DOOR_INDOOR
    collision[H - 2][14] = GID_EMPTY
    collision[H - 2][15] = GID_EMPTY

    interactive_objects.append({
        "x": (W - 2) * TILE_SIZE, "y": 1 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "basketball_hoop",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看篮筐",
            "display_name": "篮筐",
        }
    })

    interactive_objects.append({
        "x": 5 * TILE_SIZE, "y": 1 * TILE_SIZE,
        "width": 2 * TILE_SIZE, "height": TILE_SIZE,
        "type": "scoreboard",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看记分牌",
            "display_name": "记分牌",
        }
    })

    interactive_objects.append({
        "x": 8 * TILE_SIZE, "y": (H - 3) * TILE_SIZE,
        "width": 2 * TILE_SIZE, "height": TILE_SIZE,
        "type": "counter",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看器材柜",
            "display_name": "器材柜",
        }
    })

    _add_exit_trigger(trigger_objects, 14, H - 2, 2, 1,
                      "main_campus", "gym_exit")
    _add_spawn(trigger_objects, "gym_entrance", 14, H - 4)

    return W, H, ground, structures, decorations, collision, interactive_objects, trigger_objects


def design_dining_hall_f1():
    W, H = 22, 16
    ground = _fill_layer(None, W, H, GID_TILE_FLOOR)
    structures = _fill_layer(None, W, H, GID_EMPTY)
    decorations = _fill_layer(None, W, H, GID_EMPTY)
    collision = _fill_layer(None, W, H, GID_EMPTY)
    interactive_objects = []
    trigger_objects = []

    _fill_border(structures, W, H, GID_DINING_WALL_TOP)
    for y in range(2, H - 1):
        structures[y][0] = GID_DINING_WALL
        structures[y][W - 1] = GID_DINING_WALL

    for tx, ty in [(8, 3), (13, 3), (3, 7), (8, 7), (13, 7)]:
        structures[ty][tx] = GID_TABLE
        structures[ty][tx + 1] = GID_TABLE
        collision[ty][tx] = GID_COLLISION
        collision[ty][tx + 1] = GID_COLLISION
        structures[ty - 1][tx] = GID_CHAIR
        structures[ty - 1][tx + 1] = GID_CHAIR
        collision[ty - 1][tx] = GID_COLLISION
        collision[ty - 1][tx + 1] = GID_COLLISION

    for x in range(17, 21):
        structures[2][x] = GID_DINING_SERVING
        structures[3][x] = GID_DINING_SERVING
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    structures[5][19] = GID_FRIDGE
    collision[5][19] = GID_COLLISION

    structures[H - 2][10] = GID_DOOR_INDOOR
    structures[H - 2][11] = GID_DOOR_INDOOR
    collision[H - 2][10] = GID_EMPTY
    collision[H - 2][11] = GID_EMPTY

    structures[1][2] = GID_STAIRS_UP
    collision[1][2] = GID_EMPTY

    for sy in range(2, 4):
        for sx in range(2, 5):
            structures[sy][sx] = GID_EMPTY
            collision[sy][sx] = GID_EMPTY

    interactive_objects.append({
        "x": 2 * TILE_SIZE, "y": 1 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "stairs_up",
        "properties": {
            "interactive_type": "enter",
            "prompt_text": "上楼",
            "target_map": "dining_hall_f2",
            "spawn_point": "dining_f2_stairs",
            "transition_type": "floor_change",
        }
    })

    interactive_objects.append({
        "x": 19 * TILE_SIZE, "y": 2 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "counter",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看柜台",
            "display_name": "打饭窗口",
        }
    })

    for tx, ty in [(8, 3), (13, 3)]:
        interactive_objects.append({
            "x": tx * TILE_SIZE, "y": ty * TILE_SIZE,
            "width": 2 * TILE_SIZE, "height": TILE_SIZE,
            "type": "table",
            "properties": {
                "interactive_type": "examine",
                "prompt_text": "搜索餐桌",
                "display_name": "一楼餐桌",
            }
        })

    _add_exit_trigger(trigger_objects, 10, H - 2, 2, 1,
                      "main_campus", "dining_exit")
    _add_spawn(trigger_objects, "dining_entrance", 10, H - 4)
    _add_spawn(trigger_objects, "dining_f1_stairs", 3, 2)

    return W, H, ground, structures, decorations, collision, interactive_objects, trigger_objects


def design_dining_hall_f2():
    W, H = 22, 16
    ground = _fill_layer(None, W, H, GID_TILE_FLOOR)
    structures = _fill_layer(None, W, H, GID_EMPTY)
    decorations = _fill_layer(None, W, H, GID_EMPTY)
    collision = _fill_layer(None, W, H, GID_EMPTY)
    interactive_objects = []
    trigger_objects = []

    _fill_border(structures, W, H, GID_DINING_WALL_TOP)
    for y in range(2, H - 1):
        structures[y][0] = GID_DINING_WALL
        structures[y][W - 1] = GID_DINING_WALL

    for tx, ty in [(8, 3), (13, 3), (3, 7), (8, 7), (13, 7)]:
        structures[ty][tx] = GID_TABLE
        structures[ty][tx + 1] = GID_TABLE
        collision[ty][tx] = GID_COLLISION
        collision[ty][tx + 1] = GID_COLLISION
        structures[ty - 1][tx] = GID_CHAIR
        structures[ty - 1][tx + 1] = GID_CHAIR
        collision[ty - 1][tx] = GID_COLLISION
        collision[ty - 1][tx + 1] = GID_COLLISION

    for x in range(17, 21):
        ground[2][x] = GID_KITCHEN_FLOOR
        ground[3][x] = GID_KITCHEN_FLOOR
        ground[4][x] = GID_KITCHEN_FLOOR
        ground[5][x] = GID_KITCHEN_FLOOR
    structures[2][17] = GID_FRIDGE
    collision[2][17] = GID_COLLISION
    structures[5][17] = GID_COUNTER
    structures[5][18] = GID_COUNTER
    structures[5][19] = GID_COUNTER
    collision[5][17] = GID_COLLISION
    collision[5][18] = GID_COLLISION
    collision[5][19] = GID_COLLISION

    structures[1][2] = GID_STAIRS_DOWN
    collision[1][2] = GID_EMPTY

    for sy in range(2, 4):
        for sx in range(2, 5):
            structures[sy][sx] = GID_EMPTY
            collision[sy][sx] = GID_EMPTY

    interactive_objects.append({
        "x": 2 * TILE_SIZE, "y": 1 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "stairs_down",
        "properties": {
            "interactive_type": "enter",
            "prompt_text": "下楼",
            "target_map": "dining_hall_f1",
            "spawn_point": "dining_f1_stairs",
            "transition_type": "floor_change",
        }
    })

    interactive_objects.append({
        "x": 17 * TILE_SIZE, "y": 2 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "fridge",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看冰箱",
            "display_name": "后厨冰箱",
        }
    })

    for tx, ty in [(8, 3), (13, 3)]:
        interactive_objects.append({
            "x": tx * TILE_SIZE, "y": ty * TILE_SIZE,
            "width": 2 * TILE_SIZE, "height": TILE_SIZE,
            "type": "table",
            "properties": {
                "interactive_type": "examine",
                "prompt_text": "搜索餐桌",
                "display_name": "二楼餐桌",
            }
        })

    _add_spawn(trigger_objects, "dining_f2_stairs", 3, 2)

    return W, H, ground, structures, decorations, collision, interactive_objects, trigger_objects


def layer_to_csv(layer_data):
    values = []
    for row in layer_data:
        values.extend(str(v) for v in row)
    return "\n" + ",".join(values) + "\n"


def create_tmx(W, H, ground, structures, decorations, collision,
               interactive_objects, trigger_objects,
               tileset_path, output_path):
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
    tileset.set("name", "indoor_tileset")
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
    ground_layer.set("width", str(W))
    ground_layer.set("height", str(H))
    ground_data = ET.SubElement(ground_layer, "data")
    ground_data.set("encoding", "csv")
    ground_data.text = layer_to_csv(ground)
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

    tileset_output = os.path.join(base_dir, "assets", "tilesets", "indoor_tileset.png")
    map_dir = os.path.join(base_dir, "world", "map_data")

    create_tileset(tileset_output)

    tileset_rel_path = os.path.relpath(tileset_output, map_dir)
    tileset_rel_path = tileset_rel_path.replace("\\", "/")

    print("\n--- Library F1 ---")
    W, H, ground, structures, decorations, collision, objs, triggers = design_library_f1()
    create_tmx(W, H, ground, structures, decorations, collision, objs, triggers,
               tileset_rel_path, os.path.join(map_dir, "library_f1.tmx"))

    print("\n--- Library F2 ---")
    W, H, ground, structures, decorations, collision, objs, triggers = design_library_f2()
    create_tmx(W, H, ground, structures, decorations, collision, objs, triggers,
               tileset_rel_path, os.path.join(map_dir, "library_f2.tmx"))

    print("\n--- Gym ---")
    W, H, ground, structures, decorations, collision, objs, triggers = design_gym()
    create_tmx(W, H, ground, structures, decorations, collision, objs, triggers,
               tileset_rel_path, os.path.join(map_dir, "gym.tmx"))

    print("\n--- Dining Hall F1 ---")
    W, H, ground, structures, decorations, collision, objs, triggers = design_dining_hall_f1()
    create_tmx(W, H, ground, structures, decorations, collision, objs, triggers,
               tileset_rel_path, os.path.join(map_dir, "dining_hall_f1.tmx"))

    print("\n--- Dining Hall F2 ---")
    W, H, ground, structures, decorations, collision, objs, triggers = design_dining_hall_f2()
    create_tmx(W, H, ground, structures, decorations, collision, objs, triggers,
               tileset_rel_path, os.path.join(map_dir, "dining_hall_f2.tmx"))

    print("\nAll indoor maps generated successfully!")
