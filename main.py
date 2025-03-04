import pygame, sys, random
from Game import Game
from math import ceil
from spaceship import Spaceship
from Powerbeam import PowerBeam, PowerBeamMeter
import json
#Game settings
pygame.init()

START_SCREEN = 0
GAME_RUNNING = 1
GAME_OVER = 2
LEADERBOARD = 3

boom = pygame.mixer.Sound('sounds/sizzleboom.wav')
boom.set_volume(1)

game_state = START_SCREEN


SCREEN_WIDTH = 750
SCREEN_HEIGHT = 700
OFFSET = 50

GREY = (29, 29, 27)
YELLOW = (243, 216, 63)

game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, OFFSET)


font = pygame.font.Font('font/monogram.ttf', 40)
game_over_surface = font.render("GAME OVER", False, YELLOW)
score_text_surface = font.render("SCORE", False, YELLOW)
highscore_text_surface = font.render("HIGH-SCORE", False, YELLOW)
level_surface = font.render(f"LEVEL {game.level}", False, YELLOW)
ready_text_surface = font.render("READY", False, GREY)

levelup_surface = font.render("LEVEL UP!", False, YELLOW)

start_surface = font.render("PRESS ENTER TO START", False, YELLOW)
leaderboard_surface = font.render("LEADERBOARD", False, YELLOW)
enter_name_surface = font.render("ENTER YOUR NAME:", False, YELLOW)
name_input = ""
leaderboard = []

def load_leaderboard():
    global leaderboard
    try:
        with open('leaderboard.json', 'r') as f:
            leaderboard = json.load(f)
    except FileNotFoundError:
        leaderboard = []

def save_leaderboard():
    with open('leaderboard.json', 'w') as f:
        json.dump(leaderboard, f)

load_leaderboard()

screen = pygame.display.set_mode((SCREEN_WIDTH + OFFSET, SCREEN_HEIGHT + 2*OFFSET))
pygame.display.set_caption("Space Invaders")

clock = pygame.time.Clock()


laser_timer = ceil(500 / (game.level))

SHOOT_LASER = pygame.USEREVENT
pygame.time.set_timer(SHOOT_LASER, laser_timer)

ALIENSHIT = pygame.USEREVENT + 1
pygame.time.set_timer(ALIENSHIT, 10)
    

MYSTERYSHIP = pygame.USEREVENT + 2
pygame.time.set_timer(MYSTERYSHIP, random.randint(4000, 8000))

SOUND = pygame.USEREVENT + 3
pygame.time.set_timer(SOUND, 155)

POWERBEAMTIMEOUT = pygame.USEREVENT + 4

FLASH_EVENT = pygame.USEREVENT + 5
FLASH_INTERVAL = 500
pygame.time.set_timer(FLASH_EVENT, FLASH_INTERVAL)



powerbeam = None


