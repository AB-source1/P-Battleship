# screens/lobby_logic.py

import pygame
import time
import threading
import socket                         # ← for determining local IP
from network import Network
from core.game_state import GameState

class LobbyLogic:
    def __init__(self, screen, state: GameState):
        self.screen      = screen
        self.state       = state
        self.ip_input    = ""          # for join-mode typing
        self.mode        = None        # 'host' or 'join'
        self.network     = None
        self.waiting     = False       # True while host is waiting
        self.host_ip_str = ""          # populated after start_host()

    def _get_local_ip(self) -> str:
        """
        Attempts to discover the LAN IP address by opening a UDP
        socket to a public address (no packets are sent).
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # doesn't actually send packets
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def start_host(self):
        """Begin listening; show our IP and wait for a client in background."""
        try:
            # Bind to all interfaces; actual IP found below
            self.network = Network(is_host=True, host_ip="", port=5000)
        except Exception as e:
            print("Host failed:", e)
            return

        # Record our LAN IP so the player can share it
        self.host_ip_str = self._get_local_ip()

        # Enter waiting state and spin off the accept-poller
        self.waiting = True
        threading.Thread(target=self._wait_for_client, daemon=True).start()

    def _wait_for_client(self):
        """
        Blocks until Network.conn is non-None (client has connected).
        Then transition into placement.
        """
        while self.network.conn is None:
            time.sleep(0.1)

        # Connected: go into multiplayer placing
        self._enter_multiplayer(is_host=True)

    def start_join(self):
        """Try to connect to the IP typed by the player."""
        try:
            self.network = Network(
                is_host=False,
                host_ip=self.ip_input,
                port=5000
            )
        except Exception as e:
            print("Join failed:", e)
            return

        # Immediately enter placement (client conn is already set)
        self._enter_multiplayer(is_host=False)

    def _enter_multiplayer(self, is_host: bool):
        """
        Put the Network on state, mark host/guest, and switch scenes.
        """
        self.state.network = self.network
        self.state.is_host = is_host
        self.state.game_state = "placing"

    def handle_event(self, event: pygame.event.Event):
        # Text input for Join-mode
        if event.type == pygame.KEYDOWN and self.mode == "join":
            if event.key == pygame.K_BACKSPACE:
                self.ip_input = self.ip_input[:-1]
            elif event.unicode.isprintable():
                self.ip_input += event.unicode

        # Mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos

            # Host button region
            if 100 < x < 260 and 200 < y < 250:
                self.mode = "host"
                self.start_host()

            # Join button region
            if 100 < x < 260 and 300 < y < 350:
                self.mode = "join"

            # Connect button (only when typing IP)
            if self.mode == "join" and 100 < x < 260 and 360 < y < 410:
                self.start_join()
