from django.contrib.humanize.templatetags import humanize
from django.db import models

from account.models import User
from cloud.models import ServerRent


class ServerCost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    server = models.ForeignKey(ServerRent, on_delete=models.CASCADE)
    cost_amount = models.IntegerField()
    credit_amount = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            self.user.phone + " --- " + self.server.ipv4 + " --- " +
            humanize.intcomma(str(self.cost_amount)) + " --- " + humanize.intcomma(str(self.credit_amount))
        )


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.phone + " --- " + str(self.amount)


class ZarinPal(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.CharField(max_length=24)
    description = models.CharField(max_length=1024)
    status_code = models.IntegerField(default=0)
    authority = models.CharField(max_length=50, default='start')
    is_success = models.BooleanField(default=False)
    ref_id = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
