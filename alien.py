import pygame, random


class Alien(pygame.sprite.Sprite):
    def __init__(self, type, x, y):
        super().__init__()
        self.type = type
        path = f"graphics/alien_{type}.png"
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(topleft = (x,y))
        
    def update(self, direction):
        self.rect.x += direction
        
class MysteryShip(pygame.sprite.Sprite):
    def __init__(self, screen_width, offset):
        super().__init__()
        self.screen_width = screen_width
        self.image = pygame.image.load("graphics/mystery.png")
        self.offset = offset
        self.mystery_sound = pygame.mixer.Sound('sounds/ufo_highpitch.wav')
        self.mystery_sound.set_volume(0.5)
        
        x = random.choice([self.offset/2, self.screen_width  + self.offset - self.image.get_width()])
        if x == self.offset/2:
            self.speed = 3
        else:
            self.speed = -3
        
        self.rect = self.image.get_rect(topleft = (x, 90))
        
    def update(self):
        self.rect.x += self.speed
        if self.rect.right > self.screen_width + self.offset/2:
            self.kill()
            self.mystery_sound.stop()
            
        elif self.rect.left < self.offset/2:
            self.kill()
            self.mystery_sound.stop()
            