from django.urls import path

from .views import blog, list_of_blogs, category

app_name = 'blog'

urlpatterns = [
    path('<slug:slug>/', blog, name='detail-blog'),
    path('search/<slug:slug>/', category, name='category'),
    path('', list_of_blogs, name='list-of-blogs'),
]
