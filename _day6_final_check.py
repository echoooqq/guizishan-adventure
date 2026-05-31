import pygame
pygame.init()
screen = pygame.display.set_mode((100, 100))
import pytmx
from world.tilemap import TileMap
from world.transition import TransitionManager, TransitionType, TransitionState
from entities.trigger import Trigger
import os

errors = []
warnings = []

# 1. Tileset GID 映射检查（无黑色瓦片）
print("--- 1. Tileset GID 映射 ---")
for map_name in ['main_campus', 'library_f1', 'library_f2', 'gym', 'dining_hall_f1', 'dining_hall_f2']:
    tmx = pytmx.load_pygame(f'world/map_data/{map_name}.tmx')
    black_count = 0
    for layer in tmx.layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue
        for row in range(tmx.height):
            for col in range(tmx.width):
                gid = layer.data[row][col]
                if gid == 0:
                    continue
                img = tmx.get_tile_image_by_gid(gid)
                if img is None:
                    black_count += 1
                else:
                    c = img.get_at((8, 8))
                    if c.r == 0 and c.g == 0 and c.b == 0 and c.a == 255:
                        black_count += 1
    if black_count > 0:
        errors.append(f"{map_name}: {black_count} black tiles")
    else:
        print(f"  {map_name}: OK")

# 2. Spawn Point 检查
print("--- 2. Spawn Points ---")
all_maps = {}
for map_name in ['main_campus', 'library_f1', 'library_f2', 'gym', 'dining_hall_f1', 'dining_hall_f2']:
    tm = TileMap(f'world/map_data/{map_name}.tmx')
    all_maps[map_name] = tm
    print(f"  {map_name}: {list(tm.spawn_points.keys())}")

# 3. 过渡链路完整性
print("--- 3. 过渡链路 ---")
for map_name, tm in all_maps.items():
    for obj in tm.interactive_objects:
        if obj.interactive_type == 'enter':
            target = obj.properties.get('target_map')
            spawn = obj.properties.get('spawn_point')
            transition = obj.properties.get('transition_type')
            if not target:
                errors.append(f"{map_name}: enter object missing target_map")
                continue
            if not spawn:
                warnings.append(f"{map_name}: enter object missing spawn_point")
            if not transition:
                warnings.append(f"{map_name}: enter object missing transition_type")
            if target in all_maps and spawn and spawn not in all_maps[target].spawn_points:
                errors.append(f"{map_name} -> {target}: spawn '{spawn}' NOT FOUND")
            else:
                print(f"  {map_name} -> {target} ({spawn}): OK")

    for trigger in tm.triggers:
        if trigger.auto_trigger:
            target = trigger.target_map or trigger.properties.get('target_map')
            spawn = trigger.spawn_point or trigger.properties.get('spawn_point')
            if target and spawn and target in all_maps:
                if spawn not in all_maps[target].spawn_points:
                    errors.append(f"{map_name} -> {target}: spawn '{spawn}' NOT FOUND (auto)")
                else:
                    print(f"  {map_name} -> {target} ({spawn}) auto: OK")

# 4. 碰撞检查
print("--- 4. 碰撞检查 ---")
for map_name, tm in all_maps.items():
    solid_count = sum(1 for row in tm.collision_map for c in row if c)
    total = tm.width * tm.height
    pct = solid_count * 100 / total
    print(f"  {map_name}: {solid_count}/{total} ({pct:.1f}%)")

    if map_name != 'main_campus':
        border_ok = True
        for x in range(tm.width):
            if not tm.collision_map[0][x] or not tm.collision_map[tm.height-1][x]:
                border_ok = False
                break
        for y in range(tm.height):
            if not tm.collision_map[y][0] or not tm.collision_map[y][tm.width-1]:
                border_ok = False
                break
        if not border_ok:
            errors.append(f"{map_name}: border not fully solid!")
        else:
            print(f"  {map_name} border: OK")

