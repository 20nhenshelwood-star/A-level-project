import pygame
import Box2D
from Box2D import b2World, b2_staticBody, b2_dynamicBody

# --- CONSTANTS ---
WIDTH, HEIGHT = 1000, 700
FPS = 60
PPM = 40.0  # Pixels Per Metre (Box2D works in metres, Pygame in pixels)

# --- PROCEDURAL HELPER FUNCTIONS ---
def world_to_screen(pos):
    """Converts Box2D world coordinates (metres, Y-up) to Pygame screen coordinates (pixels, Y-down)."""
    return int(pos[0] * PPM), int(HEIGHT - (pos[1] * PPM))

def screen_to_world(pos):
    """Converts Pygame screen coordinates to Box2D world coordinates."""
    return pos[0] / PPM, (HEIGHT - pos[1]) / PPM

def draw_hud(screen, font, is_simulating, total_cost):
    """Procedural UI rendering function."""
    status = "SIMULATING (Press SPACE to Reset)" if is_simulating else "BUILD MODE (Press SPACE to Test)"
    text_surf = font.render(f"{status}  |  Bridge Cost: £{total_cost:.2f}", True, (255, 255, 255))
    screen.blit(text_surf, (20, 20))


# --- OOP PHYSICS CLASSES ---
class Node:
    """Represents a joint or fixed terrain anchor."""
    def __init__(self, world, x, y, is_anchor=False):
        self.is_anchor = is_anchor
        body_type = b2_staticBody if is_anchor else b2_dynamicBody
        
        # Encapsulate the Box2D body inside our custom Node class
        self.body = world.CreateBody(
            type=body_type,
            position=(x, y),
            fixedRotation=True
        )
        self.body.CreateCircleFixture(radius=0.15, density=1.0, friction=0.5)

    def draw(self, screen):
        pos = world_to_screen(self.body.position)
        colour = (220, 50, 50) if self.is_anchor else (240, 240, 240)
        pygame.draw.circle(screen, colour, pos, 7)


class Beam:
    """Base class for all bridge building materials."""
    def __init__(self, world, node_a, node_b, max_stress, cost_per_m, base_colour):
        self.world = world
        self.node_a = node_a
        self.node_b = node_b
        self.max_stress = max_stress
        self.base_colour = base_colour
        self.broken = False
        self.stress_ratio = 0.0

        # Calculate length in metres for cost
        dist = (node_a.body.position - node_b.body.position).length
        self.cost = dist * cost_per_m

        # Create a Box2D DistanceJoint between the two nodes
        self.joint = world.CreateDistanceJoint(
            bodyA=node_a.body,
            bodyB=node_b.body,
            anchorA=node_a.body.position,
            anchorB=node_b.body.position,
            frequencyHz=15.0,  # Slight elasticity makes simulation stable
            dampingRatio=0.7
        )

    def update(self, dt):
        """Checks joint reaction force and breaks the beam if stress exceeds limit."""
        if self.broken or self.joint is None:
            return

        # GetReactionForce requires inverse timestep (1 / dt)
        force = self.joint.GetReactionForce(1.0 / dt).length
        self.stress_ratio = min(force / self.max_stress, 1.0)

        if force > self.max_stress:
            self.world.DestroyJoint(self.joint)
            self.joint = None
            self.broken = True

    def draw(self, screen):
        """Draws the beam, shifting colour toward red as stress increases."""
        if self.broken:
            return

        pos_a = world_to_screen(self.node_a.body.position)
        pos_b = world_to_screen(self.node_b.body.position)

        # Interpolate colour from base_colour to bright red based on stress_ratio
        r = int(self.base_colour[0] + (255 - self.base_colour[0]) * self.stress_ratio)
        g = int(self.base_colour[1] * (1 - self.stress_ratio))
        b = int(self.base_colour[2] * (1 - self.stress_ratio))

        pygame.draw.line(screen, (r, g, b), pos_a, pos_b, 6)


# --- INHERITANCE: SPECIFIC MATERIAL SUBCLASSES ---
class WoodBeam(Beam):
    def __init__(self, world, node_a, node_b):
        super().__init__(world, node_a, node_b, max_stress=250.0, cost_per_m=10.0, base_colour=(180, 120, 60))

class SteelBeam(Beam):
    def __init__(self, world, node_a, node_b):
        super().__init__(world, node_a, node_b, max_stress=800.0, cost_per_m=25.0, base_colour=(120, 160, 200))


# --- MAIN PROCEDURAL GAME LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("H446 Bridge Builder Prototype")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 22)

    # Setup physics world with standard Earth gravity
    world = b2World(gravity=(0, -9.81), doSleep=True)
    is_simulating = False

    # Create a simple test bridge (2 anchors, 1 free middle node)
    left_anchor = Node(world, 6.0, 10.0, is_anchor=True)
    mid_node = Node(world, 12.5, 10.0, is_anchor=False)
    right_anchor = Node(world, 19.0, 10.0, is_anchor=True)
    nodes = [left_anchor, mid_node, right_anchor]

    # Build using two different subclasses (Polymorphism in action)
    beams = [
        WoodBeam(world, left_anchor, mid_node),
        SteelBeam(world, mid_node, right_anchor)
    ]

    running = True
    while running:
        dt = 1.0 / FPS

        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                is_simulating = not is_simulating

        # 2. Physics & OOP Updates
        if is_simulating:
            world.Step(dt, velocityIterations=8, positionIterations=3)
            for beam in beams:
                beam.update(dt)

        # 3. Rendering
        screen.fill((30, 35, 45))
        
        for beam in beams:
            beam.draw(screen)
        for node in nodes:
            node.draw(screen)

        total_cost = sum(b.cost for b in beams)
        draw_hud(screen, font, is_simulating, total_cost)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()