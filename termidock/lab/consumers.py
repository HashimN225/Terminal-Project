import asyncio
import docker
import threading
from channels.generic.websocket import AsyncWebsocketConsumer


class TerminalConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer that connects browser terminal to a Docker container.

    Flow:
    Browser (Xterm.js) <-> WebSocket <-> This Consumer <-> Docker Container
    """

    async def connect(self):
        """Called when browser opens a WebSocket connection."""
        self.container_id = self.scope['url_route']['kwargs']['container_id']
        self.container = None
        self.exec_socket = None
        self.sock = None
        self.running = False

        await self.accept()

        success = await asyncio.get_event_loop().run_in_executor(
            None, self._attach_to_container
        )

        if success:
            self.running = True
            self.read_thread = threading.Thread(target=self._read_output, daemon=True)
            self.read_thread.start()
            await self.send(text_data="\r\n\033[32m Connected to Ubuntu container!\033[0m\r\n\r\n")
        else:
            await self.send(text_data="\r\n\033[31m Failed to connect to container.\033[0m\r\n")
            await self.close()

    def _attach_to_container(self):
        """
        Attach to Docker container and open an interactive bash shell.
        This runs in a thread because docker calls are blocking.
        """
        try:
            client = docker.from_env()
            self.container = client.containers.get(self.container_id)

            if self.container.status != 'running':
                return False

            exec_instance = client.api.exec_create(
                self.container_id,
                '/bin/bash',
                stdin=True,
                tty=True,
                stdout=True,
                stderr=True,
            )

            self.exec_socket = client.api.exec_start(
                exec_instance['Id'],
                socket=True,
                tty=True,
            )

            self.sock = self.exec_socket._sock
            self.sock.settimeout(0.1)  
            return True

        except Exception as e:
            print(f"[TerminalConsumer] Error attaching to container: {e}")
            return False

    def _read_output(self):
        """
        Background thread: continuously reads output from Docker container
        and sends it back to the browser via WebSocket.
        """
        loop = asyncio.new_event_loop()

        while self.running:
            try:
                data = self.sock.recv(4096)
                if data:
                    loop.run_until_complete(
                        self.send(text_data=data.decode('utf-8', errors='replace'))
                    )
            except OSError:
                continue
            except Exception as e:
                if self.running:
                    print(f"[TerminalConsumer] Read error: {e}")
                break

        loop.close()

    async def receive(self, text_data=None, bytes_data=None):
        """
        Called when browser sends data (user pressed a key).
        Forward the keystroke directly into the Docker container shell.
        """
        if not self.running or not self.sock:
            return

        try:
            if text_data:
                self.sock.send(text_data.encode('utf-8'))
        except Exception as e:
            print(f"[TerminalConsumer] Error sending to container: {e}")
            await self.send(text_data=f"\r\n\033[31mConnection error: {str(e)}\033[0m\r\n")

    async def disconnect(self, close_code):
        """Called when browser disconnects. Clean up resources."""
        self.running = False

        try:
            if self.exec_socket:
                self.exec_socket.close()
        except Exception:
            pass

        print(f"[TerminalConsumer] Disconnected: {self.container_id[:12]}")