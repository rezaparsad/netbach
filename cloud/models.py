from django.db import models

from account.models import User
from config.settings import hetzner, linode
from main.media_model import Media


class Location(models.Model):
    user = models.ForeignKey(User, models.PROTECT)
    country = models.CharField(max_length=40)
    city = models.CharField(max_length=40, unique=True)
    image = models.ForeignKey(Media, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.country + ' : ' + self.city


class OperationSystem(models.Model):
    user = models.ForeignKey(User, models.PROTECT)
    name = models.CharField(max_length=40)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Token(models.Model):
    user = models.ForeignKey(User, models.PROTECT)
    name = models.CharField(max_length=128)
    key = models.CharField(max_length=512)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DataCenter(models.Model):
    user = models.ForeignKey(User, models.PROTECT)
    image = models.ForeignKey(Media, on_delete=models.CASCADE)
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    site = models.CharField(max_length=100)
    content = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    reply = None

    user = models.ForeignKey(User, models.PROTECT, related_name='cloud_server_category_user')
    reply_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=150)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    view = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # seo
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=150, null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    image_meta = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='cloud_server_category_imagemeta', null=True, blank=True)

class Server(models.Model):
    CHOICES_TYPE_DISK = (
        ('ssd', 'SSD'),
        ('nvme', 'NVME'),
        ('hdd', 'HDD')
    )

    CHOICES_TYPE_CPU = (
        ('intel', 'Intel'),
        ('amd', 'AMD'),
        ('arm64', 'Arm64')
    )

    user = models.ForeignKey(User, models.CASCADE)
    category = models.ManyToManyField(Category, blank=True)
    datacenter = models.ForeignKey(DataCenter, on_delete=models.CASCADE)
    os = models.ManyToManyField(OperationSystem)
    location = models.ManyToManyField(Location)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=200)
    ram = models.CharField(max_length=24)
    cpu = models.CharField(max_length=24)
    disk = models.CharField(max_length=24)
    type_cpu = models.CharField(max_length=15, choices=CHOICES_TYPE_CPU)
    type_disk = models.CharField(max_length=15, choices=CHOICES_TYPE_DISK)
    traffic = models.CharField(max_length=24)
    port = models.CharField(max_length=24)
    price = models.IntegerField(default=0)
    price_discount = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug


class ServerRent(models.Model):
    user = models.ForeignKey(User, models.PROTECT)
    server = models.ForeignKey(Server, models.CASCADE)
    datacenter = models.ForeignKey(DataCenter, models.CASCADE)
    os = models.ForeignKey(OperationSystem, models.CASCADE)
    location = models.ForeignKey(Location, models.CASCADE)
    token = models.ForeignKey(Token, models.CASCADE)
    slug = models.SlugField()
    cost = models.IntegerField(default=0)
    name = models.CharField(max_length=50)
    ipv4 = models.CharField(max_length=20)
    ipv6 = models.CharField(max_length=40)
    username = models.CharField(max_length=48)
    password = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)
    expire = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ipv4

    def get_datacenter(self):
        if self.datacenter.name.lower() == "hetzner":
            return hetzner
        elif self.datacenter.name.lower() == "linode":
            return linode
        return None


class ActivityServer(models.Model):
    ACTIVITY_CHOICES = (
        ('created', 'ایجاد سرور'),
        ('reboot', 'ریبوت سرور'),
        ('off', 'خاموش کردن سرور'),
        ('on', 'روشن کردن سرور'),
        ('change-passwd', 'تغییر پسورد'),
        ('delete', 'حذف سرور'),
        ('change-ip', 'تعویض آیپی'),
    )

    user = models.ForeignKey(User, models.PROTECT)
    server = models.ForeignKey(ServerRent, models.CASCADE)
    activity = models.CharField(max_length=30, choices=ACTIVITY_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
