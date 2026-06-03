"""博雅广场谜题：地砖阵法

广场中央雕塑周围有8块颜色略异的地砖，位于8个方位。
雕塑底座铭文的方位顺序暗示了正确的踩踏顺序。
玩家走到对应方位的地砖上按F踩踏，按铭文字序依次踩踏即可破解阵法。
"""
import random
import pygame
from config import TILE_SIZE


class BoyaPuzzle:
    # 8个方位名（按索引顺序：0=北, 1=东北, 2=东, 3=东南, 4=南, 5=西南, 6=西, 7=西北）
    DIRECTIONS = [
        "北", "东北", "东", "东南",
        "南", "西南", "西", "西北",
    ]

    # 8块地砖的微异颜色（石砖色调，略有深浅差异）
    TILE_COLORS = [
        (110, 105, 95),   # 北
        (100, 95, 88),    # 东北
        (105, 100, 90),   # 东
        (95, 90, 85),     # 东南
        (108, 102, 92),   # 南
        (98, 92, 86),     # 西南
        (102, 96, 90),    # 西
        (115, 108, 98),   # 西北
    ]

    # 已踩踏地砖的发光颜色（金色半透明）
    COLOR_STEPPED_GLOW = (255, 220, 80)
    COLOR_WRONG_FLASH = (255, 80, 80)

    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self.solved = False

        # 随机生成正确踩踏顺序（8个方位的排列）
        self.CORRECT_ORDER = list(range(8))
        random.shuffle(self.CORRECT_ORDER)

        # 根据随机顺序生成铭文
        self.INSCRIPTION = "·".join(self.DIRECTIONS[i] for i in self.CORRECT_ORDER)

        self._current_step = 0
        self._stepped = [False] * 8
        self._wrong_flash_timer = 0.0
        self._wrong_flash_duration = 0.5

        # 8块地砖的世界坐标（像素），由 _setup_boya_entities 设置
        self.tile_positions = []  # [(x, y), ...] 共8个

    def setup_tiles(self, center_x, center_y):
        """根据中心坐标设置8块地砖的位置（环绕雕塑，间隔1格）"""
        self.tile_positions = []
        # 8个方位偏移：距离中心32像素（间隔1格16像素 + 半格8像素 = 24像素，取32更宽松）
        # 使用 2格距离 = 32像素，让地砖与雕塑之间有1格空隙
        dist = 32  # 2格距离
        offsets = [
            (0, -dist),      # 北
            (dist, -dist),   # 东北
            (dist, 0),       # 东
            (dist, dist),    # 东南
            (0, dist),       # 南
            (-dist, dist),   # 西南
            (-dist, 0),      # 西
            (-dist, -dist),  # 西北
        ]
        for dx, dy in offsets:
            # 地砖左上角坐标 = 中心 + 偏移 - 半格（使偏移点为地砖中心）
            x = center_x + dx - TILE_SIZE // 2
            y = center_y + dy - TILE_SIZE // 2
            self.tile_positions.append((x, y))

    def get_tile_index_at(self, player_x, player_y):
        """判断玩家当前站在哪块地砖上，返回索引或 None"""
        for idx, (tx, ty) in enumerate(self.tile_positions):
            if tx <= player_x < tx + TILE_SIZE and ty <= player_y < ty + TILE_SIZE:
                return idx
        return None

    def step_tile(self, tile_idx):
        """踩踏指定索引的地砖，返回结果字典"""
        if self.solved:
            return {"result": "none", "message": "地砖阵法已经破解了。"}

        if self._stepped[tile_idx]:
            return {"result": "none", "message": "这块地砖已经踩过了。"}

        expected = self.CORRECT_ORDER[self._current_step]

        if tile_idx == expected:
            self._stepped[tile_idx] = True
            self._current_step += 1

            if self._current_step >= len(self.CORRECT_ORDER):
                self.solved = True
                self.puzzle_manager.solve("boya", self.inventory)
                return {"result": "complete", "message": "地砖阵法破解！中央雕塑缓缓移开了……"}
            return {"result": "correct", "message": ""}
        else:
            self._wrong_flash_timer = self._wrong_flash_duration
            self._current_step = 0
            self._stepped = [False] * 8
            return {"result": "wrong", "message": "顺序似乎不对，地砖恢复了原状……"}

    def is_tile_stepped(self, tile_idx):
        return self._stepped[tile_idx]

    def get_inscription_hint(self):
        return self.INSCRIPTION

    def update(self, dt):
        if self._wrong_flash_timer > 0:
            self._wrong_flash_timer -= dt
            if self._wrong_flash_timer < 0:
                self._wrong_flash_timer = 0.0

    def draw(self, surface, camera):
        """在场景上绘制8块可踩踏地砖的视觉标识、发光特效和错误闪烁"""
        if not self.tile_positions:
            return

        for idx, (tx, ty) in enumerate(self.tile_positions):
            sx, sy = camera.apply(tx, ty)
            ix, iy = int(sx), int(sy)
            rect = pygame.Rect(ix, iy, TILE_SIZE, TILE_SIZE)

            # 常态：微异底色 + 深棕边框（与普通地砖区分）
            if not self._stepped[idx]:
                tile_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                tile_surf.fill((*self.TILE_COLORS[idx], 60))
                surface.blit(tile_surf, rect.topleft)
                pygame.draw.rect(surface, (107, 91, 79), rect, 1)
            else:
                # 已踩踏：金色半透明发光 + 亮金边框
                glow_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                glow_surf.fill((*self.COLOR_STEPPED_GLOW, 120))
                surface.blit(glow_surf, rect.topleft)
                pygame.draw.rect(surface, (255, 200, 60), rect, 2)

        # 错误闪烁：全8块红色闪烁
        if self._wrong_flash_timer > 0:
            alpha = int(180 * (self._wrong_flash_timer / self._wrong_flash_duration))
            flash_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            flash_surf.fill((*self.COLOR_WRONG_FLASH, alpha))
            for tx, ty in self.tile_positions:
                sx, sy = camera.apply(tx, ty)
                surface.blit(flash_surf, (int(sx), int(sy)))
