# Author: Christopher Ash

import pygame
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import math


class PymunkSprite():
    def __init__(self, space, screen, image, shape):
        self.shape = shape
        self.screen = screen
        self.imageMaster = pygame.image.load(image).convert()
        self.imageMaster.set_colorkey(self.imageMaster.get_at((0, 0)))
        space.add(shape.body, shape)

    def flipy(self, y):
        """Small hack to convert chipmunk physics to pygame coordinates"""
        return -y + self.screen.get_width()

    def update(self):
        # image draw
        p = self.shape.body.position
        p = Vec2d(p.x, self.flipy(p.y))

        # we need to rotate 180 degrees because of the y coordinate flip
        angle_degrees = math.degrees(self.shape.body.angle) + 180
        rotated_logo_img = pygame.transform.rotate(self.imageMaster, angle_degrees)

        offset = Vec2d(rotated_logo_img.get_size()) / 2.
        p = p - offset

        self.screen.blit(rotated_logo_img, p)

        # Debug drawing
        ps = [p.rotated(self.shape.body.angle) + self.shape.body.position for p in self.shape.get_vertices()]
        ps = [(p.x, self.flipy(p.y)) for p in ps]
        ps += [ps[0]]
        pygame.draw.lines(self.screen, THECOLORS["red"], False, ps, 1)


class Body(PymunkSprite):
    def __init__(self, space, screen):
        vs = [(-25, 50), (25, 50), (25, -50), (-25, -50)]
        mass = 10
        moment = pm.moment_for_poly(mass, vs)
        body = pm.Body(mass, moment)
        shape = pm.Poly(body, vs)
        PymunkSprite.__init__(self, space, screen, "../assets/img/bodyBox.png", shape)
        self.imageMaster.set_colorkey((0, 0, 0))
        self.armConnection = pm.Body(mass, moment)
        self.legConnection = pm.Body(mass, moment)
        space.add(self.armConnection, self.legConnection)


class OffensiveBlock(PymunkSprite):
    def __init__(self, space, screen):
        vs = [(-25, 25), (25, 25), (25, -25), (-25, -25)]
        mass = 10
        moment = pm.moment_for_poly(mass, vs)
        body = pm.Body(mass, moment)
        shape = pm.Poly(body, vs)
        PymunkSprite.__init__(self, space, screen, "../assets/img/hitBox.png", shape)


class DefensiveBlock(PymunkSprite):
    def __init__(self, space, screen):
        vs = [(-20, 20), (20, 20), (20, -20), (-20, -20)]
        mass = 10
        moment = pm.moment_for_poly(mass, vs)
        body = pm.Body(mass, moment)
        shape = pm.Poly(body, vs)
        PymunkSprite.__init__(self, space, screen, "../assets/img/defBox.png", shape)


class Skeleton():
    def __init__(self, space, screen, x=0, y=0):
        self.body = pm.Body(10, 1000)
        self.torso = Body(space, screen)
        self.setPosition(x, y)
        self.space = space
        self.screen = screen

        self.head = DefensiveBlock(space, screen)
        self.head.shape.body.position = self.torso.shape.body.position + (0, 100)

        self.neck = pm.PinJoint(self.torso.shape.body, self.head.shape.body, (0, 50), (0, 25))
        self.neck.distance = 50

        self.fist = OffensiveBlock(space, screen)
        self.fist.shape.body.position.x = self.torso.shape.body.position.x + 50
        self.fist.shape.body.position.y = self.torso.shape.body.position.y + 50
        self.arm = pm.PinJoint(self.fist.shape.body, self.torso.shape.body, (0, 0), (0, 50))
        self.arm.distance = 50

        self.foot = OffensiveBlock(space, screen)
        self.foot.shape.body.position = self.torso.shape.body.position + (0, -50)
        self.leg = pm.PinJoint(self.foot.shape.body, self.torso.shape.body, (0, 25), (0, -50))
        self.leg.distance = 50

        self.components = [
            self.torso,
            self.head,
            self.fist,
            self.foot
        ]

        for component in self.components:
            component.group = 1

        space.add(self.neck, self.arm, self.leg)

    def setPosition(self, x, y):
        self.torso.shape.body.position = (x, y)

    def update(self):
        for component in self.components:
            component.update()
