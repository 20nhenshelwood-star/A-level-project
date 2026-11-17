import random
import sys

import pygame
from Box2D import b2World, b2PolygonShape, b2Vec2

pygame.init()
screen = pygame.display.set_mode((1000, 500))
pygame.display.set_caption("Physics demo")
clock = pygame.time.Clock()
title_font = pygame.font.SysFont(None, 72)
button_font = pygame.font.SysFont(None, 40)
hud_font = pygame.font.SysFont(None, 22)
FPS = 60
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False