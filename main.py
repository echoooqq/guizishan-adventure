import sys

import pygame

from config import SCREEN_WIDTH, SCREEN_HEIGHT, INTERNAL_WIDTH, INTERNAL_HEIGHT, FPS, SCALE_X, SCALE_Y, TITLE, TILE_SIZE
from game.game_manager import GameManager, GameState
from game.camera import Camera
from player.player import Player
from world.test_map import TestMap


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.internal_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

        self.clock = pygame.time.Clock()
        self.game_manager = GameManager()

        self.test_map = TestMap(20, 15)
        self.player = Player(3 * TILE_SIZE, 3 * TILE_SIZE)
        self.camera = Camera(self.test_map.pixel_width, self.test_map.pixel_height)

        self.running = True

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)

            self._handle_events()
            self._update(dt)
            self._draw()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.game_manager.state == GameState.PLAYING:
                    self.game_manager.handle_event(event)
                    return
                self.game_manager.handle_event(event)

    def _update(self, dt):
        if self.game_manager.state == GameState.PLAYING:
            self.player.handle_input(
                dt,
                collision_map=self.test_map.collision_map,
                map_cols=self.test_map.width,
                map_rows=self.test_map.height,
            )
            center_x, center_y = self.player.get_center()
            self.camera.update(center_x, center_y)

    def _draw(self):
        self.internal_surface.fill((0, 0, 0))

        if self.game_manager.state == GameState.TITLE:
            self.game_manager.draw(self.internal_surface)
        elif self.game_manager.state == GameState.PLAYING:
            self.test_map.draw(self.internal_surface, self.camera)
            self.player.draw(self.internal_surface, self.camera)
        elif self.game_manager.state in (GameState.PAUSED, GameState.INVENTORY, GameState.MAP_VIEW):
            self.test_map.draw(self.internal_surface, self.camera)
            self.player.draw(self.internal_surface, self.camera)
            self.game_manager.draw(self.internal_surface)

        scaled_surface = pygame.transform.scale(self.internal_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
