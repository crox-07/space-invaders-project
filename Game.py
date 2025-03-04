import pygame, random, time, math
from spaceship import Spaceship
from obstacle import Obstacle, shape
from alien import Alien
from Laser import Laser
from alien import MysteryShip
from Powerbeam import PowerBeamMeter, PowerBeam

class Game:
    def __init__(self, screen_width, screen_height, offset):
        # Setup
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.offset = offset
        
        # Groups/sprites
        self.spaceship_group = pygame.sprite.GroupSingle()
        self.spaceship_group.add(Spaceship(self.screen_width, self.screen_height, self.offset))
        self.obstacles = self.create_obstacles()
        self.aliens_group = pygame.sprite.Group()
        self.aliens_direction = 1
        self.alien_progress = 0
        self.create_aliens()
        self.alien_lasers_group = pygame.sprite.Group()
        self.mystery_ship_group = pygame.sprite.GroupSingle()
        self.lasers_group = pygame.sprite.Group()
        self.powerbeam_group = pygame.sprite.GroupSingle()
        
        # Game variables
        self.lives = 3
        self.run = True
        self.score = 0
        self.highscore = 0
        self.level = 1
        self.level_up_text = None
        self.level_up_start_time = None
        self.show_level_up_text = False
        self.level_up_flash_interval = 0.5
        self.levelup = False
        self.life_score = 0
        self.life_scoremax = 15000
        
        # Audio variables
        self.explosion_sound = pygame.mixer.Sound('sounds/invaderkilled.wav')
        self.explosion_sound.set_volume(0.25)
        self.load_highscore()
        self.level_up_sound = pygame.mixer.Sound('sounds/12_3.mp3')
        pygame.mixer.music.load('sounds/spacemusic.mp3')
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
        
        
        
        # Powerbeam and other mechanics
        self.aliens_hit = False
        self.powerbeam = None
        self.powerbeam_meter = PowerBeamMeter(350, 750)
        self.powerbeam_meter_group = pygame.sprite.GroupSingle(self.powerbeam_meter) # type: ignore
        self.powerbeam_charge = 0
        self.max_powerbeam_charge = 20
        self.powerbeam_ready = False
    def create_obstacles(self):
        obstacle_width = len(shape[0]) * 3
        gap = (self.screen_width + self.offset - (4 * obstacle_width)) // 5
        obstacles = []
        for i in range(4):
            offset_x = (i + 1) * gap + i * obstacle_width
            obstacle = Obstacle(offset_x, self.screen_height - 100)
            obstacles.append(obstacle)
        return obstacles
    def create_aliens(self):
        for row in range(5):
            for column in range(11):
                x = 75 + column * 55
                y = 110 + row * 55
                
                if row == 0:
                    alien_type = 3
                elif row in (1,2):
                    alien_type = 2
                else:
                    alien_type = 1
                
                alien = Alien(alien_type, x + self.offset/2, y)
                self.aliens_group.add(alien)
    def move_aliens(self):
        self.aliens_group.update(self.aliens_direction)
        alien_sprites = self.aliens_group.sprites()
        for alien in alien_sprites:
            if alien.rect.right >= self.screen_width + self.offset/2:
                if not self.aliens_hit:                 
                    self.alien_progress += 1
                    self.aliens_hit = True
                self.aliens_direction = - (1 + (self.alien_progress / 50))
                self.alien_move_down(2)
            elif alien.rect.left <= self.offset/2:
                if not self.aliens_hit:                 
                    self.alien_progress += 1
                    self.aliens_hit = True
                self.aliens_direction = 1 + (self.alien_progress / 50)
                self.alien_move_down(2)
    def alien_move_down(self, distance):
        if self.aliens_group:
            for alien in self.aliens_group.sprites():
                alien.rect.y += distance
    def alien_shoot_laser(self):
        if self.aliens_group.sprites():
            random_alien = random.choice(self.aliens_group.sprites())
            laser_sprite = Laser(random_alien.rect.center, -6, self.screen_height)
            self.alien_lasers_group.add(laser_sprite)
            
    def create_mystery_ship(self):
        self.mystery_ship_group.add(MysteryShip(self.screen_width, self.offset))
        
        
    def is_mystery_ship_present(self):
        return bool(self.mystery_ship_group)
    
    def check_for_collisions(self):
        #Spaceship
        if self.spaceship_group.sprite.lasers_group:
            for laser_sprite in self.spaceship_group.sprite.lasers_group:
                
                aliens_hit = pygame.sprite.spritecollide(laser_sprite, self.aliens_group, True)
                if aliens_hit:
                    self.explosion_sound.play()
                    for alien in aliens_hit:
                        self.score += int(math.ceil(alien.type * 100 * self.level / 2))
                        self.life_score += int(math.ceil(alien.type * 100 * self.level / 2))
                        self.check_for_highscore()
                        self.powerbeam_charge += alien.type
                        if self.powerbeam_charge >= self.max_powerbeam_charge:
                            self.powerbeam_ready = True
                        laser_sprite.kill()
                
                if pygame.sprite.spritecollide(laser_sprite, self.mystery_ship_group, True):
                    self.score += int(math.ceil(500 * self.level / 2))
                    self.life_score += int(math.ceil(500 * self.level / 2))
                    self.explosion_sound.play()
                    self.powerbeam_charge += 5
                    self.check_for_highscore()
                    if self.powerbeam_charge >= self.max_powerbeam_charge:
                        self.powerbeam_ready = True
                    laser_sprite.kill()
                    
                for obstacle in self.obstacles:
                    if pygame.sprite.spritecollide(laser_sprite, obstacle.blocks_group, True):
                        laser_sprite.kill()
        
        #Alien Lasers
        if self.alien_lasers_group:
            for laser_sprite in self.alien_lasers_group:
                if pygame.sprite.spritecollide(laser_sprite, self.spaceship_group, False):
                    laser_sprite.kill()
                    self.lives -= 1
                    if self.lives == 0:
                        self.game_over()
                    
                for obstacle in self.obstacles:
                    if pygame.sprite.spritecollide(laser_sprite, obstacle.blocks_group, True):
                        laser_sprite.kill()
                        
        
        if self.aliens_group:
            for alien in self.aliens_group:
                for obstacle in self.obstacles:
                    pygame.sprite.spritecollide(alien, obstacle.blocks_group, True)
                    
                if pygame.sprite.spritecollide(alien, self.spaceship_group, False):
                    self.game_over()
        
        # Powerbeam        
        if self.powerbeam_group:
            for powerbeam in self.powerbeam_group:
                beamaliens = pygame.sprite.spritecollide(powerbeam, self.aliens_group, True)
                if beamaliens:
                    #print('Alien hit by powerbeam')
                    self.explosion_sound.play()
                    for alien in beamaliens:
                        self.score += int(math.ceil(alien.type * 100 * self.level / 2))
                        self.life_score += int(math.ceil(alien.type * 100 * self.level / 2))
                        self.check_for_highscore()
                        #print(f'Alien of type {alien.type} killed')
                if pygame.sprite.spritecollide(powerbeam, self.mystery_ship_group, True):
                    self.explosion_sound.play()
                    self.score += int(math.ceil(500 * self.level / 2))
                    self.life_score += int(math.ceil(500 * self.level / 2))
                    
                
    def game_over(self):
        self.run = False

    def reset(self):
        self.run = True
        self.lives = 3
        self.spaceship_group.sprite.reset()
        self.aliens_group.empty()
        self.alien_lasers_group.empty()
        self.create_aliens()
        self.mystery_ship_group.empty()
        self.obstacles = self.create_obstacles()
        self.score = 0
        self.alien_progress = 0
        self.level = 1
        
    def check_for_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            
            with open("highscore.txt", 'w') as file:
                file.write(str(self.highscore))
    
    
    def load_highscore(self):
        try:
            with open("highscore.txt", 'r') as file:
                self.highscore = int(file.read())
        except FileNotFoundError:
            self.highscore = 0
            
    def level_up(self):
        if not self.aliens_group:
            self.display_level_up_text(self.level)
            self.level += 1
            self.alien_progress = 0
            self.aliens_direction = 1
            self.create_aliens()
            self.spaceship_group.sprite.reset()
            self.alien_lasers_group.empty()
            self.mystery_ship_group.empty()
            self.obstacles = self.create_obstacles()
            self.powerbeam_group.empty()
            self.levelup = True
            
    def display_level_up_text(self, level):
        font = pygame.font.Font('font/monogram.ttf', 100)
        self.level_up_text = font.render(f'LEVEL {level + 1}', False, (243, 216, 63))
        self.level_up_start_time = time.time()
        self.show_level_up_text = True
        pygame.mixer.music.pause()
        self.level_up_sound.play()
        
    def update_level_up_text(self):
        if self.show_level_up_text:
            current_time = time.time()
            if current_time - self.level_up_start_time > 3:  # type: ignore 
                self.show_level_up_text = False
                self.levelup = False
                pygame.mixer.music.unpause()
            elif int((current_time - self.level_up_start_time) / self.level_up_flash_interval) % 2 == 0: # type: ignore
                return True
            else:
                return False
        return False
    
    def update_powerbeam_meter(self):
        self.powerbeam_meter.update(self.powerbeam_charge)
        
        
    def add_life(self):
        if self.lives < 3:
            if self.life_score >= self.life_scoremax:
                self.lives +=1
                self.life_score = 0
                
    # def toggle_flash(self):
    #     self.powerbeam_meter.toggle_flash()
    
    def lifescore_update(self):
        if self.level % 5 == 0:
            self.life_scoremax = self.life_scoremax * 2
    
    