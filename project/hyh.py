"""
Start screen -> Box2D sandbox.

The pygame window opens on a menu with no physics world at all.
Clicking Start (or pressing Enter) creates the Box2D world.
Esc inside the sim throws the world away and returns to the menu.

Requires physics_sandbox.py in the same folder.
"""
import random
import sys

import pygame

from notbymebuttolearn import (
    Sandbox, to_world, WIDTH, HEIGHT, FPS, BG_COLOR, PPM,
)

MENU, SIM = "menu", "sim"


def quit_game():
    pygame.quit()
    sys.exit()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Physics demo")
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont(None, 72)
    button_font = pygame.font.SysFont(None, 40)
    hud_font = pygame.font.SysFont(None, 22)

    start_button = pygame.Rect(0, 0, 220, 70)
    start_button.center = (WIDTH // 2, HEIGHT // 2 + 40)

    state = MENU
    sandbox = None  # no Box2D world exists yet

    def start_sim():
        nonlocal state, sandbox
        sandbox = Sandbox()  # <- Box2D world is created here
        state = SIM

    def back_to_menu():
        nonlocal state, sandbox
        sandbox = None  # world is garbage collected
        state = MENU

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            # ------------------------------------------------ menu input
            if state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_button.collidepoint(event.pos):
                        start_sim()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        start_sim()
                    elif event.key == pygame.K_ESCAPE:
                        quit_game()

            # ------------------------------------------------- sim input
            elif state == SIM:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        back_to_menu()
                        continue
                    elif event.key == pygame.K_r:
                        sandbox.reset()
                    elif event.key == pygame.K_SPACE:
                        for _ in range(10):
                            pos = (random.uniform(3, WIDTH / PPM - 3), HEIGHT / PPM - 2)
                            if random.random() < 0.5:
                                sandbox.spawn_box(pos)
                            else:
                                sandbox.spawn_circle(pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    p = to_world(*event.pos)
                    if event.button == 1:
                        if not sandbox.grab(p):
                            sandbox.spawn_box(p)
                    elif event.button == 3:
                        sandbox.spawn_circle(p)
                elif event.type == pygame.MOUSEMOTION:
                    sandbox.drag(to_world(*event.pos))
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    sandbox.release()

        # ----------------------------------------------------- update/draw
        screen.fill(BG_COLOR)

        if state == MENU:
            title = title_font.render("Physics Sandbox", True, (230, 230, 240))
            screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))

            hovered = start_button.collidepoint(pygame.mouse.get_pos())
            color = (90, 160, 255) if hovered else (60, 120, 220)
            pygame.draw.rect(screen, color, start_button, border_radius=12)
            label = button_font.render("Start", True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=start_button.center))

        elif state == SIM:
            sandbox.step()
            sandbox.draw(screen)
            hud = "[LMB] box/drag  [RMB] circle  [Space] burst  [R] reset  [Esc] menu"
            screen.blit(hud_font.render(hud, True, (200, 200, 210)), (10, 8))

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()