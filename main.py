import os
import sys
import pygame
import random

# Global config
WIDTH = 480
HEIGHT = 480
FPS = 50

# Colors (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Init
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Game')
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# setup asset folders
# game_folder = os.path.dirname(__file__)
game_folder = os.path.abspath('.')
img_folder = os.path.join(game_folder, 'imgs')
snd_folder = os.path.join(game_folder, 'snds')

background = pygame.image.load(os.path.join(img_folder, 'bg.png')).convert()
background_rect = background.get_rect()
bg_starty = -background_rect.bottom  # 用于实现背景移动

player_img = pygame.image.load(os.path.join(img_folder, "playerShip2_red.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(os.path.join(img_folder, "laserRed16.png")).convert()

meteor_images = []
meteor_list =['meteorBrown_big1.png','meteorBrown_med1.png',
            'meteorBrown_med1.png','meteorBrown_med3.png',
            'meteorBrown_small1.png', 'meteorBrown_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(os.path.join(img_folder, img)).convert())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)


shoot_sound = pygame.mixer.Sound(os.path.join(snd_folder, "shoot.wav"))
shoot_sound.set_volume(0.3)
expl_sounds = []
for snd in ['Explosion1.wav', 'Explosion2.wav']:
    temp = pygame.mixer.Sound(os.path.join(snd_folder, snd))
    temp.set_volume(0.3)
    expl_sounds.append(temp)
pygame.mixer.music.load(os.path.join(snd_folder, "tgfcoder-FrozenJam-SeamlessLoop.ogg"))
pygame.mixer.music.set_volume(0.3)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        # must have image and rect property
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.smoothscale(player_img, (50, 38))
        self.image.set_colorkey(BLACK) #  ignore any pixels of the specified color
        self.rect = self.image.get_rect()
        self.radius = 25
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        # We can use the rect to put the sprite wherever we want it on the screen.
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        self.shield = 100
        
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        
        self.shoot_delay = 250
        self.last_shoot = pygame.time.get_ticks()
    
    def update(self):
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if keystate[pygame.K_UP]:
            self.speedy -= 5 
        if keystate[pygame.K_DOWN]:
            self.speedy += 5
        if keystate[pygame.K_SPACE]:
            self.shoot()
        
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            bullet = Bullet(self.rect.centerx, self.rect.top+1)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()
            
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+200)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedx = random.randrange(-3, 3)
        self.speedy = random.randrange(3, 8)
        
        # rotation
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()  # for controlling animation speed
    
    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.right < -5 or self.rect.left > WIDTH + 5:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50: # ms
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            # Rotation is destructive!
            # Only rotate once
            self.image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
    
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()  # remove this sprite from all groups


def draw_bg(screen, background, background_rect):
    global bg_starty
    if bg_starty >= 0:
        bg_starty = -background_rect.bottom
    else:
        bg_starty += int(background_rect.bottom / 100)
    # 平铺背景图
    for y in range(bg_starty, HEIGHT+abs(bg_starty), background_rect.bottom):
        for x in range(0, WIDTH, background_rect.right):
            screen.blit(background, (x, y))


def draw_text(surface, text, size, x, y, font_name='arial'):
    font_type = pygame.font.match_font(font_name)
    font = pygame.font.Font(font_type, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


def draw_shield_bar(surface, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def show_start_screen():
    global bg_starty
    # for y in range(0, WIDTH, background_rect.bottom):
    #     for x in range(0, HEIGHT, background_rect.right):
    #         screen.blit(background, (x, y))
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYUP:
                waiting = False
        draw_bg(screen, background, background_rect)
        draw_text(screen, "SHMUP!", 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, "方向键移动, 空格键开火, 回车键暂停", 22,
                WIDTH / 2, HEIGHT / 2, 'SimHei')
        draw_text(screen, "按下任何键开始", 18, WIDTH / 2, HEIGHT * 3 / 4, 'SimHei')
        pygame.display.flip()
    return True


def show_game_over_screen(scores):
    global bg_starty
    # for y in range(0, WIDTH, background_rect.bottom):
    #     for x in range(0, HEIGHT, background_rect.right):
    #         screen.blit(background, (x, y))
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYUP:
                waiting = False
        draw_bg(screen, background, background_rect)
        draw_text(screen, "SHMUP!", 64, WIDTH / 2, HEIGHT / 4)
        draw_text(screen, f"您的分数是: {scores}", 22,
                WIDTH / 2, HEIGHT / 2, 'SimHei')
        draw_text(screen, "按下任何键继续", 18, WIDTH / 2, HEIGHT * 3 / 4, 'SimHei')
        pygame.display.flip()
    return True


if __name__ == '__main__':
    player = Player()
    all_sprites.add(player)
    
    for _ in range(8):
        enemy = Mob()
        all_sprites.add(enemy)
        mobs.add(enemy)
    scores = 0
    
    pygame.mixer.music.play(loops=-1)
    is_pause = False
    game_over = False
    is_start = False
    running = True
    while running:
        clock.tick(FPS)
        if game_over:
            if not show_game_over_screen(scores):
                break
            game_over = False
            
        if not is_start:
            if not show_start_screen():
                break
            is_start = True
            all_sprites = pygame.sprite.Group()
            mobs = pygame.sprite.Group()
            bullets = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            for _ in range(8):
                newmob()
            scores = 0

        # Process input (events)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                is_pause = True
                new_WIDTH = event.size[0]
                new_HEIGHT = event.size[1]
                player.rect.centerx = int(player.rect.centerx * new_WIDTH / WIDTH)
                player.rect.centery = int(player.rect.centery * new_HEIGHT / HEIGHT)
                WIDTH = new_WIDTH
                HEIGHT = new_HEIGHT
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    is_pause = not is_pause
            elif event.type == pygame.KEYUP:
                pass
        
        if is_pause:
            continue
        
        # Update
        all_sprites.update()
        # hold space for continuous shoot
        # if is_hold_shoot:
        #     player.shoot()
        
        # check to see if a mob hit the player
        # hits = pygame.sprite.spritecollide(player, mobs, False)  # rectangle collision check
        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            player.shield -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            m = Mob()
            all_sprites.add(m)
            mobs.add(m)
            
            if player.shield <= 0:
                death_explosion = Explosion(player.rect.center, 'lg')
                all_sprites.add(death_explosion)
                player.hide()
                player.lives -= 1
                player.shield = 100
            
            if player.lives == 0 and not death_explosion.alive():
                game_over = True
                is_start = False
            
        # check if a bullet hit a mob
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            scores += 50 - hit.radius
            random.choice(expl_sounds).play()
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            m = Mob()
            all_sprites.add(m)
            mobs.add(m)
        
        # Render (draw)
        draw_bg(screen, background, background_rect)
        # screen.blit(pygame.transform.scale(background, (WIDTH, HEIGHT)), (0, 0))
        all_sprites.draw(screen)
        draw_text(screen, f"Scores: {str(scores)}", 18, WIDTH/2, 10)
        draw_shield_bar(screen, 5, 5, player.shield)
        draw_lives(screen, WIDTH-100, 5,  player.lives, player_mini_img)
        
        # after drawing everything, flip the display
        pygame.display.flip()
    
    pygame.quit()
