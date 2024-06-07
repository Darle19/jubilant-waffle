import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1920, 1080
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip_sprites(sprite_list):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprite_list]


def load_sprites(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    files = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}
    for file in files:
        sprite = pygame.image.load(join(path, file)).convert_alpha()
        sprites = []
        for i in range(sprite.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        if direction:
            all_sprites[file.replace(".png", "") + "_left"] = flip_sprites(sprites)
            all_sprites[file.replace(".png", "") + "_right"] = sprites
        else:
            all_sprites[file.replace(".png", "")] = sprites
    return all_sprites


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprites("MainCharacters", "Muj", 128, 128, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        self.count = None
        self.jump_count = 0
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = 'left'
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0

    def jump(self):
        self.y_vel = self.GRAVITY * 9
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != 'left':
            self.direction = 'left'
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != 'right':
            self.direction = 'right'
            self.animation_count = 0

    def loop(self, fps):

        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        self.fall_count += 1
        self.update_sprite()

    def update_sprite(self):
        sprite_sheet = "Idle"
        if self.x_vel != 0:
            sprite_sheet = "Run"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update_mask()

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win):
        win.blit(self.sprite, (self.rect.x, self.rect.y))

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def draw_window(window, background, player, objects):
    window.blit(background, (0, 0))
    for block in objects:
        block.draw(window)

    player.draw(window)
    pygame.display.update()


def load_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    block = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 125, size, size)
    surface.blit(block, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
        collided_objects.append(obj)
    return collided_objects


def handle_movement(player, objects):
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    if keys[pygame.K_a]:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d]:
        player.move_right(PLAYER_VEL)

    handle_vertical_collision(player, objects, player.y_vel)


def main(window):
    block_size = 96
    clock = pygame.time.Clock()
    route = join("assets", "Background", "L1.png")
    background = pygame.image.load(route)
    player = Player(100, 100, 128, 128)
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        player.loop(FPS)
        handle_movement(player, floor)
        draw_window(window, background, player, floor)
    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)