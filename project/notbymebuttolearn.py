"""
Simple physics sandbox using Box2D and pygame.

Install:  pip install box2d-py pygame

Controls:
  Left click (empty space)  spawn a box
  Left click + drag (body)  grab and throw it
  Right click               spawn a circle
  Space                     spawn a burst of random shapes
  R                         reset the world
  Esc / close window        quit
"""
import random
import sys

import pygame
from Box2D import b2World, b2PolygonShape, b2Vec2

# ---------------------------------------------------------------- settings
WIDTH, HEIGHT = 800, 600
PPM = 30.0            # pixels per meter
FPS = 60
TIME_STEP = 1.0 / FPS
VEL_ITERS, POS_ITERS = 8, 3
BG_COLOR = (24, 26, 33)
STATIC_COLOR = (90, 95, 110)


# ----------------------------------------------------------------- helpers
def to_screen(p):
    """World meters (y up) -> screen pixels (y down)."""
    return int(p[0] * PPM), int(HEIGHT - p[1] * PPM)


def to_world(px, py):
    """Screen pixels -> world meters."""
    return b2Vec2(px / PPM, (HEIGHT - py) / PPM)


def random_color():
    return tuple(random.randint(80, 255) for _ in range(3))


# ------------------------------------------------------------------- world
class Sandbox:
    def __init__(self):
        self.reset()

    def reset(self):
        self.world = b2World(gravity=(0, -9.81), doSleep=True)
        self.mouse_joint = None

        w, h = WIDTH / PPM, HEIGHT / PPM
        # Ground, ceiling-less walls (centre x, centre y, half w, half h)
        self.ground = self._static_box(w / 2, 0.5, w / 2, 0.5)
        self._static_box(0.5, h / 2, 0.5, h / 2)
        self._static_box(w - 0.5, h / 2, 0.5, h / 2)

        # A few starting boxes
        for i in range(5):
            self.spawn_box((w / 2 + (i - 2) * 1.2, 10 + i))

    def _static_box(self, x, y, hw, hh):
        body = self.world.CreateStaticBody(
            position=(x, y), shapes=b2PolygonShape(box=(hw, hh))
        )
        body.userData = STATIC_COLOR
        return body

    # -- spawning
    def spawn_box(self, pos, half=None):
        half = half or random.uniform(0.3, 0.8)
        body = self.world.CreateDynamicBody(position=pos, angle=random.uniform(0, 3.14))
        body.CreatePolygonFixture(
            box=(half, half), density=1.0, friction=0.4, restitution=0.2
        )
        body.userData = random_color()
        return body

    def spawn_circle(self, pos, radius=None):
        radius = radius or random.uniform(0.3, 0.7)
        body = self.world.CreateDynamicBody(position=pos)
        body.CreateCircleFixture(
            radius=radius, density=1.0, friction=0.3, restitution=0.5
        )
        body.userData = random_color()
        return body

    # -- mouse dragging
    def body_at(self, point):
        for body in self.world.bodies:
            if body.type == 0:  # static
                continue
            for fixture in body.fixtures:
                if fixture.TestPoint(point):
                    return body
        return None

    def grab(self, point):
        body = self.body_at(point)
        if body is None:
            return False
        self.mouse_joint = self.world.CreateMouseJoint(
            bodyA=self.ground,
            bodyB=body,
            target=point,
            maxForce=1000.0 * body.mass,
        )
        body.awake = True
        return True

    def drag(self, point):
        if self.mouse_joint:
            self.mouse_joint.target = point

    def release(self):
        if self.mouse_joint:
            self.world.DestroyJoint(self.mouse_joint)
            self.mouse_joint = None

    # -- simulation + drawing
    def step(self):
        self.world.Step(TIME_STEP, VEL_ITERS, POS_ITERS)
        self.world.ClearForces()

    def draw(self, screen):
        for body in self.world.bodies:
            color = body.userData
            for fixture in body.fixtures:
                shape = fixture.shape
                if isinstance(shape, b2PolygonShape):
                    pts = [to_screen(body.transform * v) for v in shape.vertices]
                    pygame.draw.polygon(screen, color, pts)
                    pygame.draw.polygon(screen, (15, 15, 15), pts, 2)
                else:  # circle
                    center = to_screen(body.transform * shape.pos)
                    r = int(shape.radius * PPM)
                    pygame.draw.circle(screen, color, center, r)
                    pygame.draw.circle(screen, (15, 15, 15), center, r, 2)
                    # line showing rotation
                    edge = to_screen(body.transform * (shape.pos + (shape.radius, 0)))
                    pygame.draw.line(screen, (15, 15, 15), center, edge, 2)

        if self.mouse_joint:
            a = to_screen(self.mouse_joint.anchorB)
            b = to_screen(self.mouse_joint.target)
            pygame.draw.line(screen, (255, 255, 255), a, b, 1)


# -------------------------------------------------------------------- main
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Box2D + pygame sandbox")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)
    sandbox = Sandbox()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
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

        sandbox.step()

        screen.fill(BG_COLOR)
        sandbox.draw(screen)
        hud = f"Bodies: {sandbox.world.bodyCount - 3}   FPS: {clock.get_fps():.0f}   " \
              "[LMB] box/drag  [RMB] circle  [Space] burst  [R] reset"
        screen.blit(font.render(hud, True, (200, 200, 210)), (10, 8))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()