# screens/lobby_logic.py

import pygame
import time
import threading
import socket
from network import Network
from core.game_state import GameState

"""
Module: lobby_logic.py
Purpose:
  - Pygame logic for Multiplayer Lobby: hosting or joining.
  - Manages port binding, client acceptance, and state transitions.
  - Handles text input for join-mode.
Future Hooks:
  - Implement LAN discovery via UDP broadcast.
  - Retry logic for port binding and reconnection.
"""

class LobbyLogic:
    """
    Manages the multiplayer lobby: hosting or joining a game.
    On host, it binds on ports 5000–5009 and shows the chosen address.
    On join, it parses an IP:port and connects immediately.
    """

    def __init__(self, screen, state: GameState):
        self.screen      = screen
        self.state       = state
        self.ip_input    = ""      # for join-mode typing ("IP:port")
        self.mode        = None    # 'host' or 'join'
        self.network     = None
        self.waiting     = False
        self.host_ip_str = ""      # e.g. "192.168.1.42:5003"

    def _get_local_ip(self) -> str:
        """
        Discover the local LAN IP by opening a dummy UDP socket.
        Falls back to 127.0.0.1 on error.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def start_host(self):
        """
        Begin listening as server. Binds to the first free port
        in the range 5000–5009, records that port, and spawns
        a background thread to accept the client.
        """
        try:
            self.network = Network(is_host=True, host_ip="", port=5000)
        except Exception as e:
            print("Host failed:", e)
            return

        # Display the actual bind address:port for the user
        ip = self._get_local_ip()
        self.host_ip_str = f"{ip}:{self.network.port}"

        # Kick off accept() in the background so UI remains responsive
        self.waiting = True
        threading.Thread(target=self._wait_for_client, daemon=True).start()

    def _wait_for_client(self):
        """
        Blocks until a client connects (network.conn is set),
        then transitions into the placement phase.
        """
        while self.network.conn is None:
            time.sleep(0.1)

        # Client connected: enter multiplayer placement
        self.state.network    = self.network
        self.state.is_host    = True
        self.state.game_state = "placing"

    def start_join(self):
        """
        Parse the ip_input (format "HOST:PORT") and attempt to connect.
        Defaults to port 5000 if none specified.
        """
        text = self.ip_input.strip()
        if not text:
            return

        host, port = text, 5000
        if ":" in text:
            h, p = text.split(":", 1)
            host = h.strip()
            if p.strip().isdigit():
                port = int(p.strip())

        try:
            self.network = Network(is_host=False, host_ip=host, port=port)
        except Exception as e:
            print("Join failed:", e)
            return

        # Immediately enter multiplayer placement as a client
        self.state.network    = self.network
        self.state.is_host    = False
        self.state.game_state = "placing"

    def handle_event(self, event: pygame.event.Event):
        """
        Handle text input for join-mode and
        mouse clicks (mode toggles are done in the render via lambdas).
        """
        # Text input when typing the join address
        if event.type == pygame.KEYDOWN and self.mode == "join":
            if event.key == pygame.K_BACKSPACE:
                self.ip_input = self.ip_input[:-1]
            elif event.unicode.isprintable():
                self.ip_input += event.unicode
