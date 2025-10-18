import pygame, sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GREEN = (100, 200, 100)

# ==== 背景长图 ====
bg = pygame.image.load("bg.png").convert()
LEVEL_WIDTH = bg.get_width()  # 背景宽度

# ==== 玩家参数 ====
PLAYER_W, PLAYER_H = 40, 60
player = pygame.Rect(10, 100, PLAYER_W, PLAYER_H)
vel_y = 0
gravity = 0.8
on_ground = False
player_speed = 5


# 玩家初始/重置位置
RESET_X, RESET_Y = 10, 100

# ==== 平台列表 ====
# 水平平台用 Rect
platforms = [
    pygame.Rect(0, HEIGHT-125, 350, 50),
    pygame.Rect(480, HEIGHT-200, 150, 50),
    pygame.Rect(700, HEIGHT-200, 60, 20),
    pygame.Rect(850, HEIGHT-200, 60, 20),
    pygame.Rect(800, HEIGHT-300, 30, 100),
    pygame.Rect(925, HEIGHT-420, 30, 250),
    pygame.Rect(1050, HEIGHT-460, 60, 20),
    
]

# 斜坡平台参数
# 左低右高
slope_rect = pygame.Rect(150, HEIGHT-150, 200, 50)
slope_height_offset = 80  # 右边比左边高50px

def draw_person(surface, rect):
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
    surface.blit(person, rect.topleft)

# ==== 游戏主循环 ====
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    # ==== 玩家输入 ====
    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
    if keys[pygame.K_SPACE] and on_ground:
        vel_y = -15
        on_ground = False
    if keys[pygame.K_1] or keys[pygame.K_KP1]:  # 按1重置
        player.x = 100
        player.y = 100
        vel_y = 0

    # ==== 更新玩家位置 ====
    vel_y += gravity
    player.x += dx
    player.y += vel_y

    # ==== 更新玩家位置 ====
    vel_y += gravity
    player.x += dx
    player.y += vel_y

    # ==== 玩家掉落检测 ====
    if player.y > HEIGHT or player.bottom < 0:  # 掉出屏幕底部或顶部
        player.x = RESET_X
        player.y = RESET_Y
        vel_y = 0

    # ==== 碰撞检测：水平平台 ====
    on_ground = False
    for p in platforms:
        if player.colliderect(p) and vel_y > 0:
            player.bottom = p.top
            vel_y = 0
            on_ground = True

    # ==== 碰撞检测：斜坡 ====
    px = player.centerx
    x0, y0 = slope_rect.left, slope_rect.bottom      # 左低
    x1, y1 = slope_rect.right, slope_rect.bottom - slope_height_offset  # 右高
    if x0 <= px <= x1:
        slope_y = y0 + (y1 - y0) * (px - x0) / (x1 - x0)
        if player.bottom >= slope_y:
            player.bottom = slope_y
            vel_y = 0
            on_ground = True

    # ==== 摄像机计算 ====
    camera_x = player.x - WIDTH//2
    camera_x = max(0, min(camera_x, LEVEL_WIDTH - WIDTH))

    # ==== 绘制背景 ====
    screen.blit(bg, (-camera_x, 0))

    # ==== 绘制水平平台 ====
    for p in platforms:
        pygame.draw.rect(screen, GREEN, (p.x - camera_x, p.y, p.width, p.height))

    # ==== 绘制斜坡平台 ====
    points = [
        (slope_rect.left - camera_x, slope_rect.bottom),
        (slope_rect.right - camera_x, slope_rect.bottom - slope_height_offset),
        (slope_rect.right - camera_x, slope_rect.bottom),
    ]
    pygame.draw.polygon(screen, GREEN, points)

    # ==== 绘制玩家 ====
    draw_person(screen, pygame.Rect(player.x - camera_x, player.y, PLAYER_W, PLAYER_H))

    pygame.display.flip()
    clock.tick(60)
