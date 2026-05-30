import os
import sys
import pygame
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TILE_SIZE

COLOR_GRASS = (76, 153, 0)
COLOR_GRASS_DARK = (60, 120, 0)
COLOR_PATH = (180, 160, 120)
COLOR_PATH_DARK = (150, 130, 100)
COLOR_WALL = (120, 80, 50)
COLOR_WALL_TOP = (140, 100, 60)
COLOR_WATER = (65, 105, 225)
COLOR_WATER_LIGHT = (100, 149, 237)
COLOR_TREE_TRUNK = (101, 67, 33)
COLOR_TREE_LEAF = (34, 139, 34)
COLOR_TREE_LEAF_DARK = (0, 100, 0)
COLOR_COLLISION = (255, 0, 0, 100)

TILE_COUNT = 7
MAP_WIDTH = 20
MAP_HEIGHT = 15

GID_EMPTY = 0
GID_GRASS = 1
GID_GRASS_DARK = 2
GID_PATH = 3
GID_WALL = 4
GID_WATER = 5
GID_TREE = 6
GID_COLLISION = 7


def create_tileset(output_path):
    pygame.init()
    tileset_width = TILE_COUNT * TILE_SIZE
    tileset_height = TILE_SIZE
    surface = pygame.Surface((tileset_width, tileset_height))

    for i in range(TILE_COUNT):
        x = i * TILE_SIZE
        rect = pygame.Rect(x, 0, TILE_SIZE, TILE_SIZE)

        if i == 0:
            surface.fill(COLOR_GRASS, rect)
        elif i == 1:
            surface.fill(COLOR_GRASS_DARK, rect)
        elif i == 2:
            surface.fill(COLOR_PATH, rect)
            pygame.draw.rect(surface, COLOR_PATH_DARK, (x, 0, TILE_SIZE, 1))
            pygame.draw.rect(surface, COLOR_PATH_DARK, (x, 0, 1, TILE_SIZE))
        elif i == 3:
            surface.fill(COLOR_WALL, rect)
            pygame.draw.rect(surface, COLOR_WALL_TOP, (x, 0, TILE_SIZE, 4))
            pygame.draw.line(surface, (90, 60, 30), (x, 4), (x + TILE_SIZE, 4))
            pygame.draw.line(surface, (90, 60, 30), (x + TILE_SIZE // 2, 0), (x + TILE_SIZE // 2, 4))
        elif i == 4:
            surface.fill(COLOR_WATER, rect)
            pygame.draw.line(surface, COLOR_WATER_LIGHT, (x + 2, 4), (x + 6, 4))
            pygame.draw.line(surface, COLOR_WATER_LIGHT, (x + 9, 10), (x + 13, 10))
        elif i == 5:
            surface.fill(COLOR_GRASS, rect)
            pygame.draw.rect(surface, COLOR_TREE_TRUNK, (x + 6, 10, 4, 6))
            pygame.draw.circle(surface, COLOR_TREE_LEAF, (x + 8, 6), 6)
            pygame.draw.circle(surface, COLOR_TREE_LEAF_DARK, (x + 6, 5), 3)
        elif i == 6:
            surface.fill(COLOR_GRASS, rect)
            overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            overlay.fill(COLOR_COLLISION)
            surface.blit(overlay, (x, 0))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pygame.image.save(surface, output_path)
    pygame.quit()
    print(f"Tileset saved to {output_path}")


def design_map():
    ground = [[GID_GRASS] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    terrain = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    structures = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    decorations = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    collision = [[GID_EMPTY] * MAP_WIDTH for _ in range(MAP_HEIGHT)]

    for x in range(MAP_WIDTH):
        structures[0][x] = GID_WALL
        structures[MAP_HEIGHT - 1][x] = GID_WALL
        collision[0][x] = GID_COLLISION
        collision[MAP_HEIGHT - 1][x] = GID_COLLISION
    for y in range(MAP_HEIGHT):
        structures[y][0] = GID_WALL
        structures[y][MAP_WIDTH - 1] = GID_WALL
        collision[y][0] = GID_COLLISION
        collision[y][MAP_WIDTH - 1] = GID_COLLISION

    mid_y = MAP_HEIGHT // 2
    for x in range(1, MAP_WIDTH - 1):
        ground[mid_y][x] = GID_PATH
        ground[mid_y - 1][x] = GID_PATH

    mid_x = MAP_WIDTH // 2
    for y in range(1, MAP_HEIGHT - 1):
        ground[y][mid_x] = GID_PATH
        ground[y][mid_x - 1] = GID_PATH

    buildings = [
        (3, 2, 5, 3),
        (3, 9, 5, 3),
        (13, 2, 5, 3),
        (13, 9, 5, 3),
    ]
    for bx, by, bw, bh in buildings:
        for y in range(by, by + bh):
            for x in range(bx, bx + bw):
                if 0 <= y < MAP_HEIGHT and 0 <= x < MAP_WIDTH:
                    if y == by or y == by + bh - 1:
                        structures[y][x] = GID_WALL
                        collision[y][x] = GID_COLLISION
                    elif x == bx or x == bx + bw - 1:
                        structures[y][x] = GID_WALL
                        collision[y][x] = GID_COLLISION
                    else:
                        ground[y][x] = GID_PATH

    trees = [
        (2, 5), (8, 5), (11, 5), (17, 5),
        (2, 7), (17, 7),
        (5, 12), (14, 12),
    ]
    for tx, ty in trees:
        if 0 <= ty < MAP_HEIGHT and 0 <= tx < MAP_WIDTH:
            structures[ty][tx] = GID_TREE
            collision[ty][tx] = GID_COLLISION

    pond_x, pond_y, pond_w, pond_h = 8, 10, 3, 2
    for y in range(pond_y, pond_y + pond_h):
        for x in range(pond_x, pond_x + pond_w):
            if 0 <= y < MAP_HEIGHT and 0 <= x < MAP_WIDTH:
                terrain[y][x] = GID_WATER
                collision[y][x] = GID_COLLISION

    for y in range(1, MAP_HEIGHT - 1):
        for x in range(1, MAP_WIDTH - 1):
            if ground[y][x] == GID_GRASS and (x + y) % 4 == 0:
                ground[y][x] = GID_GRASS_DARK

    return ground, terrain, structures, decorations, collision


def layer_to_csv(layer_data):
    values = []
    for row in layer_data:
        values.extend(str(v) for v in row)
    return "\n" + ",".join(values) + "\n"


def create_tmx(ground, terrain, structures, decorations, collision, tileset_path, output_path):
    root = ET.Element("map")
    root.set("version", "1.5")
    root.set("orientation", "orthogonal")
    root.set("renderorder", "right-down")
    root.set("width", str(MAP_WIDTH))
    root.set("height", str(MAP_HEIGHT))
    root.set("tilewidth", str(TILE_SIZE))
    root.set("tileheight", str(TILE_SIZE))
    root.set("infinite", "0")
    root.set("nextobjectid", "1")

    tileset = ET.SubElement(root, "tileset")
    tileset.set("firstgid", "1")
    tileset.set("name", "test_tileset")
    tileset.set("tilewidth", str(TILE_SIZE))
    tileset.set("tileheight", str(TILE_SIZE))
    tileset.set("tilecount", str(TILE_COUNT))
    tileset.set("columns", str(TILE_COUNT))

    image = ET.SubElement(tileset, "image")
    image.set("source", tileset_path)
    image.set("width", str(TILE_COUNT * TILE_SIZE))
    image.set("height", str(TILE_SIZE))

    for local_id, solid in [(3, True), (4, True), (5, True), (6, True)]:
        tile_elem = ET.SubElement(tileset, "tile")
        tile_elem.set("id", str(local_id))
        props = ET.SubElement(tile_elem, "properties")
        prop = ET.SubElement(props, "property")
        prop.set("name", "solid")
        prop.set("type", "bool")
        prop.set("value", "true" if solid else "false")

    layer_id = 1

    ground_layer = ET.SubElement(root, "layer")
    ground_layer.set("id", str(layer_id))
    ground_layer.set("name", "ground")
    ground_layer.set("width", str(MAP_WIDTH))
    ground_layer.set("height", str(MAP_HEIGHT))
    ground_data = ET.SubElement(ground_layer, "data")
    ground_data.set("encoding", "csv")
    ground_data.text = layer_to_csv(ground)
    layer_id += 1

    terrain_layer = ET.SubElement(root, "layer")
    terrain_layer.set("id", str(layer_id))
    terrain_layer.set("name", "terrain")
    terrain_layer.set("width", str(MAP_WIDTH))
    terrain_layer.set("height", str(MAP_HEIGHT))
    terrain_data = ET.SubElement(terrain_layer, "data")
    terrain_data.set("encoding", "csv")
    terrain_data.text = layer_to_csv(terrain)
    layer_id += 1

    struct_layer = ET.SubElement(root, "layer")
    struct_layer.set("id", str(layer_id))
    struct_layer.set("name", "structures")
    struct_layer.set("width", str(MAP_WIDTH))
    struct_layer.set("height", str(MAP_HEIGHT))
    struct_data = ET.SubElement(struct_layer, "data")
    struct_data.set("encoding", "csv")
    struct_data.text = layer_to_csv(structures)
    layer_id += 1

    objects_group = ET.SubElement(root, "objectgroup")
    objects_group.set("id", str(layer_id))
    objects_group.set("name", "objects")
    layer_id += 1

    coll_layer = ET.SubElement(root, "layer")
    coll_layer.set("id", str(layer_id))
    coll_layer.set("name", "collision")
    coll_layer.set("width", str(MAP_WIDTH))
    coll_layer.set("height", str(MAP_HEIGHT))
    coll_layer.set("visible", "0")
    coll_data = ET.SubElement(coll_layer, "data")
    coll_data.set("encoding", "csv")
    coll_data.text = layer_to_csv(collision)
    layer_id += 1

    triggers_group = ET.SubElement(root, "objectgroup")
    triggers_group.set("id", str(layer_id))
    triggers_group.set("name", "triggers")
    layer_id += 1

    deco_layer = ET.SubElement(root, "layer")
    deco_layer.set("id", str(layer_id))
    deco_layer.set("name", "decorations")
    deco_layer.set("width", str(MAP_WIDTH))
    deco_layer.set("height", str(MAP_HEIGHT))
    deco_data = ET.SubElement(deco_layer, "data")
    deco_data.set("encoding", "csv")
    deco_data.text = layer_to_csv(decorations)
    layer_id += 1

    root.set("nextlayerid", str(layer_id))

    tree = ET.ElementTree(root)
    ET.indent(tree, space=" ")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)
    print(f"TMX map saved to {output_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    tileset_output = os.path.join(base_dir, "assets", "tilesets", "test_tileset.png")
    tmx_output = os.path.join(base_dir, "world", "map_data", "test_map.tmx")

    tileset_rel_path = os.path.relpath(tileset_output, os.path.dirname(tmx_output))
    tileset_rel_path = tileset_rel_path.replace("\\", "/")

    create_tileset(tileset_output)
    ground, terrain, structures, decorations, collision = design_map()
    create_tmx(ground, terrain, structures, decorations, collision, tileset_rel_path, tmx_output)
