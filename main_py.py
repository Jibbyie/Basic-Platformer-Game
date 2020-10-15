import pygame
import sys

clock = pygame.time.Clock()

from pygame.locals import *

pygame.init()  # initialize pygame
pygame.display.set_caption('Basic Platformer')
WINDOW_SIZE = (900, 600)

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initialize the window

display = pygame.Surface((300, 200))  # renders all pixels twice as large in relation to the window screen

moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0

true_scroll = [0, 0]

player_image = pygame.image.load('player.png').convert()
player_image.set_colorkey((255, 255, 255))  # "Green screen", makes white border transparent

grass_image = pygame.image.load('grass.png')
TILE_SIZE = grass_image.get_width()  # width of grass tiles which is 16px
dirt_image = pygame.image.load('dirt.png')


def load_map(path):
    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map


game_map = load_map('map')


def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list


def move(rect, movement, tiles):  # x and y movement, thing moving/how/what it runs into
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)  # rect refers to player
    for tile in hit_list:
        if movement[0] > 0:  # moving right on the x axis
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:  # moving left on the x axis
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:  # y axis is flipped
        if movement[1] > 0:  # moving down on the y axis
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:  # moving  on up the y axis
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


# Essentially the players "hitbox"
player_rect = pygame.Rect(50, 50, player_image.get_width(), player_image.get_height())
background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [0.5, [30, 40, 40, 400]],
                      [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]

while True:  # game loop
    display.fill((146, 244, 255))

    true_scroll[0] += (player_rect.x - true_scroll[0] - 152) / 20  # half x axis, extra 2 references player width
    true_scroll[1] += (player_rect.y - true_scroll[1] - 106) / 20  # half y axis, extra 6 references player height
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                               background_object[1][1] - scroll[1] * background_object[0], background_object[1][2],
                               background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), obj_rect)
        else:
            pygame.draw.rect(display, (9, 91, 85), obj_rect)
    tile_rects = []  # keep track of tiles to be used for collisions
    y = 0
    for layer in game_map:
        x = 0
        for tile in layer:
            if tile == '1':  # 1 = dirt
                display.blit(dirt_image, (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))  # rendering images
            if tile == '2':  # 2 = grass
                display.blit(grass_image,
                             (x * TILE_SIZE - scroll[0], y * TILE_SIZE - scroll[1]))  # TILE_SIZE refers to pixel width
                # referenced above
            if tile != '0':  # if tile is not air
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1  # iterate across the row
        y += 1  # move to next column

    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += vertical_momentum  # up
    vertical_momentum += 0.2  # Gravity speed (always falling)
    if vertical_momentum > 3:  # constant downward acceleration cap
        vertical_momentum = 3

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:  # solves infinite jump issue
        vertical_momentum = 0
        air_timer = 0
    else:
        air_timer += 1  # if you're in the air add 1 to your leeway timer
    if collisions['top']:
        vertical_momentum = 0  # reset player momentum once head hits tile (to stop sticking)

    display.blit(player_image, (player_rect.x - scroll[0], player_rect.y - scroll[1]))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:  # If key is being pressed down
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:  # 6 frames (jumping leeway off a platform)
                    vertical_momentum = -5  # Upward jumping momentum
        if event.type == KEYUP:  # If key is released (not being held) player does not move
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(60)  # FPS
