import pygame
import pyaudio
import numpy as np

# ===== 麦克风参数 =====
CHUNK = 1024
RATE = 44100

# 初始化 PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# ===== Pygame 初始化 =====
pygame.init()
WIDTH, HEIGHT = 600, 200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Microphone Test")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# 灵敏度阈值
MIC_THRESHOLD = 2000

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ===== 读取麦克风数据 =====
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_data = np.frombuffer(data, dtype=np.int16)
    volume = np.linalg.norm(audio_data) / CHUNK

    # ===== 渲染 =====
    screen.fill((30, 30, 30))
    
    # 绘制音量条
    bar_width = int((volume / 5000) * WIDTH)
    bar_width = min(bar_width, WIDTH)
    color = (0, 255, 0) if volume > MIC_THRESHOLD else (255, 0, 0)
    pygame.draw.rect(screen, color, (0, HEIGHT//2 - 25, bar_width, 50))
    
    # 显示数值
    text = font.render(f"Volume: {int(volume)}", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    
    pygame.display.flip()
    clock.tick(30)

# ===== 关闭流 =====
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
