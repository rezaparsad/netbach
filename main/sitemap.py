from math import ceil

from django.contrib.sitemaps import Sitemap
from django.core.paginator import Paginator
from django.urls import reverse

from blog.models import Blog
from config.settings import PAGINATION_SITEMAP
from .models import Page
from cloud.models import Category


class PageListSitemap(Sitemap):
    limit = PAGINATION_SITEMAP
    protocol = 'https'

    def __init__(self, page, items) -> None:
        self.page = page
        self.item = items
    
    def items(self):
        return self.item
    
    def location(self, obj) -> str:
        if obj.slug == 'home':
            return reverse('main:home')
        return reverse('main:page', args=[str(obj.slug)])
    
    def lastmod(self, obj):
        return obj.updated

    def get_urls(self, page=1, site=None, protocol=None):
        protocol = self.get_protocol(self.protocol)
        domain = self.get_domain(site)
        return self._urls(self.page, protocol, domain)


class IndexListSitemap(Sitemap):
    limit = PAGINATION_SITEMAP
    protocol = 'https'

    def items(self):
        item = []
        page_list = Page.objects.filter(is_active=True)
        count_page = ceil(page_list.count()/PAGINATION_SITEMAP)
        for i in range(1, count_page+1):
            page_obj = Paginator(page_list, PAGINATION_SITEMAP).page(i)
            item.append({'url': f'/sitemap-page{i}.xml', 'updated': page_obj[-1].updated})

        post_list = Blog.objects.filter(is_active=True)
        count_post = ceil(post_list.count()/PAGINATION_SITEMAP)
        for i in range(1, count_post+1):
            page_obj = Paginator(post_list, PAGINATION_SITEMAP).page(i)
            item.append({'url': f'/sitemap-blog{i}.xml', 'updated': page_obj[-1].updated})
        
        post_list = Category.objects.filter(is_active=True)
        count_post = ceil(post_list.count()/PAGINATION_SITEMAP)
        for i in range(1, count_post+1):
            page_obj = Paginator(post_list, PAGINATION_SITEMAP).page(i)
            item.append({'url': f'/sitemap-blog{i}.xml', 'updated': page_obj[-1].updated})
        
        return item

    def location(self, item):
        return item['url']

    def lastmod(self, obj):
        return obj['updated']
    

def page_list_sitemap():
    sitemaps = {}
    page_list = Page.objects.filter(is_active=True)
    for i in range(1, ceil(page_list.count()/PAGINATION_SITEMAP)+1):
        sitemaps[str(i)] = PageListSitemap(i, page_list)
    return sitemaps
