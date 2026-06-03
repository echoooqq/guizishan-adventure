import os
import math
import pygame


def create_button_normal(path, w=64, h=24):
    pygame.init()
    surf = pygame.Surface((w, h))
    surf.fill((60, 60, 80))
    pygame.draw.rect(surf, (100, 100, 130), (0, 0, w, h), 2)
    pygame.draw.line(surf, (120, 120, 160), (2, 2), (w - 3, 2))
    pygame.draw.line(surf, (120, 120, 160), (2, 2), (2, h - 3))
    pygame.draw.line(surf, (40, 40, 60), (w - 2, 2), (w - 2, h - 2))
    pygame.draw.line(surf, (40, 40, 60), (2, h - 2), (w - 2, h - 2))
    pygame.image.save(surf, path)


def create_button_hover(path, w=64, h=24):
    surf = pygame.Surface((w, h))
    surf.fill((80, 80, 110))
    pygame.draw.rect(surf, (140, 140, 180), (0, 0, w, h), 2)
    pygame.draw.line(surf, (160, 160, 200), (2, 2), (w - 3, 2))
    pygame.draw.line(surf, (160, 160, 200), (2, 2), (2, h - 3))
    pygame.draw.line(surf, (50, 50, 70), (w - 2, 2), (w - 2, h - 2))
    pygame.draw.line(surf, (50, 50, 70), (2, h - 2), (w - 2, h - 2))
    pygame.image.save(surf, path)


def create_button_pressed(path, w=64, h=24):
    surf = pygame.Surface((w, h))
    surf.fill((50, 50, 70))
    pygame.draw.rect(surf, (90, 90, 120), (0, 0, w, h), 2)
    pygame.draw.line(surf, (40, 40, 60), (2, 2), (w - 3, 2))
    pygame.draw.line(surf, (40, 40, 60), (2, 2), (2, h - 3))
    pygame.draw.line(surf, (100, 100, 140), (w - 2, 2), (w - 2, h - 2))
    pygame.draw.line(surf, (100, 100, 140), (2, h - 2), (w - 2, h - 2))
    pygame.image.save(surf, path)


def create_panel_border(path, w=96, h=96):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((30, 30, 50, 200))
    pygame.draw.rect(surf, (100, 100, 140), (0, 0, w, h), 3)
    pygame.draw.rect(surf, (70, 70, 100), (3, 3, w - 6, h - 6), 1)
    corner_len = 6
    for cx, cy in [(0, 0), (w, 0), (0, h), (w, h)]:
        dx = -1 if cx > 0 else 1
        dy = -1 if cy > 0 else 1
        pygame.draw.line(surf, (140, 140, 180), (cx, cy), (cx + dx * corner_len, cy), 2)
        pygame.draw.line(surf, (140, 140, 180), (cx, cy), (cx, cy + dy * corner_len), 2)
    pygame.image.save(surf, path)


def create_dialog_border(path, w=160, h=48):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((20, 20, 40, 220))
    pygame.draw.rect(surf, (120, 100, 60), (0, 0, w, h), 2)
    pygame.draw.rect(surf, (80, 70, 40), (2, 2, w - 4, h - 4), 1)
    for cx in range(4, w - 4, 16):
        pygame.draw.circle(surf, (160, 130, 60), (cx, 1), 2)
    pygame.image.save(surf, path)


def create_inventory_slot(path, s=32):
    surf = pygame.Surface((s, s))
    surf.fill((40, 40, 60))
    pygame.draw.rect(surf, (80, 80, 110), (0, 0, s, s), 2)
    pygame.draw.line(surf, (60, 60, 80), (2, 2), (s - 3, 2))
    pygame.draw.line(surf, (60, 60, 80), (2, 2), (2, s - 3))
    pygame.draw.line(surf, (30, 30, 50), (s - 2, 2), (s - 2, s - 2))
    pygame.draw.line(surf, (30, 30, 50), (2, s - 2), (s - 2, s - 2))
    pygame.image.save(surf, path)


def create_minimap_frame(path, w=80, h=60):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (160, 140, 80), (0, 0, w, h), 2)
    pygame.draw.rect(surf, (120, 100, 60), (2, 2, w - 4, h - 4), 1)
    pygame.image.save(surf, path)


