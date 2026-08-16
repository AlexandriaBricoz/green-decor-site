from .models import SiteSettings


def site_settings(request):
    ctx = {"site_settings": SiteSettings.load()}
    if getattr(request, "user", None) and request.user.is_authenticated:
        try:
            from contacts.models import ContactRequest
            ctx["inbox_new_count"] = ContactRequest.objects.filter(processed=False).count()
        except Exception:
            ctx["inbox_new_count"] = 0
    return ctx
