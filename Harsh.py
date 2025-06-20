import os
import socket
import threading
import asyncio
import multiprocessing
from cryptography.fernet import Fernet
from functools import wraps

# Generate a key (for demo)
key = Fernet.generate_key()
cipher = Fernet(key)

# Decorator to log actions
def log_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# Metaclass for enforcing interface
class InterfaceEnforcer(type):
    def __new__(cls, name, bases, dct):
        if "process_request" not in dct:
            raise TypeError("Must implement process_request method")
        return super().__new__(cls, name, bases, dct)

# Server logic
class FileServer(metaclass=InterfaceEnforcer):
    def __init__(self, host='localhost', port=9999):
        self.host, self.port = host, port
        self.server_socket = socket.socket()
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)

    @log_action
    def start(self):
        print("Server started...")
        while True:
            client, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        data = client.recv(1024)
        decrypted = cipher.decrypt(data)
        print("Received:", decrypted.decode())
        response = self.process_request(decrypted.decode())
        encrypted = cipher.encrypt(response.encode())
        client.send(encrypted)
        client.close()

    def process_request(self, data):
        return f"Processed: {data[::-1]}"

# Recursive file searcher
def find_files_recursively(path, extension=".py"):
    results = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(extension):
                results.append(os.path.join(root, f))
    return results

# Client logic (async)
async def send_data(data):
    reader, writer = await asyncio.open_connection('localhost', 9999)
    encrypted = cipher.encrypt(data.encode())
    writer.write(encrypted)
    await writer.drain()
    response = await reader.read(1024)
    decrypted = cipher.decrypt(response)
    print("Server responded:", decrypted.decode())
    writer.close()
    await writer.wait_closed()

# Parallel execution example
def parallel_search(path):
    with multiprocessing.Pool(4) as pool:
        files = pool.map(find_files_recursively, [path]*4)
        return [item for sublist in files for item in sublist]

# Main entry
if __name__ == "__main__":
    server = FileServer()
    threading.Thread(target=server.start, daemon=True).start()
    asyncio.run(send_data("Hello from async client!"))
    results = parallel_search(".")
    print(f"Found {len(results)} Python files")
