# Author: Seth M. Fuller
# File: BlockFight.py
# Date: 11/27/2018

__docformat__ = "reStructuredText"

import sys, random
import os

description = """
---- Block File ----
A Cool Game
"""

is_interactive = False
display_flags = 0

### We must set OS env before the pygame imports..
import pygame
from pygame.locals import *
from pygame.color import *

display_size = (600, 600)

import pymunk as pm
from pymunk import Vec2d
import math

class PymunkSprite():
    def __init__(self, space, image, body, shape):
        self.body = body
        self.shape = shape
        self.imageMaster = pygame.image.load(image).convert()
        self.imageMaster.set_colorkey(self.imageMaster.get_at((0, 0)))
        space.add(body, shape)

    def flipy(self, y):
        """Small hack to convert chipmunk physics to pygame coordinates"""
        return -y + 600

    def update(self, screen):
        # image draw
        p = self.shape.body.position
        p = Vec2d(p.x, self.flipy(p.y))

        # we need to rotate 180 degrees because of the y coordinate flip
        angle_degrees = math.degrees(self.shape.body.angle) + 180
        rotated_logo_img = pygame.transform.rotate(self.imageMaster, angle_degrees)

        offset = Vec2d(rotated_logo_img.get_size()) / 2.
        p = p - offset

        screen.blit(rotated_logo_img, p)

        #Debug drawing
        ps = [p.rotated(self.shape.body.angle) + self.shape.body.position for p in self.shape.get_vertices()]
        ps = [(p.x, self.flipy(p.y)) for p in ps]
        ps += [ps[0]]
        pygame.draw.lines(screen, THECOLORS["red"], False, ps, 1)

def drawcircle(image, colour, origin, radius, width=0):
    if width == 0:
        pygame.draw.circle(image, colour, origin, int(radius))
    else:
        if radius > 65534 / 5:
            radius = 65534 / 5
        circle = pygame.Surface([radius * 2 + width, radius * 2 + width]).convert_alpha()
        circle.fill([0, 0, 0, 0])
        pygame.draw.circle(circle, colour, [circle.get_width() / 2, circle.get_height() / 2], radius + (width / 2))
        if int(radius - (width / 2)) > 0:
            pygame.draw.circle(circle, [0, 0, 0, 0], [circle.get_width() / 2, circle.get_height() / 2],
                               abs(int(radius - (width / 2))))
        image.blit(circle, [origin[0] - (circle.get_width() / 2), origin[1] - (circle.get_height() / 2)])


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
    font = pygame.font.Font(None, 16)

    ### Physics stuff
    space = pm.Space()
    space.gravity = (0.0, -1900.0)
    space.damping = 0.999  # to prevent it from blowing up.
    mouse_body = pm.Body(body_type=pm.Body.KINEMATIC)

    # Create bodies
    bodies = []
    offset_y = height / 2
    mass = 10
    radius = 25
    moment = pm.moment_for_circle(mass, 0, radius, (0, 0))

    # Create body
    body = pm.Body(mass, moment)
    body.position = (width/2, -125 + offset_y)
    body.start_position = Vec2d(body.position)

    # Create shape
    vs = [(-25, 50), (25, 50), (25, -50), (-25, -50)]
    shape = pm.Poly(body, vs)
    shape.elasticity = 0.9999999
    shape.color = THECOLORS["green"]

    # Create joint
    pj = pm.PinJoint(space.static_body, body, (width/2, 125 + offset_y), (0, 0))

    # Add objects to space
    sprite = PymunkSprite(space, "../assets/img/bodyBox.png", body, shape)
    space.add(pj)

    bodies.append(body)

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



        ### Clear screen
        screen.fill(THECOLORS["white"])

        ### Draw stuff
        for c in space.constraints:
            pv1 = c.a.position + c.anchor_a
            pv2 = c.b.position + c.anchor_b
            p1 = to_pygame(pv1)
            p2 = to_pygame(pv2)
            pygame.draw.aalines(screen, THECOLORS["lightgray"], False, [p1, p2])

        for box in space.shapes:
            p = to_pygame(box.body.position)
            sprite.update(screen)
            #drawcircle(screen, box.color, p, int(box.radius), 0)
            # pygame.draw.circle(screen, ball.color, p, int(ball.radius), 0)

        ### Update physics
        fps = 50
        iterations = 25
        dt = 1.0 / float(fps) / float(iterations)
        for x in range(iterations):  # 10 iterations to get a more stable simulation
            space.step(dt)

        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    sys.exit(main())