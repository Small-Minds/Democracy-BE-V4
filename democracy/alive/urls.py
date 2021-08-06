from django.urls import path

from democracy.alive.views import alive_view

app_name = "alive"
urlpatterns = [path("alive/", view=alive_view, name="alive")]
