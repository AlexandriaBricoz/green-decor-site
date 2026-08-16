from django.contrib import admin

from .models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "contact", "volume", "processed", "created_at")
    list_filter = ("subject", "processed", "created_at")
    search_fields = ("name", "contact", "company", "message")
    readonly_fields = ("created_at", "consent_at", "source_ip", "user_agent")
