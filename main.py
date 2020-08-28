import pygame
from pygame.locals import *
import pyganim

from statistics import mean

import random
import sys
import os
import uuid

"""
# for speed tests
import time
start = time.process_time()
print(time.process_time() - start)
"""

gravity = -1.0
dt = -0.1  # timestep


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def screenshot():
    pygame.image.save(screen, f"screenshot{str(uuid.uuid4())}.jpeg")


def reset_events():
    pygame.time.set_timer(ADDASTEROID, 250)
    pygame.time.set_timer(GAME_TIME, 1000)


def update_fps():
    fps = int(clock.get_fps())
    fps_list.append(fps)
    fps_text = score_font.render(str(fps), True, pygame.Color("coral"))
    return fps_text


def draw():
    screen.blit(skybg, (0, 0))
    pressed_keys = pygame.key.get_pressed()
    player.change_velocity(pressed_keys)
    player.update()
    asteroids.update()
    stars.update()
    for sprite in all_sprites.sprites():
        screen.blit(sprite.image, sprite.rect)
    if player.alive():
        player_animation.blit(
            screen, (player.rect.left - 13, player.rect.top - 3))
    if show_fps:
        screen.blit(update_fps(), (10, 0))
    screen.blit(score, score_rect)


def end_game():
    player.kill()
    pygame.time.set_timer(ADDASTEROID, 0)
    pygame.time.set_timer(GAME_TIME, 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__(all_sprites)
        self.image = pygame.image.load(player_image).convert_alpha()
        self.rect = pygame.Rect(0, 0, 19, 46)
        self.rect.center = (screen_width_half, screen_height)
        self.score = 0
        self.velocity = [0, 0, 0, 0]
        self.speed = 7

    def change_velocity(self, key_press):
        if key_press[K_LEFT]:
            self.velocity[0] = -self.speed
        if key_press[K_RIGHT]:
            self.velocity[1] = self.speed
        if key_press[K_UP]:
            self.velocity[2] = -self.speed
        if key_press[K_DOWN]:
            self.velocity[3] = self.speed

    def velocity_decay(self):
        for i in range(len(self.velocity)):
            if self.velocity[i] > 0:
                self.velocity[i] -= 0.7
            elif self.velocity[i] < 0:
                self.velocity[i] += 0.7

    def update(self):
        x_change = self.velocity[0] + self.velocity[1]
        y_change = self.velocity[2] + self.velocity[3]
        if x_change:
            if self.velocity[0] + self.velocity[1] > 0:
                x_change = self.velocity[1]
            else:
                x_change = self.velocity[0]
        if y_change:
            if self.velocity[2] + self.velocity[3] > 0:
                y_change = self.velocity[3]
            else:
                y_change = self.velocity[2]
        movement = [x_change, y_change]
        self.rect.move_ip(*movement)
        self.velocity_decay()

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > screen_height:
            self.rect.bottom = screen_height


class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super(Asteroid, self).__init__(asteroids, all_sprites)
        self.image = pygame.image.load(
            asteroid_images[random.randint(0, 2)]).convert()
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.image.get_rect(
            center=(random.randint(0, screen_width), 0))
        self.speed = int(5 * difficulty_time)
        self.size = self.image.get_rect()[2], self.image.get_rect()[3]

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom > screen_height + self.size[1]:
            if player.alive():
                player.score += 1
            self.kill()


class Star(pygame.sprite.Sprite):
    def __init__(self):
        super(Star, self).__init__(stars, all_sprites)
        self.image = pygame.image.load(
            star_images[random.randint(0, 3)]).convert_alpha()
        self.image.set_colorkey((255, 255, 255), RLEACCEL)
        self.size = self.image.get_rect()[2], self.image.get_rect()[3]
        self.side = random.choice([True, False])
        self.x_vel = random.randint(9, 15)
        self.y_vel = 0
        starting_point = 0 - (0.5 * self.size[0])
        if self.side:
            self.x_vel *= -1
            starting_point = screen_width + (0.5 * self.size[0])
        self.rect = self.image.get_rect(
            center=(starting_point, random.randint(0, screen_height)))

    def update(self):
        self.y_vel = self.y_vel + gravity * dt  # vertical velocity of the sprite
        self.rect.move_ip(self.x_vel, (self.y_vel + dt))
        if self.side:
            if self.rect.right < 0:
                self.kill()
        else:
            if self.rect.left > screen_width:
                self.kill()


difficulty_time = 1

show_fps = False
fps_list = []

pygame.init()

display_screen_width = int(pygame.display.Info().current_w)
display_screen_height = int(pygame.display.Info().current_h)

screen_width = display_screen_width
screen_height = display_screen_height

if display_screen_width > 600:
    screen_width = 600
else:
    screen_width -= 150

if display_screen_height > 800:
    screen_height = 800
else:
    screen_height -= 150

screen_width_half = screen_width / 2
screen_height_half = screen_height / 2

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (
    (display_screen_width / 2) - screen_width_half, display_screen_height / 2 - screen_height_half)

player_image = resource_path("assets/images/empty.png")
player_animation = pyganim.PygAnimation([(resource_path("assets/images/rocket.png"), 100),
                                         (resource_path(
                                             "assets/images/rocket1.png"), 100),
                                         (resource_path(
                                             "assets/images/rocket2.png"), 100),
                                         (resource_path(
                                             "assets/images/rocket3.png"), 100),
                                         (resource_path("assets/images/rocket4.png"), 100)])
player_animation.play()

asteroid_images = [resource_path("assets/images/meteorlarge.png"), resource_path("assets/images/meteormedium.png"),
                   resource_path("assets/images/meteorsmall.png")]
star_images = [resource_path("assets/images/starsmall.png"), resource_path("assets/images/starsmall2.png"),
               resource_path("assets/images/starmedium.png"), resource_path("assets/images/starlarge.png")]

skybg = pygame.image.load(resource_path("assets/images/skybg.jpg"))
skybg = pygame.transform.scale(skybg, (screen_width, screen_height))

program_icon = pygame.image.load(resource_path("assets/images/rocket.png"))
pygame.display.set_icon(program_icon)
pygame.display.set_caption("Touhou 69")

screen = pygame.display.set_mode(
    (screen_width, screen_height), DOUBLEBUF | HWSURFACE)

score_font = pygame.font.Font(resource_path(
    "assets/fonts/Audiowide-Regular.ttf"), 40)
score = score_font.render(f"Score: 0", True, (255, 255, 255))
score_rect = score.get_rect()
score_rect.center = (screen_width_half, 20)

asteroids = pygame.sprite.Group()
stars = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
player = Player()
clock = pygame.time.Clock()

# Create custom events for adding a new enemy.
ADDASTEROID = pygame.USEREVENT + 1
ADDSTAR = pygame.USEREVENT + 2
GAME_TIME = pygame.USEREVENT + 3

pygame.time.set_timer(ADDSTAR, 200)
reset_events()

running = True

while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_r:
                for entity in all_sprites.sprites():
                    entity.kill()
                difficulty_time = 1
                reset_events()
                score_rect.center = (screen_width_half, 20)
                player = Player()
                all_sprites.add(player)
            elif event.key == K_F2:
                screenshot()
            elif event.key == K_F3:
                show_fps = not show_fps
        elif event.type == QUIT:
            running = False
        elif event.type == ADDASTEROID:
            new_enemy = Asteroid()
        elif event.type == ADDSTAR:
            new_star = Star()
        elif event.type == GAME_TIME:
            difficulty_time += 0.1
            difficulty_log = (difficulty_time * 10) - 10
            difficulty_log = (500 * (difficulty_log ** 2)) / \
                ((difficulty_log ** 2) + (10 * difficulty_log))
            pygame.time.set_timer(ADDASTEROID, int(600 - difficulty_log))

    score = score_font.render(f"Score: {player.score}", True, (255, 255, 255))
    draw()

    if pygame.sprite.spritecollideany(player, asteroids):
        end_game()
        score_rect.center = (screen_width_half, screen_height_half)

    pygame.display.flip()
    clock.tick(60)

if fps_list:
    print(mean(fps_list))
