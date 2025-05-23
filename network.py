# network.py

import socket
import threading
import errno
import json
from queue import Queue

"""
Module: network.py
Purpose:
  - Peer-to-peer TCP JSON messaging for multiplayer.
  - Host binds to ports 5000–5009; client connects to host.
  - Messages are newline-delimited JSON dicts enqueued via Queue.
Future Hooks:
  - Implement heartbeat/ping and automatic reconnection.
  - Use UDP broadcast for lobby discovery.
"""

class Network:
    

    def __init__(self, is_host: bool, host_ip: str, port: int = 5000):
        self.queue = Queue()
        self.sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow quick reuse of the same address
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if is_host:
            # Try binding to port, or port+1, ..., port+9
            bound = False
            for p in range(port, port + 10):
                try:
                    self.sock.bind((host_ip, p))
                    self.sock.listen(1)
                    self.port = p
                    bound = True
                    break
                except OSError as e:
                    if e.errno == errno.EADDRINUSE:
                        continue
                    else:
                        raise
            if not bound:
                raise OSError(f"No free ports in range {port}-{port+9}")
            self.conn = None
            # Accept in background so UI doesn’t block
            threading.Thread(target=self._accept_client, daemon=True).start()
        else:
            # Client: connect to specified host_ip:port
            self.sock.connect((host_ip, port))
            self.conn = self.sock
            self.port = port
            threading.Thread(target=self._listen, daemon=True).start()

    def _accept_client(self):
        """
        Accept a client connection, then start listening thread.
        """
        try:
            conn, _ = self.sock.accept()
        except OSError:
            # Socket closed or error on shutdown
            self.queue.put({"type": "disconnect"})
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
                self.queue.put({"type": "disconnect"})
                break

            if not data:
                # Peer closed cleanly
                self.queue.put({"type": "disconnect"})
                break

            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    msg = json.loads(line.decode())
                    self.queue.put(msg)
                except json.JSONDecodeError:
                    # Skip malformed lines
                    pass

    def send(self, msg: dict):
        """
        Send a JSON-serializable dict, newline-terminated.
        Silently enqueues a disconnect if the connection is gone.
        """
        if not self.conn:
            self.queue.put({"type": "disconnect"})
            return
        data = json.dumps(msg).encode() + b"\n"
        try:
            self.conn.sendall(data)
        except (BrokenPipeError, OSError):
            self.queue.put({"type": "disconnect"})

    def recv(self) -> dict | None:
        """
        Non-blocking receive: returns the next queued message dict,
        or None if no message is waiting.
        """
        try:
            return self.queue.get_nowait()
        except:
            return None
