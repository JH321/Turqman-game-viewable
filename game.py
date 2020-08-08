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
        self.new_game = False
        self.escape_screen = False
        self.click = False
        self.mousex = None
        self.mousey = None
 
    def new(self):
        # start new game
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.obstacles_list = []
        self.ground = pg.sprite.Group()
        self.jetpack_fuel = 20
        self.numb_stages = 0
        self.lives = 10
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
        print("method called")
        while self.playing:
            self.clock.tick(settings.FPS)
            self.events()
            self.update()
            self.draw()
            self.show_escape_screen()
 
    def update(self):
        ''' game loop update:
            creates new level when needed 
            checks for collision of player'''
        #ends level
        if self.player.pos.x + settings.IMG_WIDTH / 2 > settings.WIDTH:
            self.player.set_spawn()
            self.numb_stages += 1
            self.lives += 2
            for plat in self.platforms:
                plat.kill()
            self.create_platforms()
        self.all_sprites.update()

        if self.lives <= 0:
            self.show_game_over_screen()

        hits = pg.sprite.spritecollide(self.player, self.platforms, False) 
        ground_hits = pg.sprite.spritecollide(self.player, self.ground, False)
        obstacle_hits = pg.sprite.spritecollide(self.player, self.obstacles, False)
        #creates obstacle platforms
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
        
       
                    # self.player.pos = self.player.rect
        self.hit_box(hits)
        #teleports player back to spawn when ground is touched
        if ground_hits or self.player.rect.left < -25 or self.player.rect.top < -25 or self.player.vel.y > 1000:
            if ground_hits:
                self.lives -= 1
            self.player.set_spawn()
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

    def hit_box(self, hits):
         #collision on normal platforms
        if hits:
            #refuels jetpack when platform hits
            if self.jetpack_fuel < settings.JETPACK_FUEL:
                self.jetpack_fuel += 1
            for hit in hits:
                self.check_collision(hit.rect)
                if self.player.vel.y > 0:
                    #hitboxes are more polished
                    #collision when player is falling with players bottom and not players sides (top and mid)
                    if self.collision[2] or self.collision[3] or self.collision[7] or self.collision[8]:
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
                self.player.pos.y = self.player.rect.bottom
            
    def events(self):
        #game loop - events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
           
            ''''if event.type == pg.KEYDOWN and event.key == pg.K_c:
                if self.numb_changes > 0:
                    self.numb_changes -= 1
                    settings.PLAYER_GRAVITY *= -1
                    if not self.is_opposite:
                        self.is_opposite = True
                    else:
                        self.is_opposite = False'''
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.escape_screen = True
            if event.type == pg.KEYDOWN and  event.key == pg.K_UP:
                print(self.is_opposite)
                self.player.jump(self.is_opposite)
 
 
    def draw(self):
        #game loop - draw
        

        self.screen.fill(settings.SKY_BLUE)
        #displays jetpack fuel
        self.draw_text("Fuel: " + str(self.jetpack_fuel), 100, 50)
        self.draw_text("Lives: " + str(self.lives), 100, 100)
        self.draw_text("Levels passed: " + str(self.numb_stages), 100, 150)
        self.all_sprites.draw(self.screen)
        pg.display.update()
 
    def show_start_screen(self):
        #game start screen
        while not self.new_game:
            self.screen.fill(settings.SKY_BLUE)
            self.draw_text("TURQMAN", (settings.WIDTH / 2 + 60) - 150, 200)

            self.get_mousepos()
            print("running")
            button_1 = pg.Rect(settings.WIDTH / 2 - 100, settings.HEIGHT / 2 - 25, 200, 50)
            if button_1.collidepoint(self.mousex, self.mousey):
                if self.click:
                    self.new_game = True
            self.click = False
            pg.draw.rect(self.screen, settings.WHITE, button_1)
            self.draw_text("Start", (settings.WIDTH / 2 + 60) - 100, (settings.HEIGHT / 2 + 10) - 25)
            self.draw_text("Arrow keys to move and jump", 0, 0)
            self.draw_text("Left Shift to sprint", 0, 40)
            self.draw_text("C key to jetpack (when off the ground)", 0, 80)
            for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.click = True
            pg.display.update()

    def show_escape_screen(self):
        while self.escape_screen:
            print("test esscape butt")
            self.screen.fill(settings.SKY_BLUE)
            self.draw_text("Options", 100, 50)
            self.get_mousepos()
            button_1 = pg.Rect(50, 100, 200, 50)
            button_2 = pg.Rect(50, 500, 200, 50)
            if button_1.collidepoint(self.mousex, self.mousey):
                if self.click:
                    self.new_game = False
                    self.playing = False
                    self.escape_screen = False
            if button_2.collidepoint(self.mousex, self.mousey):
                if self.click:
                    self.escape_screen = False
            self.click = False
            pg.draw.rect(self.screen, settings.WHITE, button_1)
            self.draw_text("Main menu", 60, 110)
            pg.draw.rect(self.screen, settings.WHITE, button_2)
            self.draw_text("Back to game", 60, 510)
            for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.click = True
            pg.display.update()

    def show_game_over_screen(self):
        game_over = True
        while game_over:
            print("test esscape butt")
            self.screen.fill(settings.SKY_BLUE)
            self.draw_text("GAME OVER", 100, 50)
            self.get_mousepos()
            button_1 = pg.Rect(50, 100, 200, 50)
            if button_1.collidepoint(self.mousex, self.mousey):
                if self.click:
                    self.new_game = False
                    self.playing = False
                    self.escape_screen = False
                    game_over = False
            self.click = False
            pg.draw.rect(self.screen, settings.WHITE, button_1)
            self.draw_text("Main menu", 60, 110)
            for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    if event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.click = True
            pg.display.update()
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

    def draw_text(self, words, x, y):
        font = pg.font.Font('freesansbold.ttf', 32)
        text = font.render(words, True, settings.BLACK)
        text_rect = text.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text, text_rect.center)
    
    def get_mousepos(self):
        self.mousex, self.mousey = pg.mouse.get_pos()
    
   
g = Game()
while g.running:
    if g.new_game:
        g.new()
        g.show_go_screen()
    else:
        g.show_start_screen()