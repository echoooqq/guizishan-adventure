import sys
import os
sys.path.insert(0, r'd:\桂子山秘境探险')

import pygame
pygame.init()

from map_scene import Scene, SCENE_WIDTH, SCENE_HEIGHT

screen = pygame.Surface((SCENE_WIDTH, SCENE_HEIGHT))

font_dir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
font_path = os.path.join(font_dir, "simhei.ttf")
if os.path.exists(font_path):
    font = pygame.font.Font(font_path, 14)
else:
    font = pygame.font.Font(None, 14)

scene_ids = ["guizhong_road", "nanhu_building", "library", "boya_square",
             "youming_gym", "dining_hall", "fountain_square", "night_secret"]

all_ok = True
for sid in scene_ids:
    try:
        scene = Scene(sid)
        scene.draw(screen, font)
        print(f"  {sid}: OK (objects={len(scene.objects)})")
    except Exception as e:
        print(f"  {sid}: FAILED - {type(e).__name__}: {e}")
        all_ok = False

if all_ok:
    print("\nAll 8 scenes render successfully!")
else:
    print("\nSome scenes failed!")

pygame.quit()
