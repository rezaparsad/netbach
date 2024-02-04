import jdatetime
from django.contrib import admin
from django.contrib.humanize.templatetags import humanize

from .models import ZarinPal, Wallet, ServerCost


class ZaripalAdmin(admin.ModelAdmin):
    search_fields = ("user__phone", )
    list_display = ("user", "get_amount", "get_created", "is_success")

    def get_amount(self, obj):
        return humanize.intcomma(obj.amount)

    def get_created(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.created).strftime('%Y/%m/%d | %H:%M:%S')


class WalletAdmin(admin.ModelAdmin):
    search_fields = ("user__phone", )
    list_display = ("user", "get_credit")

    def get_credit(self, obj):
        return humanize.intcomma(obj.amount)


class ServerCostAdmin(admin.ModelAdmin):
    search_fields = ("user__phone", "server__ipv4", "server__ipv6")
    list_display = ("user", "get_server", "get_cost", "get_amount", "get_created")

    def get_server(self, obj):
        return obj.server.ipv4

    def get_cost(self, obj):
        return humanize.intcomma(obj.cost_amount)

    def get_amount(self, obj):
        return humanize.intcomma(obj.credit_amount)

    def get_created(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.created).strftime('%Y/%m/%d | %H:%M:%S')


admin.site.register(Wallet, WalletAdmin)
admin.site.register(ServerCost, ServerCostAdmin)
admin.site.register(ZarinPal, ZaripalAdmin)

