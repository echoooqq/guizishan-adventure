import pygame

from config import PLAYER_SPEED, SPRINT_SPEED, TILE_SIZE, PLAYER_COLOR, MAX_STAMINA, SPRINT_STAMINA_COST, STAMINA_REGEN


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.direction = "down"
        self.stamina = MAX_STAMINA
        self.is_sprinting = False
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.move_speed = PLAYER_SPEED * TILE_SIZE

    def handle_input(self, dt, collision_map=None, map_cols=0, map_rows=0):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
            self.direction = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
            self.direction = "down"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
            self.direction = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
            self.direction = "right"

        self.is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if self.is_sprinting and self.stamina <= 0:
            self.is_sprinting = False

        speed = SPRINT_SPEED * TILE_SIZE if self.is_sprinting else self.move_speed

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        move_x = dx * speed * dt
        move_y = dy * speed * dt

        if collision_map is not None:
            new_x = self.x + move_x
            if not self._check_collision(new_x, self.y, collision_map, map_cols, map_rows):
                self.x = new_x

            new_y = self.y + move_y
            if not self._check_collision(self.x, new_y, collision_map, map_cols, map_rows):
                self.y = new_y
        else:
            self.x += move_x
            self.y += move_y

        if dx != 0 or dy != 0:
            self.animation_timer += dt
            if self.animation_timer >= 0.15:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_frame = 0
            self.animation_timer = 0

        if self.is_sprinting and (dx != 0 or dy != 0):
            self.stamina = max(0, self.stamina - SPRINT_STAMINA_COST * dt * 60)
        elif dx == 0 and dy == 0:
            self.stamina = min(MAX_STAMINA, self.stamina + STAMINA_REGEN * dt * 60)

    def _check_collision(self, x, y, collision_map, map_cols, map_rows):
        hitbox_shrink = 2
        left = x + hitbox_shrink
        right = x + self.width - hitbox_shrink
        top = y + hitbox_shrink
        bottom = y + self.height - hitbox_shrink

        col_l = int(left // TILE_SIZE)
        col_r = int(right // TILE_SIZE)
        row_t = int(top // TILE_SIZE)
        row_b = int(bottom // TILE_SIZE)

        for row in range(row_t, row_b + 1):
            for col in range(col_l, col_r + 1):
                if row < 0 or row >= map_rows or col < 0 or col >= map_cols:
                    return True
                if collision_map[row][col]:
                    return True
        return False

    def get_center(self):
        return self.x + self.width // 2, self.y + self.height // 2

    def draw(self, surface, camera):
        screen_x, screen_y = camera.apply(self.x, self.y)

        color = PLAYER_COLOR
        if self.is_sprinting:
            color = (100, 149, 237)

        body_rect = pygame.Rect(screen_x + 2, screen_y + 2, self.width - 4, self.height - 4)
        pygame.draw.rect(surface, color, body_rect)

        if self.direction == "up":
            pygame.draw.rect(surface, (255, 255, 255), (screen_x + 4, screen_y + 3, 3, 2))
            pygame.draw.rect(surface, (255, 255, 255), (screen_x + 9, screen_y + 3, 3, 2))
        elif self.direction == "down":
            pygame.draw.rect(surface, (255, 255, 255), (screen_x + 4, screen_y + 8, 3, 2))
            pygame.draw.rect(surface, (255, 255, 255), (screen_x + 9, screen_y + 8, 3, 2))
        elif self.direction == "left":
            pygame.draw.rect(surface, (255, 255, 255), (screen_x + 2, screen_y + 5, 3, 2))
        elif self.direction == "right":
            pygame.draw.rect(surface, (255, 255, 255), (screen_x + 11, screen_y + 5, 3, 2))

        if self.animation_frame % 2 == 1 and (self.direction in ("left", "right")):
            offset = 1 if self.animation_frame == 1 else -1
            pygame.draw.rect(surface, color, (screen_x + 3, screen_y + self.height - 2 + offset, 4, 2))
            pygame.draw.rect(surface, color, (screen_x + 9, screen_y + self.height - 2 - offset, 4, 2))
