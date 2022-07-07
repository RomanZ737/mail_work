import imaplib
import pymysql
from decouple import config
import paramiko
import time
import datetime
from pymysql.cursors import DictCursor  # Возвразает курсор в виде словаря из базы данных

# Выполняем поиск писем старше сегодняшнего дня с темой BackUp Log Report,
# перемещаем эти письма в папку BackUp_Log, из папки Входящие удлаем все кроме последнего

def search_backup_mail():
    date = datetime.date.today().strftime("%d-%b-%Y")  # Сегодняшняя дата в формате для IMAP
    strshift1 = 1
    # Выполняем поиск писем старше сегодняшнего дня с темой BackUp Log Report
    typ, data = imap.uid('search', None,
                         '(BEFORE {date} HEADER Subject "Backup Log Report")'.format(
                             date=date))  # Фильтруем нужные письма
    target_str = str(data)[str(data).find("'") + strshift1:str(data).rfind(
        "'")]  # Переводим полученные из почты данные (UID писем) в строку и обрезаем не лишние символы
    for msg_uid in target_str.split():  # Перебираем письма по UID
        imap.uid('copy', msg_uid, "BackUp_Log")
        imap.uid('store', msg_uid, '+FLAGS', '\\Deleted')
    imap.expunge()  # Удаляем помеченные письма


def firewall_acl(acl_1, acl_2):
    net_acl_list = []  # Фактический Список подсетей в faerowall
    for i in acl_1.decode("utf-8").split("\n")[6:(len(acl_1.decode("utf-8").split("\n")) - 1):2]:
        net_acl_list.append(i[27:i.rfind("/24")])
    # Сравниванием с поступившим списком и корректируем при необходимости
    for j in acl_2:  # Сравниваем список полученный из faerwall и список сформированный из почты
        if j not in net_acl_list:  # Если подсети из почты нет в фактическом списке firewall, то добавляем в новый список, который загрузим в firewall
            new_net_acl_list.append(j)
    return new_net_acl_list


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
        imap.copy(msg_num, "Mail_Error")  # Копируем отфильтрованные письма в ящик Mail_Erorr
        imap.store(msg_num, '+FLAGS', '\\Deleted')  # Помечаем письма для удаления
        if ip[:(
                ip.rfind(
                    '.'))] not in local_net_ip:  # Фальтруем от локальных сетей и добавляем в массив для переноса в базу
            net_list.append(ip[:ip.rfind('.')] + '.0')
    imap.expunge()  # Удаляем помеченные письма
    return net_list


# Фунция sql_result_poc обрабатывет результат запроса в базу данных
# и результаты обработки почты на выходе
# получается два словаря (добавить в базу данных - sql_add_array и
# обновить базу данных - sql_update_array) и один
# список (добавить в firewall)


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


def sql_data_add(add_to_array):  # Добавление данных в базу SQL
    insert_array = []
    insert_in = """INSERT INTO ip_to_block (ip, count)
                     VALUES (%s, %s)"""  # Формируем запрос к базе
    for k, v in add_to_array.items():  # Фрмируем список контежей для переменных
        insert_array.append((k, v))
    cur.executemany(insert_in, insert_array)
    connection.commit()


def sql_data_update(update_to_array):  # Обновляем данные в базе SQL
    update_array = []
    change_data = """UPDATE
                        ip_to_block
                    SET
                        count = %s
                    WHERE ip = %s"""
    for k, v in update_to_array.items():  # Фрмируем список контежей для переменных
        update_array.append((v, k))
    cur.executemany(change_data, update_array)
    connection.commit()


sql_add_array = {}  # Массив данных для добавления в базу SQL
sql_update_array = {}  # Массив данных для обновления в базы SQL
firewall_list = []  # Список данных для добавления в firewall
net_list = []  # Пустой массив для IP адресов

local_net_ip = ['10.0.1', '192.168.2', '172.16.10', '172.16.20', '10.0.100']  # Список подсетей локальной сети

"""Блок работы с почтой"""

username = config("MailuserID", default='')
password = config('Mailpassword', default='')

imap = imaplib.IMAP4_SSL("mail.zfamily.aero")  # Коннектимся к серверу
imap.login(username, password)  # Логинимся на сервер
imap.select("INBOX")  # Выбираем ящик

