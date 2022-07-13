import imaplib
from decouple import config
import datetime

username = config("MailuserID", default='')
password = config('Mailpassword', default='')

imap = imaplib.IMAP4_SSL("mail.zfamily.aero")  # Коннектимся к серверу
imap.login(username, password)  # Логинимся на сервер
imap.select("INBOX")  # Выбираем ящик

date = datetime.date.today().strftime("%d-%b-%Y")  # Сегодняшняя дата в формате для IMAP
strshift1 = 1
# Выполняем поиск писем старше сегодняшнего дня с темой BackUp Log Report, только просмотренные
typ5, data5 = imap.uid('search', None,
                       '(BEFORE {date} FROM "Home Event")'.format(date=date), 'SEEN')  # Фильтруем нужные письма, только просмотренные
target_str = str(data5)[str(data5).find("'") + strshift1:str(data5).rfind(
    "'")]  # Переводим полученные из почты данные (UID писем) в строку и обрезаем не лишние символы
for msg_uid in target_str.split():  # Перебираем письма по UID
    imap.uid('copy', msg_uid, "Home_Event")
    imap.uid('store', msg_uid, '+FLAGS', '\\Deleted')
imap.expunge()  # Удаляем помеченные письма
