import pygame


# 1. Advance the physics world (Sync Python time with Box2D time)
world.Step(timeStep, velocityIterations, positionIterations)

# 2. Clear the screen
screen.fill((0, 0, 0))

# 3. Synchronize graphics with physics positions
for body in world.bodies:
    # Get the updated position from pybox2d
    x, y = body.position 
    
    # Draw your Python graphic at that exact position
    draw_sprite(x, y) 

# 4. Flip the display
pygame.display.flip()