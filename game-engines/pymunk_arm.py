"""
Use Pymunk physics engine.

For more info on Pymunk see:
https://www.pymunk.org/en/latest/

To install pymunk:
pip install pymunk

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.pymunk_box_stacks

Click and drag with the mouse to move the boxes.
"""

import arcade
import pymunk
import timeit
import math

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Pymunk test"


class PhysicsSprite(arcade.Sprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(filename, center_x=pymunk_shape.body.position.x, center_y=pymunk_shape.body.position.y)
        self.pymunk_shape = pymunk_shape


class CircleSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(pymunk_shape, filename)
        self.width = pymunk_shape.radius * 2
        self.height = pymunk_shape.radius * 2


class BoxSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename, width, height):
        super().__init__(pymunk_shape, filename)
        self.width = width
        self.height = height

class Simulation(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # -- Pymunk
        self.space = pymunk.Space()
        self.space.iterations = 350
        self.space.gravity = (0.0, -9800.0)

        # Lists of sprites or lines
        self.sprite_list: arcade.SpriteList[PhysicsSprite] = arcade.SpriteList()
        self.static_lines = []

        # Used for dragging shapes around with the mouse
        self.shape_being_dragged = None
        self.last_mouse_position = 0, 0

        self.draw_time = 0
        self.processing_time = 0

        # Create the floor
        floor_height = 80
        aftarm_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(aftarm_body, [0, floor_height], [SCREEN_WIDTH, floor_height], 0.0)
        shape.friction = 10
        self.space.add(shape, aftarm_body)
        self.static_lines.append(shape)

        # Add the Anchor Box
        size = 8
        x = SCREEN_WIDTH/2
        y = SCREEN_HEIGHT * 0.3
        anchor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        anchor_body.position = pymunk.Vec2d(x-256, y)
        anchor_shape = pymunk.Poly.create_box(anchor_body, (size, size))
        self.space.add(anchor_body, anchor_shape)

        # Add the Aft Arm segment.
        aftarm_x = SCREEN_WIDTH/2+120
        aftarm_y = y
        arm_length=256
        arm_width=32
        mass = 1.0
        moment = pymunk.moment_for_box(mass, (arm_length, arm_width))
        aftarm_body = pymunk.Body(mass, moment)
        aftarm_body.position = pymunk.Vec2d(aftarm_x, aftarm_y)
        aa_shape = pymunk.Poly.create_box(aftarm_body, [arm_length, arm_width])
        aa_shape.elasticity = 0.05
        aa_shape.friction = 0.9
        self.space.add(aftarm_body, aa_shape)

        aa_sprite = BoxSprite(aa_shape, ":resources:images/tiles/boxCrate_double.png", width=arm_length, height=arm_width)
        self.sprite_list.append(aa_sprite)

        # Add the Aft Arm segment.
        forearm_x = SCREEN_WIDTH/2 + 372
        forearm_y = y
        arm_length=256
        arm_width=32
        mass = 1.0
        moment = pymunk.moment_for_box(mass, (arm_length, arm_width))
        forearm_body = pymunk.Body(mass, moment)
        forearm_body.position = pymunk.Vec2d(forearm_x, forearm_y)
        fa_shape = pymunk.Poly.create_box(forearm_body, [arm_length, arm_width])
        fa_shape.elasticity = 0.05
        fa_shape.friction = 0.9
        self.space.add(forearm_body, fa_shape)

        fa_sprite = BoxSprite(fa_shape, ":resources:images/tiles/boxCrate_double.png", width=arm_length, height=arm_width)
        self.sprite_list.append(fa_sprite)

        # Link the arm to the anchor.
        pj1 = pymunk.PivotJoint(anchor_body , aftarm_body, 
                pymunk.Vec2d(aftarm_x - 120 , aftarm_y),
                )
        # The hidden Anchor point shouldn't interact with the arm
        pj1.collide_bodies = False
        self.space.add(pj1)

        # Link the aft and fore-arms 
        pj2 = pymunk.PivotJoint(aftarm_body, forearm_body,
                pymunk.Vec2d(forearm_x - 120,forearm_y),
                )

        # The hidden Anchor point shouldn't interact with the arm
        pj2.collide_bodies = False
        self.space.add(pj2)

        pj2s = pymunk.DampedRotarySpring(aftarm_body, forearm_body,
                -1.5, 1000000, 50000
                )
        pj2s.activate_bodies()
        self.space.add(pj2s)

        aftarm_limit = pymunk.RotaryLimitJoint(anchor_body, aftarm_body, 0, math.pi)
        self.space.add(aftarm_limit)

        forearm_limit = pymunk.RotaryLimitJoint(aftarm_body, forearm_body, -math.pi, math.pi)
        self.space.add(forearm_limit)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # Draw all the sprites
        self.sprite_list.draw()

        # Draw the lines that aren't sprites
        for line in self.static_lines:
            body = line.body

            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            arcade.draw_line(pv1.x, pv1.y, pv2.x, pv2.y, arcade.color.WHITE, 2)

        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE, 12)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 12)

        self.draw_time = timeit.default_timer() - draw_start_time

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.last_mouse_position = x, y
            # See if we clicked on anything
            shape_list = self.space.point_query((x, y), 1, pymunk.ShapeFilter())

            # If we did, remember what we clicked on
            if len(shape_list) > 0:
                self.shape_being_dragged = shape_list[0]

        elif button == arcade.MOUSE_BUTTON_RIGHT:
            # With right mouse button, shoot a heavy coin fast.
            mass = 60
            radius = 10
            inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
            body = pymunk.Body(mass, inertia)
            body.position = x, y
            body.velocity = 2000, 0
            shape = pymunk.Circle(body, radius, pymunk.Vec2d(0, 0))
            shape.friction = 0.3
            self.space.add(body, shape)

            sprite = CircleSprite(shape, ":resources:images/items/coinGold.png")
            self.sprite_list.append(sprite)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Release the item we are holding (if any)
            self.shape_being_dragged = None

    def on_mouse_motion(self, x, y, dx, dy):
        if self.shape_being_dragged is not None:
            # If we are holding an object, move it with the mouse
            self.last_mouse_position = x, y
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = dx * 20, dy * 20

    def on_update(self, delta_time):
        start_time = timeit.default_timer()

        # Check for balls that fall off the screen
        for sprite in self.sprite_list:
            if sprite.pymunk_shape.body.position.y < 0:
                # Remove balls from physics space
                self.space.remove(sprite.pymunk_shape, sprite.pymunk_shape.body)
                # Remove balls from physics list
                sprite.remove_from_sprite_lists()

        # Update physics
        # Use a constant time step, don't use delta_time
        # See "Game loop / moving time forward"
        # https://www.pymunk.org/en/latest/overview.html#game-loop-moving-time-forward
        self.space.step(1 / 60.0)

        # If we are dragging an object, make sure it stays with the mouse. Otherwise
        # gravity will drag it down.
        if self.shape_being_dragged is not None:
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = 0, 0

        # Move sprites to where physics objects are
        for sprite in self.sprite_list:
            sprite.center_x = sprite.pymunk_shape.body.position.x
            sprite.center_y = sprite.pymunk_shape.body.position.y
            sprite.angle = math.degrees(sprite.pymunk_shape.body.angle)

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time


def main():
    Simulation(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    arcade.run()


if __name__ == "__main__":
    main()