import pygame, sys, math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GREEN = (153, 153, 142)

# ==== 背景与平台 ====
bg = pygame.image.load("bg.png").convert()
LEVEL_WIDTH = bg.get_width()
platform_img = pygame.image.load("platform.png").convert_alpha()

platforms = [
    pygame.Rect(0, HEIGHT-125, 350, 50),
    pygame.Rect(480, HEIGHT-200, 150, 50),
    pygame.Rect(700, HEIGHT-200, 60, 20),
    pygame.Rect(850, HEIGHT-200, 60, 20),
]

slope_rect = pygame.Rect(150, HEIGHT-150, 200, 50)
slope_height_offset = 80

# ==== 玩家参数 ====
PLAYER_W, PLAYER_H = 40, 60
BASE_H = PLAYER_H
player = pygame.Rect(10, 100, PLAYER_W, PLAYER_H)
vel_y = 0.2
gravity = 0.6
on_ground = False
player_speed = 3
frame = 0
RESET_X, RESET_Y = 10, 100

# ==== 加载精灵 ====
idle_sheet = pygame.image.load("idle.png").convert_alpha()  # 672x84 7帧
run_sheet  = pygame.image.load("run.png").convert_alpha()   # 768x84 8帧
jump_sheet = pygame.image.load("jump.png").convert_alpha()  # 480x84 5帧

# 精灵帧数据
IDLE_FRAMES = 7
RUN_FRAMES = 8
JUMP_FRAMES = 5

IDLE_W, IDLE_H = 672//IDLE_FRAMES, 84
RUN_W, RUN_H   = 768//RUN_FRAMES, 84
JUMP_W, JUMP_H = 480//JUMP_FRAMES, 84

ACTION_IDLE = 0
ACTION_RUN  = 1
ACTION_JUMP = 2

def get_frame(sheet, frame_index, frame_w, frame_h):
    rect = pygame.Rect(frame_index*frame_w, 0, frame_w, frame_h)
    surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
    surf.blit(sheet, (0,0), rect)
    return surf

def draw_player(surface, x, y, moving, on_ground, facing_right, frame):
    # 动作选择
    if not on_ground:
        current_action = ACTION_JUMP
        sheet = jump_sheet
        num_frames = JUMP_FRAMES
        frame_w, frame_h = JUMP_W, JUMP_H
    elif moving:
        current_action = ACTION_RUN
        sheet = run_sheet
        num_frames = RUN_FRAMES
        frame_w, frame_h = RUN_W, RUN_H
    else:
        current_action = ACTION_IDLE
        sheet = idle_sheet
        num_frames = IDLE_FRAMES
        frame_w, frame_h = IDLE_W, IDLE_H

    # 当前帧
    frame_speed = 5
    frame_index = (frame // frame_speed) % num_frames
    img = get_frame(sheet, frame_index, frame_w, frame_h)

    # 呼吸动画（仅idle）
    breath_offset = int(math.sin(frame*0.1)*2) if current_action==ACTION_IDLE else 0
    # 头部晃动（仅idle）
    head_offset = int(math.sin(frame*0.2)*1) if current_action==ACTION_IDLE else 0

    if current_action==ACTION_IDLE:
        # 临时Surface修改头部
        temp = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        temp.blit(img,(0,0))
        head_rect = pygame.Rect(0,0,frame_w,12)
        head_surf = temp.subsurface(head_rect).copy()
        temp.blit(head_surf,(head_offset, breath_offset))
        img = temp

    # 翻转
    if not facing_right:
        img = pygame.transform.flip(img, True, False)

    surface.blit(img, (x, y+breath_offset))

# ==== 主循环 ====
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    # 摄像机
    camera_x = player.x - WIDTH//2
    camera_x = max(0, min(camera_x, LEVEL_WIDTH - WIDTH))

    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed
    if keys[pygame.K_SPACE] and on_ground:
        vel_y = -15
        on_ground = False
    if keys[pygame.K_1] or keys[pygame.K_KP1]:
        player.x = RESET_X
        player.y = RESET_Y
        vel_y = 0

    # 更新位置
    vel_y += gravity
    player.x += dx
    player.y += vel_y

    if player.y > HEIGHT or player.bottom < 0:
        player.x = RESET_X
        player.y = RESET_Y
        vel_y = 0

    # 碰撞检测
    on_ground = False
    foot_rect = pygame.Rect(player.x, player.bottom-2, player.width, 4)
    for p in platforms:
        if foot_rect.colliderect(p) and vel_y>0:
            player.bottom = p.top
            vel_y = 0
            on_ground = True

    # 绘制背景
    screen.blit(bg, (-camera_x, 0))
    # 绘制平台
    for p in platforms:
        img_scaled = pygame.transform.scale(platform_img, (p.width,p.height))
        screen.blit(img_scaled, (p.x-camera_x, p.y))

    # 绘制玩家
    moving = dx != 0
    facing_right = dx>=0
    draw_player(screen, player.x-camera_x, player.y, moving, on_ground, facing_right, frame)

    frame += 1
    pygame.display.flip()
    clock.tick(60)
