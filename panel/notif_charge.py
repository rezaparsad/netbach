from sys import path
from os import path as os_path, environ
import django


path.append(os_path.join(os_path.dirname(__file__), '..'))
environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()



from account.models import User
from cloud.models import ServerRent
from wallet.models import Wallet
import datetime
from pytz import timezone
from time import sleep


while True:
    for user in User.objects.all():
        amount = Wallet.objects.get(user=user).amount
        servers = []
        for server in ServerRent.objects.filter(is_active=True):
            time_expire = datetime.datetime.now(timezone('Asia/Tehran')) + datetime.timedelta(days=1)
            if server.expire.timestamp() < time_expire.timestamp():
                servers.append(server)
        
        if servers.__len__() > 0:
            price = 0
            for server in servers:
                price += server.server.price_daily if server.payment_duration == 'daily' else server.server.price_monthly
            
            if price > amount:
                print(user.phone, amount, price)
    sleep(300)
