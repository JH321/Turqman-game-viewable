import pygame as pg
import sys
import os
import settings
vec = pg.math.Vector2
 
class Player(pg.sprite.Sprite):
    screen = pg.display.set_mode((1000, 800))
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        #self.image = screen.blit("TurqMan1.png")
        '''hg = pg.image.load('TurqMan1.png')
        hgbox = pg.Rect(0, 13, 36, 72)
        self.image = pg.Surface.blit("TurqMan1.png", (300,300), 50)'''
        self.game = game
        self.image = pg.Surface((settings.IMG_WIDTH, settings.IMG_HEIGHT))
        self.image.fill(settings.RED)
        self.rect = self.image.get_rect()
        self.set_spawn()
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
 
    def set_spawn(self):
        self.acc = vec(0, 0)
        self.vel = vec(0, 0)
        self.rect.center = (settings.IMG_WIDTH / 2, settings.HEIGHT / 2 - 25)
        self.pos = vec(self.rect.center)
 
    #jump method
    def jump(self, is_opposite):
        self.rect.y += 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        ground_hits = pg.sprite.spritecollide(self, self.game.ground, False)
        self.rect.y -= 1
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        ground_hits = pg.sprite.spritecollide(self, self.game.ground, False)
        if hits or ground_hits:
            if not is_opposite:
                self.vel.y = -settings.JUMP_VELOCITY
            else:
                self.vel.y = settings.JUMP_VELOCITY
 
    def update(self):
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        ground_hits = pg.sprite.spritecollide(self, self.game.ground, False)
        keys = pg.key.get_pressed()
        self.acc = vec(0, settings.PLAYER_GRAVITY)
        if hits or ground_hits:
            if keys[pg.K_LEFT]:
                self.acc.x = -settings.PLAYER_ACC
                print("left")
            if keys[pg.K_RIGHT]:
                self.acc.x = settings.PLAYER_ACC
                print("right")
            if keys[pg.K_LSHIFT]:
                self.acc.x *= 1.7
                print("sprint")
            self.acc.x += self.vel.x * settings.PLAYER_FRICTION
        else:
            #no player control while in mid air
            if keys[pg.K_c] and self.game.jetpack_fuel > 0:
                self.acc.y = -0.2
                self.game.jetpack_fuel -= 1
                print(self.game.jetpack_fuel)
            self.acc.x = 0
        self.vel += self.acc
        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.pos.x += self.vel.x
        if self.rect.right > settings.WIDTH:
            self.pos.x = settings.IMG_WIDTH / 2
            self.vel.x = 0
        if self.rect.left < 0:
            self.pos.x = settings.IMG_WIDTH / 2 + 1
            self.vel.x = 0
        if self.rect.top < 0:
            self.pos.y = settings.IMG_HEIGHT + 1
            self.vel.y = 0
        self.rect.midbottom = self.pos
            #self.rect.x = self.ret.ccenterx
   
class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((w,h))
        self.image.fill(settings.WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y