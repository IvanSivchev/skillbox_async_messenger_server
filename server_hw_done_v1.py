#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports
users = []
message_history = []

class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server

    def send_history(self):
        for _ in message_history[-10:]:
            self.transport.write(_.encode())

    def data_received(self, data: bytes):
        print(data)
        decoded = data.decode()


        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r\n", "")
                if self.login in users:
                    self.transport.write(f"Логин {self.login} занят, попробуйте другой\n".encode())
                    print(users)
                    self.server.clients.remove(self.login)
                else:
                    self.transport.write(
                    f"Привет, {self.login}!\n".encode()
                )
                self.send_history()
                users.append(self.login)
            else:
                self.transport.write("Неправильный логин\n".encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Клиент вышел")

    def send_message(self, content: str):
        message = f"{self.login}: {content}\n"

        for user in self.server.clients:
            user.transport.write(message.encode())
        message_history.append(f"<{self.login}>  {content}")


class Server:
    clients: list

    def __init__(self):
        self.clients = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
