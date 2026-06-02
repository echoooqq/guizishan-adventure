"""小地图 — 右下角显示，简化色块缩略图+迷雾+玩家亮点+地标

阶段1：简化色块缩略图，不同颜色代表不同地形
阶段2：羊皮纸质感底图+像素风建筑图标+迷雾遮罩+玩家闪烁亮点
"""

import os
import math
import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    TILE_SIZE,
    FONT_PATH,
)


# 小地图尺寸
MINIMAP_WIDTH = 60
MINIMAP_HEIGHT = 45
MINIMAP_MARGIN = 4

# 地形颜色映射
TERRAIN_COLORS = {
    "grass": (60, 140, 60),       # 草地：绿色
    "road": (160, 140, 120),      # 道路：灰棕色
    "water": (60, 100, 180),      # 水面：蓝色
    "building": (120, 100, 90),   # 建筑：深棕色
    "floor": (180, 160, 130),     # 室内地板：浅棕色
    "wall": (80, 70, 65),         # 墙壁：深色
    "default": (80, 80, 80),      # 默认：灰色
}

# 迷雾颜色
FOG_COLOR = (0, 0, 0, 180)

# 玩家亮点颜色
PLAYER_DOT_COLOR = (255, 255, 255)
PLAYER_DOT_RADIUS = 2

# 地标颜色
LANDMARK_COLORS = {
    "library": (100, 140, 220),
    "gym": (200, 140, 80),
    "dining_hall": (180, 100, 100),
    "fountain": (80, 180, 220),
    "boya_square": (180, 180, 80),
    "nanhu_building": (140, 100, 180),
    "gate": (220, 200, 100),
    "bus_stop": (160, 160, 160),
}

# 地标位置（地图ID -> 地标列表，每项为 (name, tile_x, tile_y)）
LANDMARKS = {
    "main_campus": [
        ("gate", 60, 72),
        ("library", 20, 20),
        ("boya_square", 85, 25),
        ("gym", 20, 55),
        ("dining_hall", 90, 55),
        ("fountain", 55, 50),
        ("bus_stop", 55, 65),
    ],
    "nanhu_campus": [
        ("nanhu_building", 20, 15),
    ],
}


