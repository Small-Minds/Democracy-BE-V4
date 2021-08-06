from django.urls import path

from democracy.reactauth.views import CustomTokenObtain, CustomTokenRefresh

app_name = "reactauth"
urlpatterns = [
    path("token/obtain/", CustomTokenObtain.as_view(), name="token_create"),
    path("token/refresh/", CustomTokenRefresh.as_view(), name="token_refresh"),
]
