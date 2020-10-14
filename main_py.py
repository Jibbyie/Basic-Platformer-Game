import pygame
import sys

clock = pygame.time.Clock()

from pygame.locals import *

pygame.init()  # initialize pygame
pygame.display.set_caption('Basic Platformer')
WINDOW_SIZE = (600, 400)

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initialize the window

display = pygame.Surface((300, 200))  # renders all pixels twice as large in relation to the window screen

player_image = pygame.image.load('player.png').convert()
player_image.set_colorkey((255, 255, 255))  # "Green screen", makes white border transparent

grass_image = pygame.image.load('grass.png')
TILE_SIZE = grass_image.get_width()  # width of grass tiles which is 16px
dirt_image = pygame.image.load('dirt.png')

game_map = [['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '2', '2', '2', '2', '2', '0', '0', '0', '0', '0', '0', '0'],
            ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
            ['2', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '2', '2'],
            ['1', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'],
            ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']]

moving_right = False
moving_left = False

player_location = [50, 50]
player_y_momentum = 0

# Essentially the players "hitbox"
player_rect = pygame.Rect(player_location[0], player_location[1], player_image.get_width(), player_image.get_height())

while True:  # game loop
    display.fill((146, 244, 255))

    tile_rects = []  # keep track of tiles to be used for collisions
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':  # 1 = dirt
                display.blit(dirt_image, (x * TILE_SIZE, y * TILE_SIZE))  # rendering images
            if tile == '2':  # 2 = grass
                display.blit(grass_image, (x * TILE_SIZE, y * TILE_SIZE))  # TILE_SIZE refers to pixel width
                # referenced above
            if tile != '0':  # if tile is not air
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1  # iterate across the row
        y += 1  # move to next column

    display.blit(player_image, player_location)

    # Bounce + Gravity | [1] refers to the y axis
    """
    if player_location[1] > WINDOW_SIZE[1] - player_image.get_height():  # if player image touches bottom of screen
        player_y_momentum = -player_y_momentum  # momentum reverses (upward momentum)
    else:
    """
    player_y_momentum += 0.2  # Gravity speed (always falling)
    player_location[1] += player_y_momentum  # downward momentum

    if moving_right:
        player_location[0] += 4
    if moving_left:
        player_location[0] -= 4

    player_rect.x = player_location[0]  # player width hitbox
    player_rect.y = player_location[1]  # player height hitbox

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:  # If key is being pressed down
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
        if event.type == KEYUP:  # If key is released (not being held) player does not move
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(60)  # FPS