class Minimap:
    """小地图"""

    def __init__(self):
        self._cache = {}
        self._player_blink_timer = 0.0
        self._player_blink_on = True
        self._explored_chunks = {}  # map_id -> set of (chunk_x, chunk_y)
        self._minimap_frame = None
        self._load_frame()

    def _load_frame(self):
        """加载小地图边框素材"""
        frame_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "ui", "sprites", "minimap_frame.png",
        )
        if os.path.exists(frame_path):
            try:
                self._minimap_frame = pygame.image.load(frame_path).convert_alpha()
            except pygame.error:
                pass

    def update(self, dt):
        """更新小地图动画（玩家亮点闪烁）"""
        self._player_blink_timer += dt
        if self._player_blink_timer >= 0.5:
            self._player_blink_timer -= 0.5
            self._player_blink_on = not self._player_blink_on

    def mark_explored(self, map_id, player_tile_x, player_tile_y, radius=8):
        """标记玩家周围区域为已探索"""
        if map_id not in self._explored_chunks:
            self._explored_chunks[map_id] = set()
        chunks = self._explored_chunks[map_id]
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    cx = (player_tile_x + dx) // 4
                    cy = (player_tile_y + dy) // 4
                    chunks.add((cx, cy))

    def is_explored(self, map_id, tile_x, tile_y):
        """检查指定位置是否已探索"""
        chunks = self._explored_chunks.get(map_id, set())
        cx = tile_x // 4
        cy = tile_y // 4
        return (cx, cy) in chunks

    def get_explored_data(self):
        """获取已探索区域数据（用于存档）"""
        result = {}
        for map_id, chunks in self._explored_chunks.items():
            result[map_id] = list(chunks)
        return result

    def load_explored_data(self, data):
        """从存档恢复已探索区域"""
        self._explored_chunks = {}
        for map_id, chunk_list in data.items():
            self._explored_chunks[map_id] = set(
                tuple(c) for c in chunk_list
            )

    def draw(self, surface, tile_map, map_id, player, camera):
        """绘制小地图到游戏画面右下角"""
        if tile_map is None:
            return

        # 生成或获取缓存的缩略图
        if map_id not in self._cache:
            self._cache[map_id] = self._render_minimap(tile_map, map_id)
        minimap_surf = self._cache[map_id]

        # 绘制迷雾
        self._draw_fog(minimap_surf, map_id, tile_map)

        # 绘制地标
        self._draw_landmarks(minimap_surf, map_id, tile_map)

        # 绘制玩家位置
        self._draw_player_dot(minimap_surf, player, tile_map)

        # 计算小地图在屏幕上的位置（右下角）
        dest_x = INTERNAL_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN
        dest_y = INTERNAL_HEIGHT - MINIMAP_HEIGHT - MINIMAP_MARGIN

        # 绘制边框背景
        border_rect = pygame.Rect(
            dest_x - 2, dest_y - 2,
            MINIMAP_WIDTH + 4, MINIMAP_HEIGHT + 4,
        )
        border_surf = pygame.Surface(
            (border_rect.width, border_rect.height), pygame.SRCALPHA
        )
        border_surf.fill((0, 0, 0, 140))
        pygame.draw.rect(
            border_surf, (100, 100, 120),
            (0, 0, border_rect.width, border_rect.height), 1,
        )
        surface.blit(border_surf, border_rect.topleft)

        # 绘制小地图
        surface.blit(minimap_surf, (dest_x, dest_y))

    def _render_minimap(self, tile_map, map_id):
        """渲染地图缩略图"""
        surf = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))
        surf.fill((30, 30, 40))

        map_w = tile_map.width
        map_h = tile_map.height
        if map_w <= 0 or map_h <= 0:
            return surf

        # 缩放比例
        scale_x = MINIMAP_WIDTH / map_w
        scale_y = MINIMAP_HEIGHT / map_h

        # 从碰撞层推断地形
        for ty in range(map_h):
            for tx in range(map_w):
                px = int(tx * scale_x)
                py = int(ty * scale_y)
                if px >= MINIMAP_WIDTH or py >= MINIMAP_HEIGHT:
                    continue

                # 判断地形类型
                color = self._get_tile_color(tile_map, tx, ty)
                surf.set_at((px, py), color)

        return surf

    def _get_tile_color(self, tile_map, tx, ty):
        """获取指定Tile在小地图上的颜色"""
        # 检查碰撞层判断是否为墙壁/建筑
        if tile_map.collision_map and ty < len(tile_map.collision_map) and tx < len(tile_map.collision_map[ty]):
            if tile_map.collision_map[ty][tx]:
                return TERRAIN_COLORS["building"]

        # 默认为草地
        return TERRAIN_COLORS["grass"]

    def _draw_fog(self, minimap_surf, map_id, tile_map):
        """在缩略图上绘制迷雾"""
        if map_id not in self._explored_chunks:
            # 全部迷雾
            fog = pygame.Surface(
                (MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA
            )
            fog.fill(FOG_COLOR)
            minimap_surf.blit(fog, (0, 0))
            return

        chunks = self._explored_chunks[map_id]
        if not chunks:
            fog = pygame.Surface(
                (MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA
            )
            fog.fill(FOG_COLOR)
            minimap_surf.blit(fog, (0, 0))
            return

        # 逐像素判断是否已探索
        map_w = tile_map.width
        map_h = tile_map.height
        if map_w <= 0 or map_h <= 0:
            return

        scale_x = MINIMAP_WIDTH / map_w
        scale_y = MINIMAP_HEIGHT / map_h

        fog = pygame.Surface(
            (MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA
        )

        # 先全部填充迷雾
        fog.fill(FOG_COLOR)

        # 清除已探索区域的迷雾
        for (cx, cy) in chunks:
            # 每个chunk覆盖4x4的tile区域
            for dy in range(4):
                for dx in range(4):
                    tile_x = cx * 4 + dx
                    tile_y = cy * 4 + dy
                    px = int(tile_x * scale_x)
                    py = int(tile_y * scale_y)
                    if 0 <= px < MINIMAP_WIDTH and 0 <= py < MINIMAP_HEIGHT:
                        fog.set_at((px, py), (0, 0, 0, 0))

        minimap_surf.blit(fog, (0, 0))

    def _draw_landmarks(self, minimap_surf, map_id, tile_map):
        """绘制地标图标"""
        landmarks = LANDMARKS.get(map_id, [])
        if not landmarks:
            return

        map_w = tile_map.width
        map_h = tile_map.height
        if map_w <= 0 or map_h <= 0:
            return

        scale_x = MINIMAP_WIDTH / map_w
        scale_y = MINIMAP_HEIGHT / map_h

        for landmark_type, tile_x, tile_y in landmarks:
            # 仅绘制已探索区域的地标
            if not self.is_explored(map_id, tile_x, tile_y):
                continue

            px = int(tile_x * scale_x)
            py = int(tile_y * scale_y)
            color = LANDMARK_COLORS.get(landmark_type, (200, 200, 200))

            # 绘制2x2像素的地标点
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < MINIMAP_WIDTH and 0 <= ny < MINIMAP_HEIGHT:
                        minimap_surf.set_at((nx, ny), color)

    def _draw_player_dot(self, minimap_surf, player, tile_map):
        """绘制玩家位置亮点"""
        if not self._player_blink_on:
            return

        map_w = tile_map.width
        map_h = tile_map.height
        if map_w <= 0 or map_h <= 0:
            return

        player_tile_x = player.x / TILE_SIZE
        player_tile_y = player.y / TILE_SIZE

        scale_x = MINIMAP_WIDTH / map_w
        scale_y = MINIMAP_HEIGHT / map_h

        px = int(player_tile_x * scale_x)
        py = int(player_tile_y * scale_y)

        # 绘制白色亮点
        for dx in range(-PLAYER_DOT_RADIUS, PLAYER_DOT_RADIUS + 1):
            for dy in range(-PLAYER_DOT_RADIUS, PLAYER_DOT_RADIUS + 1):
                if dx * dx + dy * dy <= PLAYER_DOT_RADIUS * PLAYER_DOT_RADIUS:
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < MINIMAP_WIDTH and 0 <= ny < MINIMAP_HEIGHT:
                        minimap_surf.set_at((nx, ny), PLAYER_DOT_COLOR)

    def invalidate_cache(self, map_id=None):
        """使缓存失效（地图变化时调用）"""
        if map_id:
            self._cache.pop(map_id, None)
        else:
            self._cache.clear()
