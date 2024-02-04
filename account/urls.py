from django.urls import path

from api.views import check_phone, check_code
from .views import profile, login_history, user_login, user_logout


app_name = "account"

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('send-phone/', check_phone, name="send-code"),
    path('send-code/', check_code, name="check-code"),
    path('profile/', profile, name="profile"),
    path('login-history/', login_history, name="login-history"),
]


