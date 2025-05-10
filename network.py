# network.py

import socket
import threading
import json
from queue import Queue

class Network:
    """
    TCP JSON messaging. If is_host, bind/listen then accept() in a background thread.
    Once a client connects, start the listener thread to enqueue incoming messages.
    """

    def __init__(self, is_host: bool, host_ip: str, port: int = 5000):
        self.queue = Queue()
        self.sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow address reuse so restarting host won't fail
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if is_host:
            self.sock.bind((host_ip, port))
            self.sock.listen(1)
            self.conn = None
            # Accept in background so UI doesn’t block
            threading.Thread(target=self._accept_client, daemon=True).start()
        else:
            self.sock.connect((host_ip, port))
            self.conn = self.sock
            # Start listener immediately
            threading.Thread(target=self._listen, daemon=True).start()

    def _accept_client(self):
        """Blocking accept; once done, start listening thread."""
        conn, _ = self.sock.accept()
        self.conn = conn
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        """Read newline-delimited JSON messages into self.queue without crashing."""
        buffer = b""
        while True:
            try:
                data = self.conn.recv(4096)
            except (ConnectionResetError, OSError):
                # Peer disconnected or socket closed
                break

            if not data:
                # Clean shutdown
                break

            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    msg = json.loads(line.decode())
                    self.queue.put(msg)
                except json.JSONDecodeError:
                    pass

    def send(self, msg: dict):
        """Send a JSON-serializable dict, newline-terminated."""
        data = json.dumps(msg).encode() + b"\n"
        try:
            self.conn.sendall(data)
        except (BrokenPipeError, OSError):
            # Connection gone
            pass

    def recv(self) -> dict | None:
        """Non-blocking receive: next msg or None."""
        try:
            return self.queue.get_nowait()
        except:
            return None
