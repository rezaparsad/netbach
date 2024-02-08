import datetime
import os
import sys
import time

import django
import jdatetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from wallet.models import Wallet, ServerCost
from cloud.models import ServerRent
from config.settings import hetzner, linode


def get_datacenter(server):
    if server.datacenter.name.lower() == "hetzner":
        return hetzner
    elif server.datacenter.name.lower() == "linode":
        return linode
    else:
        return None


def check_servers():
    print("Check started ... !\n\n")
    while True:
        try:
            servers = ServerRent.objects.filter(is_active=True)
            for server in servers:
                current_date = jdatetime.datetime.now()
                expire_date = jdatetime.datetime.fromgregorian(datetime=server.expire)
                if current_date >= expire_date:
                    fa_time = jdatetime.datetime.fromgregorian(datetime=datetime.datetime.now()).strftime(
                        '%Y/%m/%d | %H:%M:%S')
                    user_wallet = Wallet.objects.get(user=server.user)
                    price_per_day = server.server.price_daily
                    if user_wallet.amount < price_per_day:
                        datacenter = get_datacenter(server)
                        if datacenter is None:
                            print(f"datacenter not found ! --- {server.user.phone}--- {server.ipv4} --- {server.slug} --- {fa_time}")
                        response = datacenter.server_delete(server)
                        if response["status"] is True:
                            server.is_active = False
                            server.save()
                            print(f"[*] --- {server.user.phone} --- {server.ipv4} --- {fa_time} --- Deleted !")
                        else:
                            print(f"error in delete server --- {server.user.phone}--- {server.ipv4} --- {server.slug} --- {fa_time}")
                            print(response["error"])
                    else:
                        user_wallet.amount -= price_per_day
                        user_wallet.save()
                        server.cost += price_per_day
                        server.expire += datetime.timedelta(days=1)
                        server.save()
                        ServerCost.objects.create(
                            user=server.user,
                            server=server,
                            cost_amount=price_per_day,
                            credit_amount=user_wallet.amount,
                        )
                        print(f"[+] --- {server.user.phone} --- {server.ipv4} --- {price_per_day} --- {fa_time}")
        except Exception as e:
            print(e)
        finally:
            time.sleep(1)


if __name__ == "__main__":
    check_servers()
