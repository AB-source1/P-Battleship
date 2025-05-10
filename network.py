# network.py

import socket
import threading
import json
from queue import Queue

class Network:
    """
    Simple peer-to-peer TCP-based JSON messaging.
    One side is host (server), the other joins (client).
    Messages are newline-delimited JSON dicts.
    On socket close or error, a {"type":"disconnect"} message is enqueued.
    """

    def __init__(self, is_host: bool, host_ip: str, port: int = 5000):
        self.queue = Queue()
        self.sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow quick reuse of the same address
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if is_host:
            # — Host: bind, listen, then accept in background —
            self.sock.bind((host_ip, port))
            self.sock.listen(1)
            self.conn = None
            threading.Thread(target=self._accept_client, daemon=True).start()
        else:
            # — Client: connect immediately, then start listener —
            self.sock.connect((host_ip, port))
            self.conn = self.sock
            threading.Thread(target=self._listen, daemon=True).start()

    def _accept_client(self):
        """
        Blocking accept. Once a client connects, set self.conn
        and start the listener thread to read messages.
        """
        try:
            conn, _ = self.sock.accept()
        except OSError:
            # Socket closed or error on shutdown
            self.queue.put({"type":"disconnect"})
            return

        self.conn = conn
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        """
        Read newline-delimited JSON messages from self.conn.
        On clean close or error, enqueue a {"type":"disconnect"} message.
        """
        buffer = b""
        while True:
            try:
                data = self.conn.recv(4096)
            except (ConnectionResetError, OSError):
                # Remote hung up or socket error
                self.queue.put({"type":"disconnect"})
                break

            if not data:
                # Remote closed cleanly
                self.queue.put({"type":"disconnect"})
                break

            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    msg = json.loads(line.decode())
                    self.queue.put(msg)
                except json.JSONDecodeError:
                    # Skip malformed line
                    pass

    def send(self, msg: dict):
        """
        Send a JSON-serializable dict, terminated with newline.
        Silently drops if the connection is gone.
        """
        if not self.conn:
            return

        data = json.dumps(msg).encode() + b"\n"
        try:
            self.conn.sendall(data)
        except (BrokenPipeError, OSError):
            # Connection is closed
            self.queue.put({"type":"disconnect"})

    def recv(self) -> dict | None:
        """
        Non-blocking receive: returns the next queued message dict,
        or None if no message is waiting.
        """
        try:
            return self.queue.get_nowait()
        except:
            return None
