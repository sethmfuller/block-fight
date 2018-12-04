# Author: Christopher Ash
# File: Character.py
# Collision Handling: Austin Bearden, Seth Fuller
# Images and Sound: Seth Fuller


import pygame
import pymunk as pm
from pymunk import Vec2d
import math

COLLISION_BODY = 1
COLLISION_OFFENSE = 2
COLLISION_DEFENSE = 3

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


class BodyShape(pm.Poly):
    def __init__(self, space, body, points):
        pm.Poly.__init__(self, body, points)
        self.health = 1
        self.collision_type = COLLISION_BODY
        # We get a collision handler representation.
        handler = space.add_collision_handler(COLLISION_BODY, COLLISION_OFFENSE)

        # Then we set the collision handler's methods to what we want.
        handler.begin = self.collisionAction

    def collisionAction(self, arbiter, space, data):
        if (arbiter.is_first_contact):
            a, b = arbiter.shapes
            a.health = a.health - 1

            print("Health value: ", a.health)

            return True


class Body(PymunkSprite):
    def __init__(self, space, screen):
        vs = [(-25, 50), (25, 50), (25, -50), (-25, -50)]
        mass = 10
        moment = pm.moment_for_poly(mass, vs)
        body = pm.Body(mass, moment)
        shape = BodyShape(space, body, vs)
        PymunkSprite.__init__(self, space, screen, "../assets/img/bodyBox.png", shape)
        self.imageMaster.set_colorkey((0, 0, 0))


class OffensiveBlock(PymunkSprite):
    def __init__(self, space, screen):
        vs = [(-25, 25), (25, 25), (25, -25), (-25, -25)]
        mass = 10
        moment = pm.moment_for_poly(mass, vs)
        body = pm.Body(mass, moment)
        shape = pm.Poly(body, vs)
        PymunkSprite.__init__(self, space, screen, "../assets/img/hitBox.png", shape)
        self.shape.collision_type = COLLISION_OFFENSE


class DefenseShape(pm.Poly):
    def __init__(self, space, body, points):
        pm.Poly.__init__(self, body, points)
        self.health = 1
        self.collision_type = COLLISION_DEFENSE
        # We get a collision handler representation.
        handler = space.add_collision_handler(COLLISION_DEFENSE, COLLISION_OFFENSE)

        # Then we set the collision handler's methods to what we want.
        handler.begin = self.collisionAction

    def collisionAction(self, arbiter, space, data):
        if (arbiter.is_first_contact):
            a, b = arbiter.shapes
            a.health = a.health - 1

            print("Health value: ", a.health)

            return True


class DefensiveBlock(PymunkSprite):
    def __init__(self, space, screen):
        vs = [(-20, 20), (20, 20), (20, -20), (-20, -20)]
        mass = 10
        moment = pm.moment_for_poly(mass, vs)
        body = pm.Body(mass, moment)
        shape = DefenseShape(space, body, vs)
        PymunkSprite.__init__(self, space, screen, "../assets/img/defBox.png", shape)


