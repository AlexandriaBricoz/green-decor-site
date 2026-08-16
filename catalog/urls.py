from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("price-list.xlsx", views.price_list_xlsx, name="price_xlsx"),
    path("admin/price-list.xlsx", views.price_list_xlsx_legacy),
    path("admin/", views.inventory_list, name="inventory"),
    path("admin/plants/new/", views.plant_create, name="plant_create"),
    path("admin/plants/<int:pk>/edit/", views.plant_edit, name="plant_edit"),
    path("admin/plants/<int:pk>/toggle/", views.plant_toggle_visibility, name="plant_toggle"),
    path("admin/plants/<int:pk>/delete/", views.plant_delete, name="plant_delete"),
    path("admin/settings/", views.site_settings_edit, name="settings"),
]
