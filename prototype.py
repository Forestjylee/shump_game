import os
import pygame
import random

# Global config
WIDTH = 480
HEIGHT = 480
FPS = 30

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Init
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Game')
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# setup asset folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'imgs')


class Player(pygame.sprite.Sprite):
    def __init__(self):
        # must have image and rect property
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        # self.image.set_colorkey(BLACK) #  ignore any pixels of the specified color
        self.rect = self.image.get_rect()
        # We can use the rect to put the sprite wherever we want it on the screen.
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
    
    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
    
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top+1)
        all_sprites.add(bullet)
        bullets.add(bullet)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedx = random.randrange(-3, 3)
        self.speedy = random.randrange(3, 8)
    
    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.right < -5 or self.rect.left > WIDTH + 5:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
    
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()  # remove this sprite from all groups


if __name__ == '__main__':
    player = Player()
    all_sprites.add(player)
    
    for _ in range(8):
        enemy = Mob()
        all_sprites.add(enemy)
        mobs.add(enemy)
    
    is_hold_shoot = False
    running = True
    while running:
        clock.tick(FPS)
        # Process input (events)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_hold_shoot = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    is_hold_shoot = False
        
        # Update
        all_sprites.update()
        if is_hold_shoot:
            player.shoot()
        
        # check to see if a mob hit the player
        hits = pygame.sprite.spritecollide(player, mobs, False)
        if hits:
            running = False
            
        # check if a bullet hit a mob
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            m = Mob()
            all_sprites.add(m)
            mobs.add(m)
        
        # Render (draw)
        screen.fill(BLUE)
        all_sprites.draw(screen)
        
        # after drawing everything, flip the display
        pygame.display.flip()
    
    pygame.quit()
