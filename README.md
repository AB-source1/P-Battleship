README: Battleship Game

1. How to Play the Game

    Objective

    Prepare for war on the waves.

    In Battleships, strategy meets sabotage. Place your ships, scan the seas, and strike before your opponent sinks your fleet. Whether you’re battling the AI or another player, the goal is clear: sink all enemy ships before yours are destroyed.

    Gameplay Overview

    1. Start Screen:
    - The game opens with a dramatic battleship-themed background and tense music.
    - Main menu options:
    - Play
    - Settings
    - Pass and play (2 person local multiplayer)
    - Quit

    2. Settings:
    - Battlefield Size: Choose between:
    - 5x5
    - 10x10
    - 15x15
    The size selected determines the number of ships available.
    - AI Difficulty: Choose between:
    - Easy
    - Medium
    - Hard

    3. Ship Placement Phase:
    - Drag and drop ships onto your grid.(with a preview of the next ship to come)
    - Use the Rotate Ship button or R on your keyboard to toggle between horizontal and vertical orientation.
    - Use Undo Last Ship to reposition the last placed ship.

    4. Gameplay Phase:
    - Two grids are displayed:
    - Your fleet (shows your ship positions and hits taken)
    - Enemy grid (used to target airstrikes)
    - Turns alternate between the player and AI (or another player in multiplayer).
    - Launch airstrikes by clicking grid cells to locate and destroy enemy ships.

    5. Endgame:
    - The game ends when one side sinks all opposing ships.
    - Endgame statistics are displayed:
    - Score
    - Shots fired
    - Hits made
    - Accuracy %
    - Time per shot
    - Total gameplay time

2. App Controls and Walkthrough

    Controls

    Play – Start the game
    Settings – Customize gameplay options
    Multiplayer – Access multiplayer mode
    Quit – Exit the game
    Back – Return to the main menu 
    Restart – Restart the current game
    Close – Exit the application
    Rotate Ship – Change ship orientation
    Undo Last Ship – Remove last placed ship
    Grid Size Buttons – Choose between 5x5, 10x10, or 15x15
    Difficulty Buttons – Set AI difficulty (Easy, Medium, Hard)

    Keyboard Shortcuts:
    - Esc – Return to the main menu
    - mouse – Navigate game elements

    Walkthrough

    1. Launch the game and select Play or pass and play.
    2. Adjust settings as needed (difficulty, grid size).
    3. Choose Multiplayer or AI Mode.
    4. Place ships on your grid using drag-and-drop.
    5. Rotate and undo ship placements if needed.
    6. Begin attacking the enemy grid — the first to destroy all ships wins!
    7. View your stats at the end and optionally restart the game.

3. Updates

Gameplay and Features
- AI Difficulty Settings: Added Easy, Medium, and Hard AI difficulty levels for a more customizable experience.
- Custom Grid Sizes: Users can now select 5x5, 10x10, or 15x15 grids, dynamically changing the number of ships.
- Multiplayer Modes:
  - Local hot-seat multiplayer (Pass & Play)
  - Placeholder/structure for future online multiplayer
- Smart Ship Placement with drag-and-drop and orientation control (vertical/horizontal)
- Undo Last Ship placement option
- In-game Statistics: Game now tracks:
  - Shots taken
  - Hits/misses
  - Accuracy
  - Time per shot
  - Total game duration
- Scoring System: Final score calculated from difficulty, accuracy, and game time

GUI & UX Enhancements
- Pygame-based Graphical User Interface (original was terminal-based)
- Custom Menu System with:
  - Main menu
  - Settings
  - Multiplayer mode selector
- Mouse and Keyboard Input Support: e.g. Esc to return to menu
- Responsive layout and resolution scaling

Visual & Audio Design
- Visual Overhaul:
  - Cartoon-themed battle background and loading screen
  - Explosion and missile graphics
- Animated Feedback: Hit/miss animations on the grid
- Background Music and Sound Effects:
  - Background track
  - Sounds for hits and misses

Code Structure & Scalability
- Modular Codebase: Separated into core, game, screens, and helpers folders
- State Management System: GameState module tracks transitions between game screens
- Settings Logic & Persistence: Game settings like difficulty and grid size are maintained across sessions
- Custom Tkinter-based Main Menu launcher for startup

4. GUI Design


The interface was designed using the Golden Rules of Interface Design:
- Consistency: Buttons, fonts, and layouts maintain a uniform visual style throughout all screens.
- Feedback: Real-time feedback through hover animations, hit/miss effects, and sound cues for interactions.
- Simplicity: Clean layouts with only essential buttons and information visible. Easy for beginners to pick up.
- User-Friendly Layout: Logical grouping of controls, clear labeling, and intuitive interactions.

tkinter was used for the menu and setting screens but py game was utelised for the rest as it allowd more functionality and better visuals 

5. AI Tools

Estimated AI Assistance Used: ~75%
Areas Supported:
- Debugging error messages
- Generating code snipets and files
- Optimizing grid drawing and button interaction
- Writing endgame statistics calculation
- early refactorisation of large main file into logic and rendering and helpers 

exaple of usage of ai for code snipets and bug fixes
Prompt:
attached files relating to the bug and images of the issue
"the bug causes old ships that were placed to still remain invisable 
on the grid afer a back out, i assume we need to reset after going back
 to menu so that info isnt stored when you come back to the playing screen"

Result:
"--- a/screens/placing_render.py
+++ b/screens/placing_render.py
@@ class PlacingRender:
     def draw(self, screen, state):
         # Top bar with Restart/Quit buttons
-        def back():
-            if state.history:
-                state.skip_push = True
-                state.game_state = state.history.pop()
-            else:
-                state.game_state = "menu"
+        def back():
+            # ─── NEW: wipe out any ships/board state so it won't persist on re-entry
+            self.logic.reset()
+            if state.history:
+                state.skip_push   = True
+                state.game_state  = state.history.pop()
+            else:
+                state.game_state  = "menu"
         draw_button(screen, "Back (esc)", 10, 40, 130, 30,
                     Config.GRAY, Config.DARK_GRAY, back, 3)"

integration:
following the git style diff file it produces you can locate the file
and exact location, then select out the lines annotated by a "-" and add the new 
ones in making sure to double check indents.

