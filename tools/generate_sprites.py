"""
程序化生成游戏精灵图
生成玩家精灵表、NPC精灵表、可互动物体精灵
运行方式：python tools/generate_sprites.py
"""

import os
import math
import pygame


# ============================================================
# 颜色常量
# ============================================================
# 玩家
COLOR_PLAYER_BODY = (80, 120, 200)
COLOR_PLAYER_BODY_DARK = (60, 90, 160)
COLOR_PLAYER_HEAD = (240, 210, 180)
COLOR_PLAYER_HEAD_SHADE = (220, 190, 160)
COLOR_PLAYER_HAIR = (60, 40, 20)
COLOR_PLAYER_HAIR_LIGHT = (80, 55, 30)
COLOR_PLAYER_EYE = (20, 20, 20)
COLOR_PLAYER_PANTS = (50, 70, 140)
COLOR_PLAYER_PANTS_DARK = (40, 55, 110)
COLOR_PLAYER_SHOE = (50, 40, 30)

# NPC
COLOR_SENIOR_BODY = (80, 140, 80)
COLOR_SENIOR_BODY_DARK = (60, 110, 60)
COLOR_SENIOR_GLASS = (180, 200, 220)
COLOR_SENIOR_GLASS_FRAME = (60, 60, 60)

COLOR_LIBRARIAN_BODY = (140, 100, 160)
COLOR_LIBRARIAN_BODY_DARK = (110, 75, 130)
COLOR_LIBRARIAN_HAIR = (100, 60, 30)

COLOR_AUNTIE_BODY = (200, 80, 80)
COLOR_AUNTIE_BODY_DARK = (160, 60, 60)
COLOR_AUNTIE_HAIR = (60, 30, 20)

COLOR_PE_BODY = (60, 80, 140)
COLOR_PE_BODY_DARK = (45, 60, 110)
COLOR_PE_HAIR = (30, 25, 20)

COLOR_CAFETERIA_BODY = (220, 200, 180)
COLOR_CAFETERIA_BODY_DARK = (190, 170, 150)
COLOR_CAFETERIA_APRON = (240, 240, 240)
COLOR_CAFETERIA_HAIRNET = (180, 180, 180)

COLOR_GUARDIAN_CLOAK = (40, 80, 60)
COLOR_GUARDIAN_CLOAK_DARK = (25, 55, 40)
COLOR_GUARDIAN_EYE_GLOW = (100, 255, 100)

COLOR_PASSING_STUDENT_BODY = (120, 100, 160)
COLOR_PASSING_STUDENT_BODY_DARK = (90, 75, 130)
COLOR_PASSING_STUDENT_HAIR = (50, 30, 20)

# 通用
COLOR_SKIN = (240, 210, 180)
COLOR_SKIN_SHADE = (220, 190, 160)


# ============================================================
# 辅助函数
# ============================================================
def make_surface(w, h):
    """创建带透明通道的 Surface"""
    return pygame.Surface((w, h), pygame.SRCALPHA)


def draw_pixel(surf, x, y, color):
    """绘制单个像素"""
    if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
        surf.set_at((x, y), color)


def draw_hline(surf, x1, x2, y, color):
    """绘制水平线"""
    for x in range(min(x1, x2), max(x1, x2) + 1):
        draw_pixel(surf, x, y, color)


def draw_vline(surf, x, y1, y2, color):
    """绘制垂直线"""
    for y in range(min(y1, y2), max(y1, y2) + 1):
        draw_pixel(surf, x, y, color)


def draw_rect_filled(surf, x, y, w, h, color):
    """绘制填充矩形"""
    for dy in range(h):
        for dx in range(w):
            draw_pixel(surf, x + dx, y + dy, color)


# ============================================================
# 玩家精灵表
# ============================================================
def draw_player_frame(surf, ox, oy, direction, frame):
    """
    在精灵表上绘制玩家单帧
    ox, oy: 帧在精灵表上的偏移
    direction: 0=下, 1=左, 2=右, 3=上
    frame: 0-3, 其中0和2为站立, 1为左脚前, 3为右脚前
    """
    # 角色尺寸: 16×24, 居中绘制
    cx = ox + 8  # 中心x

    # --- 头发 ---
    if direction == 0:  # 朝下
        # 头发顶部
        draw_rect_filled(surf, cx - 4, oy + 1, 8, 3, COLOR_PLAYER_HAIR)
        draw_pixel(surf, cx - 5, oy + 2, COLOR_PLAYER_HAIR)
        draw_pixel(surf, cx + 4, oy + 2, COLOR_PLAYER_HAIR)
        # 两侧鬓角
        draw_vline(surf, cx - 5, oy + 3, oy + 5, COLOR_PLAYER_HAIR)
        draw_vline(surf, cx + 4, oy + 3, oy + 5, COLOR_PLAYER_HAIR)
    elif direction == 3:  # 朝上
        # 后脑勺
        draw_rect_filled(surf, cx - 5, oy + 1, 10, 5, COLOR_PLAYER_HAIR)
        draw_pixel(surf, cx - 5, oy + 6, COLOR_PLAYER_HAIR)
        draw_pixel(surf, cx + 4, oy + 6, COLOR_PLAYER_HAIR)
    elif direction == 1:  # 朝左
        draw_rect_filled(surf, cx - 4, oy + 1, 8, 3, COLOR_PLAYER_HAIR)
        draw_pixel(surf, cx - 5, oy + 2, COLOR_PLAYER_HAIR)
        draw_vline(surf, cx - 5, oy + 3, oy + 5, COLOR_PLAYER_HAIR)
        draw_vline(surf, cx + 3, oy + 3, oy + 4, COLOR_PLAYER_HAIR)
    elif direction == 2:  # 朝右
        draw_rect_filled(surf, cx - 4, oy + 1, 8, 3, COLOR_PLAYER_HAIR)
        draw_pixel(surf, cx + 4, oy + 2, COLOR_PLAYER_HAIR)
        draw_vline(surf, cx + 4, oy + 3, oy + 5, COLOR_PLAYER_HAIR)
        draw_vline(surf, cx - 4, oy + 3, oy + 4, COLOR_PLAYER_HAIR)

    # --- 脸部 ---
    if direction == 0:  # 朝下
        draw_rect_filled(surf, cx - 4, oy + 4, 8, 4, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx - 4, oy + 4, COLOR_PLAYER_HEAD_SHADE)
        draw_pixel(surf, cx + 3, oy + 4, COLOR_PLAYER_HEAD_SHADE)
        # 眼睛
        draw_rect_filled(surf, cx - 3, oy + 5, 2, 2, COLOR_PLAYER_EYE)
        draw_rect_filled(surf, cx + 1, oy + 5, 2, 2, COLOR_PLAYER_EYE)
        # 眼睛高光
        draw_pixel(surf, cx - 3, oy + 5, (255, 255, 255))
        draw_pixel(surf, cx + 1, oy + 5, (255, 255, 255))
    elif direction == 3:  # 朝上 - 不画脸
        draw_rect_filled(surf, cx - 4, oy + 6, 8, 2, COLOR_PLAYER_HEAD)
    elif direction == 1:  # 朝左
        draw_rect_filled(surf, cx - 4, oy + 4, 8, 4, COLOR_PLAYER_HEAD)
        # 左眼
        draw_rect_filled(surf, cx - 3, oy + 5, 2, 2, COLOR_PLAYER_EYE)
        draw_pixel(surf, cx - 3, oy + 5, (255, 255, 255))
    elif direction == 2:  # 朝右
        draw_rect_filled(surf, cx - 4, oy + 4, 8, 4, COLOR_PLAYER_HEAD)
        # 右眼
        draw_rect_filled(surf, cx + 1, oy + 5, 2, 2, COLOR_PLAYER_EYE)
        draw_pixel(surf, cx + 1, oy + 5, (255, 255, 255))

    # --- 身体（校服上衣）---
    body_top = oy + 8
    draw_rect_filled(surf, cx - 4, body_top, 8, 6, COLOR_PLAYER_BODY)
    # 衣服阴影
    if direction == 0:
        draw_vline(surf, cx - 4, body_top, body_top + 5, COLOR_PLAYER_BODY_DARK)
        draw_vline(surf, cx + 3, body_top, body_top + 5, COLOR_PLAYER_BODY_DARK)
    elif direction == 1:
        draw_vline(surf, cx + 3, body_top, body_top + 5, COLOR_PLAYER_BODY_DARK)
    elif direction == 2:
        draw_vline(surf, cx - 4, body_top, body_top + 5, COLOR_PLAYER_BODY_DARK)
    # 领口
    if direction == 0:
        draw_pixel(surf, cx - 1, body_top, (220, 220, 220))
        draw_pixel(surf, cx, body_top, (220, 220, 220))

    # --- 手臂 ---
    arm_y = body_top + 1
    if direction == 0:
        draw_pixel(surf, cx - 5, arm_y, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx - 5, arm_y + 1, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx + 4, arm_y, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx + 4, arm_y + 1, COLOR_PLAYER_HEAD)
    elif direction == 1:
        draw_pixel(surf, cx - 5, arm_y, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx - 5, arm_y + 1, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx + 4, arm_y, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx + 4, arm_y + 1, COLOR_PLAYER_HEAD)
    elif direction == 2:
        draw_pixel(surf, cx - 5, arm_y, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx - 5, arm_y + 1, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx + 4, arm_y, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx + 4, arm_y + 1, COLOR_PLAYER_HEAD)
    elif direction == 3:
        draw_pixel(surf, cx - 5, arm_y, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx - 5, arm_y + 1, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx + 4, arm_y, COLOR_PLAYER_HEAD)
        draw_pixel(surf, cx + 4, arm_y + 1, COLOR_PLAYER_HEAD)

    # --- 裤子/腿 ---
    pants_top = body_top + 6
    # 走路动画偏移
    left_leg_offset = 0
    right_leg_offset = 0
    if frame == 1:  # 左脚前
        left_leg_offset = 1
        right_leg_offset = -1
    elif frame == 3:  # 右脚前
        left_leg_offset = -1
        right_leg_offset = 1

    # 左腿
    draw_rect_filled(surf, cx - 3, pants_top, 3, 5, COLOR_PLAYER_PANTS)
    draw_rect_filled(surf, cx - 3, pants_top + 5, 3, 2, COLOR_PLAYER_SHOE)
    # 右腿
    draw_rect_filled(surf, cx, pants_top, 3, 5, COLOR_PLAYER_PANTS)
    draw_rect_filled(surf, cx, pants_top + 5, 3, 2, COLOR_PLAYER_SHOE)

    # 走路时腿的位置偏移
    if frame == 1:
        # 左脚前伸 - 在底部画偏移的鞋
        draw_rect_filled(surf, cx - 3, pants_top + 4, 3, 3, COLOR_PLAYER_PANTS_DARK)
        draw_rect_filled(surf, cx - 3, pants_top + 6, 3, 1, COLOR_PLAYER_SHOE)
        draw_rect_filled(surf, cx, pants_top + 5, 3, 2, COLOR_PLAYER_SHOE)
    elif frame == 3:
        # 右脚前伸
        draw_rect_filled(surf, cx, pants_top + 4, 3, 3, COLOR_PLAYER_PANTS_DARK)
        draw_rect_filled(surf, cx, pants_top + 6, 3, 1, COLOR_PLAYER_SHOE)
        draw_rect_filled(surf, cx - 3, pants_top + 5, 3, 2, COLOR_PLAYER_SHOE)


