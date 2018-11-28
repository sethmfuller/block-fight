import math
import pygame
import pymunk
from pymunk import Vec2d


class PymunkSprite(pymunk.Body):
    def __init__(self, image, mass, moment):
        pymunk.Body.__init__(self, mass, moment)
        self.imageMaster = pygame.image.load(image).convert()
        self.imageMaster.set_colorkey(self.imageMaster.get_at((0, 0)))

    def flipy(self, y):
        """Small hack to convert chipmunk physics to pygame coordinates"""
        return -y + 600

    def update(self, screen):
        # image draw
        p = self.position
        p = Vec2d(p.x, self.flipy(p.y))

        # we need to rotate 180 degrees because of the y coordinate flip
        angle_degrees = math.degrees(self.angle) + 180
        rotated_logo_img = pygame.transform.rotate(self.imageMaster, angle_degrees)

        offset = Vec2d(rotated_logo_img.get_size()) / 2.
        p = p - offset

        screen.blit(rotated_logo_img, p)