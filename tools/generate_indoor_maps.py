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
GID_HOOP_TOP = 16     # 篮球架上部（篮板+篮筐+篮网）
GID_HOOP_BOT = 21     # 篮球架下部（支柱+底座）
GID_SCOREBOARD = 17
GID_COMPUTER = 18
GID_DOOR_INDOOR = 19
GID_COLLISION = 20
GID_KITCHEN_FLOOR = 70
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
# 体育馆设施 tile（多部件拼接）
GID_GYM_TABLE_TL = 47    # 体育馆桌子左上
GID_GYM_TABLE_TR = 48    # 体育馆桌子右上
GID_GYM_TABLE_BL = 49    # 体育馆桌子左下
GID_GYM_TABLE_BR = 50    # 体育馆桌子右下
GID_GYM_TROPHY_TL = 51   # 奖杯展示柜左上
GID_GYM_TROPHY_TR = 52   # 奖杯展示柜右上
GID_GYM_TROPHY_ML = 53   # 奖杯展示柜左中
GID_GYM_TROPHY_MR = 54   # 奖杯展示柜右中
GID_GYM_TROPHY_BL = 55   # 奖杯展示柜左下
GID_GYM_TROPHY_BR = 56   # 奖杯展示柜右下
GID_GYM_WATER_TOP = 57   # 饮水机顶部
GID_GYM_WATER_BOT = 58   # 饮水机底部
GID_GYM_BENCH_L = 59     # 体育馆长凳左半
GID_GYM_BENCH_R = 60     # 体育馆长凳右半
GID_GYM_MAT_L = 61       # 体操垫左部
GID_GYM_MAT_M = 62       # 体操垫中部
GID_GYM_MAT_R = 63       # 体操垫右部
GID_GYM_EQUIP_L = 64     # 器材柜左半
GID_GYM_EQUIP_R = 65     # 器材柜右半
GID_SECTION_SIGN = 66   # 分区标识牌（挂在墙上或立在书架旁）
GID_DISPLAY_CABINET = 67  # 展示柜
GID_POTTED_PLANT = 68     # 盆栽
GID_SOFA = 69             # 沙发
# ---- 新增 tile（GID 71+）----
GID_MENU_BOARD = 71       # 食堂菜单牌
GID_DRINK_MACHINE = 72    # 食堂饮料机
GID_RETURN_DESK = 73      # 图书馆还书台
GID_NEWSPAPER_RACK = 74   # 图书馆报刊架
GID_WHITEBOARD = 75       # 综合楼白板
GID_FILE_CABINET = 76     # 综合楼文件柜
GID_STONE_PEDESTAL = 77   # 密室石台
GID_STONE_PILLAR_TOP = 78 # 密室石柱上部
GID_STONE_PILLAR_BOT = 79 # 密室石柱下部
GID_SPORTS_POSTER = 80    # 体育馆运动海报
GID_FIRST_AID = 81        # 体育馆急救箱

TILE_COUNT = 82