def create_player_sheet(path):
    """生成玩家精灵表: 4方向×4帧, 64×96"""
    sheet = make_surface(64, 96)
    for direction in range(4):
        for frame in range(4):
            ox = frame * 16
            oy = direction * 24
            draw_player_frame(sheet, ox, oy, direction, frame)
    pygame.image.save(sheet, path)


# ============================================================
# NPC 精灵表
# ============================================================
def draw_npc_base(surf, ox, oy, body_color, body_dark, hair_color, has_glasses=False,
                  hair_style="short", has_apron=False, apron_color=None,
                  has_hairnet=False, hairnet_color=None, has_hood=False,
                  hood_color=None, eye_glow=False, bob_offset=0):
    """
    绘制NPC基础帧
    ox, oy: 偏移
    bob_offset: 上下浮动偏移（空闲动画）
    """
    oy += bob_offset
    cx = ox + 8

    # --- 头部 ---
    if has_hood and hood_color:
        # 兜帽
        draw_rect_filled(surf, cx - 5, oy, 10, 7, hood_color)
        draw_pixel(surf, cx - 5, oy + 7, hood_color)
        draw_pixel(surf, cx + 4, oy + 7, hood_color)
        # 阴影面部
        draw_rect_filled(surf, cx - 3, oy + 3, 6, 3, (20, 20, 20))
        if eye_glow:
            draw_pixel(surf, cx - 2, oy + 4, COLOR_GUARDIAN_EYE_GLOW)
            draw_pixel(surf, cx + 1, oy + 4, COLOR_GUARDIAN_EYE_GLOW)
    else:
        # 头发
        if hair_style == "short":
            draw_rect_filled(surf, cx - 4, oy + 1, 8, 3, hair_color)
            draw_pixel(surf, cx - 5, oy + 2, hair_color)
            draw_pixel(surf, cx + 4, oy + 2, hair_color)
            draw_vline(surf, cx - 5, oy + 3, oy + 5, hair_color)
            draw_vline(surf, cx + 4, oy + 3, oy + 5, hair_color)
        elif hair_style == "bun":
            draw_rect_filled(surf, cx - 4, oy + 1, 8, 3, hair_color)
            draw_pixel(surf, cx - 5, oy + 2, hair_color)
            draw_pixel(surf, cx + 4, oy + 2, hair_color)
            # 发髻
            draw_rect_filled(surf, cx - 2, oy - 1, 4, 2, hair_color)
        elif hair_style == "curly":
            draw_rect_filled(surf, cx - 5, oy + 1, 10, 4, hair_color)
            draw_pixel(surf, cx - 5, oy + 5, hair_color)
            draw_pixel(surf, cx + 4, oy + 5, hair_color)
            # 卷发凸起
            draw_pixel(surf, cx - 5, oy, hair_color)
            draw_pixel(surf, cx - 2, oy, hair_color)
            draw_pixel(surf, cx + 1, oy, hair_color)
            draw_pixel(surf, cx + 4, oy, hair_color)
        elif hair_style == "very_short":
            draw_rect_filled(surf, cx - 4, oy + 1, 8, 2, hair_color)
            draw_pixel(surf, cx - 5, oy + 2, hair_color)
            draw_pixel(surf, cx + 4, oy + 2, hair_color)

        # 发网
        if has_hairnet and hairnet_color:
            draw_rect_filled(surf, cx - 5, oy + 1, 10, 5, (*hairnet_color[:3], 120))
            draw_rect_filled(surf, cx - 3, oy - 1, 6, 2, hairnet_color)

        # 脸
        draw_rect_filled(surf, cx - 4, oy + 4, 8, 4, COLOR_SKIN)
        draw_pixel(surf, cx - 4, oy + 4, COLOR_SKIN_SHADE)
        draw_pixel(surf, cx + 3, oy + 4, COLOR_SKIN_SHADE)

        # 眼睛
        draw_rect_filled(surf, cx - 3, oy + 5, 2, 2, COLOR_PLAYER_EYE)
        draw_rect_filled(surf, cx + 1, oy + 5, 2, 2, COLOR_PLAYER_EYE)
        draw_pixel(surf, cx - 3, oy + 5, (255, 255, 255))
        draw_pixel(surf, cx + 1, oy + 5, (255, 255, 255))

        # 眼镜
        if has_glasses:
            draw_rect_filled(surf, cx - 4, oy + 4, 3, 3, COLOR_SENIOR_GLASS)
            draw_rect_filled(surf, cx + 1, oy + 4, 3, 3, COLOR_SENIOR_GLASS)
            draw_hline(surf, cx - 1, cx, oy + 5, COLOR_SENIOR_GLASS_FRAME)
            draw_pixel(surf, cx - 4, oy + 5, COLOR_SENIOR_GLASS_FRAME)
            draw_pixel(surf, cx + 3, oy + 5, COLOR_SENIOR_GLASS_FRAME)
            # 眼睛在眼镜内重绘
            draw_rect_filled(surf, cx - 3, oy + 5, 2, 2, COLOR_PLAYER_EYE)
            draw_rect_filled(surf, cx + 1, oy + 5, 2, 2, COLOR_PLAYER_EYE)

    # --- 身体 ---
    body_top = oy + 8
    draw_rect_filled(surf, cx - 4, body_top, 8, 6, body_color)
    draw_vline(surf, cx - 4, body_top, body_top + 5, body_dark)
    draw_vline(surf, cx + 3, body_top, body_top + 5, body_dark)

    # 围裙
    if has_apron and apron_color:
        draw_rect_filled(surf, cx - 3, body_top + 1, 6, 5, apron_color)
        # 围裙带子
        draw_pixel(surf, cx - 4, body_top + 1, apron_color)
        draw_pixel(surf, cx + 3, body_top + 1, apron_color)

    # 手臂
    arm_y = body_top + 1
    draw_pixel(surf, cx - 5, arm_y, COLOR_SKIN)
    draw_pixel(surf, cx - 5, arm_y + 1, COLOR_SKIN)
    draw_pixel(surf, cx + 4, arm_y, COLOR_SKIN)
    draw_pixel(surf, cx + 4, arm_y + 1, COLOR_SKIN)

    # --- 腿 ---
    pants_top = body_top + 6
    draw_rect_filled(surf, cx - 3, pants_top, 3, 5, body_dark)
    draw_rect_filled(surf, cx, pants_top, 3, 5, body_dark)
    draw_rect_filled(surf, cx - 3, pants_top + 5, 3, 2, COLOR_PLAYER_SHOE)
    draw_rect_filled(surf, cx, pants_top + 5, 3, 2, COLOR_PLAYER_SHOE)


def create_npc_sheet(path, body_color, body_dark, hair_color, **kwargs):
    """生成NPC精灵表: 2帧空闲动画, 32×24"""
    sheet = make_surface(32, 24)
    # 帧0: 正常位置
    draw_npc_base(sheet, 0, 0, body_color, body_dark, hair_color, **kwargs)
    # 帧1: 向上浮动1像素
    draw_npc_base(sheet, 16, 0, body_color, body_dark, hair_color, bob_offset=-1, **kwargs)
    pygame.image.save(sheet, path)


