"""可互动物体模块：处理场景中的可交互元素及其精灵渲染"""
import os
import pygame
from config import INTERACTION_RANGE, TILE_SIZE

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(PROJECT_ROOT, "assets", "sprites")

# 可互动物体精灵映射：interactive_type 或 sprite_key -> 精灵文件名
OBJECT_SPRITE_MAP = {
    "osmanthus_tree": "osmanthus_tree.png",
    "osmanthus_tree_glow": "osmanthus_tree_glow.png",
    "street_lamp": "street_lamp.png",
    "bookshelf": "bookshelf.png",
    "bulletin_board": "bulletin_board.png",
    "computer_terminal": "computer_terminal.png",
    "sculpture": "sculpture.png",
    "flowerbed": "flowerbed.png",
    "fountain": "fountain.png",
    "badge_pickup": "badge_pickup.png",
    "dining_table": "dining_table.png",
    "scoreboard": "scoreboard.png",
    "equipment_cabinet": "equipment_cabinet.png",
    "door_entrance": "door_entrance.png",
    "shooting_station": "shooting_station.png",
    "osmanthus_branch": "osmanthus_branch.png",
    "old_bookmark": "old_bookmark.png",
    "water_bottle": "water_bottle.png",
    "old_badge": "old_badge.png",
    "magnifying_glass": "magnifying_glass.png",
    "floor_lamp": "floor_lamp.png",
    "magazine_rack": "magazine_rack.png",
    "water_dispenser": "water_dispenser.png",
}

# 精灵缓存
_sprite_cache = {}


def _load_object_sprite(sprite_key):
    """加载物体精灵（带缓存）"""
    if sprite_key in _sprite_cache:
        return _sprite_cache[sprite_key]
    filename = OBJECT_SPRITE_MAP.get(sprite_key)
    if filename:
        path = os.path.join(SPRITES_DIR, filename)
        if os.path.exists(path):
            sprite = pygame.image.load(path).convert_alpha()
            _sprite_cache[sprite_key] = sprite
            return sprite
    _sprite_cache[sprite_key] = None
    return None


class InteractiveObject:
    def __init__(self, x, y, width, height, interactive_type, properties=None):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.interactive_type = interactive_type
        self.properties = properties or {}
        self.interaction_range = self.properties.get("interaction_range", INTERACTION_RANGE)
        self.prompt_text = self.properties.get("prompt_text", self._default_prompt())
        self.interacted = False
        self.on_interact = None
        self.color = self.properties.get("color", (120, 100, 80))
        self.item_id = self.properties.get("item_id", "")
        self.sprite_key = self.properties.get("sprite_key", "") or self.properties.get("sprite", "")
        self._sprite = None

    def _default_prompt(self):
        prompts = {
            "dialog": "对话",
            "examine": "查看",
            "pickup": "拾取",
            "use": "使用",
            "mechanism": "操作",
            "enter": "进入",
        }
        return prompts.get(self.interactive_type, "互动")

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    def is_player_nearby(self, player_x, player_y):
        if self.interactive_type == "pickup" and self.interacted:
            return False
        dx = player_x - self.center_x
        dy = player_y - self.center_y
        return dx * dx + dy * dy <= self.interaction_range * self.interaction_range

    def interact(self):
        if self.interactive_type == "pickup" and self.interacted:
            return None
        if self.on_interact:
            return self.on_interact(self)
        result = {"type": self.interactive_type, "object": self}
        if self.interactive_type == "dialog":
            result["dialogue_id"] = self.properties.get("dialogue_id", "")
        return result

    def _ensure_sprite_loaded(self):
        """延迟加载精灵"""
        if self._sprite is None and self.sprite_key:
            self._sprite = _load_object_sprite(self.sprite_key)

    def draw(self, surface, camera):
        if self.properties.get("invisible", False):
            return
        if self.interactive_type == "pickup" and self.interacted:
            return
        if self.interactive_type == "enter":
            return

        self._ensure_sprite_loaded()
        sx, sy = camera.apply(self.x, self.y)
        ix, iy = int(sx), int(sy)

        # 使用精灵渲染
        if self._sprite is not None:
            # 居中精灵到物体区域
            sprite_w = self._sprite.get_width()
            sprite_h = self._sprite.get_height()
            offset_x = (self.width - sprite_w) // 2
            offset_y = self.height - sprite_h  # 底部对齐
            surface.blit(self._sprite, (ix + offset_x, iy + offset_y))
        else:
            # 降级：使用矩形绘制
            rect = pygame.Rect(ix, iy, self.width, self.height)
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, (200, 200, 200), rect, 1)

    def draw_prompt(self, surface, camera, font):
        sx, sy = camera.apply(self.center_x, self.y - 4)
        text_surf = font.render(f"按 F {self.prompt_text}", True, (255, 255, 255))
        text_rect = text_surf.get_rect(centerx=int(sx), bottom=int(sy))
        bg_rect = text_rect.inflate(6, 4)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 160))
        surface.blit(bg_surf, bg_rect.topleft)
        surface.blit(text_surf, text_rect)
