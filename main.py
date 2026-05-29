import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game.game_manager import GameManager


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("GuiZiShan Adventure - Campus Mystery Exploration")

    game_manager = GameManager(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_manager.handle_event(event)

        game_manager.update()
        game_manager.draw()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
