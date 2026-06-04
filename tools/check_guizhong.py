"""检测桂中路谜题位置"""

TILE_SIZE = 16
road_y_start = 36
road_y_end = 41
road_x_start = 5
road_x_end = 105

print("=" * 60)
print("桂中路谜题位置检测")
print("=" * 60)

# 北侧桂花树
print("\n【北侧桂花树】y =", road_y_start - 1, "(深棕色行)")
north_trees = []
for x in range(road_x_start + 3, road_x_end, 5):
    tx = x * TILE_SIZE + TILE_SIZE / 2
    ty = (road_y_start - 1) * TILE_SIZE
    north_trees.append((tx, ty))
    print(f"  树 #{len(north_trees)}: tile=({x}, {road_y_start - 1}), pixel=({tx}, {ty})")

# 南侧桂花树
print("\n【南侧桂花树】y =", road_y_end + 1, "(深棕色行)")
south_trees = []
for x in range(road_x_start + 5, road_x_end, 5):
    tx = x * TILE_SIZE + TILE_SIZE / 2
    ty = (road_y_end + 1) * TILE_SIZE
    south_trees.append((tx, ty))
    print(f"  树 #{len(south_trees)}: tile=({x}, {road_y_end + 1}), pixel=({tx}, {ty})")

all_trees = north_trees + south_trees
print(f"\n总计桂花树: {len(all_trees)} 棵")
print(f"北侧: {len(north_trees)} 棵, 南侧: {len(south_trees)} 棵")

# 限制为7棵
tree_count_7 = all_trees[:7]
print(f"\n谜题使用的 7 棵树位置:")
for i, (tx, ty) in enumerate(tree_count_7):
    print(f"  [{i}] pixel=({tx}, {ty})")

# 北侧路灯
print("\n【北侧路灯】y =", road_y_start - 1)
for x in range(road_x_start + 5, road_x_end, 10):
    print(f"  路灯: tile=({x}, {road_y_start - 1}), pixel=({x * TILE_SIZE + 8}, {(road_y_start - 1) * TILE_SIZE + 8})")

# 南侧路灯
print("\n【南侧路灯】y =", road_y_end + 1)
for x in range(road_x_start + 8, road_x_end, 10):
    print(f"  路灯: tile=({x}, {road_y_end + 1}), pixel=({x * TILE_SIZE + 8}, {(road_y_end + 1) * TILE_SIZE + 8})")

# 检查是否有重叠
print("\n【重叠检测】")
all_north_x = set(range(road_x_start + 3, road_x_end, 5))
all_north_lamp_x = set(range(road_x_start + 5, road_x_end, 10))
all_south_x = set(range(road_x_start + 5, road_x_end, 5))
all_south_lamp_x = set(range(road_x_start + 8, road_x_end, 10))

north_overlap = all_north_x & all_north_lamp_x
south_overlap = all_south_x & all_south_lamp_x

if north_overlap:
    print(f"  警告: 北侧树与路灯重叠 x={north_overlap}")
else:
    print("  北侧: 树与路灯无重叠")

if south_overlap:
    print(f"  警告: 南侧树与路灯重叠 x={south_overlap}")
else:
    print("  南侧: 树与路灯无重叠")

print("\n" + "=" * 60)
