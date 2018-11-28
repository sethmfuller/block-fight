# Author: Seth M. Fuller
# File: BlockFight.py
# Date: 11/27/2018

import sys
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import Character


__docformat__ = "reStructuredText"
description = """
---- Block File ----
A Cool Game
"""


is_interactive = False
display_flags = 0
display_size = (600, 600)


def main():
    pygame.init()
    screen = pygame.display.set_mode(display_size, display_flags)
    width, height = screen.get_size()

    def to_pygame(p):
        """Small hack to convert pymunk to pygame coordinates"""
        return int(p.x), int(-p.y + height)

    def from_pygame(p):
        return to_pygame(p)

    clock = pygame.time.Clock()
    running = True

    # Physics stuff
    space = pm.Space()
    space.gravity = (0.0, -1900.0)
    space.damping = 0.999  # to prevent it from blowing up.
    mouse_body = pm.Body(body_type=pm.Body.KINEMATIC)

    # Add objects to space
    sprite = Character.Body(space, screen)
    sprite.body.position = (50,50)

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == KEYDOWN and event.key == K_f:
                sprite.body.apply_impulse_at_local_point(Vec2d.unit() * 40000, (-100, 0))

        mpos = pygame.mouse.get_pos()
        p = from_pygame(Vec2d(mpos))
        mouse_body.position = p

        floor = pm.Segment(space.static_body, (0, 0), (width, 0), 0.0)
        floor.friction = 0.5
        space.add(floor)

        # Clear screen
        screen.fill(THECOLORS["white"])

        # Draw stuff
        for c in space.constraints:
            pv1 = c.a.position + c.anchor_a
            pv2 = c.b.position + c.anchor_b
            p1 = to_pygame(pv1)
            p2 = to_pygame(pv2)
            pygame.draw.aalines(screen, THECOLORS["lightgray"], False, [p1, p2])

        for box in space.shapes:
            sprite.update()

        # Update physics
        fps = 50
        iterations = 25
        dt = 1.0 / float(fps) / float(iterations)
        for x in range(iterations):  # 10 iterations to get a more stable simulation
            space.step(dt)

        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    sys.exit(main())