# ============================================================
# 可互动物体精灵
# ============================================================
def create_osmanthus_tree(path):
    """桂花树: 32×32"""
    surf = make_surface(32, 32)
    # 树干
    draw_rect_filled(surf, 13, 16, 6, 14, (100, 70, 30))
    draw_rect_filled(surf, 14, 16, 4, 14, (120, 85, 40))
    # 树根
    draw_pixel(surf, 12, 29, (80, 55, 25))
    draw_pixel(surf, 19, 29, (80, 55, 25))
    # 树冠 - 多层圆形
    for y in range(3, 18):
        for x in range(3, 29):
            dx = x - 16
            dy = y - 10
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 11:
                if dist < 8:
                    draw_pixel(surf, x, y, (50, 140, 50))
                else:
                    draw_pixel(surf, x, y, (40, 120, 40))
            elif dist < 12:
                draw_pixel(surf, x, y, (35, 100, 35))
    # 桂花小点
    flower_positions = [
        (10, 6), (14, 4), (19, 5), (22, 8), (8, 10),
        (12, 9), (17, 7), (21, 11), (9, 14), (15, 12),
        (20, 13), (13, 14), (18, 10), (11, 11), (23, 10),
    ]
    for fx, fy in flower_positions:
        draw_pixel(surf, fx, fy, (255, 220, 50))
    # 树冠高光
    draw_pixel(surf, 14, 5, (70, 170, 70))
    draw_pixel(surf, 15, 4, (70, 170, 70))
    draw_pixel(surf, 16, 5, (70, 170, 70))
    pygame.image.save(surf, path)


def create_osmanthus_tree_glow(path):
    """桂花树（发光版）: 32×32"""
    surf = make_surface(32, 32)
    # 先画普通树
    draw_rect_filled(surf, 13, 16, 6, 14, (100, 70, 30))
    draw_rect_filled(surf, 14, 16, 4, 14, (120, 85, 40))
    draw_pixel(surf, 12, 29, (80, 55, 25))
    draw_pixel(surf, 19, 29, (80, 55, 25))
    for y in range(3, 18):
        for x in range(3, 29):
            dx = x - 16
            dy = y - 10
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 11:
                if dist < 8:
                    draw_pixel(surf, x, y, (50, 140, 50))
                else:
                    draw_pixel(surf, x, y, (40, 120, 40))
            elif dist < 12:
                draw_pixel(surf, x, y, (35, 100, 35))
    flower_positions = [
        (10, 6), (14, 4), (19, 5), (22, 8), (8, 10),
        (12, 9), (17, 7), (21, 11), (9, 14), (15, 12),
        (20, 13), (13, 14), (18, 10), (11, 11), (23, 10),
    ]
    for fx, fy in flower_positions:
        draw_pixel(surf, fx, fy, (255, 220, 50))
    draw_pixel(surf, 14, 5, (70, 170, 70))
    draw_pixel(surf, 15, 4, (70, 170, 70))
    draw_pixel(surf, 16, 5, (70, 170, 70))

    # 绿色光晕
    glow_surf = make_surface(32, 32)
    for y in range(32):
        for x in range(32):
            dx = x - 16
            dy = y - 10
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 16:
                alpha = int(60 * (1 - dist / 16))
                glow_surf.set_at((x, y), (100, 255, 100, alpha))
    surf.blit(glow_surf, (0, 0))
    pygame.image.save(surf, path)


def create_street_lamp(path):
    """路灯: 16×32"""
    surf = make_surface(16, 32)
    # 灯杆
    draw_rect_filled(surf, 7, 8, 2, 22, (80, 80, 90))
    draw_rect_filled(surf, 7, 8, 1, 22, (100, 100, 110))
    # 灯杆底座
    draw_rect_filled(surf, 5, 29, 6, 2, (70, 70, 80))
    # 灯臂
    draw_hline(surf, 4, 8, 8, (80, 80, 90))
    draw_hline(surf, 4, 8, 7, (100, 100, 110))
    # 灯罩
    draw_rect_filled(surf, 3, 4, 8, 4, (200, 180, 120))
    draw_rect_filled(surf, 4, 5, 6, 2, (255, 240, 180))
    # 灯光
    for y in range(2, 6):
        for x in range(2, 12):
            dx = abs(x - 7)
            dy = abs(y - 4)
            if dx + dy < 5:
                alpha = int(80 * (1 - (dx + dy) / 5))
                current = surf.get_at((x, y))
                if current[3] == 0:
                    surf.set_at((x, y), (255, 240, 150, alpha))
    # 灯顶
    draw_rect_filled(surf, 5, 3, 4, 2, (90, 90, 100))
    pygame.image.save(surf, path)


def create_bookshelf(path):
    """书架: 32×48 - 更精致的三层书架，带装饰顶檐和分类标签"""
    surf = make_surface(32, 48)
    # 装饰顶檐
    draw_rect_filled(surf, 0, 0, 32, 4, (80, 50, 25))
    draw_rect_filled(surf, 1, 1, 30, 2, (120, 80, 40))
    # 主体框架
    draw_rect_filled(surf, 1, 4, 30, 40, (101, 67, 33))
    # 左右立柱
    draw_rect_filled(surf, 1, 4, 3, 40, (80, 50, 25))
    draw_rect_filled(surf, 28, 4, 3, 40, (80, 50, 25))
    # 三层隔板
    for shelf_y in [4, 17, 30, 43]:
        draw_hline(surf, 1, 31, shelf_y, (90, 58, 28))
        draw_hline(surf, 1, 31, shelf_y + 1, (120, 80, 40))
    # 第一层书籍 (y=5 to y=16)
    book_colors_1 = [(180, 50, 50), (50, 80, 160), (50, 140, 60), (200, 160, 40), (140, 40, 140), (180, 100, 60)]
    x = 4
    for i, color in enumerate(book_colors_1):
        w = 3 if i % 2 == 0 else 4
        draw_rect_filled(surf, x, 6, w, 10, color)
        # 书脊高光
        draw_vline(surf, x, 6, 15, (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)))
        # 书脊暗线
        draw_vline(surf, x + w - 1, 6, 15, (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)))
        x += w + 1
    # 第二层书籍 (y=18 to y=29)
    book_colors_2 = [(60, 60, 140), (160, 80, 40), (80, 160, 80), (180, 60, 100), (100, 100, 40), (60, 120, 160)]
    x = 4
    for i, color in enumerate(book_colors_2):
        w = 4 if i % 2 == 0 else 3
        draw_rect_filled(surf, x, 19, w, 10, color)
        draw_vline(surf, x, 19, 28, (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)))
        draw_vline(surf, x + w - 1, 19, 28, (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)))
        x += w + 1
    # 第三层书籍 (y=31 to y=42)
    book_colors_3 = [(140, 100, 60), (60, 120, 140), (160, 40, 80), (80, 80, 120), (120, 140, 60), (100, 60, 120)]
    x = 4
    for i, color in enumerate(book_colors_3):
        w = 3 if i % 2 == 0 else 4
        draw_rect_filled(surf, x, 32, w, 10, color)
        draw_vline(surf, x, 32, 41, (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)))
        draw_vline(surf, x + w - 1, 32, 41, (max(0, color[0]-30), max(0, color[1]-30), max(0, color[2]-30)))
        x += w + 1
    # 底部装饰线
    draw_hline(surf, 1, 31, 44, (90, 58, 28))
    draw_hline(surf, 1, 31, 45, (120, 80, 40))
    # 分类标签牌（右下角小木牌）
    draw_rect_filled(surf, 22, 38, 8, 6, (240, 230, 200))
    draw_rect_filled(surf, 22, 38, 8, 6, (0, 0, 0))  # 边框用黑色
    draw_rect_filled(surf, 23, 39, 6, 4, (240, 230, 200))
    # 标签文字线条
    draw_hline(surf, 24, 28, 40, (60, 40, 20))
    draw_hline(surf, 24, 27, 41, (60, 40, 20))
    pygame.image.save(surf, path)


def create_bulletin_board(path):
    """公告栏: 24×20"""
    surf = make_surface(24, 20)
    # 木质边框
    draw_rect_filled(surf, 0, 0, 24, 20, (120, 80, 40))
    draw_rect_filled(surf, 1, 1, 22, 18, (140, 95, 50))
    # 白色面板
    draw_rect_filled(surf, 2, 2, 20, 16, (240, 235, 220))
    # 便条
    draw_rect_filled(surf, 4, 3, 7, 5, (255, 255, 200))
    draw_rect_filled(surf, 4, 3, 7, 5, (200, 200, 150))
    draw_hline(surf, 5, 9, 5, (180, 180, 130))
    draw_hline(surf, 5, 8, 6, (180, 180, 130))
    # 另一张便条
    draw_rect_filled(surf, 13, 4, 8, 6, (200, 230, 255))
    draw_rect_filled(surf, 13, 4, 8, 6, (150, 180, 200))
    draw_hline(surf, 14, 19, 6, (130, 160, 180))
    draw_hline(surf, 14, 18, 7, (130, 160, 180))
    draw_hline(surf, 14, 19, 8, (130, 160, 180))
    # 图钉
    draw_pixel(surf, 7, 3, (200, 50, 50))
    draw_pixel(surf, 16, 4, (50, 50, 200))
    # 底部便条
    draw_rect_filled(surf, 5, 10, 6, 4, (255, 220, 200))
    draw_rect_filled(surf, 5, 10, 6, 4, (200, 170, 150))
    draw_pixel(surf, 7, 10, (50, 180, 50))
    pygame.image.save(surf, path)


