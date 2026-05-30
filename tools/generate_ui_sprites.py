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

    pygame.quit()
    print(f"UI sprites saved to {ui_dir}")
