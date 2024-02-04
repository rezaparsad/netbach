import jdatetime
from django import forms
from django.contrib import admin
from django.contrib.humanize.templatetags import humanize

from .forms import CategoryAdminFrom
from .models import Server, ServerRent, Location, OperationSystem, DataCenter, ActivityServer, Token, Category


class ServerAdmin(admin.ModelAdmin):
    list_display = ("name", "datacenter", "get_price", "is_active")
    ordering = ("-is_active", )

    def get_price(self, obj):
        return humanize.intcomma(obj.price)


class ServerRentAdmin(admin.ModelAdmin):
    search_fields = ("user__phone", "ipv4", "ipv6", "location__city", "location__country")
    list_filter = ("is_active", "datacenter", "token__name")
    list_display = ("user", "datacenter", "server", "ipv4", "location", "get_cost", "is_active", "get_created")
    ordering = ("-is_active", )

    def get_cost(self, obj):
        return humanize.intcomma(obj.cost)

    def get_created(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.created).strftime('%Y/%m/%d | %H:%M:%S')


class ActivityServerRent(admin.ModelAdmin):
    search_fields = ("user__phone", "server__ipv4", "server__ipv6", "activity")
    list_display = ("user", "server", "activity", "get_created")

    def get_created(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.created).strftime('%Y/%m/%d | %H:%M:%S')


class TokenAdmin(admin.ModelAdmin):
    exclude = ("user", )

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["name"].widget = forms.TextInput(attrs={"style": "width: 80%"})
        form.base_fields["key"].widget = forms.TextInput(attrs={"style": "width: 80%"})
        return form

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


class CategoryAdmin(admin.ModelAdmin):
    exclude = ('user', )
    form = CategoryAdminFrom

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Server, ServerAdmin)
admin.site.register(ServerRent, ServerRentAdmin)
admin.site.register(Location)
admin.site.register(OperationSystem)
admin.site.register(DataCenter)
admin.site.register(ActivityServer, ActivityServerRent)
admin.site.register(Token, TokenAdmin)
admin.site.register(Category, CategoryAdmin)
