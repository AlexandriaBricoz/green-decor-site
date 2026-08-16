from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import Plant, SiteSettings


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "age_years", "size_cm", "quantity", "price", "external_url", "is_public")
    list_editable = ("is_public",)
    search_fields = ("name", "sku")
    list_filter = ("is_public", "age_years")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Адрес и карта", {
            "fields": ("address", "map_embed_url"),
            "description": (
                "Адрес отображается в блоке «Как нас найти» и в футере. "
                "Для карты вставьте URL из embed-кода Яндекс.Карт (см. подсказку к полю)."
            ),
        }),
        ("Контакты", {
            "fields": ("phones", "email", "schedule"),
        }),
        ("Футер", {
            "fields": ("footer_about", "footer_address_title", "footer_address_note", "inn", "copyright_text"),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect(reverse("admin:catalog_sitesettings_change", args=[obj.pk]))
