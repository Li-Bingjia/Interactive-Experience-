"""
=== Controls & Gameplay Instruction ===

Controls:
 - Move Left:  ←  (Left Arrow Key)
 - Move Right: →  (Right Arrow Key)
 - Jump:       Shout/make sound via microphone
   （Microphone jump is triggered when input volume > MIC_THRESHOLD）

How to adjust microphone sensitivity:
 - Increase MIC_THRESHOLD = less sensitive (need louder sound)
 - Lower MIC_THRESHOLD   = more sensitive  (small sound can trigger jump)
   Recommended range: 20 ~ 200 depending on device

Game Goal:
 - The level scrolls horizontally to the right.
 - Player must keep moving right and jump across platforms.
 - When the player reaches the red gem at the far right side, the game ends.

Note:
 - If jump triggered by mic is too weak, adjust jump strength parameters:
     JUMP_INITIAL / JUMP_HOLD_BOOST / MAX_HOLD_FRAMES
"""
import pygame, sys, math
import pyaudio
import numpy as np

# ====== 麦克风参数 ======
MIC_THRESHOLD = 50  # 灵敏度，可调
CHUNK = 1024
RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# ====== Pygame 初始化 ======
pygame.init()
pygame.mixer.init()

# ====== 游戏状态 ======
STATE_START = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
STATE_PAUSE   = 3
game_state = STATE_START

# ====== 背景音乐 ======
pygame.mixer.music.load("bgm.mp3")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

# ====== 屏幕与时钟 ======
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Microphone Jump Game")
clock = pygame.time.Clock()

# ====== 游戏元素 ======
WHITE = (255, 255, 255)
GREEN = (153, 153, 142)

goal_sound = pygame.mixer.Sound("goal.wav")
goal_sound.set_volume(0.6)   # 可调

bg = pygame.image.load("bg.png").convert()
LEVEL_WIDTH = bg.get_width()
platform_img = pygame.image.load("platform.png").convert_alpha()

platforms = [
    pygame.Rect(0, HEIGHT-100, 200, 20),
    pygame.Rect(90, HEIGHT-400, 75, 20),
    pygame.Rect(320, HEIGHT-250, 40, 20),
    pygame.Rect(250, HEIGHT-320, 40, 20),
    pygame.Rect(280, HEIGHT-125, 200, 20),
    pygame.Rect(480, HEIGHT-200, 150, 20),
    pygame.Rect(680, HEIGHT-200, 60, 20),
    pygame.Rect(850, HEIGHT-200, 60, 20),
    pygame.Rect(950, HEIGHT-300, 60, 20),
    pygame.Rect(1050, HEIGHT-300, 60, 20),
]

medals_image = pygame.image.load("medals.png").convert_alpha()
medals_image = pygame.transform.scale(medals_image, (50, 50)) 
medals_pos = (1070, HEIGHT-360) 

medals2_image = pygame.image.load("medals2.png").convert_alpha()
medals2_image = pygame.transform.scale(medals2_image, (50, 50)) 
medals2_pos = (100, HEIGHT-460) 

PLAYER_W, PLAYER_H = 40, 60
player = pygame.Rect(10, 100, PLAYER_W, PLAYER_H)
vel_y = 0
gravity = 0.8
on_ground = False
player_speed = 3
frame = 0
RESET_X, RESET_Y = 10, 100

# ====== 精灵 ======
idle_sheet = pygame.image.load("idle.png").convert_alpha()
run_sheet  = pygame.image.load("run.png").convert_alpha()
jump_sheet = pygame.image.load("jump.png").convert_alpha()

IDLE_FRAMES, RUN_FRAMES, JUMP_FRAMES = 7, 8, 5
IDLE_W, IDLE_H = 672//IDLE_FRAMES, 84
RUN_W, RUN_H   = 768//RUN_FRAMES, 84
JUMP_W, JUMP_H = 480//JUMP_FRAMES, 84

ACTION_IDLE = 0
ACTION_RUN  = 1
ACTION_JUMP = 2

JUMP_INITIAL = -40
JUMP_HOLD_BOOST = -10
MAX_HOLD_FRAMES = 20

