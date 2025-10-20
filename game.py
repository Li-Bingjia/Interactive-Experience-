import pygame, sys, math

pygame.init()
pygame.mixer.init()  # 初始化音频

STATE_START = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
game_state = STATE_START

# 背景音乐加载与播放
pygame.mixer.music.load("bgm.mp3")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)  # 循环播放

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
    pygame.Rect(0, HEIGHT-100, 200, 20),
    pygame.Rect(90, HEIGHT-400, 75, 20),
    pygame.Rect(280, HEIGHT-125, 200, 20),
    pygame.Rect(320, HEIGHT-250, 40, 20),
    pygame.Rect(250, HEIGHT-320, 40, 20),
    pygame.Rect(480, HEIGHT-200, 150, 20),
    pygame.Rect(680, HEIGHT-200, 60, 20),
    pygame.Rect(850, HEIGHT-200, 60, 20),
    pygame.Rect(950, HEIGHT-300, 60, 20),
    pygame.Rect(1050, HEIGHT-300, 60, 20),
]

slope_rect = pygame.Rect(150, HEIGHT-150, 200, 50)
slope_height_offset = 80

medals_image = pygame.image.load("medals.png").convert_alpha()  # 保留透明通道
medals_image = pygame.transform.scale(medals_image, (50, 50)) 
medals_pos = (1070, HEIGHT-360) 

# ==== 玩家参数 ====
PLAYER_W, PLAYER_H = 40, 60
BASE_H = PLAYER_H
player = pygame.Rect(10, 100, PLAYER_W, PLAYER_H)
vel_y = 0.2
gravity = 0.9
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

JUMP_INITIAL = -12        # 一跳起跳速度
JUMP_HOLD_BOOST = -0.5    # 按住时每帧加的额外反重力
MAX_HOLD_FRAMES = 12      # 最多连续助力帧数，防止飞上天

hold_frames = 0
holding_jump = False

COYOTE_TIME = 0.12        # 离地后允许继续跳的时间（秒）
coyote_timer = 0          # 剩余缓冲时间（秒）

def get_frame(sheet, frame_index, frame_w, frame_h):
    rect = pygame.Rect(frame_index*frame_w, 0, frame_w, frame_h)
    surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
    surf.blit(sheet, (0,0), rect)
    return surf
# 角色动作设计
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
    dt = clock.get_time() / 1000  # 用于 Coyote Timer

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == STATE_START:
            # 开始界面按空格进入游戏
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = STATE_PLAYING

        elif game_state == STATE_PLAYING:
            # 按下跳跃
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if coyote_timer > 0:  # Coyote Time
                    vel_y = JUMP_INITIAL
                    holding_jump = True
                    hold_frames = 0
                    coyote_timer = 0  # 使用掉缓冲
                 # GAMEOVER 重开逻辑
        elif game_state == STATE_GAMEOVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
              player.x, player.y = RESET_X, RESET_Y
              vel_y = 0
              on_ground = False
              frame = 0
              game_state = STATE_PLAYING
              
            # 松开跳跃
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                holding_jump = False
                if vel_y < 0:
                    vel_y *= 0.4  # 松开削减上升

            # 按 1 重置
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_1 or event.key == pygame.K_KP1):
                player.x, player.y = RESET_X, RESET_Y
                vel_y = 0

    keys = pygame.key.get_pressed()

    if game_state == STATE_PLAYING:
        # ======== 移动 ========
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed

        # ======== 摄像机计算 ========
        camera_x = player.x - WIDTH // 2
        camera_x = max(0, min(camera_x, LEVEL_WIDTH - WIDTH))

        # ======== Coyote Time 计时 ========
        if on_ground:
            coyote_timer = COYOTE_TIME
        else:
            coyote_timer -= dt

        # ======== 长按跳跃 ========
        if holding_jump and keys[pygame.K_SPACE] and vel_y < 0 and hold_frames < MAX_HOLD_FRAMES:
            vel_y += JUMP_HOLD_BOOST
            hold_frames += 1

        # ======== 更新位置 ========
        vel_y += gravity
        player.x += dx
        player.y += vel_y

        # ======== 掉落重置 ========
        if player.y > HEIGHT or player.bottom < 0:
            player.x, player.y = RESET_X, RESET_Y
            vel_y = 0

        # ======== 碰撞检测 ========
        on_ground = False
        foot_rect = pygame.Rect(player.x, player.bottom-2, player.width, 4)
        for p in platforms:
            if foot_rect.colliderect(p) and vel_y > 0:
                player.bottom = p.top
                vel_y = 0
                on_ground = True

        # ======== 检查通关条件 ========
        if player.x >= 1050:  # 可以改成固定平台或区域
            game_state = STATE_GAMEOVER

    # ======== 渲染画面 ========
    screen.fill((0,0,0))

    if game_state == STATE_START:
      # 开始界面
       font = pygame.font.SysFont(None, 48)
       text = font.render("Press SPACE to Start", True, (255,255,255))
       screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

    elif game_state == STATE_PLAYING:
    # 绘制背景
        screen.blit(bg, (-camera_x, 0))
    # 绘制平台
        for p in platforms:
           img_scaled = pygame.transform.scale(platform_img, (p.width, p.height))
           screen.blit(img_scaled, (p.x - camera_x, p.y))
    
    # ===== 呼吸动画与奖牌绘制 =====
    # 奖牌呼吸
        medals_amplitude = 5
        medals_speed = 0.05
        scale_factor = 1 + (medals_amplitude * math.sin(frame * medals_speed)) / medals_image.get_height()
        new_w = int(medals_image.get_width() * scale_factor)
        new_h = int(medals_image.get_height() * scale_factor)
        offset_x = (new_w - medals_image.get_width()) // 2
        offset_y = (new_h - medals_image.get_height()) // 2
        screen.blit(pygame.transform.smoothscale(medals_image, (new_w, new_h)),
                   (medals_pos[0] - camera_x - offset_x, medals_pos[1] - offset_y))

    # 玩家呼吸动画
        player_amplitude = 2
        player_speed_breath = 0.1
        player_h = PLAYER_H + int(player_amplitude * math.sin(frame * player_speed_breath))
        player_top = player.bottom - player_h
        player_rect = pygame.Rect(player.x, player_top, PLAYER_W, player_h)

        moving = dx != 0
        facing_right = dx >= 0
        draw_player(screen, player_rect.x - camera_x, player_rect.y, moving, on_ground, facing_right, frame)

    elif game_state == STATE_GAMEOVER:
    # 黑屏 + 提示文字
      screen.fill((0,0,0))
      text = font.render("Press SPACE to Restart", True, (255,255,255))
      screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

    frame += 1
    pygame.display.flip()
    clock.tick(60)
