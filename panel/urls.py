"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from config.settings import DEBUG

from .views import (
    home, increase_credit, callback_zarinpal, transactions, ticket_list, ticket_detail,
    ticket_create, invoices
)

app_name = "panel"

urlpatterns = [
    path('robots.txt', TemplateView.as_view(template_name='files/panel-robots.txt', content_type='text/plain'), name='panel-robots'),
    path('increase-credit/', increase_credit, name="increase-credit"),
    path('ticket/list/', ticket_list, name='ticket-list'),
    path('ticket/edit/<int:pk>/', ticket_detail, name='ticket-detail'),
    path('ticket/add/', ticket_create, name='ticket-create'),
    path('transactions/', transactions, name="transactions"),
    path('invoices/', invoices, name="invoices"),
    path('callback/zarinpal/<int:pk>/', callback_zarinpal, name='callback_zarinpal'),
    path('robots.txt', TemplateView.as_view(template_name='files/panel-robots.txt', content_type='text/plain'),
         name='panel-robots'),
    path('', home, name="home"),
    path('cloud/', include('cloud.urls')),
    path('api/', include('api.urls')),
    path('accounts/', include('account.urls'))
]

if DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)