import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import escape

from .models import ContactRequest
from .telegram import is_configured, send_message

logger = logging.getLogger(__name__)


def _contact_link(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    digits = "".join(c for c in value if c.isdigit() or c == "+")
    if "@" in value and "." in value:
        return f'<a href="mailto:{escape(value)}">{escape(value)}</a>'
    if len(digits) >= 6:
        return f'<a href="tel:{escape(digits)}">{escape(value)}</a>'
    return escape(value)


def _format_request(r: ContactRequest) -> str:
    lines = [
        "<b>🌱 Новая заявка</b>",
        "",
        f"<b>Имя:</b> {escape(r.name)}",
        f"<b>Контакт:</b> {_contact_link(r.contact)}",
    ]
    if r.company:
        lines.append(f"<b>Компания:</b> {escape(r.company)}")
    lines.append(f"<b>Тема:</b> {escape(r.get_subject_display())}")
    if r.message:
        msg = r.message.strip()
        if len(msg) > 1500:
            msg = msg[:1500] + "…"
        lines += ["", f"<b>Сообщение:</b>", escape(msg)]
    lines += ["", f"<i>Создано: {r.created_at:%d.%m.%Y %H:%M}</i>"]
    return "\n".join(lines)


@receiver(post_save, sender=ContactRequest)
def notify_new_request(sender, instance: ContactRequest, created: bool, **kwargs):
    if not created:
        return
    if not is_configured():
        return
    try:
        from catalog.models import SiteSettings
        chat_id = SiteSettings.load().telegram_chat_id
    except Exception:
        logger.exception("не удалось прочитать SiteSettings.telegram_chat_id")
        return
    if not chat_id:
        return
    text = _format_request(instance)
    markup = {"inline_keyboard": [[
        {"text": "✅ Отметить как обработано", "callback_data": f"processed:{instance.pk}"}
    ]]}
    result = send_message(chat_id, text, reply_markup=markup)
    if not result.get("ok"):
        logger.warning("telegram sendMessage не удалось: %s", result)
