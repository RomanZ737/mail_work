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

# Выполняем поиск писем старше сегодняшнего дня с темой BackUp Log Report
typ, data = imap.uid('search', None,
                     '(BEFORE {date} (OR (FROM "nas@zfamily.aero") (FROM "nasd2@zfamily.aero")))'.format(date=date), 'SEEN')  # Фильтруем нужные письма
# typ, data = imap.uid('search', None,
#                      '(BEFORE {date} FROM "nas@zfamily.aero")'.format(date=date), 'SEEN')  # Фильтруем нужные письма

print(data)
new_array = []
target_str = str(data)[str(data).find("'")+strShift1:str(data).rfind("'")]  # Переводим полученные из почты данные (UID писем) в строку и обрезаем не лишние символы
for msg_uid in target_str.split():  # Перебираем письма по UID
    # imap.uid('copy', msg_uid, "NAS")
    # imap.uid('store', msg_uid, '+FLAGS', '\\Deleted')
    new_array.append(msg_uid)

print(len(new_array))
# imap.expunge()  # Удаляем помеченные письма



# message_received = imap.uid('fetch', "51914", '(RFC822)')
# print(message_received)
