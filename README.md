# Interactive-Experience-
# Voice Jump Platformer (Pygame + Microphone Control)

A simple platformer game built with **Pygame** where the player can **jump by voice** — speaking or making a sound near the microphone will trigger a jump similar to holding the spacebar.

This repository also includes a microphone testing tool to visualize sound volume in real-time before running the game.

<img width="1397" height="1046" alt="image" src="https://github.com/user-attachments/assets/f016233f-5f7d-4461-88c7-8d5491b5402c" />



## 📁 Project Structure

.
├── game.py # Main platformer game using mic for jumping
├── mic_test.py # Microphone test tool (visual volume bar)
├── bg.png # Background image
├── platform.png # Platform image
├── idle.png / run.png / jump.png # Player sprite sheets
├── medals.png / medals2.png # Decorative items
├── bgm.mp3 # Background music
└── README.md

yaml
Copy code

---

## ▶️ How to Run

### 1. Install Dependencies


pip install pygame pyaudio numpy
⚠️ Windows if pyaudio install failed：

pip install pipwin
pipwin install pyaudio

### 2. Test Microphone First
bash
Copy code
python mic_test.py
This tool shows a live volume bar.
Make a sound (speak / clap / breathe near mic) to observe volume changes.

Use this to tune MIC_THRESHOLD in game.py.

Example output:

makefile
Copy code
Volume: ████████████████  (100)
<img width="1047" height="402" alt="image" src="https://github.com/user-attachments/assets/f96f7a33-8438-4438-abc9-017c5d524c5a" />
The best volume to jump in the game is around 80-100
### 3. Run The Game
bash
Copy code
python game.py

🎮 Interaction & Controls
Control Method	Action
Speak / make sound near mic	Trigger jump (same height as spacebar jump)
← → Arrow keys	Move left / right
SPACE (start menu)	Start game / Restart after game over
P (Only lowercase key)  Pause game / Resume game
ESC / Window close	Quit (and safely close mic stream)
<img width="1391" height="1043" alt="image" src="https://github.com/user-attachments/assets/4728044a-38e7-4989-b095-eb537adb8377" />

🔊 Voice Jump Logic
The game continuously listens to microphone input using PyAudio
![1](https://github.com/user-attachments/assets/5a1ec80c-6b94-453d-9567-4b05c7c15539)

When volume exceeds defined threshold (MIC_THRESHOLD), it triggers a jump

Jump height is calibrated to mimic a full "tap space" jump, not a mini jump

📸 Screenshots / Demo 

![2](https://github.com/user-attachments/assets/8ebe9be2-c7e3-4c8a-a15c-20dead17e9c4)

The goal of the game :
Player must keep moving right and jump across platforms.
When the player reaches the red gem at the far right side, the game ends.

![3](https://github.com/user-attachments/assets/7fc3485c-198a-4644-b172-5eaf0f383577)


You can change sensitivity here (in game.py):

python
Copy code
MIC_THRESHOLD = 150  # Lower = more sensitive, Higher = harder to trigger


markdown
Copy code

## ✅ Notes
Microphone is properly closed (stream.stop_stream, stream.close, p.terminate) when quitting

If game does not detect your sound, reduce MIC_THRESHOLD

Use mic_test.py before playing to find a proper threshold

## 📎 Assets Credits
The following third-party assets are used in this project:

Type	Usage	Source	License / Notes
Background	In-game environment backgrounds	https://anokolisa.itch.io/moon-graveyard and https://edermunizz.itch.io/free-pixel-art-forest

Character	Player sprite sheets (Idle / Run / Jump)	https://xzany.itch.io/free-knight-2d-pixel-art

Music (BGM)	Background track retro-forest	https://www.fesliyanstudios.com/royalty-free-music/download/retro-forest/451

Icons	Medal and pixel icons	https://free-game-assets.itch.io/48-free-minerals-pixel-art-icons-pack
Sound effect https://mixkit.co/free-sound-effects/game/?utm_source=chatgpt.com

This project is for educational and demonstration purposes only.
All rights to the assets belong to their original authors.
