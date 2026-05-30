import logging

import pytmx
from config import TILE_SIZE

logger = logging.getLogger(__name__)


class TileMap:
    def __init__(self, tmx_path):
        self.tmx_data = None
        self.width = 0
        self.height = 0
        self.pixel_width = 0
        self.pixel_height = 0
        self.collision_map = []
        self.spawn_points = {}
        self.transitions = []
        self.interactive_objects = []
        self.npcs = []
        self.triggers = []
        self._visible_layers = []
        self._collision_layer_index = -1
        self._load_failed = False

        try:
            self.tmx_data = pytmx.load_pygame(tmx_path)
        except Exception as e:
            logger.error("地图加载失败: %s - %s", tmx_path, e)
            self._load_failed = True
            self.width = 30
            self.height = 17
            self.collision_map = [[False] * self.width for _ in range(self.height)]
            for x in range(self.width):
                self.collision_map[0][x] = True
                self.collision_map[self.height - 1][x] = True
            for y in range(self.height):
                self.collision_map[y][0] = True
                self.collision_map[y][self.width - 1] = True
            return

        self.width = self.tmx_data.width
        self.height = self.tmx_data.height
        self.pixel_width = self.width * TILE_SIZE
        self.pixel_height = self.height * TILE_SIZE
        self.collision_map = [[False] * self.width for _ in range(self.height)]
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
                    self._parse_objects(layer)
                elif layer.name == "npcs":
                    self._parse_npcs(layer)

    def _parse_triggers(self, layer):
        from entities.trigger import Trigger

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
            trigger_obj = Trigger(
                x=obj.x, y=obj.y,
                width=obj.width, height=obj.height,
                trigger_type=obj.type or "generic",
                properties=dict(obj.properties) if obj.properties else {},
            )
            self.triggers.append(trigger_obj)

    def _parse_objects(self, layer):
        from entities.interactive_object import InteractiveObject

        for obj in layer:
            props = dict(obj.properties) if obj.properties else {}
            interactive_type = props.get("interactive_type", "examine")
            obj_instance = InteractiveObject(
                x=obj.x, y=obj.y,
                width=obj.width, height=obj.height,
                interactive_type=interactive_type,
                properties=props,
            )
            self.interactive_objects.append(obj_instance)

    def _parse_npcs(self, layer):
        from entities.npc import NPC

        for obj in layer:
            props = dict(obj.properties) if obj.properties else {}
            npc_id = props.get("npc_id", "unknown_npc")
            dialogue_id = props.get("dialogue_id", npc_id)
            center_x = obj.x + obj.width / 2
            bottom_y = obj.y + obj.height
            npc = NPC(
                x=center_x, y=bottom_y,
                npc_id=npc_id,
                dialogue_id=dialogue_id,
                properties=props,
            )
            if "direction" in props:
                npc.direction = props["direction"]
            self.npcs.append(npc)

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
        if self._load_failed:
            surface.fill((40, 40, 60))
            return

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
