"""验证所有图书馆修改"""
import os
import pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()
pygame.display.set_mode((1, 1))

from world.tilemap import TileMap
from game.game_manager import GameManager

# 验证2楼
t2 = TileMap('world/map_data/library_f2.tmx')
print(f'Library F2: {len(t2.interactive_objects)} objects, {len(t2.triggers)} triggers')
bookshelf_count = 0
for o in t2.interactive_objects:
    obj_type = o.properties.get("type", "unknown")
    if obj_type == "bookshelf":
        bookshelf_count += 1
        call_number = o.properties.get("call_number", "N/A")
        sprite_key = o.properties.get("sprite_key", "N/A")
        print(f'  书架: call_number={call_number}, sprite_key={sprite_key}, pos=({o.x},{o.y}), size=({o.width}x{o.height})')
    else:
        print(f'  {obj_type}: pos=({o.x},{o.y}), size=({o.width}x{o.height})')
print(f'  书架总数: {bookshelf_count}')

# 验证1楼
t1 = TileMap('world/map_data/library_f1.tmx')
print(f'\nLibrary F1: {len(t1.interactive_objects)} objects')
for o in t1.interactive_objects:
    obj_type = o.properties.get("type", "unknown")
    sprite_key = o.properties.get("sprite_key", "N/A")
    print(f'  {obj_type}: sprite_key={sprite_key}, pos=({o.x},{o.y}), size=({o.width}x{o.height})')

# 验证精灵
sprite_path = os.path.join('assets', 'sprites', 'bookshelf.png')
sprite = pygame.image.load(sprite_path)
print(f'\nBookshelf sprite: {sprite.get_width()}x{sprite.get_height()}')

# 验证tileset
tileset_path = os.path.join('assets', 'tilesets', 'indoor_tileset.png')
tileset = pygame.image.load(tileset_path)
print(f'Indoor tileset: {tileset.get_width()}x{tileset.get_height()}')

print('\nAll OK!')
pygame.quit()
