"""Тонкая обёртка над Telegram Bot API. Без внешних клиентов, только requests."""
import io
import json
import logging
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)

_DEFAULT_API_BASE = "https://api.telegram.org"


def _api_base() -> str:
    base = (getattr(settings, "TELEGRAM_API_BASE", "") or _DEFAULT_API_BASE).rstrip("/")
    return base


def is_configured() -> bool:
    return bool(getattr(settings, "TELEGRAM_BOT_TOKEN", ""))


def _call(method: str, data: Optional[dict] = None, files: Optional[dict] = None, timeout: int = 15) -> dict:
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token:
        return {"ok": False, "description": "TELEGRAM_BOT_TOKEN не задан"}
    try:
        import requests
    except ImportError:
        logger.error("модуль requests не установлен")
        return {"ok": False, "description": "requests missing"}
    url = f"{_api_base()}/bot{token}/{method}"
    try:
        resp = requests.post(url, data=data, files=files, timeout=timeout)
        return resp.json()
    except Exception as exc:
        logger.exception("telegram API error (%s): %s", method, exc)
        return {"ok": False, "description": str(exc)}


def send_message(chat_id, text: str, reply_markup: Optional[dict] = None, parse_mode: str = "HTML") -> dict:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": "true",
    }
    if reply_markup is not None:
        payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    return _call("sendMessage", data=payload)


def send_document(chat_id, filename: str, data: bytes, caption: str = "") -> dict:
    files = {"document": (filename, io.BytesIO(data))}
    payload = {"chat_id": chat_id}
    if caption:
        payload["caption"] = caption
    return _call("sendDocument", data=payload, files=files)


def answer_callback_query(callback_query_id: str, text: str = "", show_alert: bool = False) -> dict:
    return _call("answerCallbackQuery", data={
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": "true" if show_alert else "false",
    })


def edit_message_reply_markup(chat_id, message_id, reply_markup: Optional[dict] = None) -> dict:
    return _call("editMessageReplyMarkup", data={
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": json.dumps(reply_markup or {"inline_keyboard": []}, ensure_ascii=False),
    })


def set_webhook(url: str, secret_token: str) -> dict:
    return _call("setWebhook", data={
        "url": url,
        "secret_token": secret_token,
        "allowed_updates": json.dumps(["message", "callback_query"]),
    })


def delete_webhook() -> dict:
    return _call("deleteWebhook")


def get_me() -> dict:
    return _call("getMe")
