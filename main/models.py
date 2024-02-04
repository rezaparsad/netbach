from django.db import models
from account.models import User
from .media_model import Media



class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    media = models.ForeignKey(Media, on_delete=models.PROTECT, related_name="main_page_media", null=True, blank=True)
    name = models.CharField(max_length=150)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # seo
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=150, null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    image_meta = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class FAQ(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    page = models.ForeignKey(Page, models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question


