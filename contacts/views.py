from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import ContactForm


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def submit_contact(request):
    if request.method != "POST":
        return redirect("catalog:home")

    form = ContactForm(request.POST)

    if form.is_spam():
        # Тихо принимаем заявку от бота, ничего не сохраняем.
        messages.success(
            request,
            "Заявка отправлена. Мы свяжемся с вами в ближайшее время.",
        )
        return redirect("catalog:home")

    if form.is_valid():
        req = form.save(commit=False)
        req.consent_given = True
        req.consent_at = timezone.now()
        req.source_ip = _client_ip(request)
        req.user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
        req.save()
        messages.success(
            request,
            "Заявка отправлена. Мы свяжемся с вами в ближайшее время.",
        )
        return redirect("catalog:home")

    messages.error(request, "Проверьте правильность заполнения формы.")
    return render(
        request,
        "catalog/home.html",
        {"contact_form": form, "scroll_to": "contact"},
    )
