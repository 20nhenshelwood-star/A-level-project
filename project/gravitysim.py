import pygame as pg
import math

pg.init()


SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Gravity simulator")


clock = pg.time.Clock()
FPS = 60


ball = pg.image.load("ballsmol.png")
rect = ball.get_rect()
rect.center = (SCREEN_WIDTH /2, SCREEN_HEIGHT/2 )


a=0
g = 9.81
mass = 2
velocity = pg.math.Vector2(5,0)
gpe = rect.bottom*g*mass
def findv():
    b = gpe/mass
    c = math.sqrt(b)
    return c




running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    a += 1
    if rect.bottom > SCREEN_HEIGHT+2:
        velocity.y = 0
        velocity.x = 1


#logic


    if rect.bottom > SCREEN_HEIGHT:
        velocity.y *= -1


    if rect.left < 0 or rect.right > SCREEN_WIDTH:
        velocity.x *= -1

    velocity.y += 9.81/60
 
    #velocity.y += 0.3
    rect.center += velocity


#colour
    screen.fill((255,255,255))
#draw
    screen.blit(ball, rect)
#update display
    pg.display.flip()
#limit fps
    clock.tick(FPS)
    



pg.quit()
