from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse

from contacts.telegram import delete_webhook, get_me, is_configured, set_webhook


class Command(BaseCommand):
    help = "Регистрирует webhook в Telegram Bot API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            default=None,
            help="Публичный HTTPS-URL сайта (например https://greendecor056.ru). "
                 "По умолчанию берётся из settings.TELEGRAM_BASE_URL.",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Удалить webhook и выйти.",
        )

    def handle(self, *args, **opts):
        if not is_configured():
            self.stderr.write("TELEGRAM_BOT_TOKEN не задан")
            return
        if opts["delete"]:
            self.stdout.write(str(delete_webhook()))
            return
        secret = getattr(settings, "TELEGRAM_WEBHOOK_SECRET", "")
        if not secret:
            self.stderr.write("TELEGRAM_WEBHOOK_SECRET не задан")
            return
        base_url = opts["base_url"] or getattr(settings, "TELEGRAM_BASE_URL", "")
        proxy = getattr(settings, "TELEGRAM_API_BASE", "").rstrip("/")
        if proxy:
            # Cloudflare Worker принимает /incoming/<secret>/ и проксирует
            # на TELEGRAM_BASE_URL + /contacts/telegram/webhook/<secret>/.
            url = f"{proxy}/incoming/{secret}/"
            self.stdout.write("Используем прокси для входящих webhook: " + proxy)
        else:
            if not base_url:
                self.stderr.write("Не задан --base-url и settings.TELEGRAM_BASE_URL")
                return
            path = reverse("contacts:telegram_webhook", args=[secret])
            url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        self.stdout.write(f"Регистрируем webhook: {url}")
        me = get_me()
        if me.get("ok"):
            self.stdout.write(f"Бот: @{me['result'].get('username')} ({me['result'].get('first_name')})")
        result = set_webhook(url, secret)
        self.stdout.write(str(result))
