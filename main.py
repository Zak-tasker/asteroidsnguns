import pygame
import random
from pygame import Vector2
from pygame.transform import rotozoom


def wrap_position(position, screen):
    x, y = position  # where are we
    w, h = screen.get_size()  # how big is the screen
    return Vector2(x % w, y % h)


class Ship:
    def __init__(self, position, player):
        # initialise stats
        self.position = Vector2(position)
        self.player = player
        self.dead = 0
        self.extraDead = 0
        # set sprite
        self.image = pygame.image.load('ship' + str(self.player) + '.png')
        # misc variables
        self.forward = Vector2(0, -1.5)
        self.velocity = 1
        self.particle_timer = 0
        self.particles = []
        self.explosion_timer = 0
        self.can_shoot = 0
        self.bullets = []
        self.drift = (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
        self.hitbox = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

        # tutorial display variables
        self.tutorial = True
        self.tutorialX = []
        self.tutorialY = []
        self.tutorialBright = 255

        # distributing control schemes between each player
        if self.player == 0:
            self.controls = [pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SLASH]
        else:
            self.controls = [pygame.K_w, pygame.K_a, pygame.K_d, pygame.K_g]

    def update(self):
        # setting a variable to a key input
        is_key_pressed = pygame.key.get_pressed()

        # collision detection & handling
        for a in asteroids:
            if self.hitbox.colliderect(a.hitbox):
                self.velocity = 0
            else:
                self.velocity = 1

        # checking if the player has made an input
        for i in range(4):
            if is_key_pressed[self.controls[i]]:
                # disabling the tutorial
                self.tutorial = False

        # forward
        if is_key_pressed[self.controls[0]]:
            self.position += self.forward * self.velocity
            self.drift = (self.drift + self.forward) / 1.5
            if self.particle_timer == 0:
                self.particles.append(Particle(Vector2(self.position), self.forward * -1.5, 10))
                self.particle_timer = 3
            else:
                self.particle_timer -= 1

        # left
        if is_key_pressed[self.controls[1]]:
            self.forward = self.forward.rotate(-5)

        # right
        if is_key_pressed[self.controls[2]]:
            self.forward = self.forward.rotate(5)

        # bang bang blam blam gun go pew pew shooty shooty
        if is_key_pressed[self.controls[3]] and self.can_shoot == 0:
            self.bullets.append(Bullet(Vector2(self.position), self.forward * 6))
            self.can_shoot = 250

        self.position += self.drift

        if self.can_shoot > 0:
            self.can_shoot -= clock.get_time()
        else:
            self.can_shoot = 0
        # update hitbox position
        self.hitbox.center = self.position

        # update tutorial graphic position
        self.tutorialX = [self.position.x + self.image.get_width(), self.position.x - self.image.get_width() * 4]
        self.tutorialY = [self.position.y - self.image.get_height() * 2,
                          self.position.y + self.image.get_height() * 0.2]
        # tutorial fadeout
        if self.tutorial == False:
            self.tutorialBright -= 5

    def draw(self, screen):
        self.position = wrap_position(self.position, screen)
        angle = self.forward.angle_to(Vector2(0, -1))
        rotated_surface = rotozoom(self.image, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size // 2
        screen.blit(rotated_surface, blit_position)

        # debug hitbox draw
        pygame.draw.rect(screen, (0, 0, 255), self.hitbox, 2)

        # render tutorial for each player
        tutorial = pygame.transform.scale2x(pygame.image.load("controls" + str(self.player) + ".png"))
        tutorial.set_alpha(self.tutorialBright)
        screen.blit(tutorial, (self.tutorialX[self.player], self.tutorialY[self.player]))

    def die(self):
        # play death animation once and stop
        if not self.extraDead:
            self.particles.append(Particle(Vector2(self.position), self.forward * 0, 40))
            self.extraDead = 1


# thruster particles
class Particle:
    def __init__(self, position, velocity, size):
        self.position = position
        self.velocity = velocity
        self.size = size
        # variable size

    def update(self):
        self.position += self.velocity
        self.size -= 0.5
        # shrink

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), [self.position.x, self.position.y], self.size)
        pygame.draw.circle(screen, (0, 0, 0), [self.position.x, self.position.y], self.size * 0.9)
        # draws a white circle with a smaller black circle inside it to create a ring effect


class Bullet:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity
        self.size = 4
        self.flicker = 0
        self.hitbox = pygame.Rect(0, 0, self.size, self.size)

    def update(self):
        self.position += self.velocity
        # faint flicker to allow bullets to stand out on screen
        self.flicker = random.randint(125, 255)
        # hitbox position update
        self.hitbox.center = self.position
        # collision check
        for a in asteroids:
            if self.hitbox.colliderect(a.hitbox):
                self.size = 0
                self.hitbox = pygame.Rect(0, 0, self.size, self.size)

    def draw(self, screen):
        pygame.draw.rect(screen, (self.flicker, self.flicker, self.flicker),
                         [self.position.x, self.position.y, self.size, self.size])
        # debug hitbox render
        # pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)


