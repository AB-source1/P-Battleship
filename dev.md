
# HOW TO CLONE REPOSITORY TO YOUR PC:

1. install "VSCode"
2. Install Python extention inside VS
3. install "Git" on pc
4. clone repository :
on vs, left hand side, 3rd icon (source control) or (CTRL+SHIFT+G "for windows")
click button "Clone Repository"
paste url "https://github.com/AB-source1/P-Battleship.git" (do not paste the speach marks) + press ENTER
log in to git hub if asked
save the local repository where you want the code to be on your PC 

*LINK VIDEO: https://www.youtube.com/watch?v=Nl0J_tcnhQ4*
*LINK VS instructions: https://code.visualstudio.com/docs/sourcecontrol/intro-to-git*

# HOW TO MAKE CHANGES:
*VIDEO LINK: https://www.youtube.com/watch?app=desktop&v=hyLAfceeM1E*

1. Get the latest code from cloud:
pull latest by clicking the Pull icon (3rd icon from the right, in the section titled graph) 
2. Create Branch for your changes (name it feature/......) <---- good practice for refrencing
3. Make changes
4. Stage the files you changed
5. Commit the files (add a message (short description about the commit) above the commit button)
6. Push to remote(publish branch)

# HOW TO MERGE CHANGES TO MAIN BRANCH
*VIDEO LINK: https://www.youtube.com/watch?v=5g37NElQnCQ*

1. Go to git hub (website)
2. Go pull request link: https://github.com/AB-source1/P-Battleship/pulls
3. *short cut* if visable at the top of the screen yellow tab with most recent push, press "Compare & pull request"
4. add title and message 
5. click "Create pull request" 
6. notify me in whatsapp or discord I will merge the code
7. If you are done with the feature you can checkout to main branch



# 🛠 How to Add a New Screen to P-Battleship

make sure pygame is installed using the code below in terminal 
```python
pip install pygame 
```


This guide walks you through creating a new screen in the P-Battleship project using Python and pygame.

---

## ✅ Step-by-Step: Creating a New Screen

### 1. Understand the Project Structure
Each screen is a Python class (e.g., `MenuScreen`, `SettingsScreen`) that:
- Handles events via `handleEvent(self, event, state)`
- Draws UI via `draw(self, screen, state)`

Screens are selected using the `game_state` attribute in `GameState`.

---

### 2. Create Your Screen Class

Create a file like `your_screen.py` and paste this template:

```python
import pygame
from ui import draw_text_center, draw_button
from config import Config
from game_state import GameState

class YourScreen:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state

    def handleEvent(self, event: pygame.event.Event, state: GameState):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state.game_state = "menu"

    def draw(self, screen, state: GameState):
        draw_text_center(screen, "Welcome to Your Screen!", Config.WIDTH // 2, Config.HEIGHT // 2)
        draw_button(screen, "Back", Config.WIDTH - 120, Config.HEIGHT - 60, 100, 40,
                    Config.GRAY, Config.DARK_GRAY, lambda: setattr(state, "game_state", "menu"))
```

---


3. Register the New Screen

In your main game loop, add a condition to initialize and handle your new screen.  
Follow the same pattern used for existing screens like `SettingsScreen` or `PlacingScreen`.

Make sure:
- `YourScreen` is imported at the top eg. "from screens.menu import MenuScreen"
- create instance in "game state instance" following "settingsScreen = SettingsScreen(screen,state)"
- `"your_screen"` matches the string you use to switch `state.game_state`
- You include this inside the game’s main event and draw loop

You can see similar patterns in files like `settings.py`, `placing.py`, and `playing.py`.

### 4. Add Navigation Button

From another screen (e.g., menu), add a button to reach your screen:

```python
draw_button(screen, "Your Feature", x, y, w, h, Config.GREEN, Config.DARK_GREEN, lambda: setattr(state, "game_state", "your_screen"))
```

---

## 🧰 Helpful Utilities

Use the existing tools to avoid writing boilerplate:

- `draw_button()` and `draw_text_center()` – from `ui.py`
- `Config` – layout and color constants
- `get_grid_pos()` – convert mouse to grid location (`util.py`)
- `GameState` – shared app state

---

## ✅ Final Checklist

- [ ] Create a class for your screen
- [ ] Implement `handleEvent()` and `draw()`
- [ ] Add screen switch logic in the main loop
- [ ] Add a button from another screen
- [ ] Test your screen end-to-end

---

🎉 You’re now ready to expand the game UI!

---

## 🧠 How to Add New State Variables

The `GameState` class (`game_state.py`) stores all global state needed across screens.

### ➕ To Add a New State Variable:

1. **Open** `game_state.py`
2. **Edit `reset_all()`** – add and initialize your new variable here
3. 
3. The `reset_all()` method initializes **all variables used across screens**, including:
   - `self.user_text`, `self.player_name` – for storing user input
   - `self.ship_index`, `self.placed_ships` – for tracking ship placement
   - `self.ai_turn_pending`, `self.ai_turn_start_time` – for timing enemy moves
   - `self.game_state` – current screen identifier (e.g., `"menu"`, `"playing"`)
   - `self.running` – main game loop control

   You should **add your variable here** to ensure it’s reset properly when the game restarts.

### ✅ Example:

Add a new variable `difficulty`:

```python
class GameState:
    def reset_all(self):
        self.reset_with_counts()
        self.user_text = ""
        self.player_name = ""
        self.ship_index = 0
        self.placed_ships = []
        self.ai_turn_pending = False
        self.ai_turn_start_time = 0
        self.game_state = "menu"
        self.running = True
        self.difficulty = "normal"  # NEW variable
```

You can now access or change `state.difficulty` from any screen.

---

✅ Make sure any new variable is reset appropriately when restarting or resetting the game.


