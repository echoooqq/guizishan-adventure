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
    """书架: 32×24"""
    surf = make_surface(32, 24)
    # 木质框架
    draw_rect_filled(surf, 0, 0, 32, 24, (120, 80, 40))
    draw_rect_filled(surf, 1, 1, 30, 22, (100, 65, 30))
    # 隔板
    draw_hline(surf, 1, 30, 8, (120, 80, 40))
    draw_hline(surf, 1, 30, 16, (120, 80, 40))
    # 书籍 - 第一层
    book_colors_1 = [(180, 40, 40), (40, 80, 160), (40, 140, 60), (200, 160, 40), (140, 40, 140)]
    x = 2
    for color in book_colors_1:
        w = 4 if color != book_colors_1[2] else 5
        draw_rect_filled(surf, x, 2, w, 6, color)
        draw_vline(surf, x, 2, 7, (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40)))
        x += w + 1
    # 书籍 - 第二层
    book_colors_2 = [(60, 60, 140), (160, 80, 40), (80, 160, 80), (180, 60, 100), (100, 100, 40)]
    x = 2
    for color in book_colors_2:
        w = 5 if color != book_colors_2[3] else 4
        draw_rect_filled(surf, x, 9, w, 7, color)
        draw_vline(surf, x, 9, 15, (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40)))
        x += w + 1
    # 书籍 - 第三层
    book_colors_3 = [(140, 100, 60), (60, 120, 140), (160, 40, 80), (80, 80, 120), (120, 140, 60)]
    x = 2
    for color in book_colors_3:
        w = 4 if color != book_colors_3[0] else 6
        draw_rect_filled(surf, x, 17, w, 5, color)
        draw_vline(surf, x, 17, 21, (min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40)))
        x += w + 1
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
    """校园雕塑: 20×28"""
    surf = make_surface(20, 28)
    # 底座
    draw_rect_filled(surf, 2, 22, 16, 6, (140, 140, 140))
    draw_rect_filled(surf, 3, 23, 14, 4, (160, 160, 160))
    draw_hline(surf, 2, 17, 22, (120, 120, 120))
    # 雕塑主体 - 抽象人形
    # 身体
    draw_rect_filled(surf, 8, 8, 4, 12, (170, 170, 170))
    draw_rect_filled(surf, 7, 10, 6, 8, (170, 170, 170))
    # 头
    draw_rect_filled(surf, 8, 4, 4, 5, (180, 180, 180))
    draw_rect_filled(surf, 7, 5, 6, 3, (180, 180, 180))
    # 手臂伸展
    draw_hline(surf, 3, 7, 11, (170, 170, 170))
    draw_hline(surf, 12, 16, 11, (170, 170, 170))
    # 手
    draw_pixel(surf, 3, 11, (180, 180, 180))
    draw_pixel(surf, 16, 11, (180, 180, 180))
    # 高光
    draw_vline(surf, 9, 5, 18, (190, 190, 190))
    draw_pixel(surf, 9, 4, (190, 190, 190))
    pygame.image.save(surf, path)


def create_fountain(path):
    """喷泉: 32×32"""
    surf = make_surface(32, 32)
    # 底座 - 外圈
    for y in range(20, 32):
        for x in range(32):
            dx = abs(x - 16)
            dy = y - 26
            if dx * dx + dy * dy < 196:
                draw_pixel(surf, x, y, (150, 150, 155))
            elif dx * dx + dy * dy < 225:
                draw_pixel(surf, x, y, (130, 130, 135))
    # 底座高光
    for y in range(21, 28):
        for x in range(8, 24):
            dx = abs(x - 16)
            dy = y - 26
            if dx * dx + dy * dy < 120:
                draw_pixel(surf, x, y, (165, 165, 170))
    # 水面
    for y in range(22, 28):
        for x in range(8, 24):
            dx = abs(x - 16)
            dy = y - 26
            if dx * dx + dy * dy < 80:
                draw_pixel(surf, x, y, (80, 140, 200))
    # 水面高光
    draw_pixel(surf, 13, 24, (120, 180, 240))
    draw_pixel(surf, 14, 23, (120, 180, 240))
    draw_pixel(surf, 18, 25, (120, 180, 240))
    # 中心柱
    draw_rect_filled(surf, 14, 12, 4, 12, (140, 140, 145))
    draw_rect_filled(surf, 15, 12, 2, 12, (155, 155, 160))
    # 顶部碗
    draw_rect_filled(surf, 11, 10, 10, 3, (140, 140, 145))
    draw_rect_filled(surf, 12, 11, 8, 1, (155, 155, 160))
    # 水花
    draw_pixel(surf, 15, 6, (120, 180, 240))
    draw_pixel(surf, 16, 5, (120, 180, 240))
    draw_pixel(surf, 14, 4, (100, 160, 220))
    draw_pixel(surf, 17, 4, (100, 160, 220))
    draw_pixel(surf, 13, 3, (80, 140, 200))
    draw_pixel(surf, 18, 3, (80, 140, 200))
    draw_pixel(surf, 16, 2, (80, 140, 200))
    # 水滴
    draw_pixel(surf, 12, 8, (100, 170, 230))
    draw_pixel(surf, 19, 7, (100, 170, 230))
    draw_pixel(surf, 11, 9, (80, 150, 210))
    draw_pixel(surf, 20, 9, (80, 150, 210))
    pygame.image.save(surf, path)


