import socket
import time

# Создание сокета, таймаут 1 с
conn_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
conn_socket.settimeout (1)
# Кортеж адреса и порта сервера
server_addr = ('localhost', 12000)
# 10 раз
rtts = []
for i in range(10):
    # Формирование сообщения
    message = f'Ping {i + 1} {time.time()}'
    try:
        # Попытка отправки и ожидание ответа
        conn_socket.sendto(message.encode(), server_addr)
        start_time = time.time()
        response, server = conn_socket.recvfrom(1024)
        end_time = time.time()
        # Вычисление времени возврата
        rtt = end_time - start_time
        rtts.append(rtt)
        print(f'Response from {server}: {response.decode()} RTT={rtt: .6f} s')
    # В случае таймаута считать пакет потерянным
    except socket.timeout:
        print(f'Request timed out')

# После отправки 10 сообщений закрыть сокет       
conn_socket.close()

# Статистика
print(f'10 packets transmitted, {len(rtts)} packets received, {(10 - len(rtts)) * 10}% loss\nMin rtt: {min(rtts)} s, Max rtt: {max(rtts)} s, avg rtt: {sum(rtts) / len(rtts)} s')