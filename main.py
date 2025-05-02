import pygame
from map import lvl1
pygame.init()

width, height = 800, 600

window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fantasy Hackaton 2025")
pygame.display.set_icon(pygame.image.load("images/ground.png"))
bg = pygame.image.load("images/bg.png")
bg = pygame.transform.scale(bg, (width, height))

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
        self.img_r = self.img
        self.img_l = pygame.transform.scale(img2, (w, h))
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
            self.rect.left -= self.speed
            if self.check_collisions(plats) or self.rect.x < 0:
                self.rect.x = orig_x
        if keys[pygame.K_d]:
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
            self.hp -= 1
            self.rect.x, self.rect.y = self.start_x, self.start_y
            camera.rect.x, camera.rect.y = 0, 0
        else:
            game = False
            

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


camera = Camera(0, 0, width, height, 2)

block_img = pygame.image.load("images/ground.png")
block2_img = pygame.image.load("images/ground2.png")
wall_img = pygame.image.load("images/wall.png")

block_size = 40
block_x, block_y = 0, -600
blocks = []
lifts = []
spikes = []

for row in lvl1:
    for tile in row:
        if tile == 1:
            blocks.append(Sprite(block_x, block_y, block_size, block_size, block_img))
        elif tile == 2:
            blocks.append(Sprite(block_x, block_y, block_size, block_size, wall_img))
        elif tile == 3:
            spikes.append(Sprite(block_x, block_y, block_size, block_size, pygame.image.load("images/spike.png")))
        elif tile == 4:
            lifts.append(Lift(80, 40, wall_img, 1, block_x, 0, block_y, 300, "vertical"))
        elif tile == 11:
            blocks.append(Sprite(block_x, block_y, block_size, block_size, block2_img))

        block_x += block_size
    block_x = 0
    block_y += block_size
    
player = Player(50, 490, 30, 70, pygame.image.load("images/player.png"), pygame.image.load("images/player.png"), 1, 12)
    
game = True
while game:
    window.blit(bg, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
    
    for block in blocks:
        block.draw()
    
    for spike in spikes:
        spike.draw()
        
    for l in lifts:
        l.draw()
        l.move()
    
    if any(player.rect.colliderect(s.rect) for s in spikes):
        player.damage()
    
    player.draw()
    player.move(blocks)
    player.jumping(blocks, lifts)
    camera.move(player)
    
    pygame.display.update()

pygame.quit()
