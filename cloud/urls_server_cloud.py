from django.urls import path
from .views import category, category_main


app_name = "cloud"

urlpatterns = [
    path('<slug:slug>/', category, name='server-list'),
    path('', category_main, name='home')
]
