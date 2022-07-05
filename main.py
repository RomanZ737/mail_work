import imaplib
import pymysql
from decouple import config
from pymysql.cursors import DictCursor  # Возвразает курсор в виде словаря из базы данных


def dickt_build(array_ip):  # Построение словоря IPNet из почты для сравнения с базой данных
    ip_dict = {}
    for i in array_ip:
        if i in ip_dict:
            ip_dict[i] += 1
        else:
            ip_dict[i] = 1
    return ip_dict


def net_list_build(mail_data):  # Вынимаем IP адреса и отфильтровываем их от локальных подсетей
    for msg_num in mail_data[3:len(d) - 2].split(' '):
        check, message_received = imap.fetch(msg_num,
                                             '(RFC822)')  # Вынимаем содержимое каждого из отфильтрованных сообщений
        s = str(message_received[0])  # Фрмируем строку
        ip = (s[(s.find('[')) + 1:s.find(']')])  # Вырезаем IP
        if ip[:(
                ip.rfind(
                    '.'))] not in local_net_ip:  # Фальтруем от локальных сетей и добавляем в массив для переноса в базу
            net_list.append(ip[:ip.rfind('.')] + '.0')
    return net_list


"""Фунция sql_result_poc обрабатывет результат запроса в базу данных и результаты обработки почты
на выходе получается два словаря (добавить в базу данных - sql_add_array и обновить базу данных - sql_update_array) и один список (добавить в firewall) """


def sql_result_poc(array1, array2):
    result_dict = {}

    def dict_summ(add_arr1, add_arr2):  # Фрмирует из двух словарей один суммированием
        for key1, val1 in add_arr1.items():
            result_dict[key1] = val1
        for key2, val2 in add_arr2.items():
            result_dict[key2] = val2
        return result_dict

    for i in array1:
        if i[1] in array2:
            sql_update_array[i[1]] = i[2] + array2[i[1]]
            del array2[i[1]]
    for key, val in array2.items():
        sql_add_array[key] = val

    dict_summ(sql_add_array, sql_update_array)  # Суммируем словари

    for k, v in result_dict.items():  # Отфильтровывает данные для firewall - если IPNet встерчается 5 более раз
        if v >= 5:
            firewall_list.append(k)
    return firewall_list, sql_add_array, sql_update_array


def sql_data_add(add_to_array):  # Добавление данных в базу
    insert_array = []
    insert_in = """INSERT INTO ip_to_block (ip, count)
                     VALUES (%s, %s)"""  # Формируем запрос к базе
    for k, v in add_to_array.items():  # Фрмируем список контежей для переменных
        insert_array.append((k, v))
    cur.executemany(insert_in, insert_array)
    connection.commit()


def sql_data_update(update_to_array):  # Обновляем данные в базе
    update_array = []
    change_data = """UPDATE
                        ip_to_block
                    SET
                        count = %s
                    WHERE ip = %s"""
    for k, v in update_to_array.items():  # Фрмируем список контежей для переменных
        update_array.append((v, k))
    print(update_array)
    cur.executemany(change_data, update_array)
    connection.commit()


sql_add_array = {}  # Массив данных для добавления в базу SQL
sql_update_array = {}  # Массив данных для обновления в базы SQL
firewall_list = []  # Список данных для добавления в firewall

local_net_ip = ['10.0.1', '192.168.2', '172.16.10', '172.16.20', '10.0.100']  # Список подсетей локальной сети
net_list = []  # Пустой массив для IP адресов

username = config("MailuserID", default='')
password = config('Mailpassword', default='')

imap = imaplib.IMAP4_SSL("mail.zfamily.aero")  # Коннектимся к серверу
imap.login(username, password)  # Логинимся на сервер
messages = imap.select("Mail_Error")  # Выбираем ящик !!!! - НАДО ИЗМЕНИТЬ НА INBOX
typ, data = imap.search(None, 'Subject', '"Postfix SMTP server: errors from unknown"')  # Фильтруем нужные письма

d = str(data)  # Переводим полученные из почты данные в строку

net_list_build(d)  # Список подсетей для добавления в базу

'''Этот блок разблокировать после отладки - перемещает и удаляет письма
    imap.copy(msg_num, "Mail_Error")  # Копируем отфильтрованные письма в ящик Mail_Erorr
    imap.store(msg_num, '+FLAGS', '\\Deleted')  # Помечаем письма для удаления
imap.expunge()  # Удаляем помеченные письма '''

imap.close()  # Окончание раюоты с почтовым ящиком
imap.logout()  # Окончание работы с почтовым ящиком

dict_nets = dickt_build(net_list)  # Построение словоря IP сетей для сравнения с базой данных и добавления в firewall
print("Данные из почты: ", dict_nets)

connection = pymysql.connect(  # Коннектимся к базе MySQL
    host='10.0.1.66',
    user=config("SQLusrID", default=''),
    password=config('SQLpassword', default=''),
    db='ip_blacklist',
    charset='utf8mb4',
    #    cursorclass=DictCursor  # Курсор будет возвращать значения в виде словарей
)

cur = connection.cursor()  # Создаём курсор

"""Блок создания таблицы"""
# crate_table = """CREATE TABLE ip_to_block(
#                     id INT PRIMARY KEY AUTO_INCREMENT,
#                     ip VARCHAR(255) NOT NULL,
#                     count INT);"""

get_data = """SELECT * FROM ip_to_block  # Запрос данных в SQL с повторениями меньше 5
                WHERE count < 5"""
cur.execute(get_data)
result = cur.fetchall()

"""DEBUG PRINT"""
for dicts in result:
    print(dicts)

sql_result_poc(result, dict_nets)

"""DEBUG PRINT"""
print("Добавить в SQL: ", sql_add_array)
print("Обновить SQL: ", sql_update_array)
print("Лист firwwall: ", firewall_list)

sql_data_add(sql_add_array)  # Добавляем данные в базу
sql_data_update(sql_update_array)  # Обновляем данные в базе

connection.close()
