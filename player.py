import math
import pygame

PLAYER_SIZE = 32
PLAYER_SPEED = 180


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = PLAYER_SPEED
        self.direction = "down"
        self.anim_timer = 0.0
        self.moving = False
        self.keys_held = {"up": False, "down": False, "left": False, "right": False}
        self.interaction_cooldown = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - 4, int(self.y), PLAYER_SIZE + 8, PLAYER_SIZE + 4)
    
    @property
    def center(self):
        return (self.x + PLAYER_SIZE // 2, self.y + PLAYER_SIZE // 2)

    def handle_key(self, key, pressed):
        mapping = {
            pygame.K_w: "up", pygame.K_UP: "up",
            pygame.K_s: "down", pygame.K_DOWN: "down",
            pygame.K_a: "left", pygame.K_LEFT: "left",
            pygame.K_d: "right", pygame.K_RIGHT: "right",
        }
        if key in mapping:
            self.keys_held[mapping[key]] = pressed

    def move(self, dt, collision_map):
        dx = 0
        dy = 0
        if self.keys_held["left"]:
            dx -= 1
        if self.keys_held["right"]:
            dx += 1
        if self.keys_held["up"]:
            dy -= 1
        if self.keys_held["down"]:
            dy += 1

        self.moving = dx != 0 or dy != 0
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        move_x = dx * self.speed * dt
        move_y = dy * self.speed * dt

        if collision_map is not None:
            new_x = self.x + move_x
            test_rect_x = pygame.Rect(int(new_x) - 4, int(self.y),
                                       PLAYER_SIZE + 8, PLAYER_SIZE + 4)
            if not collision_map.collides(test_rect_x):
                self.x = new_x

            new_y = self.y + move_y
            test_rect_y = pygame.Rect(int(self.x) - 4, int(new_y),
                                       PLAYER_SIZE + 8, PLAYER_SIZE + 4)
            if not collision_map.collides(test_rect_y):
                self.y = new_y
        else:
            self.x += move_x
            self.y += move_y

        if self.interaction_cooldown > 0:
            self.interaction_cooldown -= dt

    def update(self, dt):
        self.anim_timer += dt

    def draw(self, surface, camera_x=0, camera_y=0):
        bob_y = int(math.sin(self.anim_timer * 9) * 2.5) if self.moving else 0
        walk_cycle = int(math.sin(self.anim_timer * 12)) if self.moving else 0
        px = int(self.x - camera_x) + PLAYER_SIZE // 2
        py = int(self.y - camera_y) + bob_y

        skin_color = (255, 218, 185)
        hair_color = (28, 22, 18)
        shirt_color = (42, 98, 178)
        shirt_light = (62, 118, 198)
        pants_color = (52, 52, 72)
        shoe_color = (212, 162, 108)

        head_cx = px
        head_cy = py + 10
        head_r = 11
        pygame.draw.circle(surface, hair_color, (head_cx, head_cy), head_r + 3)
        pygame.draw.circle(surface, skin_color, (head_cx, head_cy + 1), head_r)

        hair_top = (22, 18, 14)
        if self.direction == "up":
            pygame.draw.arc(surface, hair_top,
                            (head_cx - head_r - 2, head_cy - head_r - 2,
                             (head_r + 2) * 2, (head_r + 2) * 2),
                            0, math.pi, 5)
        elif self.direction in ("left", "right"):
            side_offset = 3 if self.direction == "left" else -3
            pygame.draw.ellipse(surface, hair_top,
                               (head_cx - head_r - 2 + side_offset,
                                head_cy - head_r - 3, head_r * 2 + 2, head_r + 2))
        else:
            pygame.draw.ellipse(surface, hair_top,
                               (head_cx - head_r - 2, head_cy - head_r - 4,
                                head_r * 2 + 4, head_r + 3))

        eye_offset_y = head_cy + 1
        eye_spread = 5
        eye_size = 2.5
        pupil_size = 1.3
        if self.direction == "up":
            el_x = px - eye_spread
            er_x = px + eye_spread
            ey = eye_offset_y - 2
            pygame.draw.circle(surface, (255, 255, 255), (el_x, ey), int(eye_size))
            pygame.draw.circle(surface, (255, 255, 255), (er_x, ey), int(eye_size))
            pygame.draw.circle(surface, (0, 0, 0), (el_x, ey), int(pupil_size))
            pygame.draw.circle(surface, (0, 0, 0), (er_x, ey), int(pupil_size))
        elif self.direction == "down":
            el_x = px - eye_spread
            er_x = px + eye_spread
            ey = eye_offset_y + 2
            pygame.draw.circle(surface, (255, 255, 255), (el_x, ey), int(eye_size))
            pygame.draw.circle(surface, (255, 255, 255), (er_x, ey), int(eye_size))
            pygame.draw.circle(surface, (0, 0, 0), (el_x, ey + 1), int(pupil_size))
            pygame.draw.circle(surface, (0, 0, 0), (er_x, ey + 1), int(pupil_size))
            mouth_y = head_cy + 7
            pygame.draw.arc(surface, (188, 100, 90),
                           (px - 4, mouth_y - 2, 8, 5), math.pi * 0.15, math.pi * 0.85, 1)
        elif self.direction == "left":
            el_x = px - eye_spread - 1
            er_x = px + eye_spread - 1
            ey = eye_offset_y
            pygame.draw.circle(surface, (255, 255, 255), (el_x, ey), int(eye_size))
            pygame.draw.circle(surface, (255, 255, 255), (er_x, ey), int(eye_size))
            pygame.draw.circle(surface, (0, 0, 0), (el_x - 1, ey), int(pupil_size))
            pygame.draw.circle(surface, (0, 0, 0), (er_x - 1, ey), int(pupil_size))
        else:
            el_x = px - eye_spread + 1
            er_x = px + eye_spread + 1
            ey = eye_offset_y
            pygame.draw.circle(surface, (255, 255, 255), (el_x, ey), int(eye_size))
            pygame.draw.circle(surface, (255, 255, 255), (er_x, ey), int(eye_size))
            pygame.draw.circle(surface, (0, 0, 0), (el_x + 1, ey), int(pupil_size))
            pygame.draw.circle(surface, (0, 0, 0), (er_x + 1, ey), int(pupil_size))

        body_top = py + 21
        body_w = 20
        body_h = 16
        body_left = px - body_w // 2
        pygame.draw.rect(surface, shirt_color,
                         (body_left, body_top, body_w, body_h), border_radius=4)
        pygame.draw.rect(surface, shirt_light,
                         (body_left + 2, body_top + 2, body_w - 4, 6), border_radius=2)
        pygame.draw.polygon(surface, shirt_light, [
            (px - 6, body_top + 2),
            (px, body_top + 6),
            (px + 6, body_top + 2),
        ])

        arm_w = 6
        arm_l = 12
        arm_swing = walk_cycle * 3 if self.moving else 0
        left_arm_x = body_left - arm_w // 2 + arm_swing
        right_arm_x = body_left + body_w - arm_w // 2 - arm_swing
        arm_y = body_top + 2
        pygame.draw.rect(surface, shirt_color,
                         (int(left_arm_x), arm_y, arm_w, arm_l), border_radius=3)
        pygame.draw.rect(surface, shirt_color,
                         (int(right_arm_x), arm_y, arm_w, arm_l), border_radius=3)
        hand_r = 4
        pygame.draw.circle(surface, skin_color,
                           (int(left_arm_x + arm_w // 2), arm_y + arm_l), hand_r)
        pygame.draw.circle(surface, skin_color,
                           (int(right_arm_x + arm_w // 2), arm_y + arm_l), hand_r)

        pants_top = body_top + body_h - 2
        pants_h = 12
        pants_left = px - 8
        pygame.draw.rect(surface, pants_color,
                         (pants_left, pants_top, 16, pants_h), border_radius=2)

        leg_w = 7
        leg_h = 10
        leg_swing = walk_cycle * 4 if self.moving else 0
        left_leg_x = pants_left + 1 - leg_swing
        right_leg_x = pants_left + 8 + leg_swing
        leg_y = pants_top + pants_h - 3
        pygame.draw.rect(surface, pants_color,
                         (int(left_leg_x), leg_y, leg_w, leg_h), border_radius=2)
        pygame.draw.rect(surface, pants_color,
                         (int(right_leg_x), leg_y, leg_w, leg_h), border_radius=2)

        shoe_w = 9
        shoe_h = 4
        pygame.draw.ellipse(surface, shoe_color,
                           (int(left_leg_x - 1), leg_y + leg_h - 2, shoe_w, shoe_h))
        pygame.draw.ellipse(surface, shoe_color,
                           (int(right_leg_x - 1), leg_y + leg_h - 2, shoe_w, shoe_h))

        bag_back_x = body_left + body_w - 3
        bag_back_y = body_top + 3
        pygame.draw.rect(surface, (180, 140, 60),
                         (bag_back_x, bag_back_y, 6, 8), border_radius=2)
        pygame.draw.line(surface, (140, 100, 30),
                        (bag_back_x + 3, bag_back_y), (bag_back_x + 3, bag_back_y + 8), 1)


class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.smoothing = 8.0

    def follow(self, target_x, target_y, dt):
        self.target_x = target_x - self.width // 2
        self.target_y = target_y - self.height // 2
        self.target_x = max(0, min(self.target_x, self.map_width - self.width))
        self.target_y = max(0, min(self.target_y, self.map_height - self.height))

        self.x += (self.target_x - self.x) * self.smoothing * dt
        self.y += (self.target_y - self.y) * self.smoothing * dt
        self.x = max(0, min(self.x, self.map_width - self.width))
        self.y = max(0, min(self.y, self.map_height - self.height))

    def snap_to(self, target_x, target_y):
        self.target_x = target_x - self.width // 2
        self.target_y = target_y - self.height // 2
        self.target_x = max(0, min(self.target_x, self.map_width - self.width))
        self.target_y = max(0, min(self.target_y, self.map_height - self.height))
        self.x = self.target_x
        self.y = self.target_y

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def apply(self, surface, dest_surface):
        dest_surface.blit(surface, (-int(self.x), -int(self.y)))
