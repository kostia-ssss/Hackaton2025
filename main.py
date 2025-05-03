import pygame
from map import *
pygame.init()

width, height = 800, 600
CanShoot = False
num_of_hearts = 5
score = 0

window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fantasy Hackaton 2025")
pygame.display.set_icon(pygame.image.load("images/ground.png"))
bg = pygame.image.load("images/bg.png")
bg = pygame.transform.scale(bg, (width, height))
music = pygame.mixer.music.load("sounds/main_music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

class Sprite:
    def __init__(self , x , y , w , h, img):
        self.img = img
        self.rect = pygame.Rect(x, y, w, h)
        self.img = pygame.transform.scale(self.img , (w, h))
    
    def draw(self):
        window.blit(self.img , (self.rect.x - camera.rect.x, self.rect.y - camera.rect.y))
        
class Player(Sprite):
    def __init__(self , x , y , w , h , img1, img2 , speed, jumpforce):
        super().__init__(x, y, w, h, img1)
        self.img_l = self.img
        self.img_r = pygame.transform.scale(img2, (w, h))
        self.speed = speed
        self.jumpforce = jumpforce
        self.jump_pressed = False
        self.vel_y = 0
        self.gravity = 0.2
        self.max_fall_speed = 10
        self.CanJump = False
        self.hp = 5
        self.start_x, self.start_y = x, y

    def move(self, plats):
        keys = pygame.key.get_pressed()
        orig_x = self.rect.x

        if keys[pygame.K_a]:
            self.img = self.img_l
            self.rect.left -= self.speed
            if self.check_collisions(plats) or self.rect.x < 0:
                self.rect.x = orig_x
        if keys[pygame.K_d]:
            self.img = self.img_r
            self.rect.x += self.speed
            if self.check_collisions(plats):
                self.rect.x = orig_x

    def jumping(self, plats, lifts):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            if self.CanJump and not self.jump_pressed:
                self.vel_y = -self.jumpforce
                self.CanJump = False
                self.jump_pressed = True
        else:
            self.jump_pressed = False

        self.vel_y += self.gravity
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed

        self.rect.y += self.vel_y
        self.CanJump = False

        for plat in plats + lifts:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.CanJump = True
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

    def check_collisions(self, plats):
        return any(self.rect.colliderect(plat.rect) for plat in plats)
    
    def damage(self):
        global game
        if self.hp > 1:
            hearts.pop(self.hp-1)
            self.hp -= 1
            self.rect.x, self.rect.y = self.start_x, self.start_y
            camera.rect.x, camera.rect.y = 0, 0
        else:
            game = False
    
    def fire(self, pos):
        bullets.append(Bullet(self.rect.centerx + 20,self.rect.y - 15, 10, 10, pygame.image.load("images/bullet.png"), 10, pos))

class Lift(Sprite):
    def __init__(self, w, h, img, speed, x1, x2, y1, y2, type):
        super().__init__(x1, y1, w, h, img)
        self.speed = speed
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.type = type
    
    def move(self):
        if self.type == "horisontal":
            self.rect.x += self.speed
            if self.rect.x >= self.x2 or self.rect.x <= self.x1:
                self.speed *= -1
        elif self.type == "vertical":
            self.rect.y += self.speed
            if self.rect.y >= self.y2 or self.rect.y <= self.y1:
                self.speed *= -1

class Camera:
    def __init__(self, x, y, w, h, speed):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed
    
    def move(self, player: Player):
        margin_x = self.rect.width * 0.3
        margin_x2 = self.rect.width * 0.7
        margin_y = self.rect.height * 0.3
        margin_y2 = self.rect.height * 0.7

        if player.rect.centerx < self.rect.x + margin_x and self.rect.x > 0:
            self.rect.x = player.rect.centerx - margin_x
        elif player.rect.centerx > self.rect.x + margin_x2:
            self.rect.x = player.rect.centerx - margin_x2

        if player.rect.centery < self.rect.y + margin_y:
            self.rect.y = player.rect.centery - margin_y
        elif player.rect.centery > self.rect.y + margin_y2:
            self.rect.y = player.rect.centery - margin_y2

class Bullet(Sprite):
    def __init__(self, x, y, w, h, image, speed, pos):
        super().__init__(x, y, w, h, image)
        self.speed = speed
        v1 = pygame.Vector2(x, y)
        v2 = pygame.Vector2(pos[0], pos[1])
        v3 = v2 - v1
        self.vect = v3.normalize()

    def move(self):
        self.rect.x += self.vect[0] * self.speed
        self.rect.y += self.vect[1] * self.speed
        if self.rect.bottom <= 0 or self.rect.top >= height or self.rect.right <= 0 or self.rect.left >= width:
            bullets.remove(self)

class Portal(Sprite):
    def __init__(self, x, y, w, h, img):
        super().__init__(x, y, w, h, img)
        self.wait = 30
    
    def teleport(self, player: Player, p2):
        if self.wait == 0:
            player.rect.x, player.rect.y = p2.rect.x, p2.rect.y - player.rect.height
            p2.wait = 30

    def reset(self):
        if self.wait > 0:
            self.wait -= 1

camera = Camera(0, 0, width, height, 2)

block_img = pygame.image.load("images/ground.png")
block2_img = pygame.image.load("images/ground2.png")
wall_img = pygame.image.load("images/wall.png")

block_size = 40
block_x, block_y = 0, -600
blocks = []
lifts = []
spikes = []
bullets = []
hearts = []
portals = []
coins = []

for row in lvl2:
    for tile in row:
        if tile == 1:
            blocks.append(Sprite(block_x, block_y, block_size, block_size, block_img))
        elif tile == 2:
            blocks.append(Sprite(block_x, block_y, block_size, block_size, wall_img))
        elif tile == 3:
            spikes.append(Sprite(block_x, block_y, block_size, block_size, pygame.image.load("images/spike.png")))
        elif tile == 4:
            lifts.append(Lift(80, 40, wall_img, 1, block_x, 0, block_y, 300, "vertical"))
        elif tile == 7:
            coins.append(Sprite(block_x, block_y, block_size, block_size, pygame.image.load("images/diamond.png")))
        elif tile == 6:
            coins.append(Sprite(block_x, block_y, block_size, block_size, pygame.image.load("images/coin.png")))
        elif tile == 42:
            lifts.append(Lift(80, 40, wall_img, 1, block_x, 0, block_y, -440+160, "vertical"))
        elif tile == 11:
            blocks.append(Sprite(block_x, block_y, block_size, block_size, block2_img))
        elif tile == 31:
            spikes.append(Sprite(block_x, block_y, block_size, block_size, pygame.image.load("images/spike2.png")))
        elif tile == 5:
            portals.append(Portal(block_x, block_y, block_size/2, block_size, pygame.image.load("images/portal.png")))

        block_x += block_size
    block_x = 0
    block_y += block_size

for i in range(num_of_hearts):
    hearts.append(Sprite(i * 50, 0, 50, 50, pygame.image.load("images/heart.png")))

pl_img = pygame.image.load("images/player.png")
player = Player(50, 490, 30, 70, pl_img, pygame.transform.flip(pl_img, True, False), 1, 12)
gun = Sprite(player.rect.x + 10, player.rect.y - 15, 20, 50, pygame.image.load("images/gun.png"))

game = True
while game:
    window.blit(bg, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                CanShoot = not CanShoot
            if event.key == pygame.K_q and CanShoot:
                pos = pygame.mouse.get_pos()
                world_mouse_pos = (pos[0] + camera.rect.x, pos[1] + camera.rect.y)
                player.fire(world_mouse_pos)
    
    if CanShoot:
        gun.draw()
        if player.img == player.img_r:
            gun.rect.x, gun.rect.y = player.rect.x+20, player.rect.y-15
        else:
            gun.rect.x, gun.rect.y = player.rect.x-10, player.rect.y-15
    
    for block in blocks:
        block.draw()
    
    for c in coins:
        c.draw()
        if player.rect.colliderect(c.rect):
            if c.img == pygame.image.load("images/diamond.png"):
                score += 50
            else:
                score += 1
            coins.remove(c)
    
    for h in hearts:
        h.draw()
        h.rect.y = camera.rect.y
        h.rect.x = camera.rect.x + hearts.index(h)*50
    
    for spike in spikes:
        spike.draw()
    
    for p in portals:
        p.draw()
        p.reset()
        
    for l in lifts:
        l.draw()
        l.move()
    
    for b in bullets[:]:
        b.draw()
        b.move()
    
    if any(player.rect.colliderect(s.rect) for s in spikes):
        player.damage()
    
    player.draw()
    player.move(blocks)
    player.jumping(blocks, lifts)
    for i in range(len(portals)):
        for j in range(len(portals)):
            if i != j and player.rect.colliderect(portals[i].rect):
                portals[i].teleport(player, portals[j])
    camera.move(player)
    print(score)
    
    pygame.display.update()

pygame.quit()
