import imaplib
from decouple import config
import datetime

"""Magick numbers Block"""
strShift3 = 3
strShift2 = 2
strShift1 = 1

date = datetime.date.today().strftime("%d-%b-%Y")  # Сегодняшняя дата в формате для IMAP

username = config("MailuserID", default='')
password = config('Mailpassword', default='')

imap = imaplib.IMAP4_SSL("mail.zfamily.aero")  # Коннектимся к серверу
imap.login(username, password)  # Логинимся на сервер
imap.select("INBOX")  # Выбираем ящик

typ, data = imap.uid('search', None,
                     '(BEFORE {date} HEADER Subject "Backup Log Report")'.format(date=date))  # Фильтруем нужные письма
msg_list = []  # Пустой список для результатов поиска
print(data)
target_str = str(data)[str(data).find("'")+strShift1:str(data).rfind("'")]  # Переводим полученные из почты данные (UID писем) в строку и обрезаем не лишние символы
for msg_uid in target_str.split():  # Перебираем письма по UID
    msg_list.append(msg_uid)
print(msg_list)

#imap.uid('copy', '51914', "BackUp_Log")


# message_received = imap.uid('fetch', "51914", '(RFC822)')
# print(message_received)
