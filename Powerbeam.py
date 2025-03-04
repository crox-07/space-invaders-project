import pygame

FLASH_EVENT = pygame.USEREVENT + 5
FLASH_INTERVAL = 500

class PowerBeam(pygame.sprite.Sprite):
    def __init__(self, spaceship, screen_height, color = (243, 216, 63)):
        super().__init__()
        self.spaceship = spaceship
        self.color = (color)
        self.width = 10
        self.screen_height = screen_height

        self.image = pygame.Surface([self.width, 600])
        self.image.fill(self.color)
        self.rect = self.image.get_rect(midbottom=self.spaceship.rect.center)
        
    def update(self):
        self.rect.midbottom = self.spaceship.rect.center
        #print(f"PowerBeam rect: {self.rect}")
        
        
class PowerBeamMeter(pygame.sprite.Sprite):
    def __init__(self, x, y, max_charge=20):
        super().__init__()
        self.charge = 0
        self.x = x
        self.y = y
        self.max_charge = max_charge
        self.location = (x, y)
        self.width = 100
        self.height = 20
        self.border_thickness = 5
        self.ready = False
        self.flash_color = (243, 216, 63)
        self.flash_state = True
        
        # Create surfaces
        self.meter_holder_surface = pygame.Surface((self.width+ 2 * self.border_thickness, self.height+2*self.border_thickness))
        self.meter_surface = pygame.Surface((self.width, self.height))
        self.meter_bg_surface = pygame.Surface((self.width, self.height))
        
        # Fill surfaces and draw borders
        self.meter_holder_surface.fill((243, 216, 63))
        self.meter_bg_surface.fill((29, 29, 27))
        
        
    def update(self, charge):
        self.charge = charge
        self.meter_surface.fill((29, 29, 27))
        chrg_width = int((self.charge / self.max_charge) * self.width)
        pygame.draw.rect(self.meter_surface, (243, 216, 63), (0, 0, chrg_width, self.height))
        self.ready = self.charge >= self.max_charge
        
    def draw(self, screen, font):
        screen.blit(self.meter_holder_surface, (self.x - self.border_thickness, self.y - self.border_thickness))
        screen.blit(self.meter_bg_surface, (self.x, self.y))
        screen.blit(self.meter_surface, (self.x, self.y))
        if self.ready:
            color = self.flash_color if self.flash_state else (29, 29, 27)
            ready_text_surface = font.render("READY", True, color)
            screen.blit(ready_text_surface, (self.x + 10, self.y - 10))
            
    def toggle_flash(self):
        self.flash_state = not self.flash_state