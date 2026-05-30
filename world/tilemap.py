import pytmx
import pygame
from config import TILE_SIZE


class TileMap:
    def __init__(self, tmx_path):
        self.tmx_data = pytmx.load_pygame(tmx_path)
        self.width = self.tmx_data.width
        self.height = self.tmx_data.height
        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE
        self.collision_map = [[False] * self.width for _ in range(self.height)]
        self.spawn_points = {}
        self.transitions = []
        self._visible_layers = []
        self._collision_layer_index = -1
        self._parse_layers()
        self._build_collision()

    def _parse_layers(self):
        for i, layer in enumerate(self.tmx_data.layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                if layer.name == "collision":
                    self._collision_layer_index = i
                else:
                    self._visible_layers.append(i)
            elif isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "triggers":
                    self._parse_triggers(layer)
                elif layer.name == "objects":
                    pass

    def _parse_triggers(self, layer):
        for obj in layer:
            trigger = {
                "x": obj.x,
                "y": obj.y,
                "width": obj.width,
                "height": obj.height,
                "type": obj.type or "",
                "properties": dict(obj.properties) if obj.properties else {},
            }
            if "target_map" in trigger["properties"]:
                trigger["target_map"] = trigger["properties"]["target_map"]
            if "spawn_point" in trigger["properties"]:
                trigger["spawn_point"] = trigger["properties"]["spawn_point"]
            self.transitions.append(trigger)
            if "spawn_id" in trigger["properties"]:
                sx = obj.x + obj.width / 2
                sy = obj.y + obj.height / 2
                self.spawn_points[trigger["properties"]["spawn_id"]] = (sx, sy)

    def _build_collision(self):
        solid_gids = set()
        for gid, props in self.tmx_data.tile_properties.items():
            if props and props.get("solid", False):
                solid_gids.add(gid)

        if self._collision_layer_index >= 0:
            layer = self.tmx_data.layers[self._collision_layer_index]
            for y in range(self.height):
                for x in range(self.width):
                    gid = layer.data[y][x]
                    if gid != 0:
                        self.collision_map[y][x] = True
        else:
            for layer_index in self._visible_layers:
                layer = self.tmx_data.layers[layer_index]
                if not isinstance(layer, pytmx.TiledTileLayer):
                    continue
                for y in range(self.height):
                    for x in range(self.width):
                        gid = layer.data[y][x]
                        if gid in solid_gids:
                            self.collision_map[y][x] = True

    def draw(self, surface, camera):
        start_row, end_row, start_col, end_col = camera.visible_tile_range
        for layer_index in self._visible_layers:
            layer = self.tmx_data.layers[layer_index]
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            for row in range(start_row, end_row):
                for col in range(start_col, end_col):
                    gid = layer.data[row][col]
                    if gid == 0:
                        continue
                    tile_image = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        sx, sy = camera.apply(
                            col * TILE_SIZE, row * TILE_SIZE
                        )
                        surface.blit(tile_image, (int(sx), int(sy)))

    def get_spawn_position(self, spawn_id="default"):
        if spawn_id in self.spawn_points:
            return self.spawn_points[spawn_id]
        return (
            self.width // 2 * TILE_SIZE + TILE_SIZE // 2,
            self.height // 2 * TILE_SIZE + TILE_SIZE // 2,
        )

    def is_solid(self, tile_x, tile_y):
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return True
        return self.collision_map[tile_y][tile_x]