def create_hud_bar(path, w=64, h=8, fill_ratio=1.0, color=(76, 175, 80)):
    surf = pygame.Surface((w, h))
    surf.fill((40, 40, 40))
    fill_w = int((w - 2) * fill_ratio)
    if fill_w > 0:
        pygame.draw.rect(surf, color, (1, 1, fill_w, h - 2))
    pygame.draw.rect(surf, (100, 100, 100), (0, 0, w, h), 1)
    pygame.image.save(surf, path)


def create_badge_icon(path, s=12, filled=False):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = s // 2, s // 2
    r = s // 2 - 1
    if filled:
        pygame.draw.circle(surf, (255, 200, 0), (cx, cy), r)
        pygame.draw.circle(surf, (255, 230, 100), (cx, cy), r - 2)
    else:
        pygame.draw.circle(surf, (80, 80, 80), (cx, cy), r, 1)
    for angle in range(0, 360, 72):
        px = cx + int((r - 1) * math.cos(math.radians(angle)))
        py = cy + int((r - 1) * math.sin(math.radians(angle)))
        if filled:
            surf.set_at((px, py), (200, 150, 0))
        else:
            surf.set_at((px, py), (60, 60, 60))
    pygame.image.save(surf, path)


def create_key_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (200, 180, 50), (10, 10), 6, 2)
    pygame.draw.line(surf, (200, 180, 50), (16, 10), (26, 10), 2)
    pygame.draw.line(surf, (200, 180, 50), (22, 10), (22, 14), 2)
    pygame.draw.line(surf, (200, 180, 50), (26, 10), (26, 14), 2)
    pygame.image.save(surf, path)


def create_book_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (139, 69, 19), (6, 4, 20, 24))
    pygame.draw.rect(surf, (160, 82, 45), (8, 6, 16, 20))
    pygame.draw.line(surf, (100, 50, 10), (16, 6), (16, 26), 1)
    pygame.draw.line(surf, (200, 200, 200), (10, 10), (14, 10), 1)
    pygame.draw.line(surf, (200, 200, 200), (10, 14), (14, 14), 1)
    pygame.image.save(surf, path)


def create_note_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (240, 230, 200), (6, 4, 20, 24))
    pygame.draw.rect(surf, (180, 170, 140), (6, 4, 20, 24), 1)
    for dy in range(3):
        pygame.draw.line(surf, (100, 100, 100), (9, 10 + dy * 5), (23, 10 + dy * 5), 1)
    pygame.image.save(surf, path)


def create_badge_fragment_icon(path, s=32, index=1):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = s // 2, s // 2
    colors = [
        (255, 200, 0), (200, 255, 0), (0, 200, 255),
        (255, 100, 0), (200, 0, 255), (0, 255, 100), (255, 0, 100),
    ]
    color = colors[(index - 1) % len(colors)]
    points = []
    for i in range(5):
        angle = math.radians(-90 + i * 72)
        points.append((cx + int(12 * math.cos(angle)), cy + int(12 * math.sin(angle))))
        angle2 = math.radians(-90 + i * 72 + 36)
        points.append((cx + int(6 * math.cos(angle2)), cy + int(6 * math.sin(angle2))))
    pygame.draw.polygon(surf, color, points)
    pygame.draw.polygon(surf, (255, 255, 255), points, 1)
    inner_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
    pygame.draw.circle(surf, inner_color, (cx, cy), 4)
    pygame.image.save(surf, path)


def create_branch_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.line(surf, (100, 70, 30), (8, 26), (16, 12), 3)
    pygame.draw.line(surf, (100, 70, 30), (16, 12), (24, 8), 2)
    pygame.draw.line(surf, (100, 70, 30), (16, 12), (12, 6), 2)
    pygame.draw.circle(surf, (255, 200, 50), (24, 6), 3)
    pygame.draw.circle(surf, (255, 220, 80), (12, 4), 3)
    pygame.draw.circle(surf, (255, 200, 50), (20, 14), 2)
    pygame.image.save(surf, path)


