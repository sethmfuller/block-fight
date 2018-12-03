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
display_size = (800, 800)


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

    # Add objects to space
    playerOne = Character.PlayerOne(space, screen)
    playerTwo = Character.PlayerTwo(space, screen)

    floor = pm.Segment(space.static_body, (0, 0), (width, 0), 0.5)
    floor.friction = 0.5

    leftWall = pm.Segment(space.static_body, (0, 0), (0, height), 0.5)
    leftWall.friction = 0.5

    roof = pm.Segment(space.static_body, (0, height), (width, height), 0.5)
    roof.friction = 0.5

    rightWall = pm.Segment(space.static_body, (width, 0), (width, height), 0.5)
    rightWall.friction = 0.5

    space.add(floor, leftWall, roof, rightWall)

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            #Player one controls
            elif event.type == KEYDOWN and event.key == K_f:
                playerOne.kickRFoot()
            elif event.type == KEYDOWN and event.key == K_d:
                playerOne.reverseKickRFoot()
            elif event.type == KEYDOWN and event.key == K_r:
                playerOne.kickLFoot()
            elif event.type == KEYDOWN and event.key == K_e:
                playerOne.reverseKickLFoot()
            #Player two controls
            elif event.type == KEYDOWN and event.key == K_j:
                playerTwo.kickRFoot()
            elif event.type == KEYDOWN and event.key == K_k:
                playerTwo.reverseKickRFoot()
            elif event.type == KEYDOWN and event.key == K_u:
                playerTwo.kickLFoot()
            elif event.type == KEYDOWN and event.key == K_i:
                playerTwo.reverseKickLFoot()

        # Clear screen
        screen.fill(THECOLORS["white"])

        playerOne.update()
        playerTwo.update()

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
