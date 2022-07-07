import _datetime
# from datetime import datetime
# from datetime import datetime
import datetime

date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")

print(date)

now = datetime.datetime.now()
frame1 = datetime.datetime.now().strftime("%d/%m/%y 18:50")
frame2 = datetime.datetime.now().strftime("%d/%m/%y 19:58")
print("Тип данных now: ", now)
print("Тип данных frame: ", type(frame2))
# print(now.strftime("%Y-%m-%d %I:%M"))             # 2017-05-03
# print(now.strftime("%d/%m/%Y"))             # 03/05/2017
# print(now.strftime("%d/%m/%y"))             # 03/05/17
# print(now.strftime("%d %B %Y (%A)"))        # 03 May 2017 (Wednesday)
# print(now.strftime("%d/%m/%y %I:%M"))       # 03/05/17 01:36

# if frame1 < now < frame2:
#     print("OK")
