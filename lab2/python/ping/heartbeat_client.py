import socket
import time
import random

# Создание сокета, таймаут 1 с
conn_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Кортеж адреса и порта сервера
server_addr = ('localhost', 12000)
for i in range(10):
    # Формирование сообщения
    message = f'HEARTBEAT {i + 1} {time.time()}'
    print(message)
    conn_socket.sendto(message.encode(), server_addr)
    time.sleep(1)

# После отправки 10 сообщений закрыть сокет       
conn_socket.close()