class PlayerOne():
    def __init__(self, space, screen):
        self.space = space
        self.screen = screen
        width, height = screen.get_size()
        pos = (width / 4, height / 4)
        shapeFilter = pm.ShapeFilter(collisionGroups["PLAYER1"], collisionGroups["PLAYER2"])
        self.coreBody = pm.Body(10, 1000)
        self.coreBody.position = pos

        self.rightArmAlive = True
        self.leftArmAlive = True
        self.rightLegAlive = True
        self.leftLegAlive = True

        self.torso = Body(space, screen)
        self.torso.shape.filter = shapeFilter
        self.torsoRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.torso.shape.body, -math.pi / 10,
                                                      math.pi / 10)
        self.torsoLocationTie = pm.PinJoint(self.coreBody, self.torso.shape.body)
        self.torsoLocationTie.distance = 0
        self.torso.shape.body.position = pos

        # Set up arms
        self.rElbow = DefensiveBlock(self.space, self.screen)
        self.rElbow.shape.body.position = self.torso.shape.body.position + (-50, 35)
        self.rElbow.shape.filter = shapeFilter

        self.rUpperArm = pm.PinJoint(self.torso.shape.body, self.rElbow.shape.body, (0, 35), (0, 0))
        self.rUpperArm.distance = 40

        self.rFist = OffensiveBlock(self.space, self.screen)
        self.rFist.shape.filter = shapeFilter
        self.rFist.shape.body.position = self.rElbow.shape.body.position + (-25, 0)
        self.rFistRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.rFist.shape.body, -math.pi / 5,
                                                      math.pi / 5)

        self.rLowerArm = pm.PinJoint(self.rElbow.shape.body, self.rFist.shape.body)
        self.rLowerArm.distance = 50

        self.lElbow = DefensiveBlock(self.space, self.screen)
        self.lElbow.shape.body.position = self.torso.shape.body.position + (50, 35)
        self.lElbow.shape.filter = shapeFilter
        self.lUpperArm = pm.PinJoint(self.torso.shape.body, self.lElbow.shape.body, (0, 35), (0, 0))
        self.lUpperArm.distance = 40

        self.lFist = OffensiveBlock(self.space, self.screen)
        self.lFist.shape.filter = shapeFilter
        self.lFist.shape.body.position = self.lElbow.shape.body.position + (25, 0)
        self.lFistRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.lFist.shape.body, -math.pi / 5,
                                                      math.pi / 5)

        self.lLowerArm = pm.PinJoint(self.lElbow.shape.body, self.lFist.shape.body)
        self.lLowerArm.distance = 50

        # Set up legs
        self.rKnee = DefensiveBlock(self.space, self.screen)
        self.rKnee.shape.body.position = self.torso.shape.body.position + (-25, -100)
        self.rKnee.shape.filter = shapeFilter

        self.rUpperLeg = pm.PinJoint(self.torso.shape.body, self.rKnee.shape.body, (0, -50), (0, 0))
        self.rUpperLeg.distance = 40

        self.rFoot = OffensiveBlock(self.space, self.screen)
        self.rFoot.shape.friction = 1.5
        self.rFoot.shape.filter = shapeFilter
        self.rFoot.shape.body.position = self.rKnee.shape.body.position + (-25, -10)
        self.rFootRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.rFoot.shape.body, -math.pi / 5,
                                                      math.pi / 5)

        self.rLowerLeg = pm.PinJoint(self.rKnee.shape.body, self.rFoot.shape.body, (0, 0), (0, 25))
        self.rLowerLeg.distance = 50

        self.lKnee = DefensiveBlock(self.space, self.screen)
        self.lKnee.shape.body.position = self.torso.shape.body.position + (25, -100)
        self.lKnee.shape.filter = shapeFilter

        self.lUpperLeg = pm.PinJoint(self.torso.shape.body, self.lKnee.shape.body, (0, -50), (0, 0))
        self.lUpperLeg.distance = 40

        self.lFoot = OffensiveBlock(self.space, self.screen)
        self.lFoot.shape.friction = 1.5
        self.lFoot.shape.filter = shapeFilter
        self.lFoot.shape.body.position = self.lKnee.shape.body.position + (25, -10)
        self.lFootRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.lFoot.shape.body, -math.pi / 5,
                                                      math.pi / 5)

        self.lLowerLeg = pm.PinJoint(self.lKnee.shape.body, self.lFoot.shape.body, (0, 0), (0, 25))
        self.lLowerLeg.distance = 50

        self.rLegDownwardForce = pm.DampedSpring(self.coreBody, self.rFoot.shape.body, (0, 0), (0, 25), 300, 1250, 1)
        self.lLegDownwardForce = pm.DampedSpring(self.coreBody, self.lFoot.shape.body, (0, 0), (0, 25), 300, 1250, 1)

        self.space.add(self.coreBody, self.torsoRotationLimit, self.torsoLocationTie,
                       self.rUpperLeg, self.rLegDownwardForce, self.lUpperLeg, self.lLegDownwardForce,
                       self.rFootRotationLimit, self.lFootRotationLimit,
                       self.rFistRotationLimit, self.lFistRotationLimit,
                       self.lLowerLeg, self.rLowerLeg,
                       self.rUpperArm, self.rLowerArm,
                       self.lUpperArm, self.lLowerArm)

    def checkForDeath(self):
        if self.rightLegAlive:
            if self.rKnee.shape.health <= 0:
                self.rightLegAlive = False
                self.space.remove(
                    self.rKnee.shape.body,
                    self.rKnee.shape,
                    self.rUpperLeg,
                    self.rLowerLeg,
                    self.rLegDownwardForce,
                    self.rFootRotationLimit,
                    self.rFoot.shape.body,
                    self.rFoot.shape
                )

        if self.leftLegAlive:
            if self.lKnee.shape.health <= 0:
                self.leftLegAlive = False
                self.space.remove(
                    self.lKnee.shape.body,
                    self.lKnee.shape,
                    self.lUpperLeg,
                    self.lLowerLeg,
                    self.lFootRotationLimit,
                    self.lLegDownwardForce,
                    self.lFoot.shape.body,
                    self.lFoot.shape
                )

        if self.rightArmAlive:
            if self.rElbow.shape.health <= 0:
                self.rightArmAlive = False
                self.space.remove(
                    self.rFist.shape.body, self.rFist.shape,
                    self.rFistRotationLimit,
                    self.rElbow.shape.body, self.rElbow.shape,
                    self.rUpperArm,
                    self.rLowerArm
                )

        if self.leftArmAlive:
            if self.lElbow.shape.health <= 0:
                self.leftArmAlive = False
                self.space.remove(
                    self.lFist.shape, self.lFist.shape.body,
                    self.lFistRotationLimit,
                    self.lElbow.shape, self.lElbow.shape.body,
                    self.lUpperArm, self.lLowerArm
                )

    def update(self):
        self.checkForDeath()
        if self.leftArmAlive:
            self.lElbow.update()
            self.lFist.update()

        self.torso.update()

        if self.rightArmAlive:
            self.rElbow.update()
            self.rFist.update()

        if self.rightLegAlive:
            self.rFoot.update()
            self.rKnee.update()

        if self.leftLegAlive:
            self.lFoot.update()
            self.lKnee.update()

    def kickRFoot(self):
        self.rFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (1, math.sqrt(2) / 2)) * 25000, (0, 0))

    def reverseKickRFoot(self):
        self.rFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (-1, math.sqrt(2) / 2)) * 25000, (0, 0))

    def kickLFoot(self):
        self.lFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (1, math.sqrt(2) / 2)) * 25000, (0, 0))

    def reverseKickLFoot(self):
        self.lFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (-1, math.sqrt(2) / 2)) * 25000, (0, 0))

    def punchRight(self):
        self.rFist.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (1, 0)) * 50000, (0, 0))

    def reversePunchRight(self):
        self.rFist.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (-1, 0)) * 50000, (0, 0))

    def punchLeft(self):
        self.lFist.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (1, 0)) * 50000, (0, 0))

    def reversePunchLeft(self):
        self.lFist.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (-1, 0)) * 50000, (0, 0))


