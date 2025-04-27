from core.game_state import GameState

class MenuLogic:
    def __init__(self, screen, state: GameState):
        self.screen = screen
        self.state = state

    def start_game(self):
        self.state.game_state = "placing"

    def show_settings(self):
        self.state.game_state = "settings"

    def handle_event(self, event, state: GameState):
        # No specific event handling needed for menu (buttons are clicked inside rendering)
        pass
