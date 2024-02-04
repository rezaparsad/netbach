import re

import jdatetime
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

from .forms import PackTicketForm, TicketForm, InlineTicketForm
from .models import Ticket, PackTicket
from .models import User, Login


class ProxyGroup(Group):
    class Meta:
        proxy = True
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'


class UserAdmin(admin.ModelAdmin):
    list_display = ('phone', "get_last_login", "get_date_joined", 'is_active')
    search_fields = ('phone', 'first_name', 'last_name', 'email')
    list_per_page = 30

    def get_last_login(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.last_login).strftime('%Y/%m/%d | %H:%M:%S')

    def get_date_joined(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.date_joined).strftime('%Y/%m/%d | %H:%M:%S')

    def save_model(self, request, obj, form, change) -> None:
        if not obj.password[:14] == 'pbkdf2_sha256$':
            obj.password = make_password(obj.password)
        return super().save_model(request, obj, form, change)


class LoginAdmin(admin.ModelAdmin):
    search_fields = ("user__phone", "ip")
    list_display = ("user", "ip", "get_os", "get_date")

    def get_os(self, obj):
        data = ""
        results = re.findall("([L|l]inux|[W|w]indows|[M|m]ac)|([C|c]hrome|[F|f]irefox|[E|e]dge|[T|t]rident)", obj.data)
        for result in results:
            for i in result:
                if i != "":
                    data += str(i).capitalize() + " , "
        return data[:-2]

    def get_date(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.created).strftime('%Y/%m/%d | %H:%M:%S')


class TicketInline(admin.TabularInline):
    form = InlineTicketForm
    model = Ticket
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if request.user:
                kwargs['initial'] = request.user.pk
        return super(TicketInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class PackTicketAdmin(admin.ModelAdmin):
    form = PackTicketForm
    search_fields = ("user__phone", "category", "title")
    list_display = ("user", "category", "title", "status")
    inlines = [TicketInline]
    ordering = ("-updated", )

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            if formset.model == Ticket and formset.has_changed():
                obj = form.instance
                obj.status = "answer_given"
                obj.save()
                break
        super().save_related(request, form, formsets, change)


class TicketAdmin(admin.ModelAdmin):
    form = TicketForm
    list_display = ("user", "pack", "content")
    ordering = ("-updated", )


admin.site.unregister(Group)
admin.site.register(ProxyGroup)
admin.site.register(User, UserAdmin)
admin.site.register(Login, LoginAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(PackTicket, PackTicketAdmin)
