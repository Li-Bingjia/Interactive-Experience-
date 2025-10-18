import pygame, sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE=(255,255,255)
GREEN=(100,200,100)
bg = pygame.image.load("bg.png").convert()
LEVEL_WIDTH = bg.get_width()  # 比如 3000

# 定义人物尺寸
PLAYER_W, PLAYER_H = 40, 60
player = pygame.Rect(100, 100, PLAYER_W, PLAYER_H)

vel_y = 0
gravity = 0.8
on_ground = False
player_speed = 5

platforms = [
    pygame.Rect(0, HEIGHT-50, WIDTH, 50),
    pygame.Rect(200, 450, 150, 20),
    pygame.Rect(450, 350, 200, 20)
]

def draw_person(surface, rect):
    """在rect区域内画一个简易小人"""
    # 创建透明layer绘人
    person = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    cx = rect.width // 2

    # 头
    pygame.draw.circle(person, (245,205,160), (cx, 12), 10)
    pygame.draw.circle(person, (0,0,0), (cx-3,11), 2)
    pygame.draw.circle(person, (0,0,0), (cx+3,11), 2)

    # 身体
    pygame.draw.line(person, (50,150,255), (cx, 22), (cx, 45), 6)

    # 手
    pygame.draw.line(person, (50,150,255), (cx, 28), (cx-14, 38), 4)
    pygame.draw.line(person, (50,150,255), (cx, 28), (cx+14, 38), 4)

    # 腿
    pygame.draw.line(person, (0,0,0), (cx, 45), (cx-10, 60), 5)
    pygame.draw.line(person, (0,0,0), (cx, 45), (cx+10, 60), 5)

    # 画到主surface
    surface.blit(person, rect.topleft)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed

    if keys[pygame.K_SPACE] and on_ground:
        vel_y = -15
        on_ground = False

    vel_y += gravity
    player.x += dx
    player.y += vel_y

    on_ground = False
    for p in platforms:
        if player.colliderect(p) and vel_y > 0:
            player.bottom = p.top
            vel_y = 0
            on_ground = True

   # ==== 摄像机逻辑 ====
    camera_x = player.x - WIDTH // 2
    camera_x = max(0, min(camera_x, LEVEL_WIDTH - WIDTH))

    # ==== 绘制背景 ====
    screen.blit(bg, (-camera_x, 0))

    # ==== 绘制平台 ====
    for p in platforms:
        pygame.draw.rect(screen, GREEN, (p.x - camera_x, p.y, p.width, p.height))

    # ==== 绘制玩家 ====
    draw_person(screen, pygame.Rect(player.x - camera_x, player.y, PLAYER_W, PLAYER_H))

    pygame.display.flip()
    clock.tick(60)