# 5. 出口触发可达性
print("--- 5. 出口触发可达性 ---")
for map_name, tm in all_maps.items():
    for trigger in tm.triggers:
        if trigger.auto_trigger:
            tx = int(trigger.x // 16)
            ty = int(trigger.y // 16)
            tw = max(1, int(trigger.width // 16))
            th = max(1, int(trigger.height // 16))
            has_walkable = False
            for dy in range(th):
                for dx in range(tw):
                    nx, ny = tx + dx, ty + dy
                    if 0 <= ny < tm.height and 0 <= nx < tm.width:
                        if not tm.collision_map[ny][nx]:
                            has_walkable = True
            if not has_walkable:
                errors.append(f"{map_name}: auto trigger at ({tx},{ty}) entirely solid!")
            else:
                print(f"  {map_name} auto trigger ({tx},{ty}): OK")

# 6. TransitionManager 逻辑检查
print("--- 6. TransitionManager ---")
tm_mgr = TransitionManager()
assert tm_mgr.state == TransitionState.IDLE
assert not tm_mgr.is_active

tm_mgr.start_transition(TransitionType.INDOOR_ENTER, "library_f1", "library_entrance")
assert tm_mgr.state == TransitionState.FADE_OUT
assert tm_mgr.is_active

tm_mgr.update(0.5)
assert tm_mgr.state == TransitionState.LOADING

tm_mgr.update(0.01)
assert tm_mgr.state == TransitionState.FADE_IN

tm_mgr.update(0.5)
assert tm_mgr.state == TransitionState.IDLE
assert not tm_mgr.is_active
print("  TransitionManager state machine: OK")

# 7. Trigger.interact() 检查
print("--- 7. Trigger.interact() ---")
t = Trigger(10, 10, 32, 32, "stairs", {
    "target_map": "library_f2",
    "spawn_point": "library_f2_stairs",
    "transition_type": "floor_change",
})
result = t.interact()
assert result["type"] == "enter"
assert result["target_map"] == "library_f2"
assert result["spawn_point"] == "library_f2_stairs"
assert not t.auto_trigger
print("  Trigger.interact(): OK")

# 8. 双向链路检查（A→B 和 B→A 都存在）
print("--- 8. 双向链路 ---")
for map_name, tm in all_maps.items():
    for obj in tm.interactive_objects:
        if obj.interactive_type == 'enter':
            target = obj.properties.get('target_map')
            if target and target in all_maps:
                target_tm = all_maps[target]
                has_return = False
                for t_obj in target_tm.interactive_objects:
                    if t_obj.interactive_type == 'enter' and t_obj.properties.get('target_map') == map_name:
                        has_return = True
                        break
                for t_trigger in target_tm.triggers:
                    if t_trigger.auto_trigger:
                        t_target = t_trigger.target_map or t_trigger.properties.get('target_map')
                        if t_target == map_name:
                            has_return = True
                            break
                if not has_return:
                    warnings.append(f"{map_name} -> {target}: no return path!")
                else:
                    print(f"  {map_name} <-> {target}: OK")

# 9. 楼层切换链路检查
print("--- 9. 楼层切换链路 ---")
floor_pairs = [("library_f1", "library_f2"), ("dining_hall_f1", "dining_hall_f2")]
for f1, f2 in floor_pairs:
    f1_tm = all_maps[f1]
    f2_tm = all_maps[f2]
    f1_has_stairs_up = any(o.interactive_type == 'enter' and o.properties.get('target_map') == f2 for o in f1_tm.interactive_objects)
    f2_has_stairs_down = any(o.interactive_type == 'enter' and o.properties.get('target_map') == f1 for o in f2_tm.interactive_objects)
    f1_has_spawn = any(s.startswith(f1.replace('_', '_f') + '_stairs') or 'stairs' in s for s in f1_tm.spawn_points)
    f2_has_spawn = any('stairs' in s for s in f2_tm.spawn_points)
    if not f1_has_stairs_up:
        errors.append(f"{f1}: no stairs up to {f2}")
    if not f2_has_stairs_down:
        errors.append(f"{f2}: no stairs down to {f1}")
    if not f2_has_spawn:
        errors.append(f"{f2}: no stairs spawn point")
    if f1_has_stairs_up and f2_has_stairs_down:
        print(f"  {f1} <-> {f2}: OK")

print()
print("=" * 60)
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  ❌ {e}")
if warnings:
    print(f"WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"  ⚠️ {w}")
if not errors and not warnings:
    print("ALL CHECKS PASSED ✅")

pygame.quit()
