import jdatetime
from django.contrib import admin
from django.shortcuts import reverse
from django.utils.safestring import mark_safe

from config.settings import DOMAIN_URL
from .forms import BlogAdminFrom, CategoryAdminFrom
from .models import Category, Blog, ReviewRating


class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminFrom
    exclude = ('user', )
    search_fields = ("title", "slug")
    list_display = ("title", "get_slug", "get_updated", "get_created", "is_active")

    def get_slug(self, obj):
        try:
            blog_url = reverse("blog:detail-blog", args=[obj.slug])
            return mark_safe(f'<a href="{DOMAIN_URL}{blog_url}" target="_blank">{obj.slug}</a>')
        except Exception:
            return "None"

    def get_updated(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.updated).strftime('%Y/%m/%d | %H:%M:%S')

    def get_created(self, obj):
        return jdatetime.datetime.fromgregorian(datetime=obj.created).strftime('%Y/%m/%d | %H:%M:%S')

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)
        ReviewRating.objects.create(user=request.user, blog=obj)


class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminFrom
    exclude = ('user', )

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        if form.cleaned_data['reply_id'] == '':
            obj.reply_id = None
        super().save_model(request, obj, form, change)


admin.site.register(Blog, BlogAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ReviewRating)
