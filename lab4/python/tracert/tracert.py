import sys
import struct
import time
import select
import binascii
import socket
import os

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

def checksum(str):
    csum = 0
    countTo = (len(str) / 2) * 2
    count = 0
    while count < countTo:
        thisVal = str[count+1] * 256 + str[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
        
    if countTo < len(str):
        csum = csum + str[len(str) - 1]
        csum = csum & 0xffffffff
        
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer
    
def build_packet():
    # Формат заголовка: type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    ID = os.getpid() & 0xFFFF #Возвращаем идентификатор текущего процесса
    # Делаем фиктивный заголовок с нулевой контрольной суммой.
    # struct -- Интерпретирует строки как упакованные бинарные данные
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("!d", time.time())
    # Вычисляем контрольную сумму данных и заголовка.
    myChecksum = checksum(header + data)
    # Получаем реальную контрольную сумму и помещаем в заголовок.
    myChecksum = int(myChecksum) & 0xffff
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    return packet
    
def get_route(host):
    for ttl in range(1, MAX_HOPS + 1):
        timeLeft = TIMEOUT
        for _ in range(TRIES):
            # Создание сокета с заданным TTL пакетов и таймаутом
            dest = socket.gethostbyname(host)
            icmp = socket.getprotobyname('icmp')
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            mySocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                # Отправка пакета
                pack = build_packet()
                mySocket.sendto(pack, (host, 1))
                # Замер времени на получение ответа
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Время истекло
                    print(f"ttl {ttl} Response timeout")
                    continue
                recPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft -= howLongInSelect
                # Суммарный таймаут
                if timeLeft <= 0:
                    print(f"ttl {ttl} Response timeout")
                    continue
                # Попытка получить имя хоста
                try:
                    curr_host = socket.gethostbyaddr(addr[0])[0]
                except socket.herror:
                    curr_host = ''
                    
                # Извлечение ICMP-заголовка и данных
                left_bytes = recPacket[:-8]
                header = left_bytes[-8:]
                resp_type, code, checksum, resp_id, seq = struct.unpack("!bbHHh", header)
                
                if code != 0 and resp_type in (0, 3, 8, 11):
                    print(f"ttl {ttl} Echo response failed, type {resp_type} code {code}")
                    continue
                
                delay = timeReceived - startedSelect
                print(f'ttl {ttl}: rtt={delay} s {addr[0]} {curr_host}')
                break
            # Таймауты игнорируются
            except socket.timeout:
                print(f"ttl {ttl} Response timeout")
                continue
            
            except Exception as e:
                print(e)
                return
            
            # Закрытие сокета
            finally:
                mySocket.close()
                
        if dest == addr[0]:
            break

if len(sys.argv) != 2:
    print('Usage: python tracert.py host')

get_route(sys.argv[1])