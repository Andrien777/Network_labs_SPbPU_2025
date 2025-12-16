import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8

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
    
def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        # Ждем получение пакета
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Время истекло
            print("Response timeout")
            return None
        recPacket, addr = mySocket.recvfrom(1024)
        timeReceived = time.time()
        
        # Извлекаем ICMP-заголовок и данные
        left_bytes = recPacket[:-8]
        header = left_bytes[-8:]
        resp_type, code, checksum, resp_id, seq = struct.unpack("!bbHHh", header)
        
        if resp_type != 0 or resp_id != ID:
            print("Echo response failed")
            return None
        
        # Извлекаем IP-заголовок и данные
        ip_header = left_bytes[:20]
        icmp_data = struct.calcsize('d')
        ttl = struct.unpack('!B', ip_header[8:9])[0]
        time_sent = struct.unpack('!d', recPacket[28:])[0]
        delay = timeReceived - time_sent
        return (icmp_data, delay, ttl)

def sendOnePing(mySocket, destAddr, ID, seq):
    # Формат заголовка: type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Делаем фиктивный заголовок с нулевой контрольной суммой.
    # struct -- Интерпретирует строки как упакованные бинарные данные
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, seq)
    data = struct.pack("!d", time.time())
    # Вычисляем контрольную сумму данных и заголовка.
    myChecksum = checksum(header + data)
    # Получаем реальную контрольную сумму и помещаем в заголовок.
    myChecksum = int(myChecksum) & 0xffff
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, seq)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET должен иметь тип tuple, а не str
                                            #И списки, и кортежи (тип tuple) состоят из набора объектов
                                            #к которым можно обращаться по их порядковому номеру
                                                
def doOnePing(destAddr, timeout, seq):
    icmp = socket.getprotobyname("icmp")
    #SOCK_RAW – достаточно мощный тип сокета. Для подробной информации см.: http://sock-raw.org/papers/sock_raw
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    myID = os.getpid() & 0xFFFF #Возвращаем идентификатор текущего процесса
    sendOnePing(mySocket, destAddr, myID, seq)
    data = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return data
    
    
def ping(host, timeout=1):
    #timeout=1 означает: Если ответа нет в течение секунды, клиент предполагает, что
    #либо пакет запроса, либо ответный пакет потеряны
    dest = socket.gethostbyname(host)
    print("Pinging " + dest + " from Python:")
    print()
    
    rtt = []
    
    for i in range(10):
        recv = doOnePing(dest, timeout, i + 1)
        if recv == None:
            time.sleep(1)
            continue
        print(f'Response from {host}: {recv[0]} bytes, delay {recv[1]} s, TTL = {recv[2]}')
        rtt.append(recv[1])
        time.sleep(1)
    print('Stats:')
    print(f'Packets sent: 10, Packets received: {len(rtt)}, Packet loss: {(10 - len(rtt)) * 10}%')
    print(f'Min delay {min(rtt)} s, Max delay: {max(rtt)} s, Avg delay: {sum(rtt) / len(rtt)} s')

if len(sys.argv) != 2:
    print('Usage: python ping.py host')

ping(sys.argv[1])
        