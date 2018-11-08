import datetime
# from dateutil.parser import parse
# import pandas as pd

datestr = '14.03.2018 10:00'
s = datestr[0:10]

# date1 = datetime.datetime.strptime(s, '%d.%m.%Y')
# print(date1)
dat = datetime.datetime.strptime(s, '%d.%m.%Y')
def date_chek(date):
    today = datetime.datetime.today()
    return date>today
print(dat.date())
print(datetime.date.today())


#DELETE FROM public.tenders_tenders WHERE deadline < current_date