import _datetime
# from datetime import datetime
# from datetime import datetime
import datetime

# date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
#
# print(date)

now = datetime.datetime.now()

frame1 = datetime.datetime.fromisoformat(now.strftime("%Y-%m-%d") + ' 20:20:00')
frame2 = datetime.datetime.fromisoformat(now.strftime("%Y-%m-%d") + ' 20:30:00')
print(now)
print(frame1)
print(frame2)
# print(now.strftime("%Y-%m-%d %I:%M"))             # 2017-05-03
# print(now.strftime("%d/%m/%Y"))             # 03/05/2017
# print(now.strftime("%d/%m/%y"))             # 03/05/17
# print(now.strftime("%d %B %Y (%A)"))        # 03 May 2017 (Wednesday)
# print(now.strftime("%d/%m/%y %I:%M"))       # 03/05/17 01:36

if frame1 < now < frame2:
    print("OK")
else:
    print("NOT")