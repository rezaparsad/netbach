from django.contrib import admin

from .forms import PageAdminFrom
from .models import Media, Page, FAQ


class PageAdmin(admin.ModelAdmin):
    form = PageAdminFrom
    exclude = ('user', )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


class FAQAdmin(admin.ModelAdmin):
    exclude = ("user", )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Media)
admin.site.register(Page, PageAdmin)
admin.site.register(FAQ, FAQAdmin)
