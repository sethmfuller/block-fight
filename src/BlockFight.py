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
ENDGAME_EVENT = pygame.USEREVENT + 3

# Movable Text Sprite
class Text(pygame.sprite.Sprite):
    def __init__(self, scene, text, textColor, width, height, fontSize=30):
        pygame.sprite.Sprite.__init__(self)
        self.scene = scene
        self.font = pygame.font.SysFont("", fontSize)
        self.text = text
        self.textColor = textColor
        self.size = (width, height)
        self.x = 0
        self.y = 0

    def setText(self, text):
        self.text = text

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def setDimensions(self, width, height):
        self.size = (width, height)

    def update(self):
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(self.image.get_at((0, 0)))
        fontSurface = self.font.render(self.text, True, self.textColor)
        xPos = (self.image.get_width() - fontSurface.get_width()) / 2
        self.image.blit(fontSurface, (xPos, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.scene.blit(fontSurface, (self.x, self.y))

def main():
    pygame.init()
    screen = pygame.display.set_mode(display_size, display_flags)
    pygame.display.set_caption("Mace Ragdoll Fight")

    width, height = screen.get_size()

    def to_pygame(p):
        """Small hack to convert pymunk to pygame coordinates"""
        return int(p.x), int(-p.y + height)

    def from_pygame(p):
        return to_pygame(p)

    clock = pygame.time.Clock()
    keepGoing = True

    # Physics stuff
    space = pm.Space()
    space.gravity = (0.0, -1900.0)
    space.damping = 0.999  # to prevent it from blowing up.

    # Add objects to space
    playerOne = Character.PlayerOne(space, screen)
    playerTwo = Character.PlayerTwo(space, screen)
    playerOneVictoryText = Text(screen, "Player 1 Wins!", (0, 0, 0), 500, 100, 100)
    playerOneVictoryText.setPosition(-1000, -1000)
    playerTwoVictoryText = Text(screen, "Player 2 Wins!", (0, 0, 0), 500, 100, 100)
    playerTwoVictoryText.setPosition(-1000, -1000)

    floor = pm.Segment(space.static_body, (0, 0), (width, 0), 0.5)
    floor.friction = 0.5

    leftWall = pm.Segment(space.static_body, (0, 0), (0, height), 0.5)
    leftWall.friction = 0.5

    roof = pm.Segment(space.static_body, (0, height), (width, height), 0.5)
    roof.friction = 0.5

    rightWall = pm.Segment(space.static_body, (width, 0), (width, height), 0.5)
    rightWall.friction = 0.5

    space.add(floor, leftWall, roof, rightWall)

    # Play Game music
    pygame.mixer.music.load('../assets/sound/ThisIsWhoWeAre.mp3')
    pygame.mixer.music.play(-1)
    continuePlaying = True

    while keepGoing:

        for event in pygame.event.get():
            if event.type == QUIT:
                keepGoing = False
                continuePlaying = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                keepGoing = False
                continuePlaying = False
            elif event.type == Character.PLAYERONE_VICTOR:
                playerOneVictoryText.setPosition(width/3, height/2)
                pygame.time.set_timer(ENDGAME_EVENT, 2500)
            elif event.type == Character.PLAYERTWO_VICTOR:
                playerTwoVictoryText.setPosition(width/3, height/2)
                pygame.time.set_timer(ENDGAME_EVENT, 2500)
            elif event.type == ENDGAME_EVENT:
                pygame.time.set_timer(ENDGAME_EVENT, 0)
                keepGoing = False

            # Player one controls
            elif event.type == KEYDOWN and event.key == K_f:
                playerOne.kickRFoot()
            elif event.type == KEYDOWN and event.key == K_d:
                playerOne.reverseKickRFoot()
            elif event.type == KEYDOWN and event.key == K_r:
                playerOne.kickLFoot()
            elif event.type == KEYDOWN and event.key == K_e:
                playerOne.reverseKickLFoot()
            elif event.type == KEYDOWN and event.key == K_v:
                playerOne.punchRight()
            elif event.type == KEYDOWN and event.key == K_c:
                playerOne.reversePunchRight()
            elif event.type == KEYDOWN and event.key == K_x:
                playerOne.punchLeft()
            elif event.type == KEYDOWN and event.key == K_z:
                playerOne.reversePunchLeft()

            # Player two controls
            elif event.type == KEYDOWN and event.key == K_j:
                playerTwo.kickRFoot()
            elif event.type == KEYDOWN and event.key == K_k:
                playerTwo.reverseKickRFoot()
            elif event.type == KEYDOWN and event.key == K_u:
                playerTwo.kickLFoot()
            elif event.type == KEYDOWN and event.key == K_i:
                playerTwo.reverseKickLFoot()
            elif event.type == KEYDOWN and event.key == K_n:
                playerTwo.punchRight()
            elif event.type == KEYDOWN and event.key == K_m:
                playerTwo.reversePunchRight()
            elif event.type == KEYDOWN and event.key == K_COMMA:
                playerTwo.punchLeft()
            elif event.type == KEYDOWN and event.key == K_PERIOD:
                playerTwo.reversePunchLeft()

        # Clear screen
        screen.fill(THECOLORS["white"])

        playerOne.update()
        playerTwo.update()
        playerOneVictoryText.update()
        playerTwoVictoryText.update()

        for constraint in space.constraints:
            if (isinstance(constraint, pm.PinJoint)):
                pv1 = constraint.a.position + constraint.anchor_a
                pv2 = constraint.b.position + constraint.anchor_b
                p1 = to_pygame(pv1)
                p2 = to_pygame(pv2)
                pygame.draw.aalines(screen, THECOLORS["lightgray"], False, [p1, p2])

        # Update physics
        fps = 50
        iterations = 25
        dt = 1.0 / float(fps) / float(iterations)
        for x in range(iterations):  # 10 iterations to get a more stable simulation
            space.step(dt)

        pygame.display.flip()
        clock.tick(fps)
    return continuePlaying


if __name__ == '__main__':
    while (main()):
        pass
