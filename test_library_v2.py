"""验证图书馆地图和游戏逻辑"""
import os
import pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1, 1))

from world.tilemap import TileMap

# 验证2楼
t2 = TileMap('world/map_data/library_f2.tmx')
print(f'Library F2: {len(t2.interactive_objects)} objects, {len(t2.triggers)} triggers')
for o in t2.interactive_objects:
    obj_type = o.properties.get("type", "unknown")
    call_number = o.properties.get("call_number", "N/A")
    section = o.properties.get("section", "N/A")
    print(f'  obj: type={obj_type}, call_number={call_number}, section={section}, pos=({o.x},{o.y}), size=({o.width}x{o.height})')

# 验证1楼
t1 = TileMap('world/map_data/library_f1.tmx')
print(f'\nLibrary F1: {len(t1.interactive_objects)} objects')
for o in t1.interactive_objects:
    obj_type = o.properties.get("type", "unknown")
    terminal_type = o.properties.get("terminal_type", "N/A")
    print(f'  obj: type={obj_type}, terminal_type={terminal_type}')

# 验证游戏管理器导入
from game.game_manager import GameManager
print(f'\nGameManager import OK')
print(f'LIBRARY_F2_CALL_NUMBERS: {GameManager.LIBRARY_F2_CALL_NUMBERS}')
print(f'LIBRARY_CORRECT_CALL_NUMBER: {GameManager.LIBRARY_CORRECT_CALL_NUMBER}')

pygame.quit()