def create_bookmark_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (180, 150, 100), (10, 4, 12, 24))
    pygame.draw.polygon(surf, (160, 130, 80), [(10, 28), (16, 22), (22, 28)])
    pygame.draw.rect(surf, (140, 110, 70), (10, 4, 12, 24), 1)
    pygame.draw.line(surf, (120, 90, 50), (13, 10), (19, 10), 1)
    pygame.draw.line(surf, (120, 90, 50), (13, 14), (19, 14), 1)
    pygame.image.save(surf, path)


def create_magnifier_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (180, 200, 220), (14, 14), 8, 2)
    pygame.draw.circle(surf, (200, 220, 240), (14, 14), 6, 1)
    pygame.draw.line(surf, (140, 120, 80), (20, 20), (27, 27), 3)
    pygame.image.save(surf, path)


def create_badge_old_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = s // 2, s // 2
    pygame.draw.circle(surf, (180, 160, 60), (cx, cy), 10)
    pygame.draw.circle(surf, (200, 180, 80), (cx, cy), 8)
    pygame.draw.circle(surf, (160, 140, 40), (cx, cy), 10, 2)
    pygame.draw.circle(surf, (120, 100, 30), (cx, cy), 4, 1)
    pygame.image.save(surf, path)


def create_bottle_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (100, 160, 220), (10, 10, 12, 18))
    pygame.draw.rect(surf, (80, 140, 200), (10, 10, 12, 18), 1)
    pygame.draw.rect(surf, (120, 80, 60), (12, 6, 8, 6))
    pygame.draw.rect(surf, (100, 60, 40), (12, 6, 8, 6), 1)
    pygame.draw.rect(surf, (80, 200, 255), (12, 16, 8, 10))
    pygame.image.save(surf, path)


def create_sauce_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (200, 50, 30), (8, 12, 16, 16))
    pygame.draw.rect(surf, (180, 40, 20), (8, 12, 16, 16), 1)
    pygame.draw.rect(surf, (220, 200, 160), (10, 6, 12, 8))
    pygame.draw.rect(surf, (200, 180, 140), (10, 6, 12, 8), 1)
    pygame.draw.rect(surf, (100, 80, 60), (13, 4, 6, 4))
    pygame.image.save(surf, path)


def create_card_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (220, 220, 200), (6, 6, 20, 20))
    pygame.draw.rect(surf, (180, 180, 160), (6, 6, 20, 20), 1)
    pygame.draw.rect(surf, (200, 60, 60), (6, 6, 20, 4))
    pygame.draw.line(surf, (160, 160, 140), (8, 14), (24, 14), 1)
    pygame.draw.line(surf, (160, 160, 140), (8, 18), (20, 18), 1)
    pygame.image.save(surf, path)


def create_bookmark_special_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (220, 180, 100), (8, 4, 16, 24))
    pygame.draw.polygon(surf, (200, 160, 80), [(8, 28), (16, 20), (24, 28)])
    pygame.draw.rect(surf, (180, 140, 60), (8, 4, 16, 24), 1)
    pygame.draw.circle(surf, (255, 200, 50), (16, 12), 4)
    pygame.draw.circle(surf, (255, 230, 100), (16, 12), 2)
    pygame.image.save(surf, path)


def create_badge_pattern_icon(path, s=32):
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = s // 2, s // 2
    pygame.draw.circle(surf, (160, 140, 60), (cx, cy), 10)
    pygame.draw.circle(surf, (180, 160, 80), (cx, cy), 8)
    pygame.draw.circle(surf, (140, 120, 40), (cx, cy), 10, 2)
    for angle in range(0, 360, 60):
        px = cx + int(5 * math.cos(math.radians(angle)))
        py = cy + int(5 * math.sin(math.radians(angle)))
        pygame.draw.circle(surf, (100, 255, 100), (px, py), 1)
    pygame.draw.circle(surf, (100, 255, 100), (cx, cy), 2)
    pygame.image.save(surf, path)


# ===== 阶段2新增：角色头像（28×28像素）=====