hold_frames = 0
holding_jump = False
COYOTE_TIME = 0.12
coyote_timer = 0

# ====== 帧动画辅助函数 ======
def get_frame(sheet, frame_index, frame_w, frame_h):
    rect = pygame.Rect(frame_index*frame_w, 0, frame_w, frame_h)
    surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
    surf.blit(sheet, (0,0), rect)
    return surf

def draw_player(surface, x, y, moving, on_ground, facing_right, frame):
    if not on_ground:
        current_action = ACTION_JUMP
        sheet, num_frames, frame_w, frame_h = jump_sheet, JUMP_FRAMES, JUMP_W, JUMP_H
    elif moving:
        current_action = ACTION_RUN
        sheet, num_frames, frame_w, frame_h = run_sheet, RUN_FRAMES, RUN_W, RUN_H
    else:
        current_action = ACTION_IDLE
        sheet, num_frames, frame_w, frame_h = idle_sheet, IDLE_FRAMES, IDLE_W, IDLE_H

    frame_speed = 5
    frame_index = (frame // frame_speed) % num_frames
    img = get_frame(sheet, frame_index, frame_w, frame_h)

    breath_offset = int(math.sin(frame*0.1)*2) if current_action==ACTION_IDLE else 0
    head_offset = int(math.sin(frame*0.2)*1) if current_action==ACTION_IDLE else 0

    if current_action==ACTION_IDLE:
        temp = pygame.Surface(img.get_size(), pygame.SRCALPHA)
        temp.blit(img,(0,0))
        head_rect = pygame.Rect(0,0,frame_w,12)
        head_surf = temp.subsurface(head_rect).copy()
        temp.blit(head_surf,(head_offset, breath_offset))
        img = temp

    if not facing_right:
        img = pygame.transform.flip(img, True, False)

    surface.blit(img, (x, y+breath_offset))

# ====== 麦克风触发 ======
def is_sound_triggered():
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_data = np.frombuffer(data, dtype=np.int16)
    volume = np.linalg.norm(audio_data) / CHUNK
    return volume > MIC_THRESHOLD

# ====== 主循环 ======
while True:
    dt = clock.get_time() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stream.stop_stream()
            stream.close()
            p.terminate()
            pygame.quit()
            sys.exit() 

        # START 状态
        if game_state == STATE_START:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = STATE_PLAYING

        # PLAYING 状态
        elif game_state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if coyote_timer > 0:
                    vel_y = JUMP_INITIAL
                    holding_jump = True
                    hold_frames = 0
                    coyote_timer = 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                game_state = STATE_PAUSE

        # PAUSE 状态
        elif game_state == STATE_PAUSE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                game_state = STATE_PLAYING

        # GAMEOVER 状态
        elif game_state == STATE_GAMEOVER:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.x, player.y = RESET_X, RESET_Y
                vel_y = 0
                on_ground = False
                frame = 0
                game_state = STATE_PLAYING
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                holding_jump = False
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_1 or event.key == pygame.K_KP1):
                player.x, player.y = RESET_X, RESET_Y
                vel_y = 0

    keys = pygame.key.get_pressed()

    if game_state == STATE_PLAYING:
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * player_speed

        camera_x = player.x - WIDTH // 2
        camera_x = max(0, min(camera_x, LEVEL_WIDTH - WIDTH))

        if on_ground:
            coyote_timer = COYOTE_TIME
        else:
            coyote_timer -= dt

        # 麦克风触发跳跃
        if is_sound_triggered():
            if coyote_timer > 0:
                vel_y = JUMP_INITIAL
                hold_frames = 0
                holding_jump = True
                coyote_timer = 0
        else:
            holding_jump = False

        if holding_jump and vel_y < 0 and hold_frames < MAX_HOLD_FRAMES:
            vel_y += JUMP_HOLD_BOOST
            hold_frames += 1
        if vel_y < 0:
            vel_y *= 0.4

        vel_y += gravity
        player.x += dx
        player.y += vel_y

        if player.y > HEIGHT or player.bottom < 0:
            player.x, player.y = RESET_X, RESET_Y
            vel_y = 0

        on_ground = False
        foot_rect = pygame.Rect(player.x, player.bottom-2, player.width, 4)
        for p in platforms:
            if foot_rect.colliderect(p) and vel_y > 0:
                player.bottom = p.top
                vel_y = 0
                on_ground = True
        gem_rect = pygame.Rect(100, HEIGHT-460, 50, 50)  # 假设宝石位置

        if player.colliderect(gem_rect) and game_state == STATE_PLAYING:
           goal_sound.play()

        if player.x >= 1050 and game_state == STATE_PLAYING:
            goal_sound.play() 
            game_state = STATE_GAMEOVER

    # ====== 渲染 ======
    screen.fill((0,0,0))

    font = pygame.font.SysFont(None, 48)

    if game_state == STATE_START:
        text = font.render("Press SPACE to Start", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

    elif game_state == STATE_PLAYING:
        screen.blit(bg, (-camera_x, 0))
        for i, p in enumerate(platforms):
            img_scaled = pygame.transform.scale(platform_img, (p.width, p.height))
            img_scaled.set_alpha(82 if i in (1,2,3) else 255)
            screen.blit(img_scaled, (p.x - camera_x, p.y))

        # 奖牌动画
        for img, pos in [(medals_image, medals_pos), (medals2_image, medals2_pos)]:
            amplitude, speed = 5, 0.05
            scale_factor = 1 + (amplitude * math.sin(frame * speed)) / img.get_height()
            new_w, new_h = int(img.get_width()*scale_factor), int(img.get_height()*scale_factor)
            offset_x, offset_y = (new_w - img.get_width())//2, (new_h - img.get_height())//2
            screen.blit(pygame.transform.smoothscale(img, (new_w,new_h)),
                        (pos[0]-camera_x-offset_x, pos[1]-offset_y))

        player_amplitude = 2
        player_h = PLAYER_H + int(player_amplitude * math.sin(frame * 0.1))
        player_top = player.bottom - player_h
        player_rect = pygame.Rect(player.x, player_top, PLAYER_W, player_h)

        moving = dx != 0
        facing_right = dx >= 0
        draw_player(screen, player_rect.x - camera_x, player_rect.y, moving, on_ground, facing_right, frame)

    elif game_state == STATE_PAUSE:
        screen.blit(bg, (-camera_x, 0))
        for i, p in enumerate(platforms):
            img_scaled = pygame.transform.scale(platform_img, (p.width, p.height))
            img_scaled.set_alpha(82 if i in (1,2,3) else 255)
            screen.blit(img_scaled, (p.x - camera_x, p.y))

          # 奖牌动画
        for img, pos in [(medals_image, medals_pos), (medals2_image, medals2_pos)]:
            amplitude, speed = 5, 0.05
            scale_factor = 1 + (amplitude * math.sin(frame * speed)) / img.get_height()
            new_w, new_h = int(img.get_width()*scale_factor), int(img.get_height()*scale_factor)
            offset_x, offset_y = (new_w - img.get_width())//2, (new_h - img.get_height())//2
            screen.blit(pygame.transform.smoothscale(img, (new_w,new_h)),
                       (pos[0]-camera_x-offset_x, pos[1]-offset_y))

          # 玩家
        player_amplitude = 2
        player_h = PLAYER_H + int(player_amplitude * math.sin(frame * 0.1))
        player_top = player.bottom - player_h
        player_rect = pygame.Rect(player.x, player_top, PLAYER_W, player_h)
        moving = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT] != 0
        facing_right = keys[pygame.K_RIGHT] >= keys[pygame.K_LEFT]
        draw_player(screen, player_rect.x - camera_x, player_rect.y, moving, on_ground, facing_right, frame)

         # 在上面渲染暂停文字
        text = font.render("PAUSED - Press P to Resume", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 50))  # 文字显示在顶部

    elif game_state == STATE_GAMEOVER:
        text = font.render("Press SPACE to Restart", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

    frame += 1
    pygame.display.flip()
    clock.tick(60)