def create_badge_pickup(path):
    """徽章拾取物: 12×12"""
    surf = make_surface(12, 12)
    cx, cy = 6, 6
    # 光晕
    for y in range(12):
        for x in range(12):
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 6:
                alpha = int(40 * (1 - dist / 6))
                surf.set_at((x, y), (255, 220, 50, alpha))
    # 星形
    points = []
    for i in range(5):
        angle = math.radians(-90 + i * 72)
        points.append((cx + int(4 * math.cos(angle)), cy + int(4 * math.sin(angle))))
        angle2 = math.radians(-90 + i * 72 + 36)
        points.append((cx + int(2 * math.cos(angle2)), cy + int(2 * math.sin(angle2))))
    # 填充星形
    for y in range(12):
        for x in range(12):
            if _point_in_polygon(x, y, points):
                surf.set_at((x, y), (255, 215, 0))
    # 星形边框
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        _draw_line_on_surf(surf, x1, y1, x2, y2, (200, 170, 0))
    # 中心亮点
    draw_pixel(surf, cx, cy, (255, 255, 200))
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
    """记分板: 24×20"""
    surf = make_surface(24, 20)
    # 外框
    draw_rect_filled(surf, 0, 0, 24, 20, (60, 60, 70))
    draw_rect_filled(surf, 1, 1, 22, 18, (80, 80, 90))
    # 白色区域
    draw_rect_filled(surf, 2, 2, 20, 16, (240, 240, 235))
    # 分数显示区
    draw_rect_filled(surf, 3, 3, 18, 6, (220, 220, 215))
    # 数字（像素风格）
    # "00"
    _draw_digit(surf, 5, 4, 0, (40, 40, 40))
    _draw_digit(surf, 10, 4, 0, (40, 40, 40))
    # 冒号
    draw_pixel(surf, 15, 5, (40, 40, 40))
    draw_pixel(surf, 15, 7, (40, 40, 40))
    # 底部文字区
    draw_hline(surf, 3, 21, 10, (200, 200, 195))
    draw_hline(surf, 4, 12, 12, (180, 180, 175))
    draw_hline(surf, 4, 12, 14, (180, 180, 175))
    draw_hline(surf, 14, 20, 12, (180, 180, 175))
    draw_hline(surf, 14, 20, 14, (180, 180, 175))
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
    """器材柜: 24×24"""
    surf = make_surface(24, 24)
    # 柜体
    draw_rect_filled(surf, 0, 0, 24, 24, (120, 120, 130))
    draw_rect_filled(surf, 1, 1, 22, 22, (140, 140, 150))
    # 隔板
    draw_hline(surf, 1, 22, 8, (120, 120, 130))
    draw_hline(surf, 1, 22, 16, (120, 120, 130))
    # 上层
    draw_rect_filled(surf, 2, 2, 9, 6, (130, 130, 140))
    draw_rect_filled(surf, 13, 2, 9, 6, (130, 130, 140))
    # 把手
    draw_pixel(surf, 10, 5, (180, 180, 190))
    draw_pixel(surf, 13, 5, (180, 180, 190))
    # 中层
    draw_rect_filled(surf, 2, 9, 9, 7, (130, 130, 140))
    draw_rect_filled(surf, 13, 9, 9, 7, (130, 130, 140))
    # 器材轮廓（球）
    draw_pixel(surf, 5, 12, (200, 100, 50))
    draw_pixel(surf, 6, 11, (200, 100, 50))
    draw_pixel(surf, 6, 12, (220, 120, 60))
    draw_pixel(surf, 7, 12, (200, 100, 50))
    # 把手
    draw_pixel(surf, 10, 12, (180, 180, 190))
    draw_pixel(surf, 13, 12, (180, 180, 190))
    # 下层
    draw_rect_filled(surf, 2, 17, 9, 5, (130, 130, 140))
    draw_rect_filled(surf, 13, 17, 9, 5, (130, 130, 140))
    # 器材（球拍轮廓）
    draw_pixel(surf, 16, 18, (160, 120, 80))
    draw_pixel(surf, 17, 18, (160, 120, 80))
    draw_pixel(surf, 17, 19, (160, 120, 80))
    draw_pixel(surf, 18, 19, (160, 120, 80))
    draw_pixel(surf, 18, 20, (140, 100, 60))
    # 把手
    draw_pixel(surf, 10, 19, (180, 180, 190))
    draw_pixel(surf, 13, 19, (180, 180, 190))
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
        ("fountain.png", create_fountain),
        ("badge_pickup.png", create_badge_pickup),
        ("dining_table.png", create_dining_table),
        ("scoreboard.png", create_scoreboard),
        ("equipment_cabinet.png", create_equipment_cabinet),
        ("door_entrance.png", create_door_entrance),
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
