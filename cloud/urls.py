from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import server_list, home, server_detail, server_create, server_activity, server_info

app_name = "cloud"

urlpatterns = [
    path('server/list/', server_list, name="server-list"),
    path('server/create/', server_create, name="server-create"),
    path('server/detail/<slug:slug>/', server_detail, name="server-detail"),
    path('server/detail/<slug:slug>/info', server_info, name="server-info"),
    path('server/activity/<slug:slug>/', server_activity, name="server-activity"),
    path('', home, name="home")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
