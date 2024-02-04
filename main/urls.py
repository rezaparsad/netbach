from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic.base import TemplateView

from blog.sitemap import blog_list_sitemap
from .sitemap import page_list_sitemap, IndexListSitemap
from .views import home, page
from .views import link_shortener

app_name = 'main'

urlpatterns = [
    path('robots.txt', TemplateView.as_view(template_name='files/main-robots.txt', content_type='text/plain'), name='main-robots'),
    path('l/<int:counter>', link_shortener, name='link-shortener'),
    path('<slug:slug>/', page, name='page'),
    path('', home, name='home'),

    # Sitemaps
    path('sitemap.xml', sitemap, {'sitemaps': {'list': IndexListSitemap}, 'template_name': 'sitemap/sitemap.xml'}),
    path('sitemap-page<section>.xml', sitemap, {'sitemaps': page_list_sitemap()}, name='sitemap-page'),
    path('sitemap-blog<section>.xml', sitemap, {'sitemaps': blog_list_sitemap()}, name='sitemap-blog'),
]