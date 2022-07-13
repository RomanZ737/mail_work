import imaplib
from decouple import config
import datetime

date = (datetime.date.today() - datetime.timedelta(days=14)).strftime("%d-%b-%Y")

print(date)

now = datetime.datetime.now()

frame1 = datetime.datetime.fromisoformat(now.strftime("%Y-%m-%d") + ' 16:50:00')  # Промежуток времени "от"
frame2 = datetime.datetime.fromisoformat(now.strftime("%Y-%m-%d") + ' 23:59:00')  # Промежуток времени "до"

print(frame1)
print(frame2)

if frame1 < now < frame2:
    print("Время Попадает")
else:
    print("Время не попадает")