class PlayerTwo():
    def __init__(self, space, screen):
        self.space = space
        self.screen = screen
        width, height = screen.get_size()
        pos = (3 * width / 4, height / 4)
        shapeFilter = pm.ShapeFilter(collisionGroups["PLAYER2"], collisionGroups["PLAYER1"])
        self.coreBody = pm.Body(10, 1000)
        self.coreBody.position = pos

        self.rightArmAlive = True
        self.leftArmAlive = True
        self.rightLegAlive = True
        self.leftLegAlive = True

        self.torso = Body(space, screen)
        self.torso.shape.filter = shapeFilter
        self.torsoRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.torso.shape.body, -math.pi / 10,
                                                      math.pi / 10)
        self.torsoLocationTie = pm.PinJoint(self.coreBody, self.torso.shape.body)
        self.torsoLocationTie.distance = 0
        self.torso.shape.body.position = pos

        # Set up arms
        self.rElbow = DefensiveBlock(self.space, self.screen)
        self.rElbow.shape.body.position = self.torso.shape.body.position + (-50, 35)
        self.rElbow.shape.filter = shapeFilter
        self.rUpperArm = pm.PinJoint(self.torso.shape.body, self.rElbow.shape.body, (0, 35), (0, 0))
        self.rUpperArm.distance = 40

        self.rFist = OffensiveBlock(self.space, self.screen)
        self.rFist.shape.filter = shapeFilter
        self.rFist.shape.body.position = self.rElbow.shape.body.position + (-25, 0)
        self.rFistRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.rFist.shape.body, -math.pi / 5,
                                                      math.pi / 5)

        self.rLowerArm = pm.PinJoint(self.rElbow.shape.body, self.rFist.shape.body)
        self.rLowerArm.distance = 50

        self.lElbow = DefensiveBlock(self.space, self.screen)
        self.lElbow.shape.body.position = self.torso.shape.body.position + (50, 35)
        self.lElbow.shape.filter = shapeFilter
        self.lUpperArm = pm.PinJoint(self.torso.shape.body, self.lElbow.shape.body, (0, 35), (0, 0))
        self.lUpperArm.distance = 40

        self.lFist = OffensiveBlock(self.space, self.screen)
        self.lFist.shape.filter = shapeFilter
        self.lFist.shape.body.position = self.lElbow.shape.body.position + (25, 0)
        self.lFistRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.lFist.shape.body, -math.pi / 5,
                                                      math.pi / 5)

        self.lLowerArm = pm.PinJoint(self.lElbow.shape.body, self.lFist.shape.body)
        self.lLowerArm.distance = 50

        # Set up legs
        self.rKnee = DefensiveBlock(self.space, self.screen)
        self.rKnee.shape.body.position = self.torso.shape.body.position + (-25, -100)
        self.rKnee.shape.filter = shapeFilter

        self.rUpperLeg = pm.PinJoint(self.torso.shape.body, self.rKnee.shape.body, (0, -50), (0, 0))
        self.rUpperLeg.distance = 40

        self.rFoot = OffensiveBlock(self.space, self.screen)
        self.rFoot.shape.friction = 1.5
        self.rFoot.shape.filter = shapeFilter
        self.rFoot.shape.body.position = self.rKnee.shape.body.position + (-25, -10)
        self.rFootRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.rFoot.shape.body, -math.pi / 5,
                                                      math.pi / 5)

        self.rLowerLeg = pm.PinJoint(self.rKnee.shape.body, self.rFoot.shape.body, (0, 0), (0, 25))
        self.rLowerLeg.distance = 50

        self.lKnee = DefensiveBlock(self.space, self.screen)
        self.lKnee.shape.body.position = self.torso.shape.body.position + (25, -100)
        self.lKnee.shape.filter = shapeFilter

        self.lUpperLeg = pm.PinJoint(self.torso.shape.body, self.lKnee.shape.body, (0, -50), (0, 0))
        self.lUpperLeg.distance = 40

        self.lFoot = OffensiveBlock(self.space, self.screen)
        self.lFoot.shape.friction = 1.5
        self.lFoot.shape.filter = shapeFilter
        self.lFoot.shape.body.position = self.lKnee.shape.body.position + (25, -10)
        self.lFootRotationLimit = pm.RotaryLimitJoint(self.space.static_body, self.lFoot.shape.body, -math.pi / 5,
                                                      math.pi / 5)

        self.lLowerLeg = pm.PinJoint(self.lKnee.shape.body, self.lFoot.shape.body, (0, 0), (0, 25))
        self.lLowerLeg.distance = 50

        self.rLegDownwardForce = pm.DampedSpring(self.coreBody, self.rFoot.shape.body, (0, 0), (0, 25), 300, 1250, 1)
        self.lLegDownwardForce = pm.DampedSpring(self.coreBody, self.lFoot.shape.body, (0, 0), (0, 25), 300, 1250, 1)

        self.space.add(self.coreBody, self.torsoRotationLimit, self.torsoLocationTie,
                       self.rUpperLeg, self.rLegDownwardForce, self.lUpperLeg, self.lLegDownwardForce,
                       self.rFootRotationLimit, self.lFootRotationLimit,
                       self.rFistRotationLimit, self.lFistRotationLimit,
                       self.lLowerLeg, self.rLowerLeg,
                       self.rUpperArm, self.rLowerArm,
                       self.lUpperArm, self.lLowerArm)

    def checkForDeath(self):
        if self.rightLegAlive:
            if self.rKnee.shape.health <= 0:
                self.rightLegAlive = False
                self.space.remove(
                    self.rKnee.shape.body,
                    self.rKnee.shape,
                    self.rUpperLeg,
                    self.rLowerLeg,
                    self.rLegDownwardForce,
                    self.rFootRotationLimit,
                    self.rFoot.shape.body,
                    self.rFoot.shape
                )

        if self.leftLegAlive:
            if self.lKnee.shape.health <= 0:
                self.leftLegAlive = False
                self.space.remove(
                    self.lKnee.shape.body,
                    self.lKnee.shape,
                    self.lUpperLeg,
                    self.lLowerLeg,
                    self.lFootRotationLimit,
                    self.lLegDownwardForce,
                    self.lFoot.shape.body,
                    self.lFoot.shape
                )

        if self.rightArmAlive:
            if self.rElbow.shape.health <= 0:
                self.rightArmAlive = False
                self.space.remove(
                    self.rFist.shape.body, self.rFist.shape,
                    self.rFistRotationLimit,
                    self.rElbow.shape.body, self.rElbow.shape,
                    self.rUpperArm,
                    self.rLowerArm
                )

        if self.leftArmAlive:
            if self.lElbow.shape.health <= 0:
                self.leftArmAlive = False
                self.space.remove(
                    self.lFist.shape, self.lFist.shape.body,
                    self.lFistRotationLimit,
                    self.lElbow.shape, self.lElbow.shape.body,
                    self.lUpperArm, self.lLowerArm
                )

    def update(self):
        self.checkForDeath()
        if self.leftArmAlive:
            self.lElbow.update()
            self.lFist.update()

        self.torso.update()

        if self.rightArmAlive:
            self.rElbow.update()
            self.rFist.update()

        if self.rightLegAlive:
            self.rFoot.update()
            self.rKnee.update()

        if self.leftLegAlive:
            self.lFoot.update()
            self.lKnee.update()

    def kickRFoot(self):
        self.rFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (-1, math.sqrt(2) / 2)) * 25000, (0, 0))

    def reverseKickRFoot(self):
        self.rFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (1, math.sqrt(2) / 2)) * 25000, (0, 0))

    def kickLFoot(self):
        self.lFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (-1, math.sqrt(2) / 2)) * 25000, (0, 0))

    def reverseKickLFoot(self):
        self.lFoot.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (1, math.sqrt(2) / 2)) * 25000, (0, 0))

    def punchRight(self):
        self.rFist.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (-1, 0)) * 50000, (0, 0))

    def reversePunchRight(self):
        self.rFist.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (1, 0)) * 50000, (0, 0))

    def punchLeft(self):
        self.lFist.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (-1, 0)) * 50000, (0, 0))

    def reversePunchLeft(self):
        self.lFist.shape.body.apply_impulse_at_local_point((Vec2d.zero() + (1, 0)) * 50000, (0, 0))
