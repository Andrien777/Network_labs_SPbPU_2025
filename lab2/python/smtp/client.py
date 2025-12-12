from socket import *
from random import randint
import base64

# Сообщение
msg = "TEST"
# Конец сообщения по RFC 5321
endmsg = "\r\n.\r\n"

# Сервер и сокет
mailserver =  ("aspmx.l.google.com", 25)

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(mailserver)

# Соединение
recv = sock.recv(1024).decode("utf-8")
print(f"Message after connection request: {recv}")
if recv[:3] != "220":
    print("220 not received")

# Отправка HELO  
hello_command = "HELO Alice\r\n"
sock.send(hello_command.encode())
recv = sock.recv(1024).decode("utf-8")
print(recv)
if recv[:3] != "250":
    print("250 not received")

# Начало почтовой транзакции, указание "откуда"  
mail_from = "MAIL FROM: <andrew6gog@gmail.com> \r\n"
sock.send(mail_from.encode())
recv = sock.recv(1024).decode("utf-8")
print(f"after MAIL FROM command: {recv}")
if recv[:3] != "250":
    print("250 not received")

# Указание "куда"   
rcpt_to = "RCPT TO: <andrew6gog@gmail.com> \r\n"
sock.send(rcpt_to.encode())
recv = sock.recv(1024).decode("utf-8")
print(f"after RCPT TO command: {recv}")
if recv[:3] != "250":
    print("250 not received")

# Начало отправки данных
data = "DATA\r\n"
sock.send(data.encode())
recv = sock.recv(1024).decode("utf-8")
print(f"After DATA command: {recv}")
# Message Id (RFC 5322)
msgid = f"Message-ID:<{base64.b64encode((str(randint(0, 10000000)) + msg).encode())}@andrew6gog> \r\n"
sock.send(msgid.encode())
# Поле From (RFC 5322) требуется Gmail
from_msg = "From:<andrew6gog@gmail.com> \r\n"
sock.send(from_msg.encode())   
# Тема
subject = "Subject: SMTP mail client testing \r\n"
sock.send(subject.encode())
# Тело и окончание
message = msg
sock.send(message.encode())
sock.send(endmsg.encode())
recv_msg = sock.recv(1024).decode("utf-8")
print("Response after sending message body: ", recv_msg)
if recv_msg[:3] != "250":
    print("250 not received")

# Завершение транзакции 
sock.send("QUIT\r\n".encode())
message = sock.recv(1024).decode("utf-8")
print(f'Message = "{message}"')
sock.close()