# Блок ежесуточных операций с почтой, если текущее время
#     текущих суток попадает в определённый интервал времени
#      frame1 - frame2, то выполняются определённые операции

now = datetime.datetime.now()  # Текущая Дата и время

frame1 = datetime.datetime.fromisoformat(now.strftime("%Y-%m-%d") + ' 23:51:00')  # Промежуток времени "от"
frame2 = datetime.datetime.fromisoformat(now.strftime("%Y-%m-%d") + ' 23:59:00')  # Промежуток времени "до"

if frame1 < now < frame2:
    search_backup_mail()  # Выполняем поиск писем старше сегодняшнего дня с темой BackUp Log Report

"""Блок работы с почтой каждые 5 минут"""

typ, data = imap.search(None, 'Subject', '"Postfix SMTP server"')  # Фильтруем нужные письма

d = str(data)  # Переводим полученные из почты данные в строку

if len(d) > 5:  # Проверяем есть ли письма в результате поиска

    net_list_build(d)  # Список подсетей для добавления в базу

    imap.close()  # Окончание раюоты с почтовым ящиком
    imap.logout()  # Окончание работы с почтовым ящиком

    dict_nets = dickt_build(
        net_list)  # Построение словоря IP сетей для сравнения с базой данных и добавления в firewall
    """DEBUG PRINT"""
    #    print("Данные из почты: ", dict_nets)

    """Блок работы с базой данных SQL"""

    connection = pymysql.connect(  # Коннектимся к базе MySQL
        host=config("SQLhost", default=''),
        user=config("SQLusrID", default=''),
        password=config('SQLpassword', default=''),
        db=config('SQLdb', default=''),
        charset='utf8mb4',
        #    cursorclass=DictCursor  # Курсор будет возвращать значения в виде словарей
    )

    cur = connection.cursor()  # Создаём курсор

    """Блок создания таблицы"""
    # crate_table = """CREATE TABLE ip_to_block(
    #                     id INT PRIMARY KEY AUTO_INCREMENT,
    #                     ip VARCHAR(255) NOT NULL,
    #                     count INT);"""

    # Запрос данных в SQL с повторениями меньше 5
    get_data = """SELECT * FROM ip_to_block  
                    WHERE count < 5"""
    cur.execute(get_data)
    result = cur.fetchall()

    """DEBUG PRINT"""
    # print("Заброс из базы данных, повторения NET меньше 5")
    # for dicts in result:
    #     print(dicts)

    sql_result_poc(result, dict_nets)  # Обработка результата запроса SQL и данных их почты

    """DEBUG PRINT"""
    # print("Добавить в SQL: ", sql_add_array)
    # print("Обновить SQL: ", sql_update_array)
    # print("Лист firwwall: ", firewall_list)

    sql_data_add(sql_add_array)  # Добавляем данные в базу
    sql_data_update(sql_update_array)  # Обновляем данные в базе

    connection.close()

    if len(firewall_list) > 0:
        """Блок работы с USG Zyxel по SSH"""

        new_net_acl_list = []  # Список подсетей которые надо будет добавить в firewall

        hostname = config("USGhostname", default='')
        port = config("USGport", default='')
        username = config("USGuserID", default='')
        password = config("USGpassword", default='')

        # Создать объект SSH
        client = paramiko.SSHClient()
        # Автоматически добавлять стратегию, сохранять имя хоста сервера и ключевую информацию
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # подключиться к серверу
        client.connect(hostname, port, username, password, compress=True)

        channel = client.invoke_shell()  # Создаем интерактивную оболочку на SSH сервере

        channel.send(b"show geo-ip geography" + b'\n')  # Запрашиваел список подсетей в firewall
        time.sleep(1)
        stdout = channel.recv(60000)

        firewall_acl(stdout, firewall_list)  # Формируем список подсетей их firewall из ответа

        channel.send(b"configure terminal" + b'\n')  # Переходим в режим config
        time.sleep(1)

        for net_ip in new_net_acl_list:
            channel.send('geo-ip geography AQ all address ' + net_ip + '/24' + '\n')
            time.sleep(1)
            """DEBUG PRINT"""
            # print(channel.recv(60000)) # Монитор работы SSH
        client.close()

else:  # Если нет писем с ошибками
    imap.close()  # Окончание раюоты с почтовым ящиком
    imap.logout()  # Окончание работы с почтовым ящиком
    """DEBUG PRINT"""
    # print("Писем нет")