def create_computer_terminal(path):
    """电脑终端: 24×20"""
    surf = make_surface(24, 20)
    # 显示器外壳
    draw_rect_filled(surf, 2, 0, 20, 14, (80, 80, 90))
    draw_rect_filled(surf, 3, 1, 18, 12, (40, 40, 50))
    # 屏幕
    draw_rect_filled(surf, 4, 2, 16, 10, (10, 30, 10))
    # 屏幕上的绿色文字
    green = (0, 200, 0)
    green_dim = (0, 140, 0)
    for row in range(4):
        y = 3 + row * 2
        for col in range(6):
            x = 5 + col * 2
            if (row + col) % 3 != 0:
                draw_pixel(surf, x, y, green)
            else:
                draw_pixel(surf, x, y, green_dim)
    # 屏幕反光
    draw_pixel(surf, 5, 3, (0, 220, 0))
    draw_pixel(surf, 6, 3, (0, 220, 0))
    # 支架
    draw_rect_filled(surf, 10, 14, 4, 3, (80, 80, 90))
    # 底座
    draw_rect_filled(surf, 7, 17, 10, 2, (80, 80, 90))
    draw_rect_filled(surf, 8, 17, 8, 1, (100, 100, 110))
    # 键盘
    draw_rect_filled(surf, 4, 19, 16, 1, (60, 60, 70))
    pygame.image.save(surf, path)


def create_sculpture(path):
    """博雅广场雕塑: 桂花树与书卷造型, 24x32"""
    surf = make_surface(24, 32)

    # 底座 - 三层石阶
    # 底层
    draw_rect_filled(surf, 1, 26, 22, 6, (120, 118, 115))
    draw_rect_filled(surf, 2, 27, 20, 4, (140, 138, 135))
    # 中层
    draw_rect_filled(surf, 3, 23, 18, 4, (150, 148, 145))
    draw_rect_filled(surf, 4, 24, 16, 2, (165, 163, 160))
    # 顶层
    draw_rect_filled(surf, 5, 21, 14, 3, (160, 158, 155))
    # 底座铭文刻线
    draw_hline(surf, 6, 17, 22, (100, 95, 90))
    draw_hline(surf, 7, 16, 22, (180, 175, 160))

    # 书卷主体（树干/书脊）
    draw_rect_filled(surf, 10, 8, 4, 14, (90, 130, 90))
    draw_rect_filled(surf, 9, 10, 6, 10, (85, 125, 85))
    # 书卷展开部分
    draw_rect_filled(surf, 6, 12, 3, 6, (100, 140, 100))
    draw_rect_filled(surf, 15, 12, 3, 6, (100, 140, 100))
    # 书页纹理线
    draw_hline(surf, 7, 8, 14, (120, 160, 120))
    draw_hline(surf, 16, 17, 14, (120, 160, 120))
    draw_hline(surf, 7, 8, 16, (120, 160, 120))
    draw_hline(surf, 16, 17, 16, (120, 160, 120))

    # 桂花树冠 - 金色花朵簇
    # 中心花簇
    draw_rect_filled(surf, 10, 4, 4, 5, (200, 180, 60))
    draw_rect_filled(surf, 9, 5, 6, 3, (210, 190, 70))
    # 左侧花簇
    draw_rect_filled(surf, 6, 5, 3, 4, (190, 170, 55))
    draw_rect_filled(surf, 5, 6, 4, 2, (200, 180, 65))
    # 右侧花簇
    draw_rect_filled(surf, 15, 5, 3, 4, (190, 170, 55))
    draw_rect_filled(surf, 15, 6, 4, 2, (200, 180, 65))
    # 顶部花簇
    draw_rect_filled(surf, 9, 2, 6, 3, (205, 185, 65))
    draw_rect_filled(surf, 10, 1, 4, 2, (220, 200, 80))

    # 桂花细节点缀（小亮点模拟花瓣）
    draw_pixel(surf, 7, 4, (230, 210, 90))
    draw_pixel(surf, 16, 4, (230, 210, 90))
    draw_pixel(surf, 8, 3, (240, 220, 100))
    draw_pixel(surf, 15, 3, (240, 220, 100))
    draw_pixel(surf, 11, 2, (250, 230, 110))
    draw_pixel(surf, 12, 2, (250, 230, 110))

    # 高光
    draw_vline(surf, 11, 3, 20, (225, 205, 85))
    draw_pixel(surf, 11, 2, (235, 215, 95))
    draw_pixel(surf, 10, 9, (110, 150, 110))
    draw_pixel(surf, 10, 13, (110, 150, 110))

    pygame.image.save(surf, path)


def create_flowerbed(path):
    """花坛: 32x16, 横向长方形"""
    surf = make_surface(32, 16)

    # 花坛外框 - 深绿色边缘
    draw_rect_filled(surf, 0, 2, 32, 14, (60, 100, 40))
    draw_rect_filled(surf, 1, 3, 30, 12, (70, 115, 45))
    # 内部土壤
    draw_rect_filled(surf, 2, 4, 28, 10, (80, 60, 40))

    # 小花 - 红色
    draw_pixel(surf, 5, 6, (220, 60, 60))
    draw_pixel(surf, 6, 5, (220, 60, 60))
    draw_pixel(surf, 6, 7, (220, 60, 60))
    draw_pixel(surf, 7, 6, (220, 60, 60))
    draw_pixel(surf, 6, 6, (255, 100, 100))

    # 小花 - 黄色
    draw_pixel(surf, 12, 8, (220, 200, 40))
    draw_pixel(surf, 13, 7, (220, 200, 40))
    draw_pixel(surf, 13, 9, (220, 200, 40))
    draw_pixel(surf, 14, 8, (220, 200, 40))
    draw_pixel(surf, 13, 8, (255, 240, 80))

    # 小花 - 紫色
    draw_pixel(surf, 19, 5, (180, 80, 200))
    draw_pixel(surf, 20, 4, (180, 80, 200))
    draw_pixel(surf, 20, 6, (180, 80, 200))
    draw_pixel(surf, 21, 5, (180, 80, 200))
    draw_pixel(surf, 20, 5, (210, 110, 230))

    # 小花 - 白色
    draw_pixel(surf, 26, 7, (220, 220, 220))
    draw_pixel(surf, 27, 6, (220, 220, 220))
    draw_pixel(surf, 27, 8, (220, 220, 220))
    draw_pixel(surf, 28, 7, (220, 220, 220))
    draw_pixel(surf, 27, 7, (255, 255, 255))

    # 绿叶点缀
    draw_pixel(surf, 4, 8, (60, 160, 60))
    draw_pixel(surf, 8, 5, (60, 160, 60))
    draw_pixel(surf, 11, 9, (60, 160, 60))
    draw_pixel(surf, 15, 6, (60, 160, 60))
    draw_pixel(surf, 18, 8, (60, 160, 60))
    draw_pixel(surf, 22, 7, (60, 160, 60))
    draw_pixel(surf, 25, 5, (60, 160, 60))
    draw_pixel(surf, 29, 8, (60, 160, 60))

    pygame.image.save(surf, path)