class Asteroid:
    def __init__(self, position):
        self.position = Vector2(position)
        self.velocity = Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        self.image = pygame.transform.scale2x((pygame.image.load('asteroid' + str(random.randint(0, 3)) + '.png')))
        self.angle = random.randint(0, 360)
        # random spin velocity
        self.spinVelocity = random.uniform(-1, 1)
        self.hitbox = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

    def update(self):
        self.position += self.velocity
        if self.position.x < out_of_bounds[0] or \
                self.position.x > out_of_bounds[2]:
            self.velocity.x *= -1
        if self.position.y < out_of_bounds[1] or \
                self.position.y > out_of_bounds[3]:
            self.velocity.y *= -1
        # hitbox position update
        self.hitbox.center = self.position

    def draw(self, screen):
        # draw with rotation
        self.angle += self.spinVelocity
        rotated_surface = rotozoom(self.image, self.angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size // 2
        screen.blit(rotated_surface, blit_position)
        # debug hitbox render
        # pygame.draw.rect(screen, (0, 255, 0), self.hitbox, 2)


pygame.init()
screen = pygame.display.set_mode((960, 640))
pygame.display.set_caption("astroids n' guns")
game_over = False
# restart visual variables
restart = pygame.transform.scale(pygame.image.load("restart.png"), (144, 76))
restartAlpha = 0
restartOverlayScale = 1
restartOverlayScale2 = 1

# player spawns
ship = Ship((screen.get_width() * 0.1, screen.get_height() * 0.85), 0)
ship2 = Ship((screen.get_width() * 0.9, screen.get_height() * 0.15), 1)

asteroids = []
out_of_bounds = [-50, -50, screen.get_height() + 50, screen.get_height() + 50]
# asteroid spawns
for i in range(20):
    asteroids.append(Asteroid((random.randint(screen.get_width() * 0.1, screen.get_width() * 0.9),
                               random.randint(screen.get_height() * 0.1, screen.get_height() * 0.9))))

clock = pygame.time.Clock()

while not game_over:
    clock.tick(55)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
    screen.fill((0, 0, 0))

    # player collision detection and asteroid draw loop
    for a in asteroids:
        if ship.hitbox.colliderect(a.hitbox):
            ship.position -= ship.forward * 2
            ship.drift = (0, 0)
        if ship2.hitbox.colliderect(a.hitbox):
            ship2.position -= ship.forward * 2
            ship2.drift = (0, 0)
        a.update()
        a.draw(screen)

    # particle rendering
    for p in ship.particles:
        p.update()
        p.draw(screen)
    for p in ship2.particles:
        p.update()
        p.draw(screen)

    # bullet rendering
    for b in ship.bullets:
        if ship2.hitbox.colliderect(b.hitbox):
            ship2.dead = 1
        b.update()
        b.draw(screen)
    for b in ship2.bullets:
        if ship.hitbox.colliderect(b.hitbox):
            ship.dead = 1
        b.update()
        b.draw(screen)

    # player rendering
    if not ship.dead:
        ship.update()
        ship.draw(screen)
    else:
        ship.die()
        # fade restart instructions into view and begin screen close-in
        restartAlpha += 1
        restartOverlayScale2 += 2

    if not ship2.dead:
        ship2.update()
        ship2.draw(screen)
    else:
        ship2.die()
        # fade restart instructions into view and begin screen close-in
        restartAlpha += 1
        restartOverlayScale2 += 1

    # detecting the restart key
    is_key_pressed = pygame.key.get_pressed()

    if is_key_pressed[pygame.K_r]:
        # reset object positions and variables
        for a in asteroids:
            asteroids.remove(a)
        for i in range(20):
            asteroids.append(Asteroid((random.randint(screen.get_width() * 0.1, screen.get_width() * 0.9),
                                       random.randint(screen.get_height() * 0.1, screen.get_height() * 0.9))))
        ship = Ship((screen.get_width() * 0.1, screen.get_height() * 0.85), 0)
        ship2 = Ship((screen.get_width() * 0.9, screen.get_height() * 0.15), 1)
        # initialise restart animation
        restartOverlayScale = 500
        restartOverlayScale2 = 1
        restartAlpha = 0

    restartOverlay = pygame.Rect(0, 0, screen.get_width(), screen.get_height())
    # draw restart animation and screen borders
    pygame.draw.rect(screen, (255, 255, 255), restartOverlay, restartOverlayScale2)
    pygame.draw.rect(screen, (0, 0, 0), restartOverlay, restartOverlayScale2 - 2)

    pygame.draw.rect(screen, (255, 255, 255), restartOverlay, restartOverlayScale)
    pygame.draw.rect(screen, (0, 0, 0), restartOverlay, restartOverlayScale - 4)

    if restartOverlayScale > 0:
        restartOverlayScale -= 30

    restart.set_alpha(restartAlpha)
    screen.blit(restart, (0 + restart.get_width() / 4, 0 + restart.get_height() / 4))

    pygame.display.update()
pygame.quit()
