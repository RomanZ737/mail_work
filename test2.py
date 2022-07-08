import imaplib
from decouple import config
import datetime

"""Magick numbers Block"""
strShift3 = 3
strShift2 = 2
strShift1 = 1

date = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%d-%b-%Y")

print(date)

username = config("MailuserID", default='')
password = config('Mailpassword', default='')

imap = imaplib.IMAP4_SSL("mail.zfamily.aero")  # Коннектимся к серверу
imap.login(username, password)  # Логинимся на сервер
imap.select("NAS")  # Выбираем ящик

# Выполняем поиск писем старше недели
# typ, data = imap.uid('search', None,
#                      '(BEFORE {date} (OR (FROM "nas@zfamily.aero") (FROM "nasd2@zfamily.aero")))'.format(date=date), 'SEEN')  # Фильтруем нужные письма
typ, data = imap.uid('search', None,
                     '(BEFORE {date})'.format(date=date))  # Фильтруем нужные письма

# print(data)
# new_array = []

target_str = str(data)[str(data).find("'")+strShift1:str(data).rfind("'")]  # Переводим полученные из почты данные (UID писем) в строку и обрезаем не лишние символы
print("Строка с результатов NAS: ", target_str)
print("Длина строки результатов NAS: ", len(target_str))

# for msg_uid in target_str.split():  # Перебираем письма по UID
#     # imap.uid('copy', msg_uid, "NAS")
#     # imap.uid('store', msg_uid, '+FLAGS', '\\Deleted')
#     new_array.append(msg_uid)
#
# print(new_array)
# print(len(new_array))
# imap.expunge()  # Удаляем помеченные письма

imap.select("BackUp_Log")

typ, data = imap.uid('search', None,
                     '(BEFORE {date})'.format(date=date))  # Фильтруем нужные письма
target_str = str(data)[str(data).find("'")+strShift1:str(data).rfind("'")]  # Переводим полученные из почты данные (UID писем) в строку и обрезаем не лишние символы
print("Строка с результатов BackUp_Log: ", target_str)
print("Длина строки результатов BackUp_Log: ", len(target_str))

imap.select("Mail_Error")

typ, data = imap.uid('search', None,
                     '(BEFORE {date})'.format(date=date))  # Фильтруем нужные письма
target_str = str(data)[str(data).find("'")+strShift1:str(data).rfind("'")]  # Переводим полученные из почты данные (UID писем) в строку и обрезаем не лишние символы
print("Строка с результатов Mail_Error: ", target_str)
print("Длина строки результатов Mail_Error: ", len(target_str))

imap.select("System_Fault")

typ, data = imap.uid('search', None,
                     '(BEFORE {date})'.format(date=date))  # Фильтруем нужные письма
target_str = str(data)[str(data).find("'")+strShift1:str(data).rfind("'")]  # Переводим полученные из почты данные (UID писем) в строку и обрезаем не лишние символы
print("Строка с результатов System_Fault: ", target_str)
print("Длина строки результатов System_Fault: ", len(target_str))

