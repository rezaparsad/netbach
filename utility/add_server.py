import os
import sys

import django

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from account.models import User
from cloud.models import Server, DataCenter, OperationSystem, Location


datacenter_name = "Linode"
maxnovin = User.objects.get(username="maxnovin")
datacenter = DataCenter.objects.get(name=datacenter_name)
operation_systems = ['AlmaLinux 8', 'AlmaLinux 9', 'Alpine 3.15', 'Alpine 3.16', 'Alpine 3.17', 'Alpine 3.18', 'Arch Linux', 'CentOS 7', 'CentOS Stream 8', 'CentOS Stream 9', 'Debian 10', 'Debian 11', 'Debian 12', 'Fedora 36', 'Fedora 37', 'Fedora 38', 'Gentoo', 'Kali Linux', 'openSUSE Leap 15.4', 'openSUSE Leap 15.5', 'Rocky Linux 8', 'Rocky Linux 9', 'Slackware 15.0', 'Slackware 14.1', 'Ubuntu 20.04 LTS', 'Ubuntu 22.04 LTS', 'Ubuntu 22.10', 'Ubuntu 23.04', 'Ubuntu 23.10']
os = OperationSystem.objects.filter(name__in=operation_systems)
cities = ['Mumbai', 'Toronto', 'Sydney', 'Washington', 'Chicago', 'Paris', 'Seattle', 'Sao Paulo', 'Amsterdam', 'Stockholm', 'Chennai', 'Osaka', 'Milan', 'Miami', 'Jakarta', 'Los Angeles', 'Dallas', 'Fremont', 'Atlanta', 'Newark', 'London', 'Singapore', 'Frankfurt']
location = Location.objects.filter(city__in=cities)
slug = input("Enter slug: ")
name = input("Enter name: ")
ram = int(input("Enter ram: ")) * 1000
cpu = input("Enter cpu: ")
disk = int(input("Enter disk: ")) * 1000
type_cpu = "intel"
type_disk = "ssd"
traffic = int(input("Enter traffic: ")) * 1000000
port = "1000"
price_usd = 55000
amount_usd = float(input("Enter amount usd: "))
profit = 20000
server = Server.objects.create(
    user=maxnovin,
    datacenter=datacenter,
    slug=slug,
    name=name,
    ram=ram,
    cpu=cpu,
    disk=disk,
    type_cpu=type_cpu,
    type_disk=type_disk,
    traffic=traffic,
    port=port,
    price_usd=price_usd,
    amount_usd=amount_usd,
    profit=profit
)
server.os.add(*os)
server.location.add(*location)
print("created !")

