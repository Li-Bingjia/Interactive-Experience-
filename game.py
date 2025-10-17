import pygame
import sys

# 初始化
pygame.init()

# --- 基本设置 ---
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
MOVE_SPEED = 5

# 颜色
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
GREEN = (100, 200, 100)
BLACK = (0, 0, 0)

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("平台跳跃 Demo")
clock = pygame.time.Clock()

# --- 玩家类 ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT - 150)
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0

        # 左右移动
        if keys[pygame.K_LEFT]:
            dx = -MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            dx = MOVE_SPEED

        # 跳跃
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        # 重力
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10

        # 移动
        self.rect.x += dx
        self.rect.y += self.vel_y

        # 边界限制
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        # 碰撞检测
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0 and self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

# --- 平台类 ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))

# --- 生成对象 ---
player = Player()
platforms = pygame.sprite.Group()

# 地面平台
ground = Platform(0, HEIGHT - 50, WIDTH, 50)
platforms.add(ground)

# 其他平台
platforms.add(Platform(200, 450, 150, 20))
platforms.add(Platform(450, 350, 200, 20))
platforms.add(Platform(300, 250, 120, 20))

# --- 游戏主循环 ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 更新逻辑
    player.update(platforms)

    # 绘制
    screen.fill(WHITE)
    platforms.draw(screen)
    screen.blit(player.image, player.rect)

    # 刷新画面
    pygame.display.flip()
    clock.tick(FPS)
