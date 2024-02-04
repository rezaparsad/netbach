from math import ceil

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from config.settings import PAGINATION_SITEMAP
from .models import Blog


class BlogListSitemap(Sitemap):
    limit = PAGINATION_SITEMAP
    protocol = 'https'

    def __init__(self, page, items) -> None:
        self.page = page
        self.item = items
    
    def items(self):
        return self.item
    
    def location(self, obj) -> str:
        return reverse('blog:detail-blog', args=[str(obj.slug)])
    
    def lastmod(self, obj):
        return obj.updated

    def get_urls(self, page=1, site=None, protocol=None):
        protocol = self.get_protocol(self.protocol)
        domain = self.get_domain(site)
        return self._urls(self.page, protocol, domain)
    

def blog_list_sitemap():
    sitemaps = {}
    post_list = Blog.objects.filter(is_active=True)
    for i in range(1, ceil(post_list.count()/PAGINATION_SITEMAP)+1):
        sitemaps[str(i)] = BlogListSitemap(i, post_list)
    return sitemaps
