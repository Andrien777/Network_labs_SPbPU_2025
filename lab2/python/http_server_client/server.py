from socket import *
import threading

# Функция обработки запроса
def handle_request(active_socket):
    # Попытка открыть файл
    try:
        msg = active_socket.recv(1024).decode()
        filename = msg.split()[1]
        with open(filename[1:], 'rb') as f:
            # Прочтение файла
            out = f.read()
            # Отправка статуса и документа
            active_socket.send("HTTP/1.1 200 OK\n\n".encode())
            active_socket.sendall(out)
    # Ошибка при отсутствии файла
    except IOError:
        # Отправка ошибки 404
        err = "HTTP/1.1 404 Not Found\n\nFile Not Found"
        active_socket.send(err.encode())
    # Вне зависимости от выбранной ветки try/catch закрыть сокет
    finally:
        active_socket.close()

# Создать сокет и начать слушать на порту 80        
active_socket = socket(AF_INET, SOCK_STREAM)
active_socket.bind(('', 80))
active_socket.listen(5)
print("Ready\n")
while True:
    # Принять входящее подключение
    acc_sock, addr = active_socket.accept()
    print(addr)
    # Начать обработку
    th = threading.Thread(target=handle_request, args=(acc_sock, ))
    th.start()
