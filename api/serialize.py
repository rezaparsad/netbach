from rest_framework import serializers

from account.utility import human_readable_size
from cloud.models import Server


class ServerCloudSerializer(serializers.ModelSerializer):

    operation_systems = serializers.SerializerMethodField('get_operation_systems')
    locations = serializers.SerializerMethodField('get_locations')
    datacenter = serializers.SerializerMethodField('get_datacenter')
    ram = serializers.SerializerMethodField('get_ram')
    cpu = serializers.SerializerMethodField('get_cpu')
    disk = serializers.SerializerMethodField('get_disk')
    traffic = serializers.SerializerMethodField('get_traffic')
    price = serializers.SerializerMethodField('get_price')
    price_day = serializers.SerializerMethodField('get_price_day')

    class Meta:
        model = Server
        fields = [
            'slug',
            'name',
            'ram',
            'cpu',
            'disk',
            'type_disk',
            'traffic',
            'port',
            'price',
            'price_day',
            'price_discount',
            'operation_systems',
            'locations',
            'datacenter',
        ]

    def get_operation_systems(self, obj):
        return [i.name for i in obj.os.all()]
    
    def get_locations(self, obj):
        return [{'city': i.city, 'image': i.image.file.url} for i in obj.location.all()]

    def get_datacenter(self, obj):
        return {
            'datacenter': obj.datacenter.name,
            'image': obj.datacenter.image.file.url
        }

    def get_ram(self, obj):
        return human_readable_size(obj.ram)

    def get_cpu(self, obj):
        return human_readable_size(obj.cpu, cpu=True)
    
    def get_disk(self, obj):
        return human_readable_size(obj.disk)
    
    def get_traffic(self, obj):
        return human_readable_size(obj.traffic)
    
    def get_price(self, obj):
        return human_readable_size(obj.price, price=True)
    
    def get_price_day(self, obj):
        return human_readable_size(int(obj.price/30), price=True)