SOLID_GIDS = {
    GID_INDOOR_WALL, GID_INDOOR_WALL_TOP, GID_BOOKSHELF, GID_BOOKSHELF_TOP,
    GID_TABLE, GID_CHAIR, GID_COUNTER, GID_FRIDGE,
    GID_HOOP_TOP, GID_HOOP_BOT, GID_SCOREBOARD, GID_COMPUTER,
    GID_BLACKBOARD, GID_PLANT_INDOOR, GID_COLLISION,
    GID_LIB_WALL, GID_LIB_WALL_TOP, GID_LIB_READING_LAMP,
    GID_GYM_WALL, GID_GYM_WALL_TOP, GID_GYM_LOCKER,
    GID_DINING_WALL, GID_DINING_WALL_TOP, GID_DINING_SERVING,
    GID_NANHU_WALL, GID_NANHU_WALL_TOP, GID_NANHU_ELEVATOR,
    GID_SECRET_WALL, GID_SECRET_WALL_TOP, GID_SECRET_RUNE, GID_SECRET_TORCH,
    GID_OFFICE_DESK, GID_LARGE_DESK_L, GID_LARGE_DESK_R,
    GID_GYM_TABLE_TL, GID_GYM_TABLE_TR, GID_GYM_TABLE_BL, GID_GYM_TABLE_BR,
    GID_GYM_TROPHY_TL, GID_GYM_TROPHY_TR, GID_GYM_TROPHY_ML, GID_GYM_TROPHY_MR,
    GID_GYM_TROPHY_BL, GID_GYM_TROPHY_BR,
    GID_GYM_WATER_TOP, GID_GYM_WATER_BOT,
    GID_GYM_BENCH_L, GID_GYM_BENCH_R,
    GID_GYM_EQUIP_L, GID_GYM_EQUIP_R,
    GID_MENU_BOARD, GID_DRINK_MACHINE, GID_RETURN_DESK, GID_NEWSPAPER_RACK,
    GID_WHITEBOARD, GID_FILE_CABINET, GID_STONE_PEDESTAL,
    GID_STONE_PILLAR_TOP, GID_STONE_PILLAR_BOT,
    GID_SPORTS_POSTER, GID_FIRST_AID,
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
        # 瓷砖地面 - 带高光/阴影变化
        surface.fill((200, 200, 200), rect)
        # 网格线：每4px一条
        for yy in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (180, 180, 180), (x, yy), (x + TILE_SIZE, yy))
        for xx in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (180, 180, 180), (x + xx, 0), (x + xx, TILE_SIZE))
        # 每块瓷砖内部高光/暗面
        for ty in range(4):
            for tx in range(4):
                dx = tx * 4
                dy = ty * 4
                # 左上角高光像素
                surface.set_at((x + dx + 1, dy + 1), (215, 215, 215))
                # 右下角暗面像素
                surface.set_at((x + dx + 3, dy + 3), (190, 190, 190))
        # 随机色点模拟瓷砖表面微小色差
        for dx, dy in [(2, 3), (10, 5), (5, 12), (13, 11), (7, 1), (14, 14)]:
            surface.set_at((x + dx, dy), (195, 195, 195))
        # 瓷砖缝隙加深：网格线交叉点
        for yy in range(0, TILE_SIZE, 4):
            for xx in range(0, TILE_SIZE, 4):
                surface.set_at((x + xx, yy), (170, 170, 170))
    elif gid == GID_CARPET_RED:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (140, 30, 30), (x + 1, 1, 14, 14))
        pygame.draw.rect(surface, (160, 40, 40), (x + 2, 2, 12, 12))
        pygame.draw.rect(surface, (180, 50, 50), (x + 3, 3, 10, 10))
        pygame.draw.rect(surface, (140, 30, 30), (x + 5, 5, 6, 6))
    elif gid == GID_INDOOR_WALL:
        # 通用墙壁 - 砖缝纹理
        surface.fill((220, 210, 190), rect)
        # 砖缝纹理（交错排列）
        for yy in [4, 8, 12]:
            pygame.draw.line(surface, (200, 190, 170), (x, yy), (x + TILE_SIZE, yy))
        # 奇数行竖线
        for bx in [4, 12]:
            pygame.draw.line(surface, (200, 190, 170), (x + bx, 0), (x + bx, 4))
            pygame.draw.line(surface, (200, 190, 170), (x + bx, 8), (x + bx, 12))
        # 偶数行竖线
        pygame.draw.line(surface, (200, 190, 170), (x + 8, 4), (x + 8, 8))
        pygame.draw.line(surface, (200, 190, 170), (x + 8, 12), (x + 8, 16))
        # 底部暗线
        pygame.draw.line(surface, (190, 180, 160), (x, 15), (x + TILE_SIZE, 15))
        # 左上高光
        pygame.draw.line(surface, (230, 220, 200), (x, 0), (x, 15))
    elif gid == GID_INDOOR_WALL_TOP:
        # 通用墙壁顶部 - 顶部暗带+砖缝
        surface.fill((220, 210, 190), rect)
        # 顶部3px暗带
        pygame.draw.rect(surface, (200, 190, 170), (x, 0, TILE_SIZE, 3))
        # 底部暗线
        pygame.draw.line(surface, (190, 180, 160), (x, 15), (x + TILE_SIZE, 15))
        # 砖缝（仅下半部分）
        pygame.draw.line(surface, (200, 190, 170), (x, 8), (x + TILE_SIZE, 8))
        pygame.draw.line(surface, (200, 190, 170), (x, 12), (x + TILE_SIZE, 12))
        # 偶数行竖线
        pygame.draw.line(surface, (200, 190, 170), (x + 8, 8), (x + 8, 12))
        # 奇数行竖线
        for bx in [4, 12]:
            pygame.draw.line(surface, (200, 190, 170), (x + bx, 12), (x + bx, 16))
    elif gid == GID_BOOKSHELF:
        # 书架身体 - 更精致的三层书架
        surface.fill((0, 0, 0, 0), rect)  # 透明背景
        # 木质框架
        pygame.draw.rect(surface, (101, 67, 33), (x + 1, 0, 14, TILE_SIZE))
        # 左右立柱
        pygame.draw.rect(surface, (80, 50, 25), (x + 1, 0, 2, TILE_SIZE))
        pygame.draw.rect(surface, (80, 50, 25), (x + 13, 0, 2, TILE_SIZE))
        # 三层隔板
        for row in range(4):
            yy = row * 4
            pygame.draw.line(surface, (90, 58, 28), (x + 1, yy), (x + 15, yy))
            pygame.draw.line(surface, (120, 80, 40), (x + 1, yy + 1), (x + 15, yy + 1))
        # 书籍 - 每层不同颜色组合，更丰富
        shelf_books = [
            [(180, 50, 50), (50, 80, 160), (50, 140, 60), (200, 160, 40), (140, 40, 140)],
            [(60, 60, 140), (160, 80, 40), (80, 160, 80), (180, 60, 100), (100, 100, 40)],
            [(140, 100, 60), (60, 120, 140), (160, 40, 80), (80, 80, 120), (120, 140, 60)],
            [(100, 60, 120), (180, 120, 60), (60, 100, 160), (140, 80, 40), (80, 140, 100)],
        ]
        for row in range(4):
            yy = row * 4
            bx = x + 3
            for i, color in enumerate(shelf_books[row]):
                w = 2 if i % 2 == 0 else 3
                if bx + w > x + 13:
                    break
                pygame.draw.rect(surface, color, (bx, yy + 1, w, 3))
                # 书脊高光
                pygame.draw.line(surface, (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)), (bx, yy + 1), (bx, yy + 3))
                bx += w + 1
    elif gid == GID_BOOKSHELF_TOP:
        # 书架顶部 - 带装饰檐
        surface.fill((0, 0, 0, 0), rect)  # 透明背景
        # 装饰顶檐（比书架宽1px）
        pygame.draw.rect(surface, (80, 50, 25), (x, 0, 16, 2))
        pygame.draw.line(surface, (120, 80, 40), (x, 2), (x + 16, 2))
        # 书架主体
        pygame.draw.rect(surface, (101, 67, 33), (x + 1, 2, 14, 7))
        # 左右立柱
        pygame.draw.rect(surface, (80, 50, 25), (x + 1, 2, 2, 7))
        pygame.draw.rect(surface, (80, 50, 25), (x + 13, 2, 2, 7))
        # 隔板
        pygame.draw.line(surface, (90, 58, 28), (x + 1, 5), (x + 15, 5))
        pygame.draw.line(surface, (120, 80, 40), (x + 1, 6), (x + 15, 6))
        # 顶部书籍
        top_books = [(180, 50, 50), (50, 80, 160), (50, 140, 60), (200, 160, 40)]
        bx = x + 3
        for color in top_books:
            w = 2
            pygame.draw.rect(surface, color, (bx, 3, w, 2))
            pygame.draw.line(surface, (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)), (bx, 3), (bx, 4))
            bx += 3
        # 底部隔板
        pygame.draw.line(surface, (90, 58, 28), (x + 1, 9), (x + 15, 9))
        pygame.draw.line(surface, (120, 80, 40), (x + 1, 10), (x + 15, 10))
    elif gid == GID_TABLE:
        # 桌子 - 透明背景，立体感
        surface.fill((0, 0, 0, 0), rect)
        # 桌面
        pygame.draw.rect(surface, (160, 110, 60), (x + 2, 4, 12, 5))
        # 桌面内层
        pygame.draw.rect(surface, (175, 125, 70), (x + 3, 4, 10, 4))
        # 桌面高光线
        pygame.draw.line(surface, (195, 145, 85), (x + 4, 5), (x + 13, 5))
        # 桌面暗边
        pygame.draw.line(surface, (140, 95, 50), (x + 2, 8), (x + 13, 8))
        # 桌上物品：书本
        pygame.draw.rect(surface, (50, 80, 140), (x + 5, 5, 4, 2))
        # 书本高光
        pygame.draw.line(surface, (70, 100, 160), (x + 5, 5), (x + 8, 5))
        # 桌上物品：杯子
        pygame.draw.rect(surface, (200, 200, 210), (x + 11, 5, 2, 2))
        # 杯口高光
        surface.set_at((x + 11, 5), (230, 230, 240))
        # 桌腿
        pygame.draw.rect(surface, (130, 90, 45), (x + 3, 9, 2, 5))
        pygame.draw.rect(surface, (130, 90, 45), (x + 11, 9, 2, 5))
        # 桌腿内侧高光
        surface.set_at((x + 4, 10), (150, 105, 55))
        surface.set_at((x + 12, 10), (150, 105, 55))
        # 横撑
        pygame.draw.rect(surface, (110, 75, 38), (x + 4, 12, 8, 1))
        # 底部阴影
        shadow = pygame.Surface((12, 1), pygame.SRCALPHA)
        shadow.fill((80, 50, 25, 80))
        surface.blit(shadow, (x + 2, 14))
    elif gid == GID_CHAIR:
        # 椅子 - 透明背景，立体感
        surface.fill((0, 0, 0, 0), rect)
        # 椅背
        pygame.draw.rect(surface, (110, 70, 35), (x + 4, 2, 8, 4))
        # 椅背高光
        pygame.draw.line(surface, (135, 90, 50), (x + 4, 2), (x + 11, 2))
        # 椅背纹理
        pygame.draw.line(surface, (95, 58, 28), (x + 6, 3), (x + 6, 5))
        pygame.draw.line(surface, (95, 58, 28), (x + 9, 3), (x + 9, 5))
        # 椅面
        pygame.draw.rect(surface, (130, 85, 42), (x + 3, 6, 10, 3))
        # 椅面前沿高光
        pygame.draw.line(surface, (155, 105, 55), (x + 3, 6), (x + 12, 6))
        # 椅面暗边
        pygame.draw.line(surface, (110, 70, 35), (x + 3, 8), (x + 12, 8))
        # 椅腿
        pygame.draw.rect(surface, (100, 65, 30), (x + 3, 9, 2, 5))
        pygame.draw.rect(surface, (100, 65, 30), (x + 11, 9, 2, 5))
        # 椅腿内侧高光
        surface.set_at((x + 4, 10), (120, 80, 40))
        surface.set_at((x + 12, 10), (120, 80, 40))
        # 横撑
        pygame.draw.rect(surface, (90, 55, 25), (x + 4, 12, 8, 1))
        # 横撑高光
        pygame.draw.line(surface, (110, 70, 35), (x + 5, 12), (x + 7, 12))
        # 底部阴影
        shadow = pygame.Surface((10, 1), pygame.SRCALPHA)
        shadow.fill((60, 35, 15, 80))
        surface.blit(shadow, (x + 3, 14))
    elif gid == GID_COUNTER:
        # 柜台 - 透明背景，不锈钢质感+玻璃隔断
        surface.fill((0, 0, 0, 0), rect)
        # 柜台主体
        pygame.draw.rect(surface, (180, 180, 190), (x, 3, 16, 10))
        # 顶部台面高光
        pygame.draw.line(surface, (210, 210, 220), (x, 3), (x + 15, 3))
        # 底部暗边
        pygame.draw.line(surface, (150, 150, 160), (x, 12), (x + 15, 12))
        # 玻璃隔断（上半部分）
        glass = pygame.Surface((14, 3), pygame.SRCALPHA)
        glass.fill((200, 220, 240, 120))
        surface.blit(glass, (x + 1, 0))
        # 玻璃反光
        pygame.draw.line(surface, (230, 240, 255), (x + 2, 0), (x + 2, 2))
        # 柜台内部菜品（透过玻璃可见）
        pygame.draw.rect(surface, (200, 80, 60), (x + 3, 1, 3, 1))
        pygame.draw.rect(surface, (80, 160, 60), (x + 7, 1, 3, 1))
        pygame.draw.rect(surface, (200, 180, 60), (x + 11, 1, 3, 1))
        # 左右柜门
        pygame.draw.rect(surface, (160, 160, 170), (x + 1, 5, 5, 6))
        pygame.draw.rect(surface, (160, 160, 170), (x + 10, 5, 5, 6))
        # 门框线
        pygame.draw.rect(surface, (140, 140, 150), (x + 1, 5, 5, 6), 1)
        pygame.draw.rect(surface, (140, 140, 150), (x + 10, 5, 5, 6), 1)
        # 拉手
        surface.set_at((x + 5, 8), (200, 200, 210))
        surface.set_at((x + 6, 8), (200, 200, 210))
        surface.set_at((x + 9, 8), (200, 200, 210))
        surface.set_at((x + 10, 8), (200, 200, 210))
        # 底部踢脚线
        pygame.draw.rect(surface, (130, 130, 140), (x, 13, 16, 1))
        # 底部阴影
        shadow = pygame.Surface((16, 1), pygame.SRCALPHA)
        shadow.fill((100, 100, 110, 80))
        surface.blit(shadow, (x, 14))
    elif gid == GID_FRIDGE:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (200, 200, 210), (x + 2, 1, 12, 14))
        pygame.draw.rect(surface, (180, 180, 190), (x + 2, 1, 12, 14), 1)
        pygame.draw.line(surface, (160, 160, 170), (x + 2, 8), (x + 14, 8))
        pygame.draw.rect(surface, (150, 150, 160), (x + 12, 3, 1, 3))
        pygame.draw.rect(surface, (150, 150, 160), (x + 12, 10, 1, 3))
    elif gid == GID_STAIRS_DOWN:
        surface.fill((0, 0, 0, 0), rect)
        for i in range(4):
            step_y = i * 4
            step_w = TILE_SIZE - i * 4
            pygame.draw.rect(surface, (160, 120, 70), (x, step_y, step_w, 4))
            pygame.draw.line(surface, (140, 100, 55), (x, step_y + 3), (x + step_w, step_y + 3))
        pygame.draw.rect(surface, (120, 80, 40), (x, 0, TILE_SIZE, TILE_SIZE), 1)
    elif gid == GID_STAIRS_UP:
        surface.fill((0, 0, 0, 0), rect)
        for i in range(4):
            step_y = TILE_SIZE - (i + 1) * 4
            step_w = TILE_SIZE - i * 4
            pygame.draw.rect(surface, (160, 120, 70), (x, step_y, step_w, 4))
            pygame.draw.line(surface, (140, 100, 55), (x, step_y + 3), (x + step_w, step_y + 3))
        pygame.draw.rect(surface, (120, 80, 40), (x, 0, TILE_SIZE, TILE_SIZE), 1)
    elif gid == GID_COURT_FLOOR:
        # 球场地面 - 木地板纹理+球场标线
        surface.fill((200, 160, 100), rect)
        # 木地板纹理（交错竖线）
        for yy in range(0, TILE_SIZE, 4):
            pygame.draw.line(surface, (185, 145, 85), (x, yy), (x + TILE_SIZE, yy))
        offset = 0
        for yy in range(0, TILE_SIZE, 4):
            for bx in range(offset, TILE_SIZE, 8):
                pygame.draw.line(surface, (190, 150, 90), (x + bx, yy), (x + bx, yy + 4))
            offset = 8 if offset == 0 else 0
        # 球场标线（白色）
        pygame.draw.line(surface, (240, 240, 240), (x, 0), (x + TILE_SIZE, 0))
        pygame.draw.line(surface, (240, 240, 240), (x, 15), (x + TILE_SIZE, 15))
        pygame.draw.line(surface, (240, 240, 240), (x + 8, 0), (x + 8, TILE_SIZE))
        # 半圆弧（底部罚球区，用8个像素点逼近）
        for angle_idx in range(8):
            import math
            a = math.pi * angle_idx / 7
            px = int(8 + 6 * math.cos(a))
            py = int(12 - 4 * math.sin(a))
            if 0 <= px < TILE_SIZE and 0 <= py < TILE_SIZE:
                surface.set_at((x + px, py), (240, 240, 240))
    elif gid == GID_HOOP_TOP:
        # 篮球架上部：篮板+篮筐+篮网+支柱顶部
        surface.fill((0, 0, 0, 0), rect)
        # 支柱（灰色金属管，从底部延伸上来）
        pygame.draw.rect(surface, (140, 140, 150), (x + 7, 0, 2, 16))
        # 支柱高光
        surface.set_at((x + 7, 2), (165, 165, 175))
        surface.set_at((x + 7, 5), (165, 165, 175))
        surface.set_at((x + 7, 8), (165, 165, 175))
        surface.set_at((x + 7, 11), (165, 165, 175))
        # 横臂（从支柱向一侧延伸到篮板）
        pygame.draw.rect(surface, (140, 140, 150), (x + 9, 0, 5, 2))
        # 横臂高光
        pygame.draw.line(surface, (160, 160, 170), (x + 9, 0), (x + 13, 0))
        # 篮板（白色矩形，从横臂末端悬挂）
        pygame.draw.rect(surface, (240, 240, 245), (x + 10, 2, 5, 6))
        pygame.draw.rect(surface, (200, 200, 210), (x + 10, 2, 5, 6), 1)
        # 篮板内框（红色小方框）
        pygame.draw.rect(surface, (200, 60, 30), (x + 11, 3, 3, 3), 1)
        # 篮筐（红色圆环，从篮板底部伸出）
        pygame.draw.rect(surface, (200, 60, 30), (x + 9, 8, 6, 2))
        # 篮筐端点（圆环效果）
        surface.set_at((x + 9, 9), (180, 50, 25))
        surface.set_at((x + 14, 9), (180, 50, 25))
        # 篮网（白色线条）
        for nx in range(10, 15, 2):
            pygame.draw.line(surface, (230, 230, 230), (x + nx, 10), (x + nx, 14))
        pygame.draw.line(surface, (230, 230, 230), (x + 10, 14), (x + 14, 14))
    elif gid == GID_HOOP_BOT:
        # 篮球架下部：支柱+底座
        surface.fill((0, 0, 0, 0), rect)
        # 支柱（灰色金属管，从上延伸到底座）
        pygame.draw.rect(surface, (140, 140, 150), (x + 7, 0, 2, 12))
        # 支柱高光
        surface.set_at((x + 7, 2), (165, 165, 175))
        surface.set_at((x + 7, 5), (165, 165, 175))
        surface.set_at((x + 7, 8), (165, 165, 175))
        # 底座（厚重的金属底座，确保稳定）
        pygame.draw.rect(surface, (100, 100, 110), (x + 4, 12, 8, 3))
        # 底座高光
        pygame.draw.rect(surface, (120, 120, 130), (x + 5, 12, 6, 1))
        # 底座暗面
        pygame.draw.rect(surface, (80, 80, 90), (x + 4, 14, 8, 1))
        # 底座阴影
        pygame.draw.rect(surface, (70, 70, 80), (x + 5, 15, 6, 1))
    elif gid == GID_SCOREBOARD:
        # 记分牌 - 透明背景，金属框+LED屏幕
        surface.fill((0, 0, 0, 0), rect)
        # 金属外框
        pygame.draw.rect(surface, (80, 80, 90), (x + 1, 1, 14, 14))
        # 顶部/左侧高光
        pygame.draw.line(surface, (120, 120, 130), (x + 1, 1), (x + 14, 1))
        pygame.draw.line(surface, (120, 120, 130), (x + 1, 1), (x + 1, 14))
        # 底部/右侧阴影
        pygame.draw.line(surface, (60, 60, 70), (x + 1, 14), (x + 14, 14))
        pygame.draw.line(surface, (60, 60, 70), (x + 14, 1), (x + 14, 14))
        # LED屏幕
        pygame.draw.rect(surface, (20, 20, 30), (x + 2, 2, 12, 8))
        # 左队分数（红色LED点阵）
        for dy in range(3):
            for dx in range(2):
                surface.set_at((x + 3 + dx, 3 + dy), (200, 40, 40))
                surface.set_at((x + 3 + dx, 3 + dy), (200, 40, 40))
        pygame.draw.rect(surface, (200, 40, 40), (x + 3, 3, 2, 3))
        pygame.draw.rect(surface, (200, 40, 40), (x + 5, 3, 1, 3))
        # LED暗纹（未亮的LED点）
        for dy in range(3):
            for dx in range(2):
                surface.set_at((x + 6 + dx, 3 + dy), (30, 30, 40))
        # 冒号
        surface.set_at((x + 8, 4), (200, 40, 40))
        surface.set_at((x + 8, 6), (200, 40, 40))
        # 右队分数（蓝色LED点阵）
        pygame.draw.rect(surface, (40, 80, 200), (x + 9, 3, 2, 3))
        pygame.draw.rect(surface, (40, 80, 200), (x + 11, 3, 1, 3))
        # LED暗纹
        for dy in range(3):
            for dx in range(2):
                surface.set_at((x + 12 + dx, 3 + dy), (30, 30, 40))
        # 队名区
        pygame.draw.rect(surface, (60, 20, 20), (x + 2, 10, 6, 2))
        pygame.draw.rect(surface, (20, 20, 60), (x + 8, 10, 6, 2))
        # 队名文字横线模拟
        pygame.draw.line(surface, (100, 40, 40), (x + 3, 11), (x + 6, 11))
        pygame.draw.line(surface, (40, 40, 100), (x + 9, 11), (x + 12, 11))
        # 底部指示灯
        surface.set_at((x + 4, 13), (200, 50, 50))
        surface.set_at((x + 6, 13), (50, 200, 50))
        surface.set_at((x + 9, 13), (200, 200, 50))
        surface.set_at((x + 11, 13), (50, 50, 200))
        # 顶部挂钩
        surface.set_at((x + 4, 0), (100, 100, 110))
        surface.set_at((x + 11, 0), (100, 100, 110))
    elif gid == GID_COMPUTER:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (60, 60, 60), (x + 2, 1, 12, 9))
        pygame.draw.rect(surface, (80, 120, 180), (x + 3, 2, 10, 7))
        pygame.draw.rect(surface, (60, 60, 60), (x + 6, 10, 4, 2))
        pygame.draw.rect(surface, (80, 80, 80), (x + 4, 12, 8, 2))
        for dx, dy in [(5, 4), (8, 3), (11, 5)]:
            surface.set_at((x + dx, dy), (150, 200, 255))
    elif gid == GID_DOOR_INDOOR:
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (101, 67, 33), (x + 3, 1, 10, 14))
        pygame.draw.rect(surface, (80, 50, 25), (x + 3, 1, 10, 14), 1)
        pygame.draw.circle(surface, (200, 180, 50), (x + 11, 8), 1)
    elif gid == GID_COLLISION:
        surface.fill((0, 0, 0, 0), rect)
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
        surface.fill((0, 0, 0, 0), rect)
        pygame.draw.rect(surface, (100, 60, 30), (x + 1, 1, 14, 14))
        pygame.draw.rect(surface, (130, 80, 40), (x + 2, 2, 12, 12))
        pygame.draw.rect(surface, (160, 100, 50), (x + 4, 4, 8, 8))
        for dx, dy in [(5, 5), (9, 5), (5, 9), (9, 9)]:
            surface.set_at((x + dx, dy), (180, 120, 60))
    elif gid == GID_BLACKBOARD:
        surface.fill((0, 0, 0, 0), rect)
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
        # 图书馆墙壁顶部 - 暖黄底色+护墙板分隔线延伸
        surface.fill((220, 200, 160), rect)
        # 顶部3px暗带（护墙板分隔线延伸）
        pygame.draw.rect(surface, (200, 180, 140), (x, 0, TILE_SIZE, 3))
        pygame.draw.line(surface, (190, 170, 130), (x, 2), (x + TILE_SIZE, 2))
        # 底部暗线
        pygame.draw.line(surface, (180, 150, 100), (x, 15), (x + TILE_SIZE, 15))
        # 护墙板竖线延伸
        for bx in [4, 8, 12]:
            pygame.draw.line(surface, (190, 170, 130), (x + bx, 3), (x + bx, TILE_SIZE))
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
        surface.fill((0, 0, 0, 0), rect)
        # 灯柱
        pygame.draw.rect(surface, (80, 80, 80), (x + 7, 6, 2, 8))
        # 灯罩（三角形）
        pygame.draw.polygon(surface, (200, 180, 50),
                            [(x + 5, 3), (x + 10, 3), (x + 7, 1)])
        # 暖光光晕
        glow = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 240, 180, 55), (3, 3), 3)
        surface.blit(glow, (x + 5, 5))
    # 体育馆室内专属 tile
    elif gid == GID_GYM_WALL:
        surface.fill((240, 240, 245), rect)
        pygame.draw.rect(surface, (40, 80, 160), (x, 5, TILE_SIZE, 2))
        pygame.draw.rect(surface, (40, 80, 160), (x, 12, TILE_SIZE, 2))
        pygame.draw.line(surface, (230, 230, 235), (x + 8, 0), (x + 8, TILE_SIZE))
    elif gid == GID_GYM_WALL_TOP:
        # 体育馆墙壁顶部 - 白色底+蓝色条纹延伸
        surface.fill((240, 240, 245), rect)
        pygame.draw.rect(surface, (220, 220, 225), (x, 0, TILE_SIZE, 3))
        # 蓝色条纹延伸（2条蓝色横线）
        pygame.draw.rect(surface, (40, 80, 160), (x, 5, TILE_SIZE, 2))
        pygame.draw.rect(surface, (40, 80, 160), (x, 12, TILE_SIZE, 2))
    elif gid == GID_GYM_LOCKER:
        surface.fill((0, 0, 0, 0), rect)
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
        # 食堂墙壁顶部 - 白色底+橙色腰线延伸
        surface.fill((245, 245, 245), rect)
        pygame.draw.rect(surface, (225, 225, 225), (x, 0, TILE_SIZE, 3))
        # 橙色腰线延伸
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
        # 综合楼墙壁顶部 - 浅灰白底+灰色踢脚线延伸+横向装饰条
        surface.fill((240, 240, 242), rect)
        pygame.draw.rect(surface, (225, 225, 228), (x, 0, TILE_SIZE, 3))
        # 横向装饰条
        pygame.draw.line(surface, (230, 230, 232), (x, 6), (x + TILE_SIZE, 6))
        # 灰色踢脚线延伸
        pygame.draw.rect(surface, (180, 180, 185), (x, 13, TILE_SIZE, 3))
    elif gid == GID_NANHU_FLOOR:
        # 综合楼大理石地面 - 丰富纹路
        surface.fill((195, 195, 200), rect)
        # 大理石纹路（6条不同角度的斜线）
        pygame.draw.line(surface, (185, 185, 190), (x + 1, 1), (x + 6, 6))
        pygame.draw.line(surface, (188, 188, 193), (x + 9, 2), (x + 14, 10))
        pygame.draw.line(surface, (183, 183, 188), (x + 3, 8), (x + 12, 14))
        pygame.draw.line(surface, (186, 186, 191), (x + 0, 5), (x + 5, 15))
        pygame.draw.line(surface, (190, 190, 195), (x + 10, 0), (x + 15, 7))
        pygame.draw.line(surface, (184, 184, 189), (x + 7, 9), (x + 14, 15))
        # 高光/暗面渐变像素
        for dx, dy in [(1, 1), (6, 3), (12, 6), (3, 10), (9, 12), (14, 2), (7, 7), (2, 14)]:
            surface.set_at((x + dx, dy), (205, 205, 210))
        for dx, dy in [(4, 4), (10, 8), (13, 13), (0, 9)]:
            surface.set_at((x + dx, dy), (180, 180, 185))
        # 网格线（瓷砖缝）
        pygame.draw.line(surface, (190, 190, 195), (x + 8, 0), (x + 8, TILE_SIZE))
        pygame.draw.line(surface, (190, 190, 195), (x, 8), (x + TILE_SIZE, 8))
        # 微小斑点模拟石材天然纹理
        for dx, dy in [(5, 2), (11, 5), (3, 12), (14, 10)]:
            surface.set_at((x + dx, dy), (175, 175, 180))
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
        # 密室墙壁顶部 - 深灰棕底+砖缝纹理延伸
        surface.fill((70, 65, 60), rect)
        pygame.draw.rect(surface, (55, 50, 45), (x, 0, TILE_SIZE, 3))
        # 砖缝纹理延伸
        for yy in [4, 8]:
            pygame.draw.line(surface, (55, 50, 45), (x, yy), (x + TILE_SIZE, yy))
        for bx in [4, 12]:
            pygame.draw.line(surface, (55, 50, 45), (x + bx, 4), (x + bx, 8))
        pygame.draw.line(surface, (55, 50, 45), (x + 8, 8), (x + 8, 12))
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
    # 体育馆设施 tile（多部件拼接）
    elif gid == GID_GYM_TABLE_TL:
        # 体育馆桌子左上：桌面左半+运动水壶+毛巾
        surface.fill((0, 0, 0, 0), rect)
        # 桌面（浅灰金属质感）
        pygame.draw.rect(surface, (180, 185, 190), (x, 3, 16, 5))
        # 桌面高光
        pygame.draw.rect(surface, (200, 205, 210), (x + 1, 3, 14, 1))
        # 桌面暗边
        pygame.draw.rect(surface, (155, 160, 165), (x, 7, 16, 1))
        # 前面板
        pygame.draw.rect(surface, (165, 170, 175), (x, 8, 16, 3))
        # 前面板暗线
        pygame.draw.rect(surface, (145, 150, 155), (x, 10, 16, 1))
        # 运动水壶（蓝色，桌面左侧）
        pygame.draw.rect(surface, (50, 100, 180), (x + 3, 1, 3, 3))
        pygame.draw.rect(surface, (40, 80, 150), (x + 3, 0, 3, 1))
        surface.set_at((x + 4, 1), (80, 130, 210))
        # 毛巾（白色折叠条）
        pygame.draw.rect(surface, (230, 230, 235), (x + 8, 4, 5, 2))
        pygame.draw.rect(surface, (210, 210, 215), (x + 8, 5, 5, 1))
    elif gid == GID_GYM_TABLE_TR:
        # 体育馆桌子右上：桌面右半+记事板
        surface.fill((0, 0, 0, 0), rect)
        # 桌面
        pygame.draw.rect(surface, (180, 185, 190), (x, 3, 16, 5))
        # 桌面高光
        pygame.draw.rect(surface, (200, 205, 210), (x, 3, 14, 1))
        # 桌面暗边
        pygame.draw.rect(surface, (155, 160, 165), (x, 7, 16, 1))
        # 前面板
        pygame.draw.rect(surface, (165, 170, 175), (x, 8, 16, 3))
        # 前面板暗线
        pygame.draw.rect(surface, (145, 150, 155), (x, 10, 16, 1))
        # 记事板（棕色夹板+白纸）
        pygame.draw.rect(surface, (140, 100, 50), (x + 2, 1, 5, 3))
        pygame.draw.rect(surface, (240, 240, 240), (x + 3, 2, 3, 1))
    elif gid == GID_GYM_TABLE_BL:
        # 体育馆桌子左下：左桌腿+横撑左半
        surface.fill((0, 0, 0, 0), rect)
        # 左桌腿（金属管，1px宽体现细管感）
        pygame.draw.rect(surface, (140, 145, 150), (x + 3, 0, 2, 14))
        # 桌腿高光
        surface.set_at((x + 3, 1), (165, 170, 175))
        surface.set_at((x + 3, 3), (165, 170, 175))
        # 横撑（连接两腿的金属杆）
        pygame.draw.rect(surface, (130, 135, 140), (x + 3, 6, 13, 1))
        # 横撑高光
        pygame.draw.line(surface, (150, 155, 160), (x + 3, 5), (x + 15, 5))
        # 地面阴影
        pygame.draw.rect(surface, (120, 125, 130), (x + 2, 14, 3, 1))
    elif gid == GID_GYM_TABLE_BR:
        # 体育馆桌子右下：右桌腿+横撑右半
        surface.fill((0, 0, 0, 0), rect)
        # 右桌腿
        pygame.draw.rect(surface, (140, 145, 150), (x + 11, 0, 2, 14))
        # 桌腿高光
        surface.set_at((x + 11, 1), (165, 170, 175))
        surface.set_at((x + 11, 3), (165, 170, 175))
        # 横撑右半
        pygame.draw.rect(surface, (130, 135, 140), (x, 6, 12, 1))
        # 横撑高光
        pygame.draw.line(surface, (150, 155, 160), (x, 5), (x + 11, 5))
        # 地面阴影
        pygame.draw.rect(surface, (120, 125, 130), (x + 10, 14, 3, 1))
    elif gid == GID_GYM_TROPHY_TL:
        # 奖杯展示柜左上：柜顶装饰+玻璃罩左上+金色奖杯上部
        surface.fill((0, 0, 0, 0), rect)
        # 柜顶装饰线（深色木框）
        pygame.draw.rect(surface, (90, 55, 25), (x, 0, 16, 2))
        pygame.draw.rect(surface, (110, 70, 35), (x + 1, 0, 14, 1))
        # 玻璃罩（浅蓝半透明）
        pygame.draw.rect(surface, (200, 215, 235), (x + 1, 2, 15, 13))
        # 玻璃边框
        pygame.draw.rect(surface, (170, 185, 210), (x + 1, 2, 15, 13), 1)
        # 玻璃反光（左上竖线）
        pygame.draw.line(surface, (225, 235, 250), (x + 2, 3), (x + 2, 13))
        # 金色奖杯上部（杯口+杯身）
        pygame.draw.rect(surface, (220, 180, 50), (x + 4, 4, 5, 1))
        pygame.draw.rect(surface, (220, 180, 50), (x + 5, 5, 3, 4))
        # 奖杯高光
        surface.set_at((x + 6, 5), (240, 210, 90))
    elif gid == GID_GYM_TROPHY_TR:
        # 奖杯展示柜右上：柜顶装饰+玻璃罩右上+银色奖杯上部
        surface.fill((0, 0, 0, 0), rect)
        # 柜顶装饰线
        pygame.draw.rect(surface, (90, 55, 25), (x, 0, 16, 2))
        pygame.draw.rect(surface, (110, 70, 35), (x + 1, 0, 14, 1))
        # 玻璃罩
        pygame.draw.rect(surface, (200, 215, 235), (x, 2, 15, 13))
        # 玻璃边框
        pygame.draw.rect(surface, (170, 185, 210), (x, 2, 15, 13), 1)
        # 银色奖杯上部
        pygame.draw.rect(surface, (200, 200, 215), (x + 5, 5, 5, 1))
        pygame.draw.rect(surface, (200, 200, 215), (x + 6, 6, 3, 3))
        # 奖杯高光
        surface.set_at((x + 7, 6), (220, 220, 235))
    elif gid == GID_GYM_TROPHY_ML:
        # 奖杯展示柜左中：玻璃罩左中+金色奖杯底座+铜牌
        surface.fill((0, 0, 0, 0), rect)
        # 玻璃罩
        pygame.draw.rect(surface, (200, 215, 235), (x + 1, 0, 15, 16))
        pygame.draw.rect(surface, (170, 185, 210), (x + 1, 0, 15, 16), 1)
        # 玻璃反光
        pygame.draw.line(surface, (225, 235, 250), (x + 2, 0), (x + 2, 15))
        # 金色奖杯底座
        pygame.draw.rect(surface, (200, 160, 40), (x + 5, 0, 3, 1))
        pygame.draw.rect(surface, (180, 140, 30), (x + 4, 1, 5, 1))
        # 隔板（木质层板）
        pygame.draw.rect(surface, (100, 65, 30), (x + 1, 3, 14, 1))
        # 铜牌（第三层）
        pygame.draw.rect(surface, (180, 120, 50), (x + 5, 6, 3, 4))
        pygame.draw.rect(surface, (200, 140, 60), (x + 5, 6, 3, 1))
        # 铜牌绶带
        pygame.draw.rect(surface, (180, 40, 40), (x + 6, 5, 1, 1))
    elif gid == GID_GYM_TROPHY_MR:
        # 奖杯展示柜右中：玻璃罩右中+银色奖杯底座+奖状
        surface.fill((0, 0, 0, 0), rect)
        # 玻璃罩
        pygame.draw.rect(surface, (200, 215, 235), (x, 0, 15, 16))
        pygame.draw.rect(surface, (170, 185, 210), (x, 0, 15, 16), 1)
        # 银色奖杯底座
        pygame.draw.rect(surface, (180, 180, 195), (x + 6, 0, 3, 1))
        pygame.draw.rect(surface, (160, 160, 175), (x + 5, 1, 5, 1))
        # 隔板
        pygame.draw.rect(surface, (100, 65, 30), (x, 3, 15, 1))
        # 奖状（金色边框+白纸）
        pygame.draw.rect(surface, (200, 170, 50), (x + 3, 5, 7, 6))
        pygame.draw.rect(surface, (240, 235, 220), (x + 4, 6, 5, 4))
        # 奖状文字行
        for dy in range(3):
            surface.set_at((x + 5, 7 + dy), (100, 100, 120))
            surface.set_at((x + 7, 7 + dy), (100, 100, 120))
    elif gid == GID_GYM_TROPHY_BL:
        # 奖杯展示柜左下：木质底座左半+柜门+标签
        surface.fill((0, 0, 0, 0), rect)
        # 木质底座（深色）
        pygame.draw.rect(surface, (80, 50, 25), (x, 0, 16, 16))
        # 底座顶部装饰线
        pygame.draw.rect(surface, (100, 65, 35), (x, 0, 16, 1))
        # 柜门面板（略浅色）
        pygame.draw.rect(surface, (95, 60, 30), (x + 1, 2, 14, 12))
        # 柜门边框
        pygame.draw.rect(surface, (70, 42, 18), (x + 1, 2, 14, 12), 1)
        # 柜门拉手
        pygame.draw.rect(surface, (180, 160, 100), (x + 12, 7, 2, 2))
        # 标签牌（金色）
        pygame.draw.rect(surface, (200, 180, 50), (x + 3, 4, 6, 2))
        pygame.draw.rect(surface, (220, 200, 70), (x + 4, 4, 4, 1))
        # 底部踢脚线
        pygame.draw.rect(surface, (60, 35, 15), (x, 14, 16, 2))
    elif gid == GID_GYM_TROPHY_BR:
        # 奖杯展示柜右下：木质底座右半+柜门+标签
        surface.fill((0, 0, 0, 0), rect)
        # 木质底座
        pygame.draw.rect(surface, (80, 50, 25), (x, 0, 16, 16))
        # 底座顶部装饰线
        pygame.draw.rect(surface, (100, 65, 35), (x, 0, 16, 1))
        # 柜门面板
        pygame.draw.rect(surface, (95, 60, 30), (x + 1, 2, 14, 12))
        # 柜门边框
        pygame.draw.rect(surface, (70, 42, 18), (x + 1, 2, 14, 12), 1)
        # 柜门拉手
        pygame.draw.rect(surface, (180, 160, 100), (x + 2, 7, 2, 2))
        # 标签牌（银色）
        pygame.draw.rect(surface, (190, 190, 200), (x + 5, 4, 6, 2))
        pygame.draw.rect(surface, (210, 210, 220), (x + 6, 4, 4, 1))
        # 底部踢脚线
        pygame.draw.rect(surface, (60, 35, 15), (x, 14, 16, 2))
    elif gid == GID_GYM_WATER_TOP:
        # 饮水机顶部：水桶+机身顶部
        surface.fill((0, 0, 0, 0), rect)
        # 水桶（蓝色半透明，倒扣）
        pygame.draw.rect(surface, (100, 165, 225), (x + 4, 0, 8, 8))
        pygame.draw.rect(surface, (80, 145, 205), (x + 4, 0, 8, 8), 1)
        # 水桶颈部
        pygame.draw.rect(surface, (90, 155, 215), (x + 6, 0, 4, 2))
        # 水面高光
        pygame.draw.rect(surface, (130, 185, 245), (x + 5, 2, 3, 4))
        # 水桶底部（与机身衔接）
        pygame.draw.rect(surface, (85, 150, 210), (x + 5, 7, 6, 1))
        # 机身顶部
        pygame.draw.rect(surface, (230, 230, 235), (x + 3, 8, 10, 8))
        pygame.draw.rect(surface, (200, 200, 205), (x + 3, 8, 10, 8), 1)
        # 机身顶部圆弧
        pygame.draw.rect(surface, (235, 235, 240), (x + 4, 8, 8, 2))
    elif gid == GID_GYM_WATER_BOT:
        # 饮水机底部：出水口+按钮+接水盘
        surface.fill((0, 0, 0, 0), rect)
        # 机身
        pygame.draw.rect(surface, (230, 230, 235), (x + 3, 0, 10, 13))
        pygame.draw.rect(surface, (200, 200, 205), (x + 3, 0, 10, 13), 1)
        # 红色热水按钮
        pygame.draw.rect(surface, (200, 55, 55), (x + 5, 2, 2, 2))
        surface.set_at((x + 5, 2), (230, 80, 80))
        # 蓝色冷水按钮
        pygame.draw.rect(surface, (55, 100, 200), (x + 9, 2, 2, 2))
        surface.set_at((x + 9, 2), (80, 130, 230))
        # 出水口
        pygame.draw.rect(surface, (180, 180, 185), (x + 7, 5, 2, 3))
        # 接水盘
        pygame.draw.rect(surface, (190, 190, 195), (x + 4, 9, 8, 1))
        # 盘中水滴
        surface.set_at((x + 7, 10), (150, 200, 240))
        # 机身底座
        pygame.draw.rect(surface, (200, 200, 205), (x + 3, 11, 10, 2))
        # 地面阴影
        pygame.draw.rect(surface, (170, 170, 175), (x + 4, 14, 8, 1))
    elif gid == GID_GYM_BENCH_L:
        # 体育馆替补长凳左半：加厚蓝色软垫+粗金属支架+横撑+左扶手
        surface.fill((0, 0, 0, 0), rect)
        # 左扶手（圆弧形金属扶手，体育馆长凳标志性特征）
        pygame.draw.rect(surface, (160, 165, 175), (x + 1, 1, 2, 3))
        pygame.draw.rect(surface, (175, 180, 190), (x + 1, 1, 2, 1))
        # 扶手顶部圆弧
        surface.set_at((x + 2, 0), (160, 165, 175))
        # 软垫座面（深蓝色乙烯基，加厚设计，占更多画面）
        pygame.draw.rect(surface, (30, 60, 135), (x + 1, 4, 15, 7))
        # 软垫高光（上方亮面，体现皮质光泽）
        pygame.draw.rect(surface, (45, 80, 165), (x + 2, 4, 13, 3))
        # 软垫缝线（3条竖线，体现软垫分区）
        pygame.draw.line(surface, (25, 50, 120), (x + 5, 5), (x + 5, 10))
        pygame.draw.line(surface, (25, 50, 120), (x + 9, 5), (x + 9, 10))
        pygame.draw.line(surface, (25, 50, 120), (x + 13, 5), (x + 13, 10))
        # 软垫暗面（下方阴影）
        pygame.draw.rect(surface, (20, 45, 110), (x + 2, 10, 13, 1))
        # 金属左腿（粗管状，2px宽，清晰可见）
        pygame.draw.rect(surface, (145, 150, 160), (x + 2, 11, 2, 4))
        # 腿部高光
        surface.set_at((x + 2, 12), (170, 175, 185))
        surface.set_at((x + 2, 13), (170, 175, 185))
        # 横撑（连接前后腿的横杆，体育馆长凳特征）
        pygame.draw.rect(surface, (135, 140, 150), (x + 2, 13, 14, 1))
        # 横撑高光
        pygame.draw.line(surface, (155, 160, 170), (x + 2, 12), (x + 15, 12))
        # 底部脚垫
        pygame.draw.rect(surface, (100, 100, 110), (x + 1, 14, 3, 1))
    elif gid == GID_GYM_BENCH_R:
        # 体育馆替补长凳右半：加厚蓝色软垫+粗金属支架+横撑+右扶手
        surface.fill((0, 0, 0, 0), rect)
        # 右扶手
        pygame.draw.rect(surface, (160, 165, 175), (x + 13, 1, 2, 3))
        pygame.draw.rect(surface, (175, 180, 190), (x + 13, 1, 2, 1))
        # 扶手顶部圆弧
        surface.set_at((x + 13, 0), (160, 165, 175))
        # 软垫座面
        pygame.draw.rect(surface, (30, 60, 135), (x, 4, 15, 7))
        # 软垫高光
        pygame.draw.rect(surface, (45, 80, 165), (x + 1, 4, 13, 3))
        # 软垫缝线
        pygame.draw.line(surface, (25, 50, 120), (x + 3, 5), (x + 3, 10))
        pygame.draw.line(surface, (25, 50, 120), (x + 7, 5), (x + 7, 10))
        pygame.draw.line(surface, (25, 50, 120), (x + 11, 5), (x + 11, 10))
        # 软垫暗面
        pygame.draw.rect(surface, (20, 45, 110), (x + 1, 10, 13, 1))
        # 金属右腿（粗管状）
        pygame.draw.rect(surface, (145, 150, 160), (x + 12, 11, 2, 4))
        # 腿部高光
        surface.set_at((x + 12, 12), (170, 175, 185))
        surface.set_at((x + 12, 13), (170, 175, 185))
        # 横撑右半
        pygame.draw.rect(surface, (135, 140, 150), (x, 13, 13, 1))
        # 横撑高光
        pygame.draw.line(surface, (155, 160, 170), (x, 12), (x + 12, 12))
        # 底部脚垫
        pygame.draw.rect(surface, (100, 100, 110), (x + 12, 14, 3, 1))
    elif gid == GID_GYM_MAT_L:
        # 体操垫左部（展开铺平）：左圆角+4面板折叠+防滑纹理+厚度+固定带
        surface.fill((0, 0, 0, 0), rect)
        # 垫子主体（蓝色，俯视角平铺）
        pygame.draw.rect(surface, (50, 100, 180), (x + 2, 2, 14, 12))
        # 左侧圆角
        pygame.draw.rect(surface, (50, 100, 180), (x + 3, 1, 13, 1))
        pygame.draw.rect(surface, (50, 100, 180), (x + 4, 0, 12, 1))
        # 垫子厚度边缘（深色描边，体现约5cm厚度）
        pygame.draw.rect(surface, (30, 70, 145), (x + 2, 2, 14, 12), 1)
        pygame.draw.rect(surface, (30, 70, 145), (x + 3, 1, 13, 1), 1)
        pygame.draw.rect(surface, (30, 70, 145), (x + 4, 0, 12, 1), 1)
        # 面板1高光区（上半部分）
        pygame.draw.rect(surface, (65, 118, 200), (x + 3, 3, 12, 3))
        # 面板1防滑纹理（十字交叉纹路）
        for dy in range(3, 6):
            for dx in range(4, 14, 3):
                surface.set_at((x + dx, dy), (55, 108, 190))
        # 折叠接缝线1（面板1和面板2之间，暗色+高光体现层次差）
        pygame.draw.line(surface, (25, 60, 130), (x + 3, 6), (x + 14, 6))
        pygame.draw.line(surface, (75, 128, 210), (x + 3, 7), (x + 14, 7))
        # 面板2
        pygame.draw.rect(surface, (55, 105, 185), (x + 3, 7, 12, 4))
        # 面板2防滑纹理
        for dy in range(8, 11):
            for dx in range(4, 14, 3):
                surface.set_at((x + dx, dy), (48, 95, 175))
        # 折叠接缝线2（面板2和面板3之间）
        pygame.draw.line(surface, (25, 60, 130), (x + 3, 11), (x + 14, 11))
        pygame.draw.line(surface, (75, 128, 210), (x + 3, 12), (x + 14, 12))
        # 面板3（底部，略暗，体现阴影）
        pygame.draw.rect(surface, (45, 92, 170), (x + 3, 12, 12, 2))
        # 左上角固定带（魔术贴绑带）
        pygame.draw.rect(surface, (200, 180, 50), (x + 3, 3, 2, 1))
        # 左下角固定带
        pygame.draw.rect(surface, (200, 180, 50), (x + 3, 13, 2, 1))
    elif gid == GID_GYM_MAT_M:
        # 体操垫中部（展开铺平）：4面板折叠+防滑纹理+厚度+固定带
        surface.fill((0, 0, 0, 0), rect)
        # 垫子主体
        pygame.draw.rect(surface, (50, 100, 180), (x, 2, 16, 12))
        # 垫子厚度边缘
        pygame.draw.rect(surface, (30, 70, 145), (x, 2, 16, 12), 1)
        # 面板1高光区
        pygame.draw.rect(surface, (65, 118, 200), (x + 1, 3, 14, 3))
        # 面板1防滑纹理
        for dy in range(3, 6):
            for dx in range(2, 15, 3):
                surface.set_at((x + dx, dy), (55, 108, 190))
        # 折叠接缝线1
        pygame.draw.line(surface, (25, 60, 130), (x + 1, 6), (x + 14, 6))
        pygame.draw.line(surface, (75, 128, 210), (x + 1, 7), (x + 14, 7))
        # 面板2
        pygame.draw.rect(surface, (55, 105, 185), (x + 1, 7, 14, 4))
        # 面板2防滑纹理
        for dy in range(8, 11):
            for dx in range(2, 15, 3):
                surface.set_at((x + dx, dy), (48, 95, 175))
        # 折叠接缝线2
        pygame.draw.line(surface, (25, 60, 130), (x + 1, 11), (x + 14, 11))
        pygame.draw.line(surface, (75, 128, 210), (x + 1, 12), (x + 14, 12))
        # 面板3
        pygame.draw.rect(surface, (45, 92, 170), (x + 1, 12, 14, 2))
        # 中部纵向折叠线（体操垫通常沿长边折叠）
        pygame.draw.line(surface, (40, 85, 165), (x + 8, 3), (x + 8, 13))
    elif gid == GID_GYM_MAT_R:
        # 体操垫右部（展开铺平）：右圆角+4面板折叠+防滑纹理+厚度+固定带
        surface.fill((0, 0, 0, 0), rect)
        # 垫子主体
        pygame.draw.rect(surface, (50, 100, 180), (x, 2, 14, 12))
        # 右侧圆角
        pygame.draw.rect(surface, (50, 100, 180), (x, 1, 13, 1))
        pygame.draw.rect(surface, (50, 100, 180), (x, 0, 12, 1))
        # 垫子厚度边缘
        pygame.draw.rect(surface, (30, 70, 145), (x, 2, 14, 12), 1)
        pygame.draw.rect(surface, (30, 70, 145), (x, 1, 13, 1), 1)
        pygame.draw.rect(surface, (30, 70, 145), (x, 0, 12, 1), 1)
        # 面板1高光区
        pygame.draw.rect(surface, (65, 118, 200), (x + 1, 3, 12, 3))
        # 面板1防滑纹理
        for dy in range(3, 6):
            for dx in range(2, 12, 3):
                surface.set_at((x + dx, dy), (55, 108, 190))
        # 折叠接缝线1
        pygame.draw.line(surface, (25, 60, 130), (x + 1, 6), (x + 12, 6))
        pygame.draw.line(surface, (75, 128, 210), (x + 1, 7), (x + 12, 7))
        # 面板2
        pygame.draw.rect(surface, (55, 105, 185), (x + 1, 7, 12, 4))
        # 面板2防滑纹理
        for dy in range(8, 11):
            for dx in range(2, 12, 3):
                surface.set_at((x + dx, dy), (48, 95, 175))
        # 折叠接缝线2
        pygame.draw.line(surface, (25, 60, 130), (x + 1, 11), (x + 12, 11))
        pygame.draw.line(surface, (75, 128, 210), (x + 1, 12), (x + 12, 12))
        # 面板3
        pygame.draw.rect(surface, (45, 92, 170), (x + 1, 12, 12, 2))
        # 右上角固定带
        pygame.draw.rect(surface, (200, 180, 50), (x + 11, 3, 2, 1))
        # 右下角固定带
        pygame.draw.rect(surface, (200, 180, 50), (x + 11, 13, 2, 1))
    elif gid == GID_GYM_EQUIP_L:
        # 器材柜左半：金属框架+3个储物格+球类+标签+滑轮
        surface.fill((0, 0, 0, 0), rect)
        # 柜体（银灰色金属）
        pygame.draw.rect(surface, (170, 175, 185), (x, 1, 16, 13))
        # 柜体边框
        pygame.draw.rect(surface, (130, 135, 145), (x, 1, 16, 13), 1)
        # 顶部横梁
        pygame.draw.rect(surface, (150, 155, 165), (x, 1, 16, 2))
        # 格1（左上）：篮球（橙色圆）
        pygame.draw.rect(surface, (155, 160, 170), (x + 1, 3, 6, 4))
        pygame.draw.rect(surface, (130, 135, 145), (x + 1, 3, 6, 4), 1)
        pygame.draw.circle(surface, (220, 130, 40), (x + 4, 5), 2)
        # 篮球纹线
        surface.set_at((x + 3, 4), (200, 110, 30))
        surface.set_at((x + 5, 5), (200, 110, 30))
        # 格1标签
        pygame.draw.rect(surface, (240, 240, 240), (x + 2, 7, 4, 1))
        # 格2（左中）：排球（蓝白条纹）
        pygame.draw.rect(surface, (155, 160, 170), (x + 1, 8, 6, 4))
        pygame.draw.rect(surface, (130, 135, 145), (x + 1, 8, 6, 4), 1)
        pygame.draw.circle(surface, (240, 240, 250), (x + 4, 10), 2)
        # 排球条纹
        surface.set_at((x + 3, 9), (60, 100, 200))
        surface.set_at((x + 5, 10), (60, 100, 200))
        surface.set_at((x + 4, 9), (60, 100, 200))
        # 格2标签
        pygame.draw.rect(surface, (240, 240, 240), (x + 2, 12, 4, 1))
        # 底部横梁
        pygame.draw.rect(surface, (150, 155, 165), (x, 13, 16, 1))
        # 滑轮（底部2个）
        pygame.draw.rect(surface, (80, 80, 90), (x + 3, 14, 2, 2))
        pygame.draw.rect(surface, (100, 100, 110), (x + 3, 14, 2, 1))
    elif gid == GID_GYM_EQUIP_R:
        # 器材柜右半：金属框架+3个储物格+球类+标签+滑轮
        surface.fill((0, 0, 0, 0), rect)
        # 柜体
        pygame.draw.rect(surface, (170, 175, 185), (x, 1, 16, 13))
        # 柜体边框
        pygame.draw.rect(surface, (130, 135, 145), (x, 1, 16, 13), 1)
        # 顶部横梁
        pygame.draw.rect(surface, (150, 155, 165), (x, 1, 16, 2))
        # 格3（右上）：足球（黑白）
        pygame.draw.rect(surface, (155, 160, 170), (x + 1, 3, 6, 4))
        pygame.draw.rect(surface, (130, 135, 145), (x + 1, 3, 6, 4), 1)
        pygame.draw.circle(surface, (240, 240, 240), (x + 4, 5), 2)
        # 足球黑色五边形纹
        surface.set_at((x + 4, 4), (40, 40, 50))
        surface.set_at((x + 3, 5), (40, 40, 50))
        surface.set_at((x + 5, 5), (40, 40, 50))
        # 格3标签
        pygame.draw.rect(surface, (240, 240, 240), (x + 2, 7, 4, 1))
        # 格4（右中）：羽毛球拍+球
        pygame.draw.rect(surface, (155, 160, 170), (x + 1, 8, 6, 4))
        pygame.draw.rect(surface, (130, 135, 145), (x + 1, 8, 6, 4), 1)
        # 羽毛球拍（竖线+椭圆拍头）
        pygame.draw.line(surface, (140, 100, 50), (x + 3, 9), (x + 3, 11))
        pygame.draw.rect(surface, (180, 180, 190), (x + 2, 8, 3, 2))
        pygame.draw.rect(surface, (160, 160, 170), (x + 2, 8, 3, 2), 1)
        # 羽毛球（白色小圆+尾部）
        pygame.draw.circle(surface, (240, 240, 240), (x + 6, 10), 1)
        surface.set_at((x + 7, 10), (220, 220, 220))
        # 格4标签
        pygame.draw.rect(surface, (240, 240, 240), (x + 2, 12, 4, 1))
        # 格5（右下角小格）：跳绳/手球
        pygame.draw.rect(surface, (155, 160, 170), (x + 9, 3, 6, 4))
        pygame.draw.rect(surface, (130, 135, 145), (x + 9, 3, 6, 4), 1)
        # 手球（红色小球）
        pygame.draw.circle(surface, (200, 60, 60), (x + 12, 5), 2)
        surface.set_at((x + 12, 4), (220, 80, 80))
        # 格5标签
        pygame.draw.rect(surface, (240, 240, 240), (x + 10, 7, 4, 1))
        # 格6（右下小格）：哨子/秒表
        pygame.draw.rect(surface, (155, 160, 170), (x + 9, 8, 6, 4))
        pygame.draw.rect(surface, (130, 135, 145), (x + 9, 8, 6, 4), 1)
        # 秒表（圆形+按钮）
        pygame.draw.circle(surface, (60, 60, 70), (x + 12, 10), 2)
        surface.set_at((x + 12, 8), (80, 80, 90))
        # 格6标签
        pygame.draw.rect(surface, (240, 240, 240), (x + 10, 12, 4, 1))
        # 底部横梁
        pygame.draw.rect(surface, (150, 155, 165), (x, 13, 16, 1))
        # 滑轮（底部2个）
        pygame.draw.rect(surface, (80, 80, 90), (x + 11, 14, 2, 2))
        pygame.draw.rect(surface, (100, 100, 110), (x + 11, 14, 2, 1))
    elif gid == GID_SECTION_SIGN:
        # 分区标识牌 - 小木牌
        surface.fill((0, 0, 0, 0), rect)
        # 木牌底板
        pygame.draw.rect(surface, (120, 80, 40), (x + 2, 2, 12, 12))
        pygame.draw.rect(surface, (140, 95, 50), (x + 3, 3, 10, 10))
        # 边框
        pygame.draw.rect(surface, (80, 50, 25), (x + 2, 2, 12, 12), 1)
        # 文字区域（浅色底）
        pygame.draw.rect(surface, (240, 230, 200), (x + 4, 4, 8, 8))
        # 简单文字线条（代表文字）
        pygame.draw.line(surface, (60, 40, 20), (x + 5, 6), (x + 11, 6))
        pygame.draw.line(surface, (60, 40, 20), (x + 5, 8), (x + 9, 8))
        pygame.draw.line(surface, (60, 40, 20), (x + 5, 10), (x + 11, 10))
    elif gid == GID_DISPLAY_CABINET:
        # 展示柜 - 玻璃柜
        surface.fill((0, 0, 0, 0), rect)
        # 柜体
        pygame.draw.rect(surface, (101, 67, 33), (x + 1, 2, 14, 12))
        # 玻璃面板
        pygame.draw.rect(surface, (180, 210, 230), (x + 2, 3, 12, 6))
        pygame.draw.rect(surface, (160, 190, 210), (x + 2, 3, 12, 6), 1)
        # 玻璃反光
        pygame.draw.line(surface, (220, 240, 255), (x + 3, 4), (x + 6, 4))
        pygame.draw.line(surface, (220, 240, 255), (x + 3, 5), (x + 5, 5))
        # 底部木框
        pygame.draw.rect(surface, (80, 50, 25), (x + 1, 9, 14, 2))
        # 柜内物品（小方块代表展品）
        pygame.draw.rect(surface, (200, 180, 140), (x + 4, 10, 3, 3))
        pygame.draw.rect(surface, (140, 160, 180), (x + 9, 10, 3, 3))
        # 底座
        pygame.draw.rect(surface, (80, 50, 25), (x + 2, 13, 12, 2))
    elif gid == GID_POTTED_PLANT:
        # 盆栽
        surface.fill((0, 0, 0, 0), rect)
        # 花盆
        pygame.draw.rect(surface, (160, 80, 40), (x + 5, 10, 6, 5))
        pygame.draw.rect(surface, (140, 65, 30), (x + 4, 10, 8, 1))
        # 土壤
        pygame.draw.rect(surface, (100, 70, 40), (x + 5, 10, 6, 2))
        # 植物茎
        pygame.draw.line(surface, (50, 100, 40), (x + 8, 10), (x + 8, 4))
        # 叶子
        pygame.draw.circle(surface, (60, 130, 50), (x + 6, 5), 3)
        pygame.draw.circle(surface, (50, 120, 45), (x + 10, 4), 3)
        pygame.draw.circle(surface, (70, 140, 55), (x + 8, 3), 3)
        pygame.draw.circle(surface, (55, 125, 48), (x + 5, 7), 2)
        pygame.draw.circle(surface, (65, 135, 52), (x + 11, 6), 2)
    elif gid == GID_SOFA:
        # 沙发（2格宽，左半部分）
        surface.fill((0, 0, 0, 0), rect)
        # 靠背
        pygame.draw.rect(surface, (120, 60, 40), (x, 2, 16, 5))
        # 坐垫
        pygame.draw.rect(surface, (140, 75, 50), (x, 7, 16, 6))
        # 扶手
        pygame.draw.rect(surface, (100, 50, 35), (x, 2, 3, 11))
        pygame.draw.rect(surface, (100, 50, 35), (x + 13, 2, 3, 11))
        # 坐垫分隔线
        pygame.draw.line(surface, (120, 60, 40), (x + 8, 7), (x + 8, 12))
        # 靠背纹理
        pygame.draw.line(surface, (130, 65, 42), (x + 4, 3), (x + 4, 6))
        pygame.draw.line(surface, (130, 65, 42), (x + 8, 3), (x + 8, 6))
        pygame.draw.line(surface, (130, 65, 42), (x + 12, 3), (x + 12, 6))
        # 腿
        pygame.draw.rect(surface, (80, 50, 25), (x + 2, 13, 2, 2))
        pygame.draw.rect(surface, (80, 50, 25), (x + 12, 13, 2, 2))
    elif gid == GID_MENU_BOARD:
        # 食堂菜单牌 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 悬挂支架
        pygame.draw.line(surface, (80, 50, 25), (x + 4, 0), (x + 8, 3))
        pygame.draw.line(surface, (80, 50, 25), (x + 11, 0), (x + 8, 3))
        # 木框
        pygame.draw.rect(surface, (120, 80, 40), (x + 2, 3, 12, 11))
        # 内板
        pygame.draw.rect(surface, (240, 230, 200), (x + 3, 4, 10, 9))
        # 标题条
        pygame.draw.rect(surface, (230, 130, 50), (x + 4, 5, 8, 2))
        # 菜品文字线
        for ty in range(4):
            pygame.draw.line(surface, (100, 70, 40), (x + 4, 8 + ty * 2), (x + 9, 8 + ty * 2))
        # 价格标记
        surface.set_at((x + 11, 8), (200, 50, 50))
        surface.set_at((x + 11, 10), (200, 50, 50))
        surface.set_at((x + 11, 12), (200, 50, 50))
    elif gid == GID_DRINK_MACHINE:
        # 食堂饮料机 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 机身
        pygame.draw.rect(surface, (180, 180, 190), (x + 3, 1, 10, 13))
        # 顶部圆弧
        pygame.draw.rect(surface, (190, 190, 200), (x + 4, 0, 8, 2))
        # 透明门
        glass = pygame.Surface((8, 6), pygame.SRCALPHA)
        glass.fill((200, 220, 240, 120))
        surface.blit(glass, (x + 4, 2))
        # 反光竖线
        pygame.draw.line(surface, (230, 240, 255), (x + 5, 2), (x + 5, 7))
        # 饮料罐（门内可见）
        pygame.draw.rect(surface, (200, 50, 50), (x + 5, 3, 2, 3))
        pygame.draw.rect(surface, (220, 180, 40), (x + 7, 3, 2, 3))
        pygame.draw.rect(surface, (50, 100, 200), (x + 9, 3, 2, 3))
        # 出货口
        pygame.draw.rect(surface, (60, 60, 70), (x + 5, 9, 6, 2))
        # 按钮
        surface.set_at((x + 4, 9), (200, 50, 50))
        surface.set_at((x + 4, 10), (50, 200, 50))
        surface.set_at((x + 4, 11), (50, 50, 200))
        # 底座
        pygame.draw.rect(surface, (150, 150, 160), (x + 3, 14, 10, 1))
        # 阴影
        shadow = pygame.Surface((10, 1), pygame.SRCALPHA)
        shadow.fill((100, 100, 110, 80))
        surface.blit(shadow, (x + 3, 15))
    elif gid == GID_RETURN_DESK:
        # 图书馆还书台 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 台面
        pygame.draw.rect(surface, (110, 75, 40), (x + 1, 3, 14, 4))
        # 高光
        pygame.draw.line(surface, (135, 95, 55), (x + 1, 3), (x + 14, 3))
        # 暗边
        pygame.draw.line(surface, (90, 60, 30), (x + 1, 6), (x + 14, 6))
        # 还书槽
        pygame.draw.rect(surface, (40, 40, 50), (x + 5, 4, 6, 2))
        # 槽口高光
        pygame.draw.line(surface, (60, 60, 70), (x + 5, 4), (x + 10, 4))
        # 电脑屏幕（台面右侧）
        pygame.draw.rect(surface, (60, 60, 70), (x + 12, 2, 2, 1))
        pygame.draw.rect(surface, (60, 60, 70), (x + 12, 0, 2, 2))
        pygame.draw.rect(surface, (80, 120, 180), (x + 11, 0, 4, 2))
        # 前面板
        pygame.draw.rect(surface, (90, 60, 30), (x + 1, 7, 14, 5))
        # 暗线
        pygame.draw.line(surface, (80, 50, 25), (x + 1, 10), (x + 14, 10))
        # 底部阴影
        shadow = pygame.Surface((14, 1), pygame.SRCALPHA)
        shadow.fill((60, 35, 15, 80))
        surface.blit(shadow, (x + 1, 12))
    elif gid == GID_NEWSPAPER_RACK:
        # 图书馆报刊架 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 主体框架
        pygame.draw.rect(surface, (101, 67, 33), (x + 2, 1, 12, 13))
        # 边框
        pygame.draw.rect(surface, (80, 50, 25), (x + 2, 1, 12, 13), 1)
        # 倾斜展示面（3层）
        pygame.draw.rect(surface, (220, 210, 190), (x + 3, 2, 10, 3))
        # 杂志头
        pygame.draw.rect(surface, (200, 50, 50), (x + 4, 2, 3, 2))
        pygame.draw.rect(surface, (50, 80, 200), (x + 8, 2, 3, 2))
        # 第2层
        pygame.draw.rect(surface, (220, 210, 190), (x + 3, 6, 10, 3))
        pygame.draw.rect(surface, (50, 160, 60), (x + 4, 6, 3, 2))
        pygame.draw.rect(surface, (220, 180, 40), (x + 8, 6, 3, 2))
        # 第3层
        pygame.draw.rect(surface, (220, 210, 190), (x + 3, 10, 10, 3))
        pygame.draw.rect(surface, (140, 40, 140), (x + 4, 10, 3, 2))
        pygame.draw.rect(surface, (230, 130, 50), (x + 8, 10, 3, 2))
        # 隔板线
        pygame.draw.line(surface, (80, 50, 25), (x + 2, 5), (x + 14, 5))
        pygame.draw.line(surface, (80, 50, 25), (x + 2, 9), (x + 14, 9))
        # 底板
        pygame.draw.rect(surface, (80, 50, 25), (x + 2, 13, 12, 1))
        # 底部阴影
        shadow = pygame.Surface((12, 1), pygame.SRCALPHA)
        shadow.fill((60, 35, 15, 80))
        surface.blit(shadow, (x + 2, 14))
    elif gid == GID_WHITEBOARD:
        # 综合楼白板 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 金属边框
        pygame.draw.rect(surface, (160, 160, 170), (x + 1, 1, 14, 14))
        # 高光
        pygame.draw.line(surface, (190, 190, 200), (x + 1, 1), (x + 14, 1))
        pygame.draw.line(surface, (190, 190, 200), (x + 1, 1), (x + 1, 14))
        # 阴影
        pygame.draw.line(surface, (130, 130, 140), (x + 1, 14), (x + 14, 14))
        pygame.draw.line(surface, (130, 130, 140), (x + 14, 1), (x + 14, 14))
        # 白色板面
        pygame.draw.rect(surface, (245, 245, 250), (x + 2, 2, 12, 10))
        # 彩色磁贴
        pygame.draw.rect(surface, (220, 60, 60), (x + 3, 3, 2, 2))
        pygame.draw.rect(surface, (60, 100, 200), (x + 7, 4, 2, 2))
        pygame.draw.rect(surface, (60, 180, 80), (x + 11, 3, 2, 2))
        # 马克笔痕迹
        pygame.draw.line(surface, (200, 200, 210), (x + 3, 7), (x + 10, 7))
        pygame.draw.line(surface, (200, 200, 210), (x + 5, 9), (x + 12, 9))
        # 底部笔槽
        pygame.draw.rect(surface, (150, 150, 160), (x + 2, 12, 12, 2))
        # 3支笔
        surface.set_at((x + 4, 12), (220, 50, 50))
        surface.set_at((x + 7, 12), (50, 50, 220))
        surface.set_at((x + 10, 12), (30, 30, 30))
    elif gid == GID_FILE_CABINET:
        # 综合楼文件柜 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 柜体
        pygame.draw.rect(surface, (180, 180, 190), (x + 2, 1, 12, 13))
        # 边框
        pygame.draw.rect(surface, (140, 140, 150), (x + 2, 1, 12, 13), 1)
        # 高光
        pygame.draw.line(surface, (200, 200, 210), (x + 2, 1), (x + 2, 13))
        # 4层抽屉
        for i in range(4):
            dy = 2 + i * 3
            pygame.draw.rect(surface, (165, 165, 175), (x + 3, dy, 10, 2))
            # 抽屉分隔线
            pygame.draw.line(surface, (140, 140, 150), (x + 3, dy + 2), (x + 12, dy + 2))
            # 拉手
            surface.set_at((x + 7, dy), (200, 200, 210))
            surface.set_at((x + 8, dy), (200, 200, 210))
            # 标签槽
            pygame.draw.rect(surface, (220, 220, 230), (x + 5, dy + 1, 3, 1))
        # 底座
        pygame.draw.rect(surface, (140, 140, 150), (x + 2, 14, 12, 1))
        # 阴影
        shadow = pygame.Surface((12, 1), pygame.SRCALPHA)
        shadow.fill((100, 100, 110, 80))
        surface.blit(shadow, (x + 2, 15))
    elif gid == GID_STONE_PEDESTAL:
        # 密室石台 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 台面
        pygame.draw.rect(surface, (140, 138, 135), (x + 2, 2, 12, 3))
        # 高光
        pygame.draw.line(surface, (165, 163, 160), (x + 2, 2), (x + 13, 2))
        # 暗面
        pygame.draw.line(surface, (120, 118, 115), (x + 2, 4), (x + 13, 4))
        # 台柱
        pygame.draw.rect(surface, (130, 128, 125), (x + 5, 5, 6, 7))
        # 纹理线
        pygame.draw.line(surface, (120, 118, 115), (x + 7, 5), (x + 7, 11))
        pygame.draw.line(surface, (120, 118, 115), (x + 9, 5), (x + 9, 11))
        # 台座
        pygame.draw.rect(surface, (140, 138, 135), (x + 3, 12, 10, 2))
        # 暗面
        pygame.draw.line(surface, (110, 108, 105), (x + 3, 13), (x + 12, 13))
        # 台面物品（古书）
        pygame.draw.rect(surface, (120, 90, 50), (x + 5, 1, 6, 2))
        # 卷轴
        pygame.draw.rect(surface, (200, 180, 140), (x + 11, 1, 3, 1))
        # 绿色微光
        glow = pygame.Surface((4, 4), pygame.SRCALPHA)
        glow.fill((50, 180, 80, 40))
        surface.blit(glow, (x + 6, 0))
        surface.blit(glow, (x + 10, 2))
        # 阴影
        shadow = pygame.Surface((10, 1), pygame.SRCALPHA)
        shadow.fill((70, 65, 60, 80))
        surface.blit(shadow, (x + 3, 14))
    elif gid == GID_STONE_PILLAR_TOP:
        # 密室石柱上部 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 柱头装饰
        pygame.draw.rect(surface, (130, 128, 125), (x + 3, 0, 10, 3))
        # 柱头高光
        pygame.draw.line(surface, (155, 153, 150), (x + 3, 0), (x + 12, 0))
        # 柱头下沿暗线
        pygame.draw.line(surface, (110, 108, 105), (x + 3, 2), (x + 12, 2))
        # 柱身
        pygame.draw.rect(surface, (120, 118, 115), (x + 5, 3, 6, 13))
        # 纹理竖线
        pygame.draw.line(surface, (110, 108, 105), (x + 7, 3), (x + 7, 15))
        pygame.draw.line(surface, (110, 108, 105), (x + 9, 3), (x + 9, 15))
        # 高光竖线
        pygame.draw.line(surface, (135, 133, 130), (x + 5, 3), (x + 5, 15))
        # 裂缝
        pygame.draw.line(surface, (100, 95, 90), (x + 8, 5), (x + 9, 8))
        pygame.draw.line(surface, (100, 95, 90), (x + 6, 10), (x + 7, 13))
    elif gid == GID_STONE_PILLAR_BOT:
        # 密室石柱下部 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 柱身延续
        pygame.draw.rect(surface, (120, 118, 115), (x + 5, 0, 6, 10))
        # 纹理竖线
        pygame.draw.line(surface, (110, 108, 105), (x + 7, 0), (x + 7, 9))
        pygame.draw.line(surface, (110, 108, 105), (x + 9, 0), (x + 9, 9))
        # 高光竖线
        pygame.draw.line(surface, (135, 133, 130), (x + 5, 0), (x + 5, 9))
        # 柱基
        pygame.draw.rect(surface, (130, 128, 125), (x + 3, 10, 10, 4))
        # 柱基高光
        pygame.draw.line(surface, (155, 153, 150), (x + 3, 10), (x + 12, 10))
        # 柱基暗面
        pygame.draw.line(surface, (100, 98, 95), (x + 3, 13), (x + 12, 13))
        # 阴影
        shadow = pygame.Surface((10, 1), pygame.SRCALPHA)
        shadow.fill((70, 65, 60, 80))
        surface.blit(shadow, (x + 3, 14))
    elif gid == GID_SPORTS_POSTER:
        # 体育馆运动海报 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 海报纸
        pygame.draw.rect(surface, (240, 240, 245), (x + 2, 1, 12, 14))
        # 边框
        pygame.draw.rect(surface, (200, 200, 210), (x + 2, 1, 12, 14), 1)
        # 蓝色标题条
        pygame.draw.rect(surface, (40, 80, 160), (x + 3, 2, 10, 3))
        # 人物剪影（跑步人形）
        for dx, dy in [(6, 6), (7, 5), (7, 7), (8, 6), (8, 8), (9, 7)]:
            surface.set_at((x + dx, dy), (60, 60, 70))
        # 文字横线
        pygame.draw.line(surface, (100, 100, 120), (x + 4, 10), (x + 10, 10))
        pygame.draw.line(surface, (100, 100, 120), (x + 4, 12), (x + 10, 12))
        pygame.draw.line(surface, (100, 100, 120), (x + 4, 13), (x + 8, 13))
        # 图钉
        surface.set_at((x + 4, 1), (200, 50, 50))
        surface.set_at((x + 11, 1), (50, 50, 200))
    elif gid == GID_FIRST_AID:
        # 体育馆急救箱 - 透明背景
        surface.fill((0, 0, 0, 0), rect)
        # 箱体
        pygame.draw.rect(surface, (220, 220, 230), (x + 2, 2, 12, 11))
        # 边框
        pygame.draw.rect(surface, (180, 180, 190), (x + 2, 2, 12, 11), 1)
        # 红十字标志
        pygame.draw.rect(surface, (220, 50, 50), (x + 5, 5, 6, 2))
        pygame.draw.rect(surface, (220, 50, 50), (x + 7, 4, 2, 4))
        # 把手
        pygame.draw.rect(surface, (160, 160, 170), (x + 6, 1, 4, 1))
        # 箱门分隔线
        pygame.draw.line(surface, (180, 180, 190), (x + 2, 8), (x + 13, 8))
        # 下层
        pygame.draw.rect(surface, (210, 210, 220), (x + 3, 9, 10, 3))
        # 阴影
        shadow = pygame.Surface((12, 1), pygame.SRCALPHA)
        shadow.fill((140, 140, 150, 80))
        surface.blit(shadow, (x + 2, 13))


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

    # 左侧查询终端（桌子+电脑）
    structures[10][2] = GID_TABLE
    collision[10][2] = GID_COLLISION
    structures[9][2] = GID_COMPUTER
    collision[9][2] = GID_COLLISION

    # 右侧查询终端（桌子+电脑）
    structures[10][21] = GID_TABLE
    collision[10][21] = GID_COLLISION
    structures[9][21] = GID_COMPUTER
    collision[9][21] = GID_COLLISION

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
            "terminal_type": "call_number_guide",
            "invisible": "true",
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
            "invisible": "true",
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
                "invisible": "true",
            }
        })

    _add_exit_trigger(trigger_objects, 11, H - 2, 2, 1,
                      "main_campus", "library_exit")
    _add_spawn(trigger_objects, "library_entrance", 11, H - 4)
    _add_spawn(trigger_objects, "library_f1_stairs", 20, 2)

    # 新增：中央区域还书台（2x1长桌，自带电脑图案）
    structures[10][9] = GID_TABLE
    structures[10][10] = GID_TABLE
    collision[10][9] = GID_COLLISION
    collision[10][10] = GID_COLLISION
    # 新增：右下角报刊架（移到不覆盖电脑的位置）
    structures[14][14] = GID_NEWSPAPER_RACK
    collision[14][14] = GID_COLLISION
    # 报刊架交互对象
    interactive_objects.append({
        "x": 14 * TILE_SIZE, "y": 14 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "magazine_rack",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看报刊架",
            "display_name": "报刊架",
        }
    })

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

    # 上左区域书架（x=5-6, y=1-3）：哲学 B + 语言 H
    for x in range(5, 7):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        structures[3][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    # 上中区域书架（x=11-12, y=1-3）：马列 A + 文学 I
    for x in range(11, 13):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        structures[3][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    # 上右区域书架（x=18-19, y=1-3）：社科 C + 历史 K
    for x in range(18, 20):
        structures[1][x] = GID_BOOKSHELF_TOP
        structures[2][x] = GID_BOOKSHELF
        structures[3][x] = GID_BOOKSHELF
        collision[1][x] = GID_COLLISION
        collision[2][x] = GID_COLLISION
        collision[3][x] = GID_COLLISION

    # 下左区域书架（x=4-5, y=7-8）：数理 O + 天文 P
    for x in range(4, 6):
        structures[7][x] = GID_BOOKSHELF
        structures[8][x] = GID_BOOKSHELF
        collision[7][x] = GID_COLLISION
        collision[8][x] = GID_COLLISION

    # 下右区域书架（x=18-19, y=7-8）：生物 Q + 建筑 TU
    for x in range(18, 20):
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

    # 10个书架交互对象（5个区域，每区2个，带索书号）
    # 上左区域：哲学 B + 语言 H
    interactive_objects.append({
        "x": 5 * TILE_SIZE, "y": 2 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·哲学",
            "call_number": "B821/L3",
        }
    })
    interactive_objects.append({
        "x": 6 * TILE_SIZE, "y": 2 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·语言",
            "call_number": "H119/Z4",
        }
    })
    # 上中区域：马列 A + 文学 I
    interactive_objects.append({
        "x": 11 * TILE_SIZE, "y": 2 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·马列",
            "call_number": "A123.4/W1",
        }
    })
    interactive_objects.append({
        "x": 12 * TILE_SIZE, "y": 2 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·文学",
            "call_number": "I242/Z7",
        }
    })
    # 上右区域：社科 C + 历史 K（正确书架在此区域）
    interactive_objects.append({
        "x": 18 * TILE_SIZE, "y": 2 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·社科",
            "call_number": "C912/D4",
        }
    })
    interactive_objects.append({
        "x": 19 * TILE_SIZE, "y": 2 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·历史",
            "call_number": "K291.5/Z3",
        }
    })
    # 下左区域：数理 O + 天文 P
    interactive_objects.append({
        "x": 4 * TILE_SIZE, "y": 7 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·数理",
            "call_number": "O413/C2",
        }
    })
    interactive_objects.append({
        "x": 5 * TILE_SIZE, "y": 7 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·天文",
            "call_number": "P462/W5",
        }
    })
    # 下右区域：生物 Q + 建筑 TU
    interactive_objects.append({
        "x": 18 * TILE_SIZE, "y": 7 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·生物",
            "call_number": "Q949/L1",
        }
    })
    interactive_objects.append({
        "x": 19 * TILE_SIZE, "y": 7 * TILE_SIZE,
        "width": TILE_SIZE, "height": 2 * TILE_SIZE,
        "type": "bookshelf",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看书架",
            "display_name": "书架·建筑",
            "call_number": "TU984/H6",
        }
    })

    # 5个分类标识牌 tile + 交互对象
    # 上左标识牌
    structures[4][4] = GID_SECTION_SIGN
    collision[4][4] = GID_COLLISION
    interactive_objects.append({
        "x": 4 * TILE_SIZE, "y": 4 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "section_sign",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看标识牌",
            "display_name": "分类标识牌",
            "section_text": "哲学 B · 语言 H",
        }
    })
    # 上中标识牌
    structures[4][10] = GID_SECTION_SIGN
    collision[4][10] = GID_COLLISION
    interactive_objects.append({
        "x": 10 * TILE_SIZE, "y": 4 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "section_sign",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看标识牌",
            "display_name": "分类标识牌",
            "section_text": "马列 A · 文学 I",
        }
    })
    # 上右标识牌
    structures[4][17] = GID_SECTION_SIGN
    collision[4][17] = GID_COLLISION
    interactive_objects.append({
        "x": 17 * TILE_SIZE, "y": 4 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "section_sign",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看标识牌",
            "display_name": "分类标识牌",
            "section_text": "社科 C · 历史 K",
        }
    })
    # 下左标识牌
    structures[9][3] = GID_SECTION_SIGN
    collision[9][3] = GID_COLLISION
    interactive_objects.append({
        "x": 3 * TILE_SIZE, "y": 9 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "section_sign",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看标识牌",
            "display_name": "分类标识牌",
            "section_text": "数理 O · 天文 P",
        }
    })
    # 下右标识牌
    structures[9][18] = GID_SECTION_SIGN
    collision[9][18] = GID_COLLISION
    interactive_objects.append({
        "x": 18 * TILE_SIZE, "y": 9 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "section_sign",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看标识牌",
            "display_name": "分类标识牌",
            "section_text": "生物 Q · 建筑 TU",
        }
    })

    _add_spawn(trigger_objects, "library_f2_stairs", 3, 2)

    # 新增：左下角报刊架
    structures[10][2] = GID_NEWSPAPER_RACK
    collision[10][2] = GID_COLLISION
    # 报刊架交互对象
    interactive_objects.append({
        "x": 2 * TILE_SIZE, "y": 10 * TILE_SIZE,
        "width": TILE_SIZE, "height": TILE_SIZE,
        "type": "magazine_rack",
        "properties": {
            "interactive_type": "examine",
            "prompt_text": "查看报刊架",
            "display_name": "报刊架",
        }
    })

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

    # 记分牌（顶部中央）
    for x in range(12, 16):
        structures[1][x] = GID_SCOREBOARD
        collision[1][x] = GID_COLLISION

    # 篮球架（左侧，y=1-2，上部篮板+下部支柱底座）
    structures[1][2] = GID_HOOP_TOP
    collision[1][2] = GID_COLLISION
    structures[2][2] = GID_HOOP_BOT
    collision[2][2] = GID_COLLISION

    # 篮球架（右侧，y=1-2）
    structures[1][W - 3] = GID_HOOP_TOP
    collision[1][W - 3] = GID_COLLISION
    structures[2][W - 3] = GID_HOOP_BOT
    collision[2][W - 3] = GID_COLLISION

    # 左墙更衣柜（x=1, y=3-5，进门换衣区）
    structures[3][1] = GID_GYM_LOCKER
    collision[3][1] = GID_COLLISION
    structures[4][1] = GID_GYM_LOCKER
    collision[4][1] = GID_COLLISION
    structures[5][1] = GID_GYM_LOCKER
    collision[5][1] = GID_COLLISION

    # 右墙更衣柜（x=28, y=3-5，不碰墙x=29）
    structures[3][28] = GID_GYM_LOCKER
    collision[3][28] = GID_COLLISION
    structures[4][28] = GID_GYM_LOCKER
    collision[4][28] = GID_COLLISION
    structures[5][28] = GID_GYM_LOCKER
    collision[5][28] = GID_COLLISION

    # 左墙奖杯展示柜（x=1-2, y=7-9，与更衣柜隔1格）
    structures[7][1] = GID_GYM_TROPHY_TL
    structures[7][2] = GID_GYM_TROPHY_TR
    structures[8][1] = GID_GYM_TROPHY_ML
    structures[8][2] = GID_GYM_TROPHY_MR
    structures[9][1] = GID_GYM_TROPHY_BL
    structures[9][2] = GID_GYM_TROPHY_BR
    collision[7][1] = GID_COLLISION
    collision[7][2] = GID_COLLISION
    collision[8][1] = GID_COLLISION
    collision[8][2] = GID_COLLISION
    collision[9][1] = GID_COLLISION
    collision[9][2] = GID_COLLISION

    # 右墙奖杯展示柜（x=27-28, y=7-9，不碰墙x=29）
    structures[7][27] = GID_GYM_TROPHY_TL
    structures[7][28] = GID_GYM_TROPHY_TR
    structures[8][27] = GID_GYM_TROPHY_ML
    structures[8][28] = GID_GYM_TROPHY_MR
    structures[9][27] = GID_GYM_TROPHY_BL
    structures[9][28] = GID_GYM_TROPHY_BR
    collision[7][27] = GID_COLLISION
    collision[7][28] = GID_COLLISION
    collision[8][27] = GID_COLLISION
    collision[8][28] = GID_COLLISION
    collision[9][27] = GID_COLLISION
    collision[9][28] = GID_COLLISION

    # 左侧饮水机（x=4, y=7-8，靠近替补席）
    structures[7][4] = GID_GYM_WATER_TOP
    structures[8][4] = GID_GYM_WATER_BOT
    collision[7][4] = GID_COLLISION
    collision[8][4] = GID_COLLISION

    # 右侧饮水机（x=25, y=7-8）
    structures[7][25] = GID_GYM_WATER_TOP
    structures[8][25] = GID_GYM_WATER_BOT
    collision[7][25] = GID_COLLISION
    collision[8][25] = GID_COLLISION

    # 左侧替补长凳（x=4-5, y=11，球场边线）
    structures[11][4] = GID_GYM_BENCH_L
    structures[11][5] = GID_GYM_BENCH_R
    collision[11][4] = GID_COLLISION
    collision[11][5] = GID_COLLISION

    # 右侧替补长凳（x=24-25, y=11）
    structures[11][24] = GID_GYM_BENCH_L
    structures[11][25] = GID_GYM_BENCH_R
    collision[11][24] = GID_COLLISION
    collision[11][25] = GID_COLLISION

    # 左侧桌子（x=4-5, y=13-14，替补席后方放水壶毛巾）
    structures[13][4] = GID_GYM_TABLE_TL
    structures[13][5] = GID_GYM_TABLE_TR
    structures[14][4] = GID_GYM_TABLE_BL
    structures[14][5] = GID_GYM_TABLE_BR
    collision[13][4] = GID_COLLISION
    collision[13][5] = GID_COLLISION
    collision[14][4] = GID_COLLISION
    collision[14][5] = GID_COLLISION

    # 右侧桌子（x=24-25, y=13-14）
    structures[13][24] = GID_GYM_TABLE_TL
    structures[13][25] = GID_GYM_TABLE_TR
    structures[14][24] = GID_GYM_TABLE_BL
    structures[14][25] = GID_GYM_TABLE_BR
    collision[13][24] = GID_COLLISION
    collision[13][25] = GID_COLLISION
    collision[14][24] = GID_COLLISION
    collision[14][25] = GID_COLLISION

    # 体操垫（左上角偏下，3×2，装饰层无碰撞，展开铺平）
    decorations[4][3] = GID_GYM_MAT_L
    decorations[4][4] = GID_GYM_MAT_M
    decorations[4][5] = GID_GYM_MAT_R
    decorations[5][3] = GID_GYM_MAT_L
    decorations[5][4] = GID_GYM_MAT_M
    decorations[5][5] = GID_GYM_MAT_R

    # 急救箱（底部区域，原冰箱位置）
    structures[16][5] = GID_FIRST_AID
    collision[16][5] = GID_COLLISION

    # 器材柜（底部中央偏左，2格宽）
    structures[16][8] = GID_GYM_EQUIP_L
    structures[16][9] = GID_GYM_EQUIP_R
    collision[16][8] = GID_COLLISION
    collision[16][9] = GID_COLLISION

    # 门
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

    # 新增：左墙运动海报
    structures[6][1] = GID_SPORTS_POSTER
    collision[6][1] = GID_COLLISION
    # 新增：右墙运动海报
    structures[6][28] = GID_SPORTS_POSTER
    collision[6][28] = GID_COLLISION

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

    # 新增：取餐窗口旁的菜单牌
    structures[1][5] = GID_MENU_BOARD
    collision[1][5] = GID_COLLISION
    # 新增：冰箱旁的饮料机
    structures[5][16] = GID_DRINK_MACHINE
    collision[5][16] = GID_COLLISION

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

    # 新增：楼梯旁菜单牌
    structures[1][5] = GID_MENU_BOARD
    collision[1][5] = GID_COLLISION
    # 新增：后厨区旁饮料机
    structures[6][16] = GID_DRINK_MACHINE
    collision[6][16] = GID_COLLISION

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
