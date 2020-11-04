import pygame
import sys
import os
import random

pygame.init()  # initialize pygame
clock = pygame.time.Clock()

from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 512)  # frequency, size (1=mono 2=stereo), buffer to make non delayed sounds
pygame.mixer.set_num_channels(64)  # number of channels for sounds to play

pygame.display.set_caption('Basic Platformer')
WINDOW_SIZE = (900, 600)

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initialize the window

display = pygame.Surface((300, 200))  # renders all pixels twice as large in relation to the window screen

moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0

true_scroll = [0, 0]

grass_image = pygame.image.load('grass.png')
TILE_SIZE = grass_image.get_width()  # width of grass tiles which is 16px
dirt_image = pygame.image.load('dirt.png')
plant_img = pygame.image.load('plant.png').convert()
plant_img.set_colorkey((255, 255, 255))

tile_index = {1: grass_image,
              2: dirt_image,
              3: plant_img
              }

grass_sound_timer = 0  # to stop sound from constantly playing
jump_sound = pygame.mixer.Sound('jump.wav')
grass_sounds = [pygame.mixer.Sound('grass_0.wav'), pygame.mixer.Sound('grass_1.wav')]
pygame.mixer.music.load('music.wav')
pygame.mixer.music.play(-1)  # -1 plays infinitely
grass_sounds[0].set_volume(0.2)
grass_sounds[1].set_volume(0.2)

CHUNK_SIZE = 8


def generate_chunk(x, y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0  # nothing
            if target_y > 10:
                tile_type = 2  # dirt
            elif target_y == 10:
                tile_type = 1  # grass
            elif target_y == 9:
                if random.randint(1, 5) == 1:
                    tile_type = 3  # plant
            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])
    return chunk_data


global animation_frames
animation_frames = {}


def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255, 255, 255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


animation_database = {}

animation_database['run'] = load_animation('player_animations/run', [7, 7])
animation_database['idle'] = load_animation('player_animations/idle', [7, 7, 40])

player_action = 'idle'
player_frame = 0
player_flip = False

game_map = {}


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
player_rect = pygame.Rect(100, 100, 5, 13)
background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [0.5, [30, 40, 40, 400]],
                      [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]

while True:  # game loop
    display.fill((146, 244, 255))

    if grass_sound_timer > 0:
        grass_sound_timer -= 1

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
    for y in range(3):
        for x in range(4):
            target_x = x - 1 + int(round(scroll[0] / (CHUNK_SIZE * 16)))
            target_y = y - 1 + int(round(scroll[1] / (CHUNK_SIZE * 16)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = generate_chunk(target_x, target_y)
            for tile in game_map[target_chunk]:
                display.blit(tile_index[tile[1]], (tile[0][0] * 16 - scroll[0], tile[0][1] * 16 - scroll[1]))
                if tile[1] in [1, 2]:
                    tile_rects.append(pygame.Rect(tile[0][0] * 16, tile[0][1] * 16, 16, 16))

    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += vertical_momentum  # up
    vertical_momentum += 0.2  # Gravity speed (always falling)
    if vertical_momentum > 3:  # constant downward acceleration cap
        vertical_momentum = 3

    if player_movement[0] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = False
    if player_movement[0] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')
    if player_movement[0] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = True

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:  # solves infinite jump issue
        vertical_momentum = 0
        air_timer = 0
        if player_movement[0] != 0:  # moving on the x axis
            if grass_sound_timer == 0:  # will only play if timer is 0
                grass_sound_timer = 30  # stops the sound from constantly playing
                random.choice(grass_sounds).play()
    else:
        air_timer += 1  # if you're in the air add 1 to your leeway timer
    if collisions['top']:
        vertical_momentum = 0  # reset player momentum once head hits tile (to stop sticking)

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img, player_flip, False),
                 (player_rect.x - scroll[0], player_rect.y - scroll[1]))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:  # If key is being pressed down
            if event.key == K_w:
                pygame.mixer.music.fadeout(2000)
            if event.key == K_e:
                pygame.mixer.music.play(-1)
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:  # 6 frames (jumping leeway off a platform)
                    vertical_momentum = -5  # Upward jumping momentum
                    jump_sound.play()
        if event.type == KEYUP:  # If key is released (not being held) player does not move
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(60)  # FPS
