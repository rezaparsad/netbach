from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Category
from config.settings import PAGINATION_SITEMAP
from math import ceil



class CloudServerListSitemap(Sitemap):
    limit = PAGINATION_SITEMAP
    protocol = 'https'

    def __init__(self, page, items) -> None:
        self.page = page
        self.item = items
    
    def items(self):
        return self.item
    
    def location(self, obj) -> str:
        if obj.slug == 'home':
            return reverse('cloud:home')
        return reverse('cloud:server-list', args=[str(obj.slug)])
    
    def lastmod(self, obj):
        return obj.updated

    def get_urls(self, page=1, site=None, protocol=None):
        protocol = self.get_protocol(self.protocol)
        domain = self.get_domain(site)
        return self._urls(self.page, protocol, domain)
    

def cloud_server_list_sitemap():
    sitemaps = {}
    post_list = Category.objects.filter(is_active=True)
    for i in range(1, ceil(post_list.count()/PAGINATION_SITEMAP)+1):
        sitemaps[str(i)] = CloudServerListSitemap(i, post_list)
    return sitemaps