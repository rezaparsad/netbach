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
        servers: ServerRent = []
        for server in ServerRent.objects.filter(is_active=True):
            if server.expire.timestamp() < datetime.datetime.now(timezone('Asia/Tehran')) + datetime.timedelta(days=1):
                servers.append(server)
        
        price = 0
        for server in servers:
            price += server.server.price_daily if server.payment_duration == 'daily' else server.server.price_monthly
        
        if price > amount:
            print(amount, price)
            print(user.phone)
    sleep(300)
