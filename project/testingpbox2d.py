from Box2D import b2World, b2PolygonShape

# Create physics world
world = b2World(gravity=(0, -9.81), doSleep=True)

# Static ground (half-extents: 10 wide each way, 1 tall each way)
ground = world.CreateStaticBody(
    position=(0, -5),
    shapes=b2PolygonShape(box=(10, 1)),
)

# Dynamic bodies
bodies = []
for x in range(-5, 5):
    body = world.CreateDynamicBody(position=(x, 5))
    body.CreatePolygonFixture(box=(0.5, 0.5), density=1.0, friction=0.3)
    bodies.append(body)

# Simulation loop
for step in range(60):
    world.Step(1 / 60, 6, 2)  # dt, velocity iterations, position iterations

# Check results
for b in bodies:
    print(f"{b.position.x:.2f}, {b.position.y:.2f}")