while True:
    for event in pygame.event.get():
        if not game.levelup:    
            if not game.run and game_state != START_SCREEN :
                game_state = LEADERBOARD
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if game_state == START_SCREEN:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    game_state = GAME_RUNNING
                    game.run = True
            elif game_state == GAME_RUNNING:
                if event.type == SHOOT_LASER and game.run:
                    game.alien_shoot_laser()
                if event.type == MYSTERYSHIP and game.run:
                    game.create_mystery_ship()
                    pygame.time.set_timer(MYSTERYSHIP, random.randint(4000, 8000))
                if event.type == SOUND and game.is_mystery_ship_present():
                    game.mystery_ship_group.sprite.mystery_sound.play()
                if event.type == ALIENSHIT and game.run:
                    game.aliens_hit = False
                if event.type == POWERBEAMTIMEOUT:
                    if powerbeam:
                        powerbeam.kill()
                        powerbeam = None
                if event.type == FLASH_EVENT:
                    game.powerbeam_meter.toggle_flash()
            elif game_state == LEADERBOARD:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name_input:
                        leaderboard.append({'name': name_input, 'score': game.score})
                        leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:10]
                        save_leaderboard()
                        game_state = START_SCREEN
                        name_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        name_input += event.unicode
    
    keys = pygame.key.get_pressed()
    if game_state == GAME_RUNNING:
        if keys[pygame.K_SPACE] and game.run == False:
            game.reset()
        if keys[pygame.K_LSHIFT] and game.powerbeam_ready:    
            if powerbeam is None:
                powerbeam = PowerBeam(game.spaceship_group.sprite, SCREEN_HEIGHT)
                game.powerbeam_group.add(powerbeam)
                game.powerbeam_charge = 0
                game.powerbeam_ready = False
                pygame.time.set_timer(POWERBEAMTIMEOUT, 500)
                boom.play()
                #print("powerbeam created")
    
            
    #Updating
    if game_state == GAME_RUNNING and not game.levelup:
        game.spaceship_group.update() # Update spaceship_group
        game.move_aliens() # Update alien movement
        game.alien_lasers_group.update() # Update alien_lasers_group
        game.mystery_ship_group.update() # Update mystery_ship_group
        game.lasers_group.update()  # Update lasers_group
        game.powerbeam_group.update()  # Update powerbeam_group
        game.check_for_collisions() # Check for collisions
        game.check_for_highscore() # Check for highscore
        game.level_up() # Check for levelup
        game.update_powerbeam_meter() # Update powerbeam_meter
        game.add_life() # Add lives if necessary
        game.lifescore_update() # Update lifescore requirement
    # if game.levelup == True:
    #     screen.blit(level_surface, (570, 740, 50
    #     game.levelup = False
        
        
    #Drawing
    screen.fill(GREY)
    pygame.draw.rect(screen, YELLOW, (10, 10, 780, 780), 2, 0, 60, 60, 60, 60)
    pygame.draw.line(screen, YELLOW, (25, 730), (775, 730), 3)
    
    if game_state == START_SCREEN:
        screen.blit(start_surface, ((SCREEN_WIDTH // 2 - start_surface.get_width() // 2) - 180 ,SCREEN_HEIGHT // 2 - start_surface.get_height() // 2))
        
        y_offset = 150
        ldbrd = font.render("LEADERBOARD", False, YELLOW)
        screen.blit(ldbrd, ((SCREEN_WIDTH // 2 - ldbrd.get_width() // 2) + 180, y_offset - 50))
        for entry in leaderboard:
            entry_surface = font.render(f"{entry['name']}: {entry['score']}", False, YELLOW)
            screen.blit(entry_surface, ((SCREEN_WIDTH // 2 - entry_surface.get_width() // 2) + 180, y_offset))
            y_offset += 50
    elif game_state == GAME_RUNNING:
        if game.run:
            screen.blit(level_surface, (570, 740, 50, 50))
        else:
            screen.blit(game_over_surface, (570, 740, 50, 50))
    
        x = 50
        for life in range(game.lives):
            screen.blit(game.spaceship_group.sprite.image, (x, 745))
            x += 50
        
        level_surface = font.render(f"LEVEL {game.level}", False, YELLOW)
        
        screen.blit(score_text_surface, (50, 15, 50, 50))
        formatted_score = str(game.score).zfill(5)
        score_surface = font.render(formatted_score, False, YELLOW)
        screen.blit(score_surface, (50, 40, 50, 50))
        screen.blit(highscore_text_surface, (550, 15, 50, 50))
        formatted_high_score = str(game.highscore).zfill(5)
        highscore_surface = font.render(formatted_high_score, False, YELLOW)
        screen.blit(highscore_surface, (625, 40, 50, 50))
        
        game.spaceship_group.draw(screen)
        game.spaceship_group.sprite.lasers_group.draw(screen)
        for obstacle in game.obstacles:
            obstacle.blocks_group.draw(screen)
        game.aliens_group.draw(screen)
        game.alien_lasers_group.draw(screen)
        game.mystery_ship_group.draw(screen)
        game.lasers_group.draw(screen)
        game.powerbeam_group.draw(screen)
        
        game.powerbeam_meter.draw(screen, font)
        
        if game.update_level_up_text():
            screen.blit(game.level_up_text, ((SCREEN_WIDTH + OFFSET) // 2 - game.level_up_text.get_width() // 2, (SCREEN_HEIGHT + OFFSET) // 2 - game.level_up_text.get_height() // 2)) # type: ignore
        
        
    elif game_state == LEADERBOARD:
        screen.blit(enter_name_surface, (SCREEN_WIDTH // 2 - enter_name_surface.get_width() // 2, SCREEN_HEIGHT // 2 - enter_name_surface.get_height() // 2))
        name_surface = font.render(name_input, False, YELLOW)
        screen.blit(name_surface, (SCREEN_WIDTH // 2 - name_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    #Refreshing the screen and limiting the frame rate to 60 frames per second
    pygame.display.update()
    clock.tick(60)
    laser_timer = ceil(500 / (game.level))