def create_portrait_senior_student(path, s=28):
    """神秘学长头像：绿色校服，眼镜，深色头发"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    # 背景
    pygame.draw.circle(surf, (40, 60, 40), (s // 2, s // 2), 13)
    # 头
    pygame.draw.circle(surf, (240, 210, 180), (s // 2, s // 2 - 2), 8)
    # 头发
    pygame.draw.arc(surf, (40, 30, 20), (s // 2 - 8, s // 2 - 10, 16, 12), 0, math.pi, 3)
    # 眼镜
    pygame.draw.circle(surf, (200, 200, 220), (s // 2 - 3, s // 2 - 2), 3, 1)
    pygame.draw.circle(surf, (200, 200, 220), (s // 2 + 3, s // 2 - 2), 3, 1)
    pygame.draw.line(surf, (200, 200, 220), (s // 2 - 1, s // 2 - 2), (s // 2 + 1, s // 2 - 2), 1)
    # 眼睛
    surf.set_at((s // 2 - 3, s // 2 - 2), (40, 40, 40))
    surf.set_at((s // 2 + 3, s // 2 - 2), (40, 40, 40))
    # 嘴
    pygame.draw.line(surf, (180, 120, 100), (s // 2 - 2, s // 2 + 3), (s // 2 + 2, s // 2 + 3), 1)
    pygame.image.save(surf, path)


def create_portrait_librarian(path, s=28):
    """图书管理员头像：紫色制服，发髻"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (60, 40, 60), (s // 2, s // 2), 13)
    pygame.draw.circle(surf, (240, 210, 180), (s // 2, s // 2 - 1), 8)
    # 发髻
    pygame.draw.circle(surf, (120, 80, 40), (s // 2, s // 2 - 9), 4)
    pygame.draw.arc(surf, (120, 80, 40), (s // 2 - 8, s // 2 - 9, 16, 10), 0, math.pi, 3)
    # 眼睛
    surf.set_at((s // 2 - 3, s // 2 - 1), (40, 40, 40))
    surf.set_at((s // 2 + 3, s // 2 - 1), (40, 40, 40))
    # 微笑
    pygame.draw.arc(surf, (180, 120, 100), (s // 2 - 3, s // 2 + 1, 6, 4), math.pi, 2 * math.pi, 1)
    pygame.image.save(surf, path)


def create_portrait_dancing_auntie(path, s=28):
    """广场舞阿姨头像：红色衣服，卷发"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (80, 30, 30), (s // 2, s // 2), 13)
    pygame.draw.circle(surf, (240, 200, 170), (s // 2, s // 2 - 1), 8)
    # 卷发
    for angle in range(-120, 120, 30):
        fx = s // 2 + int(9 * math.cos(math.radians(angle)))
        fy = s // 2 - 1 + int(9 * math.sin(math.radians(angle)))
        pygame.draw.circle(surf, (80, 40, 20), (fx, fy), 3)
    # 眼睛
    surf.set_at((s // 2 - 3, s // 2 - 1), (40, 40, 40))
    surf.set_at((s // 2 + 3, s // 2 - 1), (40, 40, 40))
    # 大笑
    pygame.draw.arc(surf, (200, 100, 80), (s // 2 - 3, s // 2 + 1, 6, 5), math.pi, 2 * math.pi, 1)
    pygame.image.save(surf, path)


def create_portrait_pe_teacher(path, s=28):
    """体育老师头像：深蓝运动服，短发"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (30, 40, 70), (s // 2, s // 2), 13)
    pygame.draw.circle(surf, (230, 200, 170), (s // 2, s // 2 - 1), 8)
    # 短发
    pygame.draw.rect(surf, (50, 40, 30), (s // 2 - 7, s // 2 - 9, 14, 5))
    # 眼睛
    surf.set_at((s // 2 - 3, s // 2 - 1), (40, 40, 40))
    surf.set_at((s // 2 + 3, s // 2 - 1), (40, 40, 40))
    # 嘴
    pygame.draw.line(surf, (180, 120, 100), (s // 2 - 2, s // 2 + 3), (s // 2 + 2, s // 2 + 3), 1)
    pygame.image.save(surf, path)


def create_portrait_cafeteria_auntie(path, s=28):
    """食堂阿姨头像：白围裙，发网"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (70, 60, 50), (s // 2, s // 2), 13)
    pygame.draw.circle(surf, (240, 210, 180), (s // 2, s // 2 - 1), 8)
    # 发网
    pygame.draw.circle(surf, (220, 220, 200), (s // 2, s // 2 - 4), 9, 1)
    # 眼睛
    surf.set_at((s // 2 - 3, s // 2 - 1), (40, 40, 40))
    surf.set_at((s // 2 + 3, s // 2 - 1), (40, 40, 40))
    # 微笑
    pygame.draw.arc(surf, (200, 120, 100), (s // 2 - 3, s // 2 + 1, 6, 4), math.pi, 2 * math.pi, 1)
    pygame.image.save(surf, path)


def create_portrait_guardian(path, s=28):
    """秘境守护者头像：深绿斗篷兜帽，发光眼"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (20, 40, 30), (s // 2, s // 2), 13)
    # 兜帽
    pygame.draw.polygon(surf, (30, 60, 40), [
        (s // 2 - 9, s // 2 + 6), (s // 2, s // 2 - 10), (s // 2 + 9, s // 2 + 6)
    ])
    # 阴影中的脸
    pygame.draw.circle(surf, (20, 30, 25), (s // 2, s // 2), 7)
    # 发光的眼睛
    pygame.draw.circle(surf, (100, 255, 100), (s // 2 - 3, s // 2 - 1), 2)
    pygame.draw.circle(surf, (100, 255, 100), (s // 2 + 3, s // 2 - 1), 2)
    pygame.draw.circle(surf, (200, 255, 200), (s // 2 - 3, s // 2 - 1), 1)
    pygame.draw.circle(surf, (200, 255, 200), (s // 2 + 3, s // 2 - 1), 1)
    pygame.image.save(surf, path)


# ===== 阶段2新增：HUD图标 =====

def create_hud_stamina_icon(path, s=12):
    """体力图标：桂花形"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = s // 2, s // 2
    # 桂花5瓣
    for angle in range(0, 360, 72):
        px = cx + int(4 * math.cos(math.radians(angle - 90)))
        py = cy + int(4 * math.sin(math.radians(angle - 90)))
        pygame.draw.circle(surf, (76, 175, 80), (px, py), 2)
    pygame.draw.circle(surf, (255, 220, 80), (cx, cy), 2)
    pygame.image.save(surf, path)


def create_hud_badge_icon(path, s=12):
    """徽章图标：桂花形金色"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = s // 2, s // 2
    for angle in range(0, 360, 72):
        px = cx + int(4 * math.cos(math.radians(angle - 90)))
        py = cy + int(4 * math.sin(math.radians(angle - 90)))
        pygame.draw.circle(surf, (255, 200, 0), (px, py), 2)
    pygame.draw.circle(surf, (255, 240, 100), (cx, cy), 2)
    pygame.image.save(surf, path)


def create_hud_sun_icon(path, s=8):
    """太阳图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = s // 2, s // 2
    pygame.draw.circle(surf, (255, 220, 80), (cx, cy), 2)
    for angle in range(0, 360, 45):
        px = cx + int(3 * math.cos(math.radians(angle)))
        py = cy + int(3 * math.sin(math.radians(angle)))
        surf.set_at((px, py), (255, 200, 50))
    pygame.image.save(surf, path)


def create_hud_moon_icon(path, s=8):
    """月亮图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    cx, cy = s // 2, s // 2
    pygame.draw.circle(surf, (200, 200, 240), (cx, cy), 3)
    pygame.draw.circle(surf, (0, 0, 0, 0), (cx + 1, cy - 1), 2)  # 月牙效果
    pygame.image.save(surf, path)


# ===== 阶段2新增：额外道具图标 =====

def create_osmanthus_cake_icon(path, s=32):
    """桂花糕图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    # 方形糕点
    pygame.draw.rect(surf, (240, 220, 160), (8, 8, 16, 16))
    pygame.draw.rect(surf, (200, 180, 120), (8, 8, 16, 16), 1)
    # 桂花装饰
    pygame.draw.circle(surf, (255, 200, 50), (16, 16), 3)
    pygame.draw.circle(surf, (255, 230, 100), (16, 16), 1)
    pygame.image.save(surf, path)


def create_call_number_note_icon(path, s=32):
    """索书号便签图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (255, 250, 230), (6, 4, 20, 24))
    pygame.draw.rect(surf, (180, 170, 140), (6, 4, 20, 24), 1)
    # 文字行
    pygame.draw.line(surf, (100, 100, 100), (9, 10), (23, 10), 1)
    pygame.draw.line(surf, (100, 100, 100), (9, 14), (23, 14), 1)
    pygame.draw.line(surf, (200, 50, 50), (9, 18), (21, 18), 1)  # 红色索书号
    pygame.image.save(surf, path)


def create_special_book_icon(path, s=32):
    """古旧典籍图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    # 厚书
    pygame.draw.rect(surf, (120, 80, 40), (6, 4, 20, 24))
    pygame.draw.rect(surf, (160, 120, 60), (8, 6, 16, 20))
    pygame.draw.line(surf, (80, 50, 20), (16, 6), (16, 26), 2)
    # 金色装饰
    pygame.draw.circle(surf, (255, 200, 50), (12, 14), 2)
    pygame.draw.circle(surf, (255, 200, 50), (20, 14), 2)
    pygame.image.save(surf, path)


def create_lab_key_icon(path, s=32):
    """实验室钥匙图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (180, 180, 200), (10, 10), 6, 2)
    pygame.draw.line(surf, (180, 180, 200), (16, 10), (26, 10), 2)
    pygame.draw.line(surf, (180, 180, 200), (22, 10), (22, 14), 2)
    pygame.draw.line(surf, (180, 180, 200), (26, 10), (26, 14), 2)
    pygame.image.save(surf, path)


def create_equipment_key_icon(path, s=32):
    """器材室钥匙图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.circle(surf, (200, 160, 50), (10, 10), 6, 2)
    pygame.draw.line(surf, (200, 160, 50), (16, 10), (26, 10), 2)
    pygame.draw.line(surf, (200, 160, 50), (20, 10), (20, 15), 2)
    pygame.draw.line(surf, (200, 160, 50), (24, 10), (24, 15), 2)
    pygame.image.save(surf, path)


def create_scoreboard_note_icon(path, s=32):
    """记分牌便条图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (240, 230, 200), (6, 4, 20, 24))
    pygame.draw.rect(surf, (180, 170, 140), (6, 4, 20, 24), 1)
    # 数字
    pygame.draw.line(surf, (40, 40, 40), (10, 10), (14, 10), 1)
    pygame.draw.line(surf, (40, 40, 40), (14, 10), (14, 16), 1)
    pygame.draw.line(surf, (40, 40, 40), (10, 16), (14, 16), 1)
    pygame.image.save(surf, path)


def create_sculpture_rubbing_icon(path, s=32):
    """雕塑铭文拓片图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (220, 210, 190), (6, 4, 20, 24))
    pygame.draw.rect(surf, (160, 150, 130), (6, 4, 20, 24), 1)
    # 拓片纹理
    for dy in range(4):
        for dx in range(3):
            px = 10 + dx * 5
            py = 9 + dy * 4
            pygame.draw.rect(surf, (80, 70, 60), (px, py, 3, 2))
    pygame.image.save(surf, path)


def create_chili_sauce_icon(path, s=32):
    """辣椒酱图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (220, 50, 30), (8, 12, 16, 16))
    pygame.draw.rect(surf, (180, 40, 20), (8, 12, 16, 16), 1)
    pygame.draw.rect(surf, (220, 200, 160), (10, 6, 12, 8))
    pygame.draw.rect(surf, (200, 180, 140), (10, 6, 12, 8), 1)
    # 辣椒装饰
    pygame.draw.circle(surf, (255, 80, 30), (16, 20), 3)
    pygame.image.save(surf, path)


def create_water_bottle_icon(path, s=32):
    """水壶图标"""
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (100, 160, 220), (10, 10, 12, 18))
    pygame.draw.rect(surf, (80, 140, 200), (10, 10, 12, 18), 1)
    pygame.draw.rect(surf, (120, 80, 60), (12, 6, 8, 6))
    pygame.draw.rect(surf, (100, 60, 40), (12, 6, 8, 6), 1)
    pygame.draw.rect(surf, (80, 200, 255), (12, 16, 8, 10))
    # 水滴
    pygame.draw.circle(surf, (150, 220, 255), (20, 22), 2)
    pygame.image.save(surf, path)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ui_dir = os.path.join(base_dir, "assets", "ui", "sprites")
    os.makedirs(ui_dir, exist_ok=True)

    create_button_normal(os.path.join(ui_dir, "button_normal.png"))
    create_button_hover(os.path.join(ui_dir, "button_hover.png"))
    create_button_pressed(os.path.join(ui_dir, "button_pressed.png"))
    create_panel_border(os.path.join(ui_dir, "panel_border.png"))
    create_dialog_border(os.path.join(ui_dir, "dialog_border.png"))
    create_inventory_slot(os.path.join(ui_dir, "inventory_slot.png"))
    create_minimap_frame(os.path.join(ui_dir, "minimap_frame.png"))

    create_hud_bar(os.path.join(ui_dir, "hud_stamina_full.png"), fill_ratio=1.0, color=(76, 175, 80))
    create_hud_bar(os.path.join(ui_dir, "hud_stamina_half.png"), fill_ratio=0.5, color=(255, 193, 7))
    create_hud_bar(os.path.join(ui_dir, "hud_stamina_low.png"), fill_ratio=0.2, color=(244, 67, 54))

    create_badge_icon(os.path.join(ui_dir, "badge_filled.png"), filled=True)
    create_badge_icon(os.path.join(ui_dir, "badge_empty.png"), filled=False)

    create_key_icon(os.path.join(ui_dir, "icon_key.png"))
    create_book_icon(os.path.join(ui_dir, "icon_book.png"))
    create_note_icon(os.path.join(ui_dir, "icon_note.png"))

    for i in range(1, 8):
        create_badge_fragment_icon(os.path.join(ui_dir, f"badge_fragment_{i}.png"), index=i)

    create_branch_icon(os.path.join(ui_dir, "branch.png"))
    create_bookmark_icon(os.path.join(ui_dir, "bookmark.png"))
    create_magnifier_icon(os.path.join(ui_dir, "magnifier.png"))
    create_badge_old_icon(os.path.join(ui_dir, "badge_old.png"))
    create_bottle_icon(os.path.join(ui_dir, "bottle.png"))
    create_sauce_icon(os.path.join(ui_dir, "sauce.png"))
    create_card_icon(os.path.join(ui_dir, "card.png"))
    create_bookmark_special_icon(os.path.join(ui_dir, "bookmark_special.png"))
    create_badge_pattern_icon(os.path.join(ui_dir, "badge_pattern.png"))

    # 阶段2新增：角色头像（28×28像素）
    create_portrait_senior_student(os.path.join(ui_dir, "portrait_senior_student.png"))
    create_portrait_librarian(os.path.join(ui_dir, "portrait_librarian.png"))
    create_portrait_dancing_auntie(os.path.join(ui_dir, "portrait_dancing_auntie.png"))
    create_portrait_pe_teacher(os.path.join(ui_dir, "portrait_pe_teacher.png"))
    create_portrait_cafeteria_auntie(os.path.join(ui_dir, "portrait_cafeteria_auntie.png"))
    create_portrait_guardian(os.path.join(ui_dir, "portrait_guardian.png"))

    # 阶段2新增：HUD图标
    create_hud_stamina_icon(os.path.join(ui_dir, "hud_stamina_icon.png"))
    create_hud_badge_icon(os.path.join(ui_dir, "hud_badge_icon.png"))
    create_hud_sun_icon(os.path.join(ui_dir, "hud_sun_icon.png"))
    create_hud_moon_icon(os.path.join(ui_dir, "hud_moon_icon.png"))

    # 阶段2新增：额外道具图标
    create_osmanthus_cake_icon(os.path.join(ui_dir, "osmanthus_cake.png"))
    create_call_number_note_icon(os.path.join(ui_dir, "call_number_note.png"))
    create_special_book_icon(os.path.join(ui_dir, "special_book.png"))
    create_lab_key_icon(os.path.join(ui_dir, "lab_key.png"))
    create_equipment_key_icon(os.path.join(ui_dir, "equipment_key.png"))
    create_scoreboard_note_icon(os.path.join(ui_dir, "scoreboard_note.png"))
    create_sculpture_rubbing_icon(os.path.join(ui_dir, "sculpture_rubbing.png"))
    create_chili_sauce_icon(os.path.join(ui_dir, "chili_sauce.png"))
    create_water_bottle_icon(os.path.join(ui_dir, "water_bottle.png"))

    pygame.quit()
    print(f"UI sprites saved to {ui_dir}")
