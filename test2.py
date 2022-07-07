import imaplib
from decouple import config
import datetime

username = config("MailuserID", default='')
password = config('Mailpassword', default='')

imap = imaplib.IMAP4_SSL("mail.zfamily.aero")  # Коннектимся к серверу
imap.login(username, password)  # Логинимся на сервер
imap.select("INBOX")  # Выбираем ящик
typ, data = imap.uid('search', None, 'FROM', '"event@zfamily.aero"')  # Фильтруем нужные письма

d = str(data)  # Переводим полученные из почты данные в строку
print(data)
