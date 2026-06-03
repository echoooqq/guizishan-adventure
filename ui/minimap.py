"""小地图 — 角色中心雷达式 + 全屏迷雾地图

角落小地图：始终以玩家位置为中心，显示周围区域（雷达式）
全屏地图（M键）：显示整个地图，已探索区域清晰，未探索区域半透明迷雾
地图渲染：从Tiled地图实际图层采样，缩放为缩略图，显示真实环境外观
迷雾：深蓝灰色半透明，已探索边缘距离渐变羽化
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


# 角落小地图尺寸
MINIMAP_WIDTH = 60
MINIMAP_HEIGHT = 45
MINIMAP_MARGIN = 4

# 雷达视野半径（小地图上显示的tile范围）
RADAR_RADIUS_TILES = 30

# 迷雾颜色 — 深蓝灰色半透明
FOG_RGB = (10, 15, 35)
FOG_ALPHA_RADAR = 140       # 角落小地图迷雾最大alpha
FOG_ALPHA_FULLSCREEN = 160  # 全屏地图迷雾最大alpha

# 羽化宽度（chunk单位，1 chunk = 4 tile）
FEATHER_RADIUS_CHUNKS = 3   # 边缘3个chunk宽度渐变

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

# 地标中文名称（全屏地图用）
LANDMARK_NAMES = {
    "library": "图书馆",
    "gym": "体育馆",
    "dining_hall": "食堂",
    "fountain": "喷泉",
    "boya_square": "博雅广场",
    "nanhu_building": "综合楼",
    "gate": "校门",
    "bus_stop": "校车站",
}


class Minimap:
    """小地图 — 角色中心雷达式"""

    def __init__(self):
        self._fullmap_render_cache = {}  # map_id -> 原始分辨率全图Surface
        self._fullmap_cache = {}  # map_id -> 缩放后的缩略图Surface（含迷雾）
        self._explored_chunks = {}  # map_id -> set of (chunk_x, chunk_y)
        self._fog_dirty = set()  # 需要重新渲染迷雾的map_id集合
        self._fullscreen_fog_cache = {}  # (map_id, render_w, render_h) -> fog Surface
        # 雷达迷雾缓存（问题2修复：避免每帧重算）
        self._radar_fog_cache_key = None  # (map_id, player_chunk_x, player_chunk_y)
        self._radar_fog_cache_surf = None
        self._minimap_frame = None
        self._font = None
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

    def _get_font(self, size=8):
        """获取字体（延迟加载），默认小字号用于雷达，可指定更大字号用于全屏"""
        if size == 8:
            if self._font is None:
                self._font = pygame.font.Font(FONT_PATH, 8)
            return self._font
        else:
            if not hasattr(self, '_font_cache'):
                self._font_cache = {}
            if size not in self._font_cache:
                self._font_cache[size] = pygame.font.Font(FONT_PATH, size)
            return self._font_cache[size]

    def update(self, dt):
        """更新小地图状态"""
        pass

    def mark_explored(self, map_id, player_tile_x, player_tile_y, radius=8):
        """标记玩家周围区域为已探索"""
        if map_id not in self._explored_chunks:
            self._explored_chunks[map_id] = set()
        chunks = self._explored_chunks[map_id]
        old_count = len(chunks)
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    cx = (player_tile_x + dx) // 4
                    cy = (player_tile_y + dy) // 4
                    chunks.add((cx, cy))
        # 如果有新chunk被探索，标记迷雾需要重绘
        if len(chunks) > old_count:
            self._fog_dirty.add(map_id)
            # 清除迷雾缓存
            keys_to_remove = [k for k in self._fullscreen_fog_cache if k[0] == map_id]
            for k in keys_to_remove:
                del self._fullscreen_fog_cache[k]
            self._fullmap_cache.pop(map_id, None)
            # 清除雷达迷雾缓存
            self._radar_fog_cache_key = None

    def is_explored(self, map_id, tile_x, tile_y):
        """检查指定位置是否已探索"""
        chunks = self._explored_chunks.get(map_id, set())
        cx = tile_x // 4
        cy = tile_y // 4
        return (cx, cy) in chunks

    def _get_chunk_distance(self, map_id, chunk_x, chunk_y):
        """计算指定chunk到最近已探索chunk的距离（chunk单位）"""
        chunks = self._explored_chunks.get(map_id, set())
        if not chunks:
            return FEATHER_RADIUS_CHUNKS + 1

        if (chunk_x, chunk_y) in chunks:
            return 0

        min_dist = FEATHER_RADIUS_CHUNKS + 1
        search_r = FEATHER_RADIUS_CHUNKS
        for dx in range(-search_r, search_r + 1):
            for dy in range(-search_r, search_r + 1):
                if (chunk_x + dx, chunk_y + dy) in chunks:
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < min_dist:
                        min_dist = dist
        return min_dist

    def _get_fog_alpha(self, chunk_dist, max_alpha):
        """根据chunk距离计算迷雾alpha值（羽化渐变）"""
        if chunk_dist <= 0:
            return 0
        if chunk_dist >= FEATHER_RADIUS_CHUNKS:
            return max_alpha
        ratio = chunk_dist / FEATHER_RADIUS_CHUNKS
        return int(max_alpha * ratio)

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
        self._fog_dirty = set(self._explored_chunks.keys())
        self._fullscreen_fog_cache.clear()
        self._fullmap_cache.clear()
        self._radar_fog_cache_key = None

    # ─── 从Tiled地图渲染真实外观 ───

    def _render_fullmap_tiles(self, tile_map, map_id):
        """从Tiled地图的实际图层渲染全图（原始分辨率），结果缓存"""
        if map_id in self._fullmap_render_cache:
            return self._fullmap_render_cache[map_id]

        map_w = tile_map.width
        map_h = tile_map.height
        pixel_w = map_w * TILE_SIZE
        pixel_h = map_h * TILE_SIZE

        surf = pygame.Surface((pixel_w, pixel_h))
        surf.fill((25, 28, 40))

        if tile_map._load_failed or tile_map.tmx_data is None:
            self._fullmap_render_cache[map_id] = surf
            return surf

        for layer_index in tile_map._visible_layers:
            layer = tile_map.tmx_data.layers[layer_index]
            if not hasattr(layer, 'data'):
                continue
            for row in range(map_h):
                for col in range(map_w):
                    gid = layer.data[row][col]
                    if gid == 0:
                        continue
                    tile_image = tile_map.tmx_data.get_tile_image_by_gid(gid)
                    if tile_image:
                        surf.blit(tile_image, (col * TILE_SIZE, row * TILE_SIZE))

        self._fullmap_render_cache[map_id] = surf
        return surf

    # ─── 角落小地图（雷达式，以玩家为中心） ───

    def draw(self, surface, tile_map, map_id, player, camera):
        """绘制雷达式小地图到游戏画面右下角"""
        if tile_map is None:
            return

        map_w = tile_map.width
        map_h = tile_map.height
        if map_w <= 0 or map_h <= 0:
            return

        # 获取全图渲染结果（缓存）
        fullmap = self._render_fullmap_tiles(tile_map, map_id)

        # 玩家像素坐标
        player_px = player.x
        player_py = player.y

        # 雷达视野对应的像素范围
        radar_px_w = RADAR_RADIUS_TILES * 2 * TILE_SIZE
        radar_px_h = RADAR_RADIUS_TILES * 2 * TILE_SIZE

        # 裁剪区域（以玩家为中心）
        crop_x = player_px - radar_px_w / 2
        crop_y = player_py - radar_px_h / 2

        # 创建小地图Surface
        minimap_surf = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)
        minimap_surf.fill((20, 22, 35, 200))

        # 【问题1修复】正确处理边缘裁剪偏移
        # 计算裁剪区域与全图的交集
        src_x = max(0, int(crop_x))
        src_y = max(0, int(crop_y))
        src_right = min(fullmap.get_width(), int(crop_x + radar_px_w))
        src_bottom = min(fullmap.get_height(), int(crop_y + radar_px_h))
        src_w = src_right - src_x
        src_h = src_bottom - src_y

        if src_w > 0 and src_h > 0:
            cropped = fullmap.subsurface(pygame.Rect(src_x, src_y, src_w, src_h))
            # 计算裁剪区域在小地图上的偏移位置（保持居中）
            # crop偏移量 = 实际裁剪起点 - 期望裁剪起点
            offset_x_in_crop = src_x - crop_x  # crop_x可能为负，src_x=0，偏移为正
            offset_y_in_crop = src_y - crop_y
            # 缩放比例
            scale_x = MINIMAP_WIDTH / radar_px_w
            scale_y = MINIMAP_HEIGHT / radar_px_h
            # 裁剪区域缩放后的尺寸和位置
            scaled_w = max(1, int(src_w * scale_x))
            scaled_h = max(1, int(src_h * scale_y))
            dest_x = int(offset_x_in_crop * scale_x)
            dest_y = int(offset_y_in_crop * scale_y)
            scaled = pygame.transform.smoothscale(cropped, (scaled_w, scaled_h))
            minimap_surf.blit(scaled, (dest_x, dest_y))

        # 未探索区域叠加羽化迷雾（带缓存）
        fog = self._render_fog_radar_cached(map_id, tile_map, player_px, player_py)
        minimap_surf.blit(fog, (0, 0))

        # 绘制地标（仅已探索区域）
        self._draw_landmarks_radar(minimap_surf, map_id, player_px, player_py)

        # 绘制玩家中心亮点（常亮）
        center_x = MINIMAP_WIDTH // 2
        center_y = MINIMAP_HEIGHT // 2
        for dx in range(-PLAYER_DOT_RADIUS, PLAYER_DOT_RADIUS + 1):
            for dy in range(-PLAYER_DOT_RADIUS, PLAYER_DOT_RADIUS + 1):
                if dx * dx + dy * dy <= PLAYER_DOT_RADIUS * PLAYER_DOT_RADIUS:
                    nx, ny = center_x + dx, center_y + dy
                    if 0 <= nx < MINIMAP_WIDTH and 0 <= ny < MINIMAP_HEIGHT:
                        minimap_surf.set_at((nx, ny), PLAYER_DOT_COLOR)

        # 绘制到屏幕右下角
        dest_x = INTERNAL_WIDTH - MINIMAP_WIDTH - MINIMAP_MARGIN
        dest_y = INTERNAL_HEIGHT - MINIMAP_HEIGHT - MINIMAP_MARGIN

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
        surface.blit(minimap_surf, (dest_x, dest_y))

    def _render_fog_radar_cached(self, map_id, tile_map, player_px, player_py):
        """渲染雷达式小地图的迷雾层（带缓存，问题2修复）

        当玩家所在chunk不变且无新探索时，复用上一帧的迷雾Surface
        """
        player_tx = int(player_px / TILE_SIZE)
        player_ty = int(player_py / TILE_SIZE)
        player_cx = player_tx // 4
        player_cy = player_ty // 4

        cache_key = (map_id, player_cx, player_cy)

        if self._radar_fog_cache_key == cache_key and self._radar_fog_cache_surf is not None:
            return self._radar_fog_cache_surf

        # 需要重新渲染
        fog = self._render_fog_radar(map_id, tile_map, player_px, player_py)
        self._radar_fog_cache_key = cache_key
        self._radar_fog_cache_surf = fog
        return fog

    def _render_fog_radar(self, map_id, tile_map, player_px, player_py):
        """渲染雷达式小地图的迷雾层（含羽化渐变）"""
        fog = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)

        map_w = tile_map.width
        map_h = tile_map.height

        tiles_per_pixel_x = (RADAR_RADIUS_TILES * 2) / MINIMAP_WIDTH
        tiles_per_pixel_y = (RADAR_RADIUS_TILES * 2) / MINIMAP_HEIGHT

        player_tx = player_px / TILE_SIZE
        player_ty = player_py / TILE_SIZE

        # 预计算chunk距离缓存
        chunk_dist_cache = {}

        for py in range(MINIMAP_HEIGHT):
            for px in range(MINIMAP_WIDTH):
                tile_x = int(player_tx - RADAR_RADIUS_TILES + px * tiles_per_pixel_x)
                tile_y = int(player_ty - RADAR_RADIUS_TILES + py * tiles_per_pixel_y)

                if tile_x < 0 or tile_x >= map_w or tile_y < 0 or tile_y >= map_h:
                    continue

                cx = tile_x // 4
                cy = tile_y // 4

                if (cx, cy) not in chunk_dist_cache:
                    chunk_dist_cache[(cx, cy)] = self._get_chunk_distance(map_id, cx, cy)

                dist = chunk_dist_cache[(cx, cy)]
                alpha = self._get_fog_alpha(dist, FOG_ALPHA_RADAR)

                if alpha > 0:
                    fog.set_at((px, py), (FOG_RGB[0], FOG_RGB[1], FOG_RGB[2], alpha))

        return fog

    def _draw_landmarks_radar(self, minimap_surf, map_id, player_px, player_py):
        """在雷达式小地图上绘制地标"""
        landmarks = LANDMARKS.get(map_id, [])
        if not landmarks:
            return

        player_tx = player_px / TILE_SIZE
        player_ty = player_py / TILE_SIZE
        tiles_per_pixel_x = (RADAR_RADIUS_TILES * 2) / MINIMAP_WIDTH
        tiles_per_pixel_y = (RADAR_RADIUS_TILES * 2) / MINIMAP_HEIGHT

        for landmark_type, tile_x, tile_y in landmarks:
            if not self.is_explored(map_id, tile_x, tile_y):
                continue

            dx = tile_x - player_tx
            dy = tile_y - player_ty
            px = int(MINIMAP_WIDTH / 2 + dx / tiles_per_pixel_x)
            py = int(MINIMAP_HEIGHT / 2 + dy / tiles_per_pixel_y)

            if px < 1 or px >= MINIMAP_WIDTH - 1 or py < 1 or py >= MINIMAP_HEIGHT - 1:
                continue

            color = LANDMARK_COLORS.get(landmark_type, (200, 200, 200))
            for ddx in range(-1, 2):
                for ddy in range(-1, 2):
                    nx, ny = px + ddx, py + ddy
                    if 0 <= nx < MINIMAP_WIDTH and 0 <= ny < MINIMAP_HEIGHT:
                        minimap_surf.set_at((nx, ny), color)

    # ─── 全屏地图（M键，显示整个地图+迷雾） ───

    def draw_fullscreen(self, surface, tile_map, map_id, player, all_maps=None):
        """绘制全屏地图视图"""
        if tile_map is None:
            return

        map_w = tile_map.width
        map_h = tile_map.height
        if map_w <= 0 or map_h <= 0:
            return

        # 全屏地图区域
        map_area_x = 20
        map_area_y = 30
        map_area_w = INTERNAL_WIDTH - 40
        map_area_h = INTERNAL_HEIGHT - 50

        # 缩放比例（保持宽高比）
        scale = min(map_area_w / map_w, map_area_h / map_h)
        render_w = int(map_w * scale)
        render_h = int(map_h * scale)
        offset_x = map_area_x + (map_area_w - render_w) // 2
        offset_y = map_area_y + (map_area_h - render_h) // 2

        # 从Tiled图层渲染全图并缩放
        fullmap = self._render_fullmap_tiles(tile_map, map_id)
        scaled_map = pygame.transform.smoothscale(fullmap, (render_w, render_h))
        surface.blit(scaled_map, (offset_x, offset_y))

        # 绘制迷雾层（含羽化渐变，带缓存）
        cache_key = (map_id, render_w, render_h)
        if cache_key not in self._fullscreen_fog_cache:
            # 【问题3修复】使用chunk级别渲染代替逐像素渲染
            fog_surf = self._render_fog_fullscreen_chunk(map_id, tile_map, render_w, render_h, scale)
            self._fullscreen_fog_cache[cache_key] = fog_surf
            self._fog_dirty.discard(map_id)
        surface.blit(self._fullscreen_fog_cache[cache_key], (offset_x, offset_y))

        # 绘制地标（仅已探索区域）
        self._draw_landmarks_fullscreen(surface, map_id, scale, offset_x, offset_y)

        # 绘制玩家位置（常亮白色亮点）
        player_tx = player.x / TILE_SIZE
        player_ty = player.y / TILE_SIZE
        px = int(offset_x + player_tx * scale)
        py = int(offset_y + player_ty * scale)

        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx * dx + dy * dy <= 9:
                    nx, ny = px + dx, py + dy
                    if 0 <= nx < INTERNAL_WIDTH and 0 <= ny < INTERNAL_HEIGHT:
                        surface.set_at((nx, ny), PLAYER_DOT_COLOR)

        # 绘制其他校区的缩略图
        if all_maps:
            other_x = 10
            other_y = INTERNAL_HEIGHT - 70
            for other_id, other_map in all_maps.items():
                if other_id == map_id:
                    continue
                if other_id not in self._fullmap_cache:
                    other_fullmap = self._render_fullmap_tiles(other_map, other_id)
                    small_w = 50
                    small_h = 38
                    small_surf = pygame.transform.smoothscale(other_fullmap, (small_w, small_h))
                    small_scale = min(small_w / other_map.width, small_h / other_map.height)
                    small_fog = self._render_fog_fullscreen_chunk(other_id, other_map, small_w, small_h, small_scale)
                    small_surf.blit(small_fog, (0, 0))
                    self._fullmap_cache[other_id] = small_surf

                small_cached = self._fullmap_cache[other_id]
                surface.blit(small_cached, (other_x, other_y))

                font = self._get_font()
                name = "南湖校区" if "nanhu" in other_id else "本部校区"
                name_surf = font.render(name, True, (180, 180, 200))
                surface.blit(name_surf, (other_x, other_y - 10))
                other_x += 60

    def _render_fog_fullscreen_chunk(self, map_id, tile_map, render_w, render_h, scale):
        """渲染全屏地图的迷雾层（chunk级别，问题3修复）

        按chunk（4x4 tile）为单位渲染迷雾，而非逐像素，
        大幅减少计算量（约1/16），然后用smoothscale平滑过渡
        """
        map_w = tile_map.width
        map_h = tile_map.height
        if map_w <= 0 or map_h <= 0:
            fog = pygame.Surface((render_w, render_h), pygame.SRCALPHA)
            fog.fill((FOG_RGB[0], FOG_RGB[1], FOG_RGB[2], FOG_ALPHA_FULLSCREEN))
            return fog

        # 计算chunk网格尺寸
        chunks_x = (map_w + 3) // 4
        chunks_y = (map_h + 3) // 4

        # 在chunk分辨率上渲染迷雾
        chunk_surf = pygame.Surface((chunks_x, chunks_y), pygame.SRCALPHA)

        for cy in range(chunks_y):
            for cx in range(chunks_x):
                dist = self._get_chunk_distance(map_id, cx, cy)
                alpha = self._get_fog_alpha(dist, FOG_ALPHA_FULLSCREEN)
                if alpha > 0:
                    chunk_surf.set_at((cx, cy), (FOG_RGB[0], FOG_RGB[1], FOG_RGB[2], alpha))

        # 缩放到目标尺寸（smoothscale自动平滑过渡）
        fog = pygame.transform.smoothscale(chunk_surf, (render_w, render_h))
        return fog

    def _draw_landmarks_fullscreen(self, surface, map_id, scale, offset_x, offset_y):
        """在全屏地图上绘制地标图标和名称"""
        landmarks = LANDMARKS.get(map_id, [])
        if not landmarks:
            return

        font = self._get_font(12)

        for landmark_type, tile_x, tile_y in landmarks:
            if not self.is_explored(map_id, tile_x, tile_y):
                continue

            px = int(offset_x + tile_x * scale)
            py = int(offset_y + tile_y * scale)
            color = LANDMARK_COLORS.get(landmark_type, (200, 200, 200))

            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx * dx + dy * dy <= 4:
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < INTERNAL_WIDTH and 0 <= ny < INTERNAL_HEIGHT:
                            surface.set_at((nx, ny), color)

            name = LANDMARK_NAMES.get(landmark_type, "")
            if name:
                name_surf = font.render(name, True, (255, 255, 255))
                name_rect = name_surf.get_rect(left=px + 5, centery=py)
                # 描边文字：4方向深色描边，更自然美观
                outline_color = (60, 55, 45)
                for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    outline_surf = font.render(name, True, outline_color)
                    surface.blit(outline_surf, (name_rect.x + ox, name_rect.y + oy))
                surface.blit(name_surf, name_rect)

    def invalidate_cache(self, map_id=None):
        """使缓存失效（地图变化时调用）"""
        if map_id:
            self._fullmap_render_cache.pop(map_id, None)
            self._fullmap_cache.pop(map_id, None)
            keys_to_remove = [k for k in self._fullscreen_fog_cache if k[0] == map_id]
            for k in keys_to_remove:
                del self._fullscreen_fog_cache[k]
        else:
            self._fullmap_render_cache.clear()
            self._fullmap_cache.clear()
            self._fullscreen_fog_cache.clear()
        self._radar_fog_cache_key = None
