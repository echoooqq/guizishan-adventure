import random
import pygame
from config import (
    FONT_PATH,
    FONT_INFO_SIZE,
    COLOR_WHITE,
)


class GuizhongPuzzle:
    TREE_COUNT = 7

    STATE_IDLE = "idle"
    STATE_EXAMINED = "examined"
    STATE_SHAKING = "shaking"
    STATE_BADGE_DROPPING = "badge_dropping"
    STATE_BADGE_DROPPED = "badge_dropped"
    STATE_SOLVED = "solved"

    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self.solved = False

        self.glowing_tree_index = random.randint(0, self.TREE_COUNT - 1)
        self.tree_positions = []

        self._state = self.STATE_IDLE
        self._shake_timer = 0.0
        self._shake_duration = 1.0
        self._shake_offset = 0
        self._badge_fall_timer = 0.0
        self._badge_fall_duration = 0.8
        self._badge_y_offset = 0.0

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)

    def setup_trees(self, tree_positions):
        self.tree_positions = tree_positions[:self.TREE_COUNT]
        while len(self.tree_positions) < self.TREE_COUNT:
            self.tree_positions.append((
                100 + len(self.tree_positions) * 60,
                100,
            ))

    @property
    def state(self):
        return self._state

    @property
    def is_animating(self):
        return self._state in (self.STATE_SHAKING, self.STATE_BADGE_DROPPING)

    @property
    def is_badge_dropped(self):
        return self._state == self.STATE_BADGE_DROPPED

    def get_glowing_tree_pos(self):
        if 0 <= self.glowing_tree_index < len(self.tree_positions):
            return self.tree_positions[self.glowing_tree_index]
        return None

    def examine_tree(self):
        if self._state != self.STATE_IDLE:
            return False
        self._state = self.STATE_EXAMINED
        return True

    def shake_tree(self):
        if self._state != self.STATE_EXAMINED:
            return False
        self._state = self.STATE_SHAKING
        self._shake_timer = 0.0
        self.puzzle_manager.start_puzzle("guizhong")
        return True

    def mark_solved(self):
        self._state = self.STATE_SOLVED
        self.solved = True
        if self.puzzle_manager.get_state("guizhong").value != "solved":
            self.puzzle_manager.solve("guizhong")

    def update(self, dt):
        if self._state == self.STATE_SHAKING:
            self._shake_timer += dt
            progress = self._shake_timer / self._shake_duration
            self._shake_offset = int(3 * pygame.math.Vector2(1, 0).rotate(
                progress * 720
            ).x)
            if self._shake_timer >= self._shake_duration:
                self._shake_offset = 0
                self._state = self.STATE_BADGE_DROPPING
                self._badge_fall_timer = 0.0
                self._badge_y_offset = -20.0

        elif self._state == self.STATE_BADGE_DROPPING:
            self._badge_fall_timer += dt
            progress = min(self._badge_fall_timer / self._badge_fall_duration, 1.0)
            self._badge_y_offset = -20.0 + 20.0 * progress
            if progress >= 1.0:
                self._state = self.STATE_BADGE_DROPPED

    def draw(self, surface, camera, is_night=True):
        for i, (tx, ty) in enumerate(self.tree_positions):
            is_glowing = (i == self.glowing_tree_index) and is_night
            draw_x, draw_y = camera.apply(tx, ty)

            if is_glowing and self._state == self.STATE_SHAKING:
                draw_x += self._shake_offset

            self._draw_tree(surface, int(draw_x), int(draw_y), is_glowing)

        if self._state in (self.STATE_BADGE_DROPPING, self.STATE_BADGE_DROPPED):
            pos = self.get_glowing_tree_pos()
            if pos:
                bx, by = camera.apply(pos[0], pos[1] + 8)
                badge_y = by + self._badge_y_offset
                self._draw_badge(surface, int(bx), int(badge_y))

    def _draw_tree(self, surface, x, y, is_glowing):
        trunk_rect = pygame.Rect(x - 2, y - 4, 4, 12)
        pygame.draw.rect(surface, (100, 70, 40), trunk_rect)

        crown_color = (60, 140, 50) if not is_glowing else (100, 200, 80)
        crown_rect = pygame.Rect(x - 8, y - 16, 16, 14)
        pygame.draw.ellipse(surface, crown_color, crown_rect)

        flower_color = (255, 200, 0) if not is_glowing else (255, 230, 100)
        flower_highlight = (255, 230, 100) if not is_glowing else (255, 245, 180)
        surface_rect = surface.get_rect()
        for fx, fy in [(-5, -14), (-2, -12), (2, -14), (5, -12),
                       (-6, -10), (-1, -9), (3, -10), (6, -8),
                       (-4, -7), (0, -6), (4, -7)]:
            px, py = x + fx, y + fy
            if surface_rect.collidepoint(px, py):
                surface.set_at((px, py), flower_color)
        for fx, fy in [(-3, -13), (1, -11), (4, -13), (-4, -8), (2, -7)]:
            px, py = x + fx, y + fy
            if surface_rect.collidepoint(px, py):
                surface.set_at((px, py), flower_highlight)

        if is_glowing and self._state not in (self.STATE_SOLVED,):
            glow_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            alpha = int(80 + 40 * abs(pygame.time.get_ticks() % 1000 - 500) / 500)
            pygame.draw.ellipse(glow_surf, (200, 255, 150, alpha), (0, 0, 32, 32))
            surface.blit(glow_surf, (x - 16, y - 24))

    def _draw_badge(self, surface, x, y):
        pygame.draw.circle(surface, (255, 215, 0), (x, y), 5)
        pygame.draw.circle(surface, (255, 255, 200), (x, y), 3)
        glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 215, 0, 60), (10, 10), 10)
        surface.blit(glow_surf, (x - 10, y - 10))
