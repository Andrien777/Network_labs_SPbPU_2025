from socket import *
import sys
import pathlib

if len(sys.argv) <= 1:
    print('Usage: python proxy.py proxy_ip proxy_port')
    sys.exit(2)
# Создаем серверный сокет, привязываем его к порту и начинаем слушать
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], int(sys.argv[2])))
tcpSerSock.listen(1024)

# Кэшированные страницы в ОЗУ
cache = {}

# Имя сайта для добавления к нему путей до объектов
webname = ''

while 1:
    # Начинаем получать данные от клиента
    print('Ready...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Connected to:', addr)
    message = tcpCliSock.recv(1024).decode('utf-8')
    print(message)
    # Извлекаем имя файла из сообщения
    try:
        print('Filename: ', message.split()[1])
        filename = message.split()[1].partition("/")[2]
        print('Decoded filename: ', filename)
        filetouse = "D:\\Code\\Network_labs_repo\\lab2\\python\\proxy\\" + filename
        filetouse = filetouse.replace('/', '\\', -1)
        print('Decoded filename with path: ', filetouse)
    except:
        continue
    if webname == '' or filename.startswith('www.'):
        webname = filename
    try:
        # Проверяем, есть ли файл в кэше
        if filetouse in cache:
            print('Found page in RAM cache')
            # Прокси-сервер определяет попадание в кэш и генерирует ответное сообщение
            tcpCliSock.send(cache[filetouse])
        else:
            with open(filetouse, "rb") as f:
                outputdata = f.readlines()
                print('Reading from disk cache')
            # Прокси-сервер определяет попадание в кэш и генерирует ответное сообщение
            for line in outputdata:
                tcpCliSock.send(line)
            # Сохранение в ОЗУ-кэш
            cache[filetouse] = b''
            for line in outputdata:
                cache[filetouse] += line
    except FileNotFoundError:
        try:
            # Создаем сокет на прокси-сервере
            c = socket(AF_INET, SOCK_STREAM)
            if webname != filename:
                hostn = webname
            else:
                hostn = filename
            print('Request to ', hostn)
            # Соединяемся с сокетом по порту 80
            c.connect((hostn, 80))
            # Создаем временный файл на этом сокете и запрашиваем порт 80 файл, который нужен клиенту
            fileobj = c.makefile('rwb')
            if webname != filename:
                fileobj.write(("GET "+"http://" + hostn + '/' + filename + " HTTP/1.0\n\n").encode('utf-8'))
            else:
                fileobj.write(("GET "+"http://" + filename + " HTTP/1.0\n\n").encode('utf-8'))           
            fileobj.flush()
            
            # Читаем ответ в буфер
            # Создаем новый файл в кэше для запрашиваемого файла
            # А также отправляем ответ из буфера и соответствующий файл на сокет клиента
            pathlib.Path(filetouse).parent.mkdir(parents=True, exist_ok=True)
            with open(filetouse, "wb") as tmpFile:
                buf = fileobj.readlines()
                for line in buf:
                    tmpFile.write(line)
                    tcpCliSock.send(line)
            
        except Exception as e:
            print(f"Error in request: {e}")
            tcpCliSock.send("HTTP/1.0 500 Internal Server Error\r\n".encode('utf-8'))
            tcpCliSock.send("Content-Type:text/html\r\n".encode('utf-8'))
            tcpCliSock.send("\r\n".encode('utf-8'))
        
        finally:
            c.close()
            
    # Закрываем сокет клиента
    tcpCliSock.close()