import paramiko
import time

hostname = "192.168.2.1"
port = 22
username = "admin"
password = "Roman777))_Pilot99"

# Создать объект SSH
client = paramiko.SSHClient()
# Автоматически добавлять стратегию, сохранять имя хоста сервера и ключевую информацию
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# подключиться к серверу
client.connect(hostname, port, username, password, compress=True)

# Выполнить команду linux
channel = client.invoke_shell()  # Создаем интерактивную оболочку на SSH сервере
# stdin, stdout, stderr = client.exec_command('configure terminal /')
# time.sleep(1)
# stdin, stdout, stderr = client.exec_command('show geo-ip geography /')
# time.sleep(1)
#command = "show geo-ip geography"
net_acl_list = []  # Список подсетей в faerowall
channel.send(b"show geo-ip geography" + b'\n')  # Запрашиваел список подсетей в firewall
time.sleep(1)
stdout = channel.recv(60000)
# Формируем список подсетей их firewall из ответа
for i in stdout.decode("utf-8").split("\n")[6:(len(stdout.decode("utf-8").split("\n"))-1):2]:
    net_acl_list.append(i[27:i.rfind("/24")])

channel.send(b"configure terminal" + b'\n')  #  Переходим в режим config
time.sleep(1)
net_ip = "113.116.72.0/24"
channel.send('geo-ip geography AQ all address ' + net_ip + '\n')
time.sleep(1)
stdout2 = channel.recv(60000)
client.close()
print("Было: ", net_acl_list)
print(stdout2)


