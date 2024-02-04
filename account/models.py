from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.settings import redis
from main.media_model import Media


class User(AbstractUser):
    image = models.ImageField(blank=True)
    email = models.EmailField(_('email address'), blank=True, null=True)
    phone = models.CharField(unique=True, max_length=20)
    id_card = models.CharField(max_length=20, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=40, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self) -> str:
        return self.phone or self.email or self.username

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)


class Login(models.Model):
    user = models.ForeignKey(User, models.PROTECT)
    ip = models.CharField(max_length=40)
    data = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.phone


class PackTicket(models.Model):
    CHOICES_CATEGORY = (
        ('server_cloud', 'سرور کلودی'),
    )
    CHOICES_STATUS = (
        ('answer_given', 'پاسخ داده شده'),
        ('waiting_answer', 'در انتظار پاسخ'),
        ('closed', 'بسته شده'),
    )

    user = models.ForeignKey(User, models.PROTECT)
    category = models.CharField(max_length=30, choices=CHOICES_CATEGORY)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=48, choices=CHOICES_STATUS)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + "---" + self.title


class Ticket(models.Model):
    user = models.ForeignKey(User, models.PROTECT)
    pack = models.ForeignKey(PackTicket, models.CASCADE)
    content = models.CharField(max_length=1024)
    image = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + "---" + str(self.pack)

    def save(self, *args, **kwargs):
        is_exists = False
        if not self.pk and not self.user.is_staff:
            is_exists = True
        super(Ticket, self).save(*args, **kwargs)
        if is_exists:
            redis.sadd("TicketList", self.pk)