def create_fountain(path):
    """喷泉: 96×96，完整喷泉外观含7个凹槽"""
    surf = make_surface(96, 96)

    # ---- 背景：石板路纹理（与喷泉广场地面一致）----
    stone_base = (180, 160, 120)
    stone_line = (150, 130, 100)
    stone_line2 = (160, 140, 110)
    surf.fill(stone_base)
    # 石板网格线（模拟16×16 tile的石板路纹理）
    for ty in range(0, 96, 16):
        draw_hline(surf, 0, 95, ty, stone_line)
    for tx in range(0, 96, 16):
        draw_vline(surf, tx, 0, 95, stone_line)
    # 石板内部纹理线
    for ty in range(0, 96, 16):
        for tx in range(0, 96, 16):
            draw_hline(surf, tx + 8, tx + 15, ty + 8, stone_line2)
            draw_vline(surf, tx + 8, ty, ty + 8, stone_line2)
            draw_hline(surf, tx, tx + 7, ty + 8, stone_line2)
            draw_vline(surf, tx + 4, ty + 8, ty + 15, stone_line2)
    # 石板上的随机深浅斑点
    for tx, ty in [(3,5),(18,3),(35,7),(50,2),(67,6),(82,4),
                   (5,18),(22,22),(38,17),(55,20),(72,19),(88,21),
                   (8,35),(25,38),(42,33),(58,36),(75,34),(90,37),
                   (3,50),(20,53),(37,48),(53,51),(70,49),(85,52),
                   (6,66),(23,69),(40,64),(56,67),(73,65),(88,68),
                   (4,82),(21,85),(38,80),(54,83),(71,81),(86,84)]:
        draw_pixel(surf, tx, ty, (170, 150, 110))

    cx, cy = 48, 56  # 喷泉底座中心（稍微上移，让底座更饱满）

    # ---- 底座（多层椭圆营造立体感，放大尺寸）----
    # 最外层阴影
    for y in range(30, 92):
        for x in range(96):
            dx = abs(x - cx)
            dy = y - cy
            if (dx / 46) ** 2 + (dy / 28) ** 2 < 1.0:
                draw_pixel(surf, x, y, (110, 108, 105))
    # 底座主体
    for y in range(32, 90):
        for x in range(2, 94):
            dx = abs(x - cx)
            dy = y - cy
            if (dx / 44) ** 2 + (dy / 26) ** 2 < 1.0:
                draw_pixel(surf, x, y, (160, 158, 155))
    # 内层暗面
    for y in range(34, 88):
        for x in range(6, 90):
            dx = abs(x - cx)
            dy = y - cy
            if (dx / 40) ** 2 + (dy / 22) ** 2 < 1.0:
                draw_pixel(surf, x, y, (145, 143, 140))
    # 内圈
    for y in range(36, 86):
        for x in range(10, 86):
            dx = abs(x - cx)
            dy = y - cy
            if (dx / 36) ** 2 + (dy / 18) ** 2 < 1.0:
                draw_pixel(surf, x, y, (130, 128, 125))

    # 石纹纹理（底座上的深浅斑点）
    stone_dark = [(16,38),(28,34),(40,40),(55,36),(68,42),(80,38),(90,44),
                  (12,50),(24,54),(36,48),(50,52),(62,56),(74,50),(86,54),
                  (18,62),(30,66),(44,60),(56,64),(68,68),(80,62),(92,66),
                  (22,74),(36,76),(52,72),(66,78),(82,74)]
    stone_light = [(20,40),(32,36),(46,38),(58,40),(70,44),(82,40),
                   (14,52),(26,56),(40,50),(52,54),(66,52),(78,56),
                   (20,64),(32,68),(48,62),(60,66),(74,64),(86,68)]
    for tx, ty in stone_dark:
        draw_pixel(surf, tx, ty, (140, 138, 135))
    for tx, ty in stone_light:
        draw_pixel(surf, tx, ty, (170, 168, 165))

    # ---- 水面 ----
    for y in range(40, 84):
        for x in range(14, 82):
            dx = abs(x - cx)
            dy = y - cy
            if (dx / 32) ** 2 + (dy / 16) ** 2 < 1.0:
                draw_pixel(surf, x, y, (50, 100, 200))
    # 水面波纹（同心弧线）
    for y in range(42, 82):
        for x in range(18, 78):
            dx = abs(x - cx)
            dy = y - cy
            r = (dx / 28) ** 2 + (dy / 14) ** 2
            if 0.3 < r < 0.5:
                draw_pixel(surf, x, y, (70, 130, 220))
            if 0.6 < r < 0.75:
                draw_pixel(surf, x, y, (65, 120, 210))
    # 水面高光
    for tx, ty in [(36,48),(40,46),(44,50),(48,47),(54,52),(58,49),(62,54)]:
        draw_pixel(surf, tx, ty, (120, 180, 245))
    for tx, ty in [(34,58),(38,60),(52,62),(56,64)]:
        draw_pixel(surf, tx, ty, (100, 165, 235))

    # ---- 7个凹槽（均匀分布在底座椭圆边缘）----
    slot_rx, slot_ry = 40, 22
    for i in range(7):
        angle = math.radians(-90 + i * 360 / 7)
        sx = int(cx + slot_rx * math.cos(angle))
        sy = int(cy + slot_ry * math.sin(angle))
        # 凹槽：5×5深色凹陷
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                draw_pixel(surf, sx + dx, sy + dy, (55, 50, 45))
        # 凹槽中心更暗
        draw_pixel(surf, sx, sy, (35, 30, 25))
        # 凹槽内圈纹理
        draw_pixel(surf, sx - 1, sy, (45, 40, 35))
        draw_pixel(surf, sx + 1, sy, (45, 40, 35))
        draw_pixel(surf, sx, sy - 1, (45, 40, 35))
        draw_pixel(surf, sx, sy + 1, (45, 40, 35))
        # 金色边框
        draw_pixel(surf, sx + 2, sy - 2, (210, 180, 60))
        draw_pixel(surf, sx + 3, sy - 1, (200, 170, 55))
        draw_pixel(surf, sx - 2, sy + 2, (170, 140, 45))
        draw_pixel(surf, sx - 3, sy + 1, (160, 130, 40))

    # ---- 中心柱 ----
    draw_rect_filled(surf, 42, 16, 12, 44, (130, 128, 125))
    draw_rect_filled(surf, 44, 16, 8, 44, (155, 153, 150))
    # 柱身纹理
    for ty in range(18, 58, 4):
        draw_pixel(surf, 42, ty, (140, 138, 135))
        draw_pixel(surf, 53, ty + 2, (140, 138, 135))
        draw_pixel(surf, 44, ty + 1, (165, 163, 160))

    # ---- 顶部碗状结构 ----
    # 碗身（梯形）
    for y in range(10, 18):
        half_w = 15 - (y - 10)  # 上宽下窄
        draw_hline(surf, cx - half_w, cx + half_w, y, (140, 138, 135))
    # 碗内沿高光
    draw_hline(surf, cx - 14, cx + 14, 10, (165, 163, 160))
    draw_hline(surf, cx - 13, cx + 13, 11, (175, 173, 170))
    # 碗沿
    draw_hline(surf, cx - 15, cx + 15, 10, (180, 178, 175))

    # ---- 水花（从碗口喷出）----
    # 中心水柱
    draw_rect_filled(surf, 46, 0, 4, 12, (100, 170, 240))
    draw_rect_filled(surf, 47, 0, 2, 12, (120, 190, 250))
    # 顶部水珠
    draw_pixel(surf, 47, 0, (130, 200, 255))
    draw_pixel(surf, 48, 0, (120, 190, 250))
    # 第一层飞溅
    draw_pixel(surf, 44, 1, (100, 170, 240))
    draw_pixel(surf, 51, 1, (100, 170, 240))
    draw_pixel(surf, 43, 3, (90, 160, 230))
    draw_pixel(surf, 52, 3, (90, 160, 230))
    # 第二层飞溅
    draw_pixel(surf, 40, 5, (80, 150, 220))
    draw_pixel(surf, 55, 5, (80, 150, 220))
    draw_pixel(surf, 38, 8, (70, 140, 210))
    draw_pixel(surf, 57, 8, (70, 140, 210))
    # 侧面水滴
    draw_pixel(surf, 36, 11, (60, 130, 200))
    draw_pixel(surf, 59, 11, (60, 130, 200))
    draw_pixel(surf, 34, 14, (50, 120, 190))
    draw_pixel(surf, 61, 14, (50, 120, 190))
    # 碗口溢出水滴
    draw_pixel(surf, 34, 18, (80, 150, 220))
    draw_pixel(surf, 61, 18, (80, 150, 220))
    draw_pixel(surf, 32, 20, (70, 140, 210))
    draw_pixel(surf, 63, 20, (70, 140, 210))

    pygame.image.save(surf, path)


def create_badge_pickup(path):
    """桂花徽章碎片拾取物: 16x16, 桂花造型+金色光晕"""
    surf = make_surface(16, 16)
    cx, cy = 8, 8

    # 金色光晕（外层淡金）
    for y in range(16):
        for x in range(16):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 7.5:
                alpha = int(50 * (1 - dist / 7.5))
                surf.set_at((x, y), (255, 210, 60, alpha))

    # 桂花花瓣 - 4瓣对称分布
    petal_color = (255, 215, 0)
    petal_highlight = (255, 235, 80)
    petal_shadow = (220, 180, 0)

    # 上花瓣
    draw_rect_filled(surf, 7, 2, 2, 4, petal_color)
    draw_pixel(surf, 7, 2, petal_highlight)
    draw_pixel(surf, 8, 2, petal_highlight)
    draw_pixel(surf, 7, 5, petal_shadow)
    draw_pixel(surf, 8, 5, petal_shadow)
    # 下花瓣
    draw_rect_filled(surf, 7, 10, 2, 4, petal_color)
    draw_pixel(surf, 7, 10, petal_highlight)
    draw_pixel(surf, 8, 10, petal_highlight)
    draw_pixel(surf, 7, 13, petal_shadow)
    draw_pixel(surf, 8, 13, petal_shadow)
    # 左花瓣
    draw_rect_filled(surf, 2, 7, 4, 2, petal_color)
    draw_pixel(surf, 2, 7, petal_highlight)
    draw_pixel(surf, 2, 8, petal_highlight)
    draw_pixel(surf, 5, 7, petal_shadow)
    draw_pixel(surf, 5, 8, petal_shadow)
    # 右花瓣
    draw_rect_filled(surf, 10, 7, 4, 2, petal_color)
    draw_pixel(surf, 10, 7, petal_highlight)
    draw_pixel(surf, 10, 8, petal_highlight)
    draw_pixel(surf, 13, 7, petal_shadow)
    draw_pixel(surf, 13, 8, petal_shadow)

    # 对角小花瓣（增加桂花层次感）
    draw_pixel(surf, 5, 5, (240, 200, 40))
    draw_pixel(surf, 10, 5, (240, 200, 40))
    draw_pixel(surf, 5, 10, (240, 200, 40))
    draw_pixel(surf, 10, 10, (240, 200, 40))

    # 花蕊中心
    draw_rect_filled(surf, 7, 7, 2, 2, (255, 240, 120))
    draw_pixel(surf, 7, 7, (255, 255, 200))
    draw_pixel(surf, 8, 8, (255, 255, 200))

    # 中心最亮点
    draw_pixel(surf, 7, 7, (255, 255, 230))

    pygame.image.save(surf, path)


