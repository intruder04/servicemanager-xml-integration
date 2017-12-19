import pytz, datetime
local = pytz.timezone ("Europe/Moscow")
naive = datetime.datetime.strptime ("2017.07.04 06:15:00", "%Y.%m.%d %H:%M:%S")
local_dt = local.localize(naive, is_dst=None).timestamp()
print(local_dt)

