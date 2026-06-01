import random
import pygame
from config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    FONT_PATH,
    FONT_INFO_SIZE,
    COLOR_WHITE,
    COLOR_BLACK,
    TILE_SIZE,
)
from ui.dialog_box import create_border_surface, draw_nine_slice


class GuizhongPuzzle:
    TREE_COUNT = 7

    def __init__(self, puzzle_manager, inventory):
        self.puzzle_manager = puzzle_manager
        self.inventory = inventory
        self.active = False
        self.solved = False
        self.on_complete = None

        self.glowing_tree_index = random.randint(0, self.TREE_COUNT - 1)
        self.tree_positions = []
        self._shaking = False
        self._shake_timer = 0.0
        self._shake_duration = 1.0
        self._shake_offset = 0
        self._badge_dropped = False
        self._badge_fall_timer = 0.0
        self._badge_fall_duration = 0.8
        self._badge_y_offset = 0.0
        self._show_result = False
        self._result_timer = 0.0
        self._result_duration = 2.0

        self.font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        self.border_image = create_border_surface()

    def setup_trees(self, tree_positions):
        self.tree_positions = tree_positions[:self.TREE_COUNT]
        while len(self.tree_positions) < self.TREE_COUNT:
            self.tree_positions.append((
                100 + len(self.tree_positions) * 60,
                100,
            ))

    def start(self, on_complete=None):
        if self.puzzle_manager.get_state("guizhong").value == "solved":
            return False
        self.active = True
        self.solved = False
        self.on_complete = on_complete
        self._shaking = False
        self._shake_timer = 0.0
        self._badge_dropped = False
        self._badge_fall_timer = 0.0
        self._show_result = False
        self._result_timer = 0.0
        self.glowing_tree_index = random.randint(0, len(self.tree_positions) - 1)
        self.puzzle_manager.start_puzzle("guizhong")
        return True

    def get_glowing_tree_pos(self):
        if 0 <= self.glowing_tree_index < len(self.tree_positions):
            return self.tree_positions[self.glowing_tree_index]
        return None

    def is_near_glowing_tree(self, player_x, player_y, range_dist=40):
        pos = self.get_glowing_tree_pos()
        if pos is None:
            return False
        dx = player_x - pos[0]
        dy = player_y - pos[1]
        return dx * dx + dy * dy <= range_dist * range_dist

    def shake_tree(self):
        if self._shaking or self._badge_dropped:
            return
        self._shaking = True
        self._shake_timer = 0.0

    def handle_event(self, event):
        if not self.active:
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_f, pygame.K_SPACE):
            if self._show_result:
                self._finish()
            elif not self._shaking and not self._badge_dropped:
                self.shake_tree()
        elif event.key == pygame.K_ESCAPE:
            self._finish()

    def update(self, dt):
        if not self.active:
            return

        if self._shaking:
            self._shake_timer += dt
            progress = self._shake_timer / self._shake_duration
            self._shake_offset = int(3 * pygame.math.Vector2(1, 0).rotate(
                progress * 720
            ).x)
            if self._shake_timer >= self._shake_duration:
                self._shaking = False
                self._shake_offset = 0
                self._badge_dropped = True
                self._badge_fall_timer = 0.0
                self._badge_y_offset = -20.0

        if self._badge_dropped and not self._show_result:
            self._badge_fall_timer += dt
            progress = min(self._badge_fall_timer / self._badge_fall_duration, 1.0)
            self._badge_y_offset = -20.0 + 20.0 * progress
            if progress >= 1.0:
                self._show_result = True
                self._result_timer = 0.0
                self.solved = True
                self.puzzle_manager.solve("guizhong", self.inventory)

        if self._show_result:
            self._result_timer += dt

    def _finish(self):
        self.active = False
        if self.on_complete:
            callback = self.on_complete
            self.on_complete = None
            callback()

    def draw(self, surface, camera=None):
        if not self.active:
            return

        for i, (tx, ty) in enumerate(self.tree_positions):
            is_glowing = (i == self.glowing_tree_index)
            draw_x, draw_y = tx, ty
            if camera:
                draw_x, draw_y = camera.apply(tx, ty)
            else:
                draw_x, draw_y = tx, ty

            if is_glowing and self._shaking:
                draw_x += self._shake_offset

            self._draw_tree(surface, int(draw_x), int(draw_y), is_glowing)

        if self._badge_dropped:
            pos = self.get_glowing_tree_pos()
            if pos:
                bx, by = pos[0], pos[1] + 8
                if camera:
                    bx, by = camera.apply(bx, by)
                badge_y = by + self._badge_y_offset
                self._draw_badge(surface, int(bx), int(badge_y))

        if self._show_result:
            self._draw_result_overlay(surface)

    def _draw_tree(self, surface, x, y, is_glowing):
        trunk_rect = pygame.Rect(x - 2, y - 4, 4, 12)
        pygame.draw.rect(surface, (100, 70, 40), trunk_rect)

        crown_color = (60, 140, 50) if not is_glowing else (100, 200, 80)
        crown_rect = pygame.Rect(x - 8, y - 16, 16, 14)
        pygame.draw.ellipse(surface, crown_color, crown_rect)

        if is_glowing and not self._badge_dropped:
            glow_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            alpha = int(80 + 40 * abs(pygame.time.get_ticks() % 1000 - 500) / 500)
            pygame.draw.ellipse(glow_surf, (200, 255, 150, alpha), (0, 0, 32, 32))
            surface.blit(glow_surf, (x - 16, y - 24))

            prompt = self.font.render("按 F 摇树", True, COLOR_WHITE)
            prompt_rect = prompt.get_rect(centerx=x, bottom=y - 20)
            bg_rect = prompt_rect.inflate(6, 4)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 160))
            surface.blit(bg_surf, bg_rect.topleft)
            surface.blit(prompt, prompt_rect)

    def _draw_badge(self, surface, x, y):
        pygame.draw.circle(surface, (255, 215, 0), (x, y), 5)
        pygame.draw.circle(surface, (255, 255, 200), (x, y), 3)
        glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 215, 0, 60), (10, 10), 10)
        surface.blit(glow_surf, (x - 10, y - 10))

    def _draw_result_overlay(self, surface):
        box_w, box_h = 240, 50
        box_x = (INTERNAL_WIDTH - box_w) // 2
        box_y = (INTERNAL_HEIGHT - box_h) // 2

        draw_nine_slice(
            surface, self.border_image,
            (box_x, box_y, box_w, box_h),
        )

        text = self.font.render("获得了桂花徽章碎片·壹！", True, (255, 215, 0))
        text_rect = text.get_rect(centerx=box_x + box_w // 2, centery=box_y + box_h // 2 - 6)
        surface.blit(text, text_rect)

        hint = self.font.render("按 F 继续", True, COLOR_WHITE)
        hint_rect = hint.get_rect(centerx=box_x + box_w // 2, centery=box_y + box_h // 2 + 10)
        surface.blit(hint, hint_rect)