def _point_in_polygon(x, y, polygon):
    """判断点是否在多边形内"""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _draw_line_on_surf(surf, x0, y0, x1, y1, color):
    """在 Surface 上画线（Bresenham）"""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < surf.get_width() and 0 <= y0 < surf.get_height():
            surf.set_at((x0, y0), color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def create_dining_table(path):
    """餐桌: 24×16"""
    surf = make_surface(24, 16)
    # 桌面
    draw_rect_filled(surf, 2, 4, 20, 4, (160, 110, 60))
    draw_rect_filled(surf, 3, 4, 18, 3, (180, 130, 70))
    # 桌面高光
    draw_hline(surf, 4, 20, 5, (200, 150, 80))
    # 桌腿
    draw_rect_filled(surf, 3, 8, 2, 7, (130, 90, 45))
    draw_rect_filled(surf, 19, 8, 2, 7, (130, 90, 45))
    # 桌腿内侧
    draw_pixel(surf, 4, 9, (150, 105, 55))
    draw_pixel(surf, 20, 9, (150, 105, 55))
    # 桌上餐具
    draw_pixel(surf, 8, 5, (200, 200, 200))  # 盘子
    draw_pixel(surf, 9, 5, (200, 200, 200))
    draw_pixel(surf, 8, 4, (220, 220, 220))
    draw_pixel(surf, 15, 5, (180, 180, 180))  # 杯子
    draw_pixel(surf, 15, 4, (200, 200, 220))
    pygame.image.save(surf, path)


def create_scoreboard(path):
    """记分牌: 32×28，体育馆电子记分牌（美化版）
    包含：金属外框、LED风格数字显示、队名区域、装饰细节
    """
    surf = make_surface(32, 28)
    # ---- 金属外框 ----
    draw_rect_filled(surf, 0, 0, 32, 28, (70, 70, 80))
    # 外框高光（顶部和左侧）
    draw_hline(surf, 0, 31, 0, (100, 100, 110))
    draw_vline(surf, 0, 0, 27, (100, 100, 110))
    # 外框阴影（底部和右侧）
    draw_hline(surf, 0, 31, 27, (50, 50, 60))
    draw_vline(surf, 31, 0, 27, (50, 50, 60))
    # 内框
    draw_rect_filled(surf, 1, 1, 30, 26, (55, 55, 65))
    # ---- 主面板（深色背景，模拟LED屏幕） ----
    draw_rect_filled(surf, 2, 2, 28, 24, (15, 15, 25))
    # ---- 分数显示区（上半部分） ----
    draw_rect_filled(surf, 3, 3, 26, 12, (10, 10, 18))
    # 分数区边框
    draw_hline(surf, 3, 28, 3, (40, 40, 50))
    draw_hline(surf, 3, 28, 14, (40, 40, 50))
    # 左队分数（红色LED风格）
    _draw_digit(surf, 5, 5, 0, (220, 50, 50))
    _draw_digit(surf, 9, 5, 0, (220, 50, 50))
    # 冒号分隔
    draw_pixel(surf, 14, 6, (220, 50, 50))
    draw_pixel(surf, 14, 9, (220, 50, 50))
    # 右队分数（蓝色LED风格）
    _draw_digit(surf, 17, 5, 0, (50, 80, 220))
    _draw_digit(surf, 21, 5, 0, (50, 80, 220))
    # LED背景暗纹（模拟未亮的LED点）
    for y in range(5, 10):
        for x in range(5, 13):
            if surf.get_at((x, y)) == (10, 10, 18, 255):
                draw_pixel(surf, x, y, (18, 12, 18))
    for y in range(5, 10):
        for x in range(17, 25):
            if surf.get_at((x, y)) == (10, 10, 18, 255):
                draw_pixel(surf, x, y, (12, 14, 25))
    # ---- 队名/文字区（下半部分） ----
    draw_rect_filled(surf, 3, 15, 26, 10, (20, 20, 30))
    # 队名区域分隔线
    draw_vline(surf, 16, 15, 24, (40, 40, 50))
    # 左队名区域（红色调）
    draw_rect_filled(surf, 4, 16, 11, 8, (25, 15, 18))
    draw_hline(surf, 5, 13, 18, (180, 60, 60))  # 简化队名
    draw_hline(surf, 5, 13, 20, (150, 50, 50))
    # 右队名区域（蓝色调）
    draw_rect_filled(surf, 17, 16, 11, 8, (15, 18, 28))
    draw_hline(surf, 18, 26, 18, (60, 80, 180))  # 简化队名
    draw_hline(surf, 18, 26, 20, (50, 60, 150))
    # ---- 底部装饰灯（小圆点模拟LED指示灯） ----
    draw_pixel(surf, 8, 25, (50, 180, 50))   # 绿色电源灯
    draw_pixel(surf, 14, 25, (180, 180, 50))  # 黄色状态灯
    draw_pixel(surf, 20, 25, (50, 50, 180))   # 蓝色信号灯
    draw_pixel(surf, 26, 25, (180, 50, 50))   # 红色告警灯
    # ---- 安装支架（顶部两个挂钩） ----
    draw_pixel(surf, 6, 0, (90, 90, 100))
    draw_pixel(surf, 6, 1, (80, 80, 90))
    draw_pixel(surf, 25, 0, (90, 90, 100))
    draw_pixel(surf, 25, 1, (80, 80, 90))
    pygame.image.save(surf, path)


def _draw_digit(surf, x, y, digit, color):
    """绘制3×5像素数字"""
    patterns = {
        0: ["111", "101", "101", "101", "111"],
        1: ["010", "110", "010", "010", "111"],
        2: ["111", "001", "111", "100", "111"],
        3: ["111", "001", "111", "001", "111"],
        4: ["101", "101", "111", "001", "001"],
        5: ["111", "100", "111", "001", "111"],
        6: ["111", "100", "111", "101", "111"],
        7: ["111", "001", "001", "001", "001"],
        8: ["111", "101", "111", "101", "111"],
        9: ["111", "101", "111", "001", "111"],
    }
    pattern = patterns.get(digit, patterns[0])
    for row, line in enumerate(pattern):
        for col, ch in enumerate(line):
            if ch == '1':
                draw_pixel(surf, x + col, y + row, color)


def create_equipment_cabinet(path):
    """器材柜: 32×32，体育馆金属器材柜（美化版）
    包含：金属柜体、多层隔间、透明门、器材展示、标签牌
    """
    surf = make_surface(32, 32)
    # ---- 柜体外壳 ----
    draw_rect_filled(surf, 0, 0, 32, 32, (90, 95, 105))
    # 外壳高光（顶部和左侧）
    draw_hline(surf, 0, 31, 0, (120, 125, 135))
    draw_vline(surf, 0, 0, 31, (120, 125, 135))
    # 外壳阴影（底部和右侧）
    draw_hline(surf, 0, 31, 31, (60, 65, 75))
    draw_vline(surf, 31, 0, 31, (60, 65, 75))
    # 内部面板
    draw_rect_filled(surf, 1, 1, 30, 30, (100, 105, 115))
    # ---- 顶部标签牌 ----
    draw_rect_filled(surf, 2, 2, 28, 3, (70, 75, 85))
    draw_hline(surf, 4, 27, 3, (160, 160, 170))  # 标签文字
    draw_hline(surf, 4, 20, 3, (180, 180, 190))  # 标签文字高光
    # ---- 上层隔间（透明门+篮球） ----
    draw_rect_filled(surf, 2, 6, 13, 8, (80, 85, 95))
    draw_rect_filled(surf, 3, 7, 11, 6, (110, 115, 125))
    # 透明门效果（浅色覆盖）
    draw_rect_filled(surf, 3, 7, 11, 6, (120, 130, 145))
    # 门内篮球
    draw_pixel(surf, 7, 9, (220, 110, 40))
    draw_pixel(surf, 8, 9, (230, 120, 50))
    draw_pixel(surf, 8, 10, (210, 100, 30))
    draw_pixel(surf, 7, 10, (200, 90, 25))
    # 门把手
    draw_pixel(surf, 12, 9, (180, 180, 190))
    draw_pixel(surf, 12, 10, (160, 160, 170))
    # 上层右隔间
    draw_rect_filled(surf, 17, 6, 13, 8, (80, 85, 95))
    draw_rect_filled(surf, 18, 7, 11, 6, (120, 130, 145))
    # 门内排球
    draw_pixel(surf, 22, 9, (240, 240, 245))
    draw_pixel(surf, 23, 9, (230, 230, 235))
    draw_pixel(surf, 23, 10, (220, 220, 225))
    draw_pixel(surf, 22, 10, (235, 235, 240))
    # 排球纹线
    draw_pixel(surf, 22, 9, (200, 80, 80))
    draw_pixel(surf, 23, 10, (80, 80, 200))
    # 门把手
    draw_pixel(surf, 18, 9, (180, 180, 190))
    draw_pixel(surf, 18, 10, (160, 160, 170))
    # ---- 中层隔板线 ----
    draw_hline(surf, 2, 29, 14, (70, 75, 85))
    draw_hline(surf, 2, 29, 15, (110, 115, 125))
    # ---- 中层隔间（球拍+护具） ----
    draw_rect_filled(surf, 2, 16, 13, 7, (80, 85, 95))
    draw_rect_filled(surf, 3, 17, 11, 5, (120, 130, 145))
    # 门内球拍
    draw_pixel(surf, 5, 17, (160, 120, 80))
    draw_pixel(surf, 6, 17, (170, 130, 90))
    draw_pixel(surf, 6, 18, (160, 120, 80))
    draw_pixel(surf, 7, 18, (150, 110, 70))
    draw_pixel(surf, 7, 19, (140, 100, 60))
    # 球拍手柄
    draw_pixel(surf, 8, 19, (120, 90, 50))
    draw_pixel(surf, 8, 20, (110, 80, 40))
    # 门把手
    draw_pixel(surf, 12, 18, (180, 180, 190))
    draw_pixel(surf, 12, 19, (160, 160, 170))
    # 中层右隔间
    draw_rect_filled(surf, 17, 16, 13, 7, (80, 85, 95))
    draw_rect_filled(surf, 18, 17, 11, 5, (120, 130, 145))
    # 门内护膝
    draw_pixel(surf, 21, 18, (60, 60, 160))
    draw_pixel(surf, 22, 18, (70, 70, 170))
    draw_pixel(surf, 22, 19, (60, 60, 160))
    draw_pixel(surf, 23, 19, (50, 50, 150))
    # 门把手
    draw_pixel(surf, 18, 18, (180, 180, 190))
    draw_pixel(surf, 18, 19, (160, 160, 170))
    # ---- 下层隔板线 ----
    draw_hline(surf, 2, 29, 23, (70, 75, 85))
    draw_hline(surf, 2, 29, 24, (110, 115, 125))
    # ---- 下层（大隔间，放大型器材） ----
    draw_rect_filled(surf, 2, 25, 28, 5, (80, 85, 95))
    draw_rect_filled(surf, 3, 26, 26, 3, (120, 130, 145))
    # 门内哑铃
    draw_pixel(surf, 8, 27, (140, 140, 150))
    draw_pixel(surf, 9, 27, (100, 100, 110))
    draw_pixel(surf, 10, 27, (100, 100, 110))
    draw_pixel(surf, 11, 27, (140, 140, 150))
    # 门内跳绳
    draw_pixel(surf, 18, 26, (200, 160, 60))
    draw_pixel(surf, 19, 27, (200, 160, 60))
    draw_pixel(surf, 20, 27, (200, 160, 60))
    draw_pixel(surf, 21, 26, (200, 160, 60))
    # 下层门把手
    draw_pixel(surf, 15, 27, (180, 180, 190))
    # ---- 中间竖隔板 ----
    draw_vline(surf, 16, 6, 30, (70, 75, 85))
    draw_vline(surf, 15, 6, 30, (110, 115, 125))
    # ---- 底部踢脚线 ----
    draw_hline(surf, 1, 30, 30, (60, 65, 75))
    pygame.image.save(surf, path)


def create_door_entrance(path):
    """门入口: 16×24"""
    surf = make_surface(16, 24)
    # 门框
    draw_rect_filled(surf, 0, 0, 16, 24, (100, 70, 35))
    draw_rect_filled(surf, 1, 1, 14, 22, (80, 55, 25))
    # 门板
    draw_rect_filled(surf, 2, 2, 12, 20, (120, 85, 45))
    draw_rect_filled(surf, 3, 3, 10, 18, (140, 100, 55))
    # 门板纹理
    draw_hline(surf, 3, 12, 10, (130, 90, 50))
    draw_hline(surf, 3, 12, 14, (130, 90, 50))
    # 门把手
    draw_rect_filled(surf, 10, 10, 2, 3, (200, 180, 60))
    draw_pixel(surf, 10, 11, (220, 200, 80))
    # 门上方横梁
    draw_rect_filled(surf, 0, 0, 16, 2, (90, 60, 30))
    # 门内暗处（表示室内）
    draw_rect_filled(surf, 4, 4, 8, 6, (50, 40, 30))
    draw_rect_filled(surf, 4, 11, 8, 9, (50, 40, 30))
    # 门内微光
    draw_pixel(surf, 7, 5, (70, 60, 45))
    draw_pixel(surf, 8, 6, (70, 60, 45))
    pygame.image.save(surf, path)


def create_shooting_station(path):
    """投篮站: 24×48，篮球架（加高版，比例接近现实）
    现实中篮筐高3.05m，人高1.7m，比例≈1.79
    NPC高24px，篮筐高度≈43px，加上底座总高48px
    """
    surf = make_surface(24, 48)
    # ---- 篮板支架（更高，从底座延伸到篮板） ----
    draw_rect_filled(surf, 18, 6, 3, 36, (120, 120, 130))
    # 支架高光
    draw_pixel(surf, 19, 8, (140, 140, 150))
    draw_pixel(surf, 19, 16, (130, 130, 140))
    draw_pixel(surf, 19, 24, (135, 135, 145))
    draw_pixel(surf, 19, 32, (130, 130, 140))
    # ---- 横向支撑臂（连接支架与篮板） ----
    draw_hline(surf, 14, 18, 8, (110, 110, 120))
    draw_hline(surf, 14, 18, 9, (100, 100, 110))
    # ---- 篮板（更高位置，接近顶部） ----
    draw_rect_filled(surf, 8, 6, 10, 8, (230, 230, 240))
    draw_rect_filled(surf, 9, 7, 8, 6, (210, 210, 220))
    # 篮板内框（红色方框）
    draw_rect_filled(surf, 10, 8, 6, 4, (190, 190, 200))
    draw_hline(surf, 11, 14, 9, (220, 60, 40))
    draw_hline(surf, 11, 14, 10, (220, 60, 40))
    # 篮板边框
    draw_hline(surf, 8, 17, 6, (180, 180, 190))
    draw_hline(surf, 8, 17, 13, (180, 180, 190))
    draw_vline(surf, 8, 6, 13, (180, 180, 190))
    draw_vline(surf, 17, 6, 13, (180, 180, 190))
    # ---- 篮筐（橙红色，从篮板下方伸出） ----
    draw_hline(surf, 4, 11, 14, (220, 90, 30))
    draw_hline(surf, 4, 11, 15, (200, 70, 20))
    # 篮筐连接点
    draw_pixel(surf, 11, 14, (200, 80, 25))
    draw_pixel(surf, 11, 15, (180, 60, 15))
    # ---- 篮网（白色竖线+横线编织） ----
    draw_vline(surf, 5, 15, 20, (230, 230, 240))
    draw_vline(surf, 7, 15, 21, (220, 220, 230))
    draw_vline(surf, 9, 15, 21, (220, 220, 230))
    draw_hline(surf, 5, 9, 18, (210, 210, 220))
    draw_hline(surf, 5, 9, 20, (200, 200, 210))
    # ---- 底座 ----
    draw_rect_filled(surf, 15, 40, 7, 4, (100, 100, 110))
    draw_rect_filled(surf, 14, 43, 9, 3, (80, 80, 90))
    # 底座高光
    draw_pixel(surf, 16, 40, (120, 120, 130))
    draw_pixel(surf, 17, 40, (115, 115, 125))
    # 底座斜撑（从支架到底座的加固结构）
    draw_pixel(surf, 16, 39, (100, 100, 110))
    draw_pixel(surf, 15, 38, (95, 95, 105))
    # ---- 篮球（地面位置） ----
    draw_pixel(surf, 5, 43, (240, 140, 60))
    draw_pixel(surf, 6, 42, (240, 140, 60))
    draw_pixel(surf, 6, 43, (220, 120, 40))
    draw_pixel(surf, 7, 43, (220, 120, 40))
    draw_pixel(surf, 5, 42, (220, 120, 40))
    # 球上纹线
    draw_pixel(surf, 6, 43, (180, 80, 20))
    # 篮球高光
    draw_pixel(surf, 5, 42, (250, 160, 80))
    pygame.image.save(surf, path)


def create_osmanthus_branch(path):
    """桂花枝: 12×12，拾取物"""
    surf = make_surface(12, 12)
    # 枝条（棕色弧线）
    draw_pixel(surf, 2, 9, (100, 70, 30))
    draw_pixel(surf, 3, 8, (110, 75, 35))
    draw_pixel(surf, 4, 7, (110, 75, 35))
    draw_pixel(surf, 5, 6, (120, 80, 40))
    draw_pixel(surf, 6, 5, (120, 80, 40))
    draw_pixel(surf, 7, 4, (110, 75, 35))
    draw_pixel(surf, 8, 3, (100, 70, 30))
    draw_pixel(surf, 9, 2, (100, 70, 30))
    # 叶子（绿色椭圆）
    draw_pixel(surf, 3, 7, (60, 140, 40))
    draw_pixel(surf, 4, 6, (70, 150, 50))
    draw_pixel(surf, 6, 4, (60, 140, 40))
    draw_pixel(surf, 7, 3, (70, 150, 50))
    draw_pixel(surf, 8, 4, (65, 145, 45))
    # 桂花（黄色小点）
    draw_pixel(surf, 4, 5, (240, 220, 60))
    draw_pixel(surf, 5, 4, (255, 230, 70))
    draw_pixel(surf, 6, 3, (240, 220, 60))
    draw_pixel(surf, 7, 2, (255, 230, 70))
    draw_pixel(surf, 8, 2, (240, 220, 60))
    draw_pixel(surf, 9, 1, (255, 230, 70))
    # 花朵高光
    draw_pixel(surf, 5, 3, (255, 245, 120))
    draw_pixel(surf, 8, 1, (255, 245, 120))
    pygame.image.save(surf, path)


def create_old_bookmark(path):
    """古旧书签: 12×12，拾取物"""
    surf = make_surface(12, 12)
    # 书签主体（竹黄色长条）
    draw_rect_filled(surf, 4, 1, 4, 9, (190, 160, 90))
    draw_rect_filled(surf, 5, 1, 2, 9, (200, 170, 100))
    # 暗色纹理
    draw_pixel(surf, 4, 3, (170, 140, 75))
    draw_pixel(surf, 7, 5, (170, 140, 75))
    draw_pixel(surf, 5, 7, (170, 140, 75))
    # 顶部装饰（红色横条）
    draw_rect_filled(surf, 3, 1, 6, 2, (160, 50, 40))
    draw_pixel(surf, 4, 1, (180, 60, 50))
    # 顶部圆孔
    draw_pixel(surf, 6, 1, (190, 160, 90))
    # 穗子（从底部垂下）
    draw_pixel(surf, 5, 10, (160, 50, 40))
    draw_pixel(surf, 6, 10, (160, 50, 40))
    draw_pixel(surf, 5, 11, (140, 40, 30))
    draw_pixel(surf, 6, 11, (140, 40, 30))
    # 穗子流苏
    draw_pixel(surf, 4, 11, (140, 40, 30))
    draw_pixel(surf, 7, 11, (140, 40, 30))
    # 中间文字纹（小横线模拟古文）
    draw_pixel(surf, 5, 4, (140, 110, 60))
    draw_pixel(surf, 6, 4, (140, 110, 60))
    draw_pixel(surf, 5, 6, (140, 110, 60))
    draw_pixel(surf, 6, 6, (140, 110, 60))
    draw_pixel(surf, 5, 8, (140, 110, 60))
    draw_pixel(surf, 6, 8, (140, 110, 60))
    pygame.image.save(surf, path)


def create_water_bottle(path):
    """水壶: 12×12，拾取物"""
    surf = make_surface(12, 12)
    # 壶盖（白色）
    draw_rect_filled(surf, 4, 1, 4, 2, (220, 220, 230))
    draw_pixel(surf, 5, 0, (200, 200, 210))
    draw_pixel(surf, 6, 0, (200, 200, 210))
    # 壶身（蓝色）
    draw_rect_filled(surf, 3, 3, 6, 7, (80, 140, 210))
    draw_rect_filled(surf, 4, 3, 4, 7, (100, 160, 230))
    # 壶身高光
    draw_pixel(surf, 4, 4, (140, 190, 250))
    draw_pixel(surf, 4, 5, (130, 180, 245))
    draw_pixel(surf, 4, 6, (120, 170, 240))
    # 壶身暗面
    draw_pixel(surf, 8, 4, (60, 120, 190))
    draw_pixel(surf, 8, 6, (60, 120, 190))
    # 壶底
    draw_rect_filled(surf, 3, 9, 6, 1, (60, 110, 180))
    # 标签（白色小条）
    draw_rect_filled(surf, 5, 5, 2, 3, (230, 230, 240))
    draw_pixel(surf, 5, 6, (200, 200, 210))
    pygame.image.save(surf, path)


def create_old_badge(path):
    """旧校徽: 12×12，拾取物"""
    surf = make_surface(12, 12)
    # 徽章外圈（铜色）
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            dist = dx * dx + dy * dy
            if dist <= 20:
                draw_pixel(surf, 6 + dx, 6 + dy, (180, 150, 80))
    # 徽章内圈（深铜色）
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            dist = dx * dx + dy * dy
            if dist <= 11:
                draw_pixel(surf, 6 + dx, 6 + dy, (150, 120, 60))
    # 徽章中心图案（暗色）
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            dist = dx * dx + dy * dy
            if dist <= 5:
                draw_pixel(surf, 6 + dx, 6 + dy, (120, 90, 40))
    # 中心高光点
    draw_pixel(surf, 5, 5, (210, 180, 100))
    # 边缘高光
    draw_pixel(surf, 3, 3, (200, 170, 90))
    draw_pixel(surf, 8, 4, (190, 160, 85))
    # 暗面
    draw_pixel(surf, 4, 8, (140, 110, 55))
    draw_pixel(surf, 8, 8, (140, 110, 55))
    pygame.image.save(surf, path)


def create_magnifying_glass(path):
    """放大镜: 12×12，拾取物"""
    surf = make_surface(12, 12)
    # 镜片（圆形，蓝色高光）
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            dist = dx * dx + dy * dy
            if dist <= 9:
                draw_pixel(surf, 4 + dx, 4 + dy, (160, 200, 240))
    # 镜片内部高光
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            dist = dx * dx + dy * dy
            if dist <= 5:
                draw_pixel(surf, 4 + dx, 4 + dy, (180, 220, 255))
    # 镜片中心亮点
    draw_pixel(surf, 3, 3, (220, 240, 255))
    draw_pixel(surf, 4, 4, (200, 230, 250))
    # 镜框（深棕色圆环）
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            dist = dx * dx + dy * dy
            if 8 < dist <= 11:
                draw_pixel(surf, 4 + dx, 4 + dy, (100, 70, 35))
    # 镜框高光
    draw_pixel(surf, 2, 2, (130, 90, 50))
    # 手柄（棕色，斜向右下）
    draw_pixel(surf, 7, 7, (110, 75, 35))
    draw_pixel(surf, 8, 8, (120, 80, 40))
    draw_pixel(surf, 9, 9, (110, 75, 35))
    draw_pixel(surf, 10, 10, (100, 70, 30))
    draw_pixel(surf, 11, 11, (90, 60, 25))
    # 手柄高光
    draw_pixel(surf, 8, 7, (140, 100, 55))
    draw_pixel(surf, 9, 8, (130, 90, 50))
    pygame.image.save(surf, path)


# ============================================================
# 主函数
# ============================================================
if __name__ == "__main__":
    pygame.init()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sprites_dir = os.path.join(base_dir, "assets", "sprites")
    os.makedirs(sprites_dir, exist_ok=True)

    generated_files = []

    # --- 玩家精灵表 ---
    player_path = os.path.join(sprites_dir, "player_sheet.png")
    create_player_sheet(player_path)
    generated_files.append("player_sheet.png")
    print("[OK] 玩家精灵表已生成")

    # --- NPC 精灵表 ---
    npc_configs = [
        ("senior_student_sheet.png", COLOR_SENIOR_BODY, COLOR_SENIOR_BODY_DARK,
         COLOR_PLAYER_HAIR, {"has_glasses": True, "hair_style": "short"}),
        ("librarian_sheet.png", COLOR_LIBRARIAN_BODY, COLOR_LIBRARIAN_BODY_DARK,
         COLOR_LIBRARIAN_HAIR, {"hair_style": "bun"}),
        ("dancing_auntie_sheet.png", COLOR_AUNTIE_BODY, COLOR_AUNTIE_BODY_DARK,
         COLOR_AUNTIE_HAIR, {"hair_style": "curly"}),
        ("pe_teacher_sheet.png", COLOR_PE_BODY, COLOR_PE_BODY_DARK,
         COLOR_PE_HAIR, {"hair_style": "very_short"}),
        ("cafeteria_auntie_sheet.png", COLOR_CAFETERIA_BODY, COLOR_CAFETERIA_BODY_DARK,
         COLOR_CAFETERIA_HAIRNET, {"has_apron": True, "apron_color": COLOR_CAFETERIA_APRON,
                                   "has_hairnet": True, "hairnet_color": COLOR_CAFETERIA_HAIRNET,
                                   "hair_style": "curly"}),
        ("guardian_sheet.png", COLOR_GUARDIAN_CLOAK, COLOR_GUARDIAN_CLOAK_DARK,
         (0, 0, 0), {"has_hood": True, "hood_color": COLOR_GUARDIAN_CLOAK, "eye_glow": True}),
        ("passing_student_sheet.png", COLOR_PASSING_STUDENT_BODY, COLOR_PASSING_STUDENT_BODY_DARK,
         COLOR_PASSING_STUDENT_HAIR, {"hair_style": "short"}),
    ]

    for filename, body, body_dark, hair, kwargs in npc_configs:
        npc_path = os.path.join(sprites_dir, filename)
        create_npc_sheet(npc_path, body, body_dark, hair, **kwargs)
        generated_files.append(filename)
        print(f"[OK] NPC精灵表已生成: {filename}")

    # --- 可互动物体精灵 ---
    object_generators = [
        ("osmanthus_tree.png", create_osmanthus_tree),
        ("osmanthus_tree_glow.png", create_osmanthus_tree_glow),
        ("street_lamp.png", create_street_lamp),
        ("bookshelf.png", create_bookshelf),
        ("bulletin_board.png", create_bulletin_board),
        ("computer_terminal.png", create_computer_terminal),
        ("sculpture.png", create_sculpture),
        ("flowerbed.png", create_flowerbed),
        ("fountain.png", create_fountain),
        ("badge_pickup.png", create_badge_pickup),
        ("dining_table.png", create_dining_table),
        ("scoreboard.png", create_scoreboard),
        ("equipment_cabinet.png", create_equipment_cabinet),
        ("door_entrance.png", create_door_entrance),
        ("shooting_station.png", create_shooting_station),
        ("osmanthus_branch.png", create_osmanthus_branch),
        ("old_bookmark.png", create_old_bookmark),
        ("water_bottle.png", create_water_bottle),
        ("old_badge.png", create_old_badge),
        ("magnifying_glass.png", create_magnifying_glass),
    ]

    for filename, generator in object_generators:
        obj_path = os.path.join(sprites_dir, filename)
        generator(obj_path)
        generated_files.append(filename)
        print(f"[OK] 物体精灵已生成: {filename}")

    pygame.quit()
    print(f"\n全部完成! 共生成 {len(generated_files)} 个精灵文件")
    print(f"保存路径: {sprites_dir}")
    for f in generated_files:
        print(f"  - {f}")
