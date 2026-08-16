from django.urls import path

from . import views

app_name = "contacts"

urlpatterns = [
    path("submit/", views.submit_contact, name="submit"),
]
