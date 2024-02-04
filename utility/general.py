import os
import sys

import django

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from cloud.models import ServerRent, Token


servers = ServerRent.objects.filter(is_active=False)
for server in servers:
    server.token = Token.objects.get(name__iexact="mohsen", datacenter=server.datacenter)
    server.save()

print("done")
