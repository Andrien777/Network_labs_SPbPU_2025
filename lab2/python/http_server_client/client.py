import sys
from socket import *

# Проверка аргументов командной строки
if len(sys.argv) != 4:
    print("Usage: python client.py ip port file")
    sys.exit(1)

# Разбор аргументов   
ip = sys.argv[1]
port = int(sys.argv[2])
file = sys.argv[3]

# Попытка отправки запроса
try:
    active_socket = socket(AF_INET, SOCK_STREAM)
    active_socket.connect((ip, port))
    # Формирование GET-запроса
    request = f"GET {file} HTTP/1.1\nHost: {ip}\n\n"
    active_socket.send(request.encode())
    # Получение ответа
    response = active_socket.recv(8192).decode()
    print(response)
# Вывод сообщения об ошибке
except Exception as e:
    print(f"Err: {e}")
# Закрытие сокета в любом случае
finally:
    active_socket.close()