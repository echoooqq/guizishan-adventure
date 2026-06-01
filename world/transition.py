import os
import pygame
from enum import Enum, auto
from config import INTERNAL_WIDTH, INTERNAL_HEIGHT, FONT_PATH, FONT_INFO_SIZE


class TransitionType(Enum):
    INDOOR_ENTER = "indoor_enter"
    INDOOR_EXIT = "indoor_exit"
    FLOOR_CHANGE = "floor_change"
    CAMPUS_BUS = "campus_bus"


class TransitionState(Enum):
    IDLE = auto()
    FADE_OUT = auto()
    LOADING = auto()
    FADE_IN = auto()
    BUS_ANIM = auto()


class TransitionManager:
    FADE_DURATION = 0.5
    BUS_ANIM_DURATION = 2.5

    def __init__(self):
        self.state = TransitionState.IDLE
        self.transition_type = TransitionType.INDOOR_ENTER
        self.timer = 0.0
        self.alpha = 0
        self.target_map = None
        self.spawn_point = None
        self.on_load_callback = None
        self._bus_offset = 0.0
        self._bus_label = ""
        self._font = None
        self._init_font()

    def _init_font(self):
        try:
            self._font = pygame.font.Font(FONT_PATH, FONT_INFO_SIZE)
        except Exception:
            self._font = pygame.font.Font(None, FONT_INFO_SIZE)

    def start_transition(self, transition_type, target_map, spawn_point,
                         on_load_callback=None, bus_label=""):
        if self.state != TransitionState.IDLE:
            return
        self.transition_type = transition_type
        self.target_map = target_map
        self.spawn_point = spawn_point
        self.on_load_callback = on_load_callback
        self.timer = 0.0
        self.alpha = 0

        if transition_type == TransitionType.CAMPUS_BUS:
            self._bus_label = bus_label
        else:
            self._bus_label = ""

        self.state = TransitionState.FADE_OUT

    def update(self, dt):
        if self.state == TransitionState.IDLE:
            return

        self.timer += dt

        if self.state == TransitionState.FADE_OUT:
            progress = min(1.0, self.timer / self.FADE_DURATION)
            self.alpha = int(255 * progress)
            if progress >= 1.0:
                self.alpha = 255
                self.state = TransitionState.LOADING
                self.timer = 0.0

        elif self.state == TransitionState.LOADING:
            if self.on_load_callback:
                self.on_load_callback(self.target_map, self.spawn_point)
                self.on_load_callback = None
            if self.transition_type == TransitionType.CAMPUS_BUS:
                self.state = TransitionState.BUS_ANIM
                self._bus_offset = -INTERNAL_WIDTH
                self.timer = 0.0
            else:
                self.state = TransitionState.FADE_IN
                self.timer = 0.0

        elif self.state == TransitionState.BUS_ANIM:
            progress = min(1.0, self.timer / self.BUS_ANIM_DURATION)
            self._bus_offset = -INTERNAL_WIDTH + (INTERNAL_WIDTH * 2 + 60) * progress
            if progress >= 1.0:
                self.state = TransitionState.FADE_IN
                self.timer = 0.0

        elif self.state == TransitionState.FADE_IN:
            progress = min(1.0, self.timer / self.FADE_DURATION)
            self.alpha = int(255 * (1.0 - progress))
            if progress >= 1.0:
                self.alpha = 0
                self.state = TransitionState.IDLE
                self.timer = 0.0

    def draw(self, surface):
        if self.state == TransitionState.IDLE:
            return

        if self.state == TransitionState.FADE_OUT or self.state == TransitionState.FADE_IN:
            overlay = pygame.Surface(
                (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, self.alpha))
            surface.blit(overlay, (0, 0))

        elif self.state == TransitionState.BUS_ANIM:
            overlay = pygame.Surface(
                (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((20, 25, 40, 235))
            surface.blit(overlay, (0, 0))

            road_y = INTERNAL_HEIGHT // 2 + 22
            pygame.draw.rect(surface, (60, 60, 60),
                             (0, road_y, INTERNAL_WIDTH, 12))
            for x in range(0, INTERNAL_WIDTH, 20):
                pygame.draw.rect(surface, (200, 200, 100),
                                 (x, road_y + 5, 10, 2))

            self._draw_bus(surface)
            self._draw_bus_label(surface)

        elif self.state == TransitionState.LOADING:
            overlay = pygame.Surface(
                (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 255))
            surface.blit(overlay, (0, 0))

    def _draw_bus(self, surface):
        bus_x = int(self._bus_offset)
        bus_y = INTERNAL_HEIGHT // 2 - 20
        bus_w = 60
        bus_h = 40

        pygame.draw.rect(surface, (0, 100, 180),
                         (bus_x, bus_y, bus_w, bus_h), border_radius=4)
        pygame.draw.rect(surface, (0, 80, 150),
                         (bus_x, bus_y, bus_w, bus_h), 2, border_radius=4)

        for i in range(3):
            wx = bus_x + 8 + i * 16
            pygame.draw.rect(surface, (180, 220, 255),
                             (wx, bus_y + 5, 10, 10))
            pygame.draw.rect(surface, (100, 160, 220),
                             (wx, bus_y + 5, 10, 10), 1)

        pygame.draw.rect(surface, (200, 200, 200),
                         (bus_x + 2, bus_y + bus_h - 8, bus_w - 4, 6))

        pygame.draw.circle(surface, (60, 60, 60),
                           (bus_x + 12, bus_y + bus_h), 5)
        pygame.draw.circle(surface, (40, 40, 40),
                           (bus_x + 12, bus_y + bus_h), 5, 1)
        pygame.draw.circle(surface, (60, 60, 60),
                           (bus_x + bus_w - 12, bus_y + bus_h), 5)
        pygame.draw.circle(surface, (40, 40, 40),
                           (bus_x + bus_w - 12, bus_y + bus_h), 5, 1)

        pygame.draw.rect(surface, (255, 255, 200),
                         (bus_x + bus_w - 3, bus_y + 12, 4, 4))
        pygame.draw.rect(surface, (255, 100, 100),
                         (bus_x - 1, bus_y + 12, 4, 4))

    def _draw_bus_label(self, surface):
        if not self._bus_label or not self._font:
            return

        label_surf = self._font.render(self._bus_label, True, (255, 255, 255))
        label_rect = label_surf.get_rect(
            centerx=INTERNAL_WIDTH // 2,
            centery=INTERNAL_HEIGHT // 2 - 40
        )

        bg_rect = label_rect.inflate(12, 6)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 160))
        surface.blit(bg_surf, bg_rect.topleft)
        surface.blit(label_surf, label_rect)

        dots = "." * (int(self.timer * 2) % 4)
        dot_surf = self._font.render(dots, True, (200, 200, 200))
        dot_rect = dot_surf.get_rect(
            left=label_rect.right + 2,
            centery=label_rect.centery
        )
        surface.blit(dot_surf, dot_rect)

    @property
    def is_active(self):
        return self.state != TransitionState.IDLE

    @property
    def is_loading(self):
        return self.state == TransitionState.LOADING
