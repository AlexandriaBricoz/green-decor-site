from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("consent/", views.consent, name="consent"),
    path("price-list.xlsx", views.price_list_xlsx, name="price_xlsx"),
    path("admin/price-list.xlsx", views.price_list_xlsx_legacy),
    path("admin/", views.inventory_list, name="inventory"),
    path("admin/plants/new/", views.plant_create, name="plant_create"),
    path("admin/plants/<int:pk>/edit/", views.plant_edit, name="plant_edit"),
    path("admin/plants/<int:pk>/toggle/", views.plant_toggle_visibility, name="plant_toggle"),
    path("admin/plants/<int:pk>/delete/", views.plant_delete, name="plant_delete"),
    path("admin/settings/", views.site_settings_edit, name="settings"),
    path("admin/inbox/", views.inbox_list, name="inbox"),
    path("admin/inbox/export.xlsx", views.inbox_export_xlsx, name="inbox_xlsx"),
    path("admin/inbox/<int:pk>/", views.inbox_detail, name="inbox_detail"),
    path("admin/inbox/<int:pk>/toggle/", views.inbox_toggle, name="inbox_toggle"),
    path("admin/inbox/<int:pk>/delete/", views.inbox_delete, name="inbox_delete"),
]
