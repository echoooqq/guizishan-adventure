"""玩家模块：处理玩家移动、体力、背包和精灵渲染"""
import os
import pygame
from config import (
    TILE_SIZE,
    PLAYER_SPEED,
    SPRINT_SPEED,
    SPRINT_STAMINA_COST,
    STAMINA_REGEN,
    MAX_STAMINA,
    PLAYER_WIDTH,
    PLAYER_HEIGHT,
    PLAYER_HITBOX_WIDTH,
    PLAYER_HITBOX_HEIGHT,
    COLOR_BLACK,
    COLOR_PLAYER_BODY,
    COLOR_PLAYER_HEAD,
    COLOR_PLAYER_HAIR,
)
from world.entity import Entity
from player.inventory import Inventory

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITE_PATH = os.path.join(PROJECT_ROOT, "assets", "sprites", "player_sheet.png")

# 精灵表参数
SPRITE_FRAME_W = 16
SPRITE_FRAME_H = 24
SPRITE_COLS = 4  # 每行4帧
SPRITE_ROWS = 4  # 4个方向：下、左、右、上
DIRECTION_ROW = {"down": 0, "left": 1, "right": 2, "up": 3}


class Player(Entity):
    _sprite_sheet = None  # 类变量，共享精灵表

    def __init__(self, x, y):
        super().__init__(
            x, y,
            width=PLAYER_WIDTH,
            height=PLAYER_HEIGHT,
            hitbox_width=PLAYER_HITBOX_WIDTH,
            hitbox_height=PLAYER_HITBOX_HEIGHT,
        )
        self.stamina = MAX_STAMINA
        self.is_sprinting = False
        self.inventory = Inventory()
        self._load_sprites()

    @classmethod
    def _load_sprites(cls):
        """加载玩家精灵表（仅加载一次）"""
        if cls._sprite_sheet is not None:
            return
        if os.path.exists(SPRITE_PATH):
            cls._sprite_sheet = pygame.image.load(SPRITE_PATH).convert_alpha()
        else:
            cls._sprite_sheet = None

    def update(self, dt, keys, collision_map, map_width, map_height):
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1.0

        if dy < 0:
            self.direction = "up"
        elif dy > 0:
            self.direction = "down"
        elif dx < 0:
            self.direction = "left"
        elif dx > 0:
            self.direction = "right"

        self.is_moving = dx != 0 or dy != 0

        self.is_sprinting = (
            (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
            and self.is_moving
            and self.stamina > 0
        )
        speed = SPRINT_SPEED * TILE_SIZE if self.is_sprinting else PLAYER_SPEED * TILE_SIZE

        if self.stamina <= 0 and not self.is_sprinting:
            speed *= 0.7

        if self.is_sprinting:
            self.stamina = max(0, self.stamina - SPRINT_STAMINA_COST * dt)
        elif not self.is_moving:
            self.stamina = min(MAX_STAMINA, self.stamina + STAMINA_REGEN * dt)

        self.move_with_collision(
            dx, dy, speed, dt,
            collision_map, map_width, map_height,
        )

        self.update_animation(dt)

    def draw(self, surface, camera):
        draw_x, draw_y = camera.apply(
            self.x - self.width / 2,
            self.y - self.height,
        )
        ix, iy = int(draw_x), int(draw_y)

        # 使用精灵表渲染
        if self._sprite_sheet is not None:
            row = DIRECTION_ROW.get(self.direction, 0)
            col = self.animation_frame % SPRITE_COLS
            src_rect = pygame.Rect(
                col * SPRITE_FRAME_W, row * SPRITE_FRAME_H,
                SPRITE_FRAME_W, SPRITE_FRAME_H,
            )
            # 居中对齐精灵到碰撞盒上方
            offset_x = (PLAYER_WIDTH - SPRITE_FRAME_W) // 2
            offset_y = PLAYER_HEIGHT - SPRITE_FRAME_H
            surface.blit(self._sprite_sheet, (ix + offset_x, iy + offset_y), src_rect)
        else:
            # 降级：使用代码绘制
            self._draw_fallback(surface, ix, iy)

    def _draw_fallback(self, surface, ix, iy):
        """降级绘制：当精灵表不可用时使用代码绘制"""
        body_rect = pygame.Rect(ix + 1, iy + 8, self.width - 2, self.height - 8)
        pygame.draw.rect(surface, COLOR_PLAYER_BODY, body_rect)

        head_rect = pygame.Rect(ix + 2, iy + 1, self.width - 4, 8)
        pygame.draw.rect(surface, COLOR_PLAYER_HEAD, head_rect)

        hair_rect = pygame.Rect(ix + 2, iy, self.width - 4, 3)
        pygame.draw.rect(surface, COLOR_PLAYER_HAIR, hair_rect)

        if self.direction == "down":
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 4, iy + 4, 2, 2))
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 8, iy + 4, 2, 2))
        elif self.direction == "up":
            pass
        elif self.direction == "left":
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 3, iy + 4, 2, 2))
        elif self.direction == "right":
            pygame.draw.rect(surface, COLOR_BLACK, (ix + 9, iy + 4, 2, 2))

        if self.is_moving and self.animation_frame in (1, 3):
            offset = 1 if self.animation_frame == 1 else -1
            leg_y = iy + self.height - 3
            pygame.draw.rect(surface, COLOR_PLAYER_BODY, (ix + 3, leg_y + offset, 3, 3))
            pygame.draw.rect(surface, COLOR_PLAYER_BODY, (ix + 8, leg_y - offset, 3, 3))
