import pygame as pg
import random
import settings
import player
 
class Game:
    def __init__(self):
        #initialize game window
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pg.display.set_caption("Platformer")
        self.clock = pg.time.Clock()
        self.running = True
 
    def new(self):
        # start new game
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.obstacles_list = []
        self.ground = pg.sprite.Group()
        self.numb_changes = 4
        self.is_opposite = False #determines if gravity is inverse
        self.player = player.Player(self)
        self.all_sprites.add(self.player)
        self.collision = [None] * 10
        #creates platforms
        self.create_platforms()
        #self.create_test_level()
        #creates ground
        p_ground = player.Platform(*settings.GROUND_PLATFORM)
        self.all_sprites.add(p_ground)
        self.ground.add(p_ground)
        #creates obstacle
            
        self.run()
 
    def run(self):
        
        self.playing = True
        while self.playing:
            self.clock.tick(settings.FPS)
            self.events()
            self.update()
            self.draw()
 
    def update(self):
        ''' game loop update:
            creates new level when needed 
            checks for collision of player'''
        if self.player.pos.x + settings.IMG_WIDTH / 2 > settings.WIDTH:
            self.player.set_spawn()
            self.numb_changes = 4
            for plat in self.platforms:
                plat.kill()
            self.create_platforms()
        self.all_sprites.update()
        hits = pg.sprite.spritecollide(self.player, self.platforms, False) 
        ground_hits = pg.sprite.spritecollide(self.player, self.ground, False)
        obstacle_hits = pg.sprite.spritecollide(self.player, self.obstacles, False)
        timer = random.random()
        if len(self.obstacles_list) < 7 and timer < 0.05:
            p = player.Platform(*settings.CREATE_OBSTACLES())
            self.all_sprites.add(p)
            self.obstacles.add(p)
            self.obstacles_list.append(p)
        for plat in self.obstacles_list:
            if plat.rect.right > -10:
                plat.rect.x -= 10
            else:
                plat.kill()
                self.obstacles_list.remove(plat)
        
        #collision on normal platforms
        if hits:
            for hit in hits:
                self.check_collision(hit.rect)
                if self.player.vel.y > 0:
                    #hitboxes are more polished
                    #collision when player is falling with players bottom and not players sides (top and mid)
                    if self.collision[2] or self.collision[3] or self.collision[7]:
                        self.player.rect.bottom = hit.rect.top + 1
                        self.player.vel.y = 0
                    else:
                        if self.collision[0] or self.collision[4]:
                            self.player.rect.left = hit.rect.right + 1
                        if self.collision[1] or self.collision[5]:
                            self.player.rect.right = hit.rect.left - 1
                        self.player.vel.x = 0
                #collision when player is jumping
                elif self.player.vel.y < 0:
                    #collision for hitting the bottom of a platform
                    if self.collision[6] or self.collision[0] or self.collision[1]:
                        self.player.rect.top = hit.rect.bottom - 1
                        self.player.vel.y = 0
                    #collision for hitting left side of platform
                    elif self.collision[4] or self.collision[2]:
                        self.player.vel.x = 0
                        self.player.rect.left = hit.rect.right + 1
                    #collision for hitting right side of platform
                    elif self.collision[5] or self.collision[3]:
                        self.player.vel.x = 0
                        self.player.rect.right = hit.rect.left - 1
                #need to fix velocity keeps adding to position even when in collision
                elif self.player.vel.y == 0:
                    #collision when right side of player hits platform while not jumping
                    if self.collision[1] or self.collision[5]:
                        self.player.rect.right = hit.rect.left - 1
                        self.player.vel.x = 0
                        self.player.acc.x = 0
                        self.player.pos.x = self.player.rect.right - settings.IMG_WIDTH / 2
                    #collision when left side of player hits platform while not jumping
                    elif self.collision[0] or self.collision[4]:
                        self.player.rect.left = hit.rect.right + 1
                        self.player.vel.x = 0
                        self.player.acc.x = 0
                        self.player.pos.x = self.player.rect.left + settings.IMG_WIDTH / 2
                    elif self.collision[2] or self.collision[3]:
                        self.player.rect.bottom = hit.rect.top + 1
                self.player.pos.y = self.player.rect.bottom
                    # self.player.pos = self.player.rect
        #teleports player back to spawn when ground is touched
        if ground_hits or self.player.rect.left < -25 or self.player.rect.top < -25:
            self.player.set_spawn()
            self.player.vel.x = 0
            self.player.vel.y = 0
        if obstacle_hits:
            self.player.vel.x *= -2
            self.player.vel.y *= -2
            obstacle_hits[0].kill()
            self.obstacles_list.remove(obstacle_hits[0])


    def check_collision(self, rect):
        self.collision[0] = rect.collidepoint(self.player.rect.topleft)
        self.collision[1] = rect.collidepoint(self.player.rect.topright)
        self.collision[2] = rect.collidepoint(self.player.rect.bottomleft)
        self.collision[3] = rect.collidepoint(self.player.rect.bottomright)

        self.collision[4] = rect.collidepoint(self.player.rect.midleft)
        self.collision[5] = rect.collidepoint(self.player.rect.midright)
        self.collision[6] = rect.collidepoint(self.player.rect.midtop)
        self.collision[7] = rect.collidepoint(self.player.rect.midbottom)

        self.collision[8] = rect.collidepoint(self.player.rect.center)

            
    def events(self):
        #game loop - events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
           
            if event.type == pg.KEYDOWN and event.key == pg.K_c:
                if self.numb_changes > 0:
                    self.numb_changes -= 1
                    settings.PLAYER_GRAVITY *= -1
                    if not self.is_opposite:
                        self.is_opposite = True
                    else:
                        self.is_opposite = False
            if event.type == pg.KEYDOWN and  event.key == pg.K_UP:
                print(self.is_opposite)
                self.player.jump(self.is_opposite)
 
 
    def draw(self):
        #game loop - draw
        

        self.screen.fill(settings.SKY_BLUE)
        self.all_sprites.draw(self.screen)
        font = pg.font.Font('freesansbold.ttf', 32)
        gravity_count = font.render(str(self.numb_changes), True, settings.WHITE, settings.BLACK)
        text_rect = gravity_count.get_rect()
        text_rect.center = (settings.WIDTH + 50, settings.HEIGHT + 50)
        self.screen.blit(gravity_count, text_rect)
        pg.display.update()
        pg.display.flip()
 
    def show_start_screen(self):
        #game start screen
        pass
 
    def show_go_screen(self):
        pass

    def create_platforms(self):
        for plat in settings.CREATE_PLATFORMS():
            p = player.Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)
    def create_test_level(self):
        for plat in settings.TEST_LEVEL:
            p = player.Platform(*plat)
            self.all_sprites.add(p)
            self.platforms.add(p)

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()
 
pg.quit()