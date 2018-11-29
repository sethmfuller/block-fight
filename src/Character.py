# Author: Christopher Ash

import pygame
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import math

COLLISION_BODY = 0
COLLISION_OFFENSE = 1
COLLISION_DEFENSE = 2

collisionGroups = {
    "PLAYER1": 0b01,
    "PLAYER2": 0b10
}


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
        self.shape.collision_type = COLLISION_BODY


class OffensiveBlock(PymunkSprite):
    def __init__(self, space, screen):
        vs = [(-25, 25), (25, 25), (25, -25), (-25, -25)]
        mass = 10
        moment = pm.moment_for_poly(mass, vs)
        body = pm.Body(mass, moment)
        shape = pm.Poly(body, vs)
        PymunkSprite.__init__(self, space, screen, "../assets/img/hitBox.png", shape)
        self.shape.collision_type = COLLISION_OFFENSE


class DefensiveBlock(PymunkSprite):
    def __init__(self, space, screen):
        vs = [(-20, 20), (20, 20), (20, -20), (-20, -20)]
        mass = 10
        moment = pm.moment_for_poly(mass, vs)
        body = pm.Body(mass, moment)
        shape = pm.Poly(body, vs)
        PymunkSprite.__init__(self, space, screen, "../assets/img/defBox.png", shape)
        self.shape.collision_type = COLLISION_DEFENSE


class PlayerOne():
    def __init__(self, space, screen):
        self.space = space
        self.screen = screen
        pos = (100, 200)
        self.coreBody = pm.Body(10, 1000)
        self.coreBody.position = pos

        self.torso = Body(space, screen)
        self.torso.shape.filter = pm.ShapeFilter(collisionGroups["PLAYER1"], collisionGroups["PLAYER2"])
        self.torsoRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.torso.shape.body, -math.pi / 10,
                                                      math.pi / 10)
        self.torsoLocationTie = pm.PinJoint(self.coreBody, self.torso.shape.body)
        self.torsoLocationTie.distance = 0
        self.torso.shape.body.position = pos
        self.torso.shape.body.apply_impulse_at_local_point(Vec2d.unit() * 10000, (10, -10))

        self.rFoot = OffensiveBlock(self.space, self.screen)
        self.rFoot.shape.friction = 1.5
        self.rFoot.shape.filter = pm.ShapeFilter(collisionGroups["PLAYER1"], collisionGroups["PLAYER2"])
        self.rFoot.shape.body.position = self.torso.shape.body.position + (-25, -100)
        self.rLeg = pm.PinJoint(self.torso.shape.body, self.rFoot.shape.body, (0, -50), (0, 25))
        self.rLegDownwardForce = pm.DampedSpring(self.coreBody, self.rFoot.shape.body, (0, 0), (0, 25), 125, 1000, 1)
        self.rFootRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.rFoot.shape.body, -math.pi/5, math.pi/5)

        self.lFoot = OffensiveBlock(self.space, self.screen)
        self.lFoot.shape.friction = 1.5
        self.lFoot.shape.filter = pm.ShapeFilter(collisionGroups["PLAYER1"], collisionGroups["PLAYER2"])
        self.lFoot.shape.body.position = self.torso.shape.body.position + (25, -100)
        self.lLeg = pm.PinJoint(self.torso.shape.body, self.lFoot.shape.body, (0, -50), (0, 25))
        self.lLegDownwardForce = pm.DampedSpring(self.coreBody, self.lFoot.shape.body, (0, 0), (0, 25), 125, 1000, 1)
        self.lFootRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.lFoot.shape.body, -math.pi/5, math.pi/5)

        self.space.add(self.coreBody, self.torsoRotationLimit, self.torsoLocationTie, self.rLeg, self.rLegDownwardForce,
                       self.lLeg, self.lLegDownwardForce, self.rFootRotationLimit, self.lFootRotationLimit)

    def update(self):
        self.torso.update()
        self.rFoot.update()
        self.lFoot.update()

    def kickRFoot(self):
        self.rFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (math.sqrt(2)/2, math.sqrt(2)/2)) * 10000, (0, 0))

    def reverseKickRFoot(self):
        self.rFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (-math.sqrt(2) / 2, math.sqrt(2) / 2)) * 10000, (0, 0))
