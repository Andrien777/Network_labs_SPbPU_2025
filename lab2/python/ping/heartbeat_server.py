import random
from socket import *
import time
import threading
# Создаем UDP-сокет
# Для UDP используем SOCK_DGRAM
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Связываем порт 12000 с сокетом сервера
serverSocket.bind(('', 12000))

# Моменты последней активности клиентов
last_heard = {}

# Обработка сокета в отдельном потоке для корректного обнаружения неактивных клиентов
def socket_handler(sock):
    while True:
        # Получаем пакеты от клиента с адресом address
        message, address = sock.recvfrom(1024)
        # Извлечение данных
        txt = message.decode().split()
        # Если Heartbeat
        if txt[0] == 'HEARTBEAT':
            last_heard[str(address)] = time.time()
            print(f'Received HEARTBEAT from {address}, timestamp {last_heard[str(address)]}')
    
th = threading.Thread(target=socket_handler, args=(serverSocket, ))
th.start()

while True:
    # Мониторинг активности
    inactive = []
    for (addr, timestamp_heard) in last_heard.items():
        if time.time() - timestamp_heard > 3:
            print(f'Client {addr} has not sent heartbeat in 3 seconds')
            inactive.append(addr)
    # Удаление неактивных клиентов
    for addr in inactive:
        last_heard.pop(addr)
        