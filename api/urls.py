from django.urls import path
from django.views.generic.base import TemplateView
from rest_framework.routers import SimpleRouter

from .views import (
    check_phone, check_code, payment, ServerCloudDetail, ServerCloudList, ServerCloudRentViewSet,
    ServerCloudBuy, submit_blog_review
)

router = SimpleRouter()
router.register("server-rent/cloud/action", ServerCloudRentViewSet, basename="server-rent")

app_name = "api"

urlpatterns = [
    path('robots.txt', TemplateView.as_view(template_name='files/api-robots.txt', content_type='text/plain'),
         name='api-robots'),
    path('payment/', payment, name="payment"),
    path('server/cloud/detail/<slug:slug>/', ServerCloudDetail.as_view(), name='server-detail'),
    path('server/cloud/buy/<slug:slug>/', ServerCloudBuy.as_view(), name='server-buy'),
    path('server/cloud/list/', ServerCloudList.as_view(), name='server-list'),
    path('blog/review/<slug:slug>/', submit_blog_review, name='blog-review'),
]

urlpatterns += router.urls


