import re

from django import forms

from .models import Plant, SiteSettings


_INPUT_CLASS = (
    "w-full bg-surface-container-low border-none rounded-lg p-4 "
    "focus:ring-2 focus:ring-primary/40 transition-all "
    "placeholder:text-stone-400"
)


class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = (
            "name",
            "sku",
            "age_years",
            "size_cm",
            "quantity",
            "price",
            "photo",
            "external_url",
            "description",
            "is_public",
        )
        widgets = {
            "name": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "Напр. Ель колючая Глаука"}
            ),
            "sku": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "SKO-PIC-001"}
            ),
            "age_years": forms.NumberInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "5", "min": 0}
            ),
            "size_cm": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "120-150"}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "100", "min": 0}
            ),
            "price": forms.NumberInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "4500", "step": "0.01"}
            ),
            "external_url": forms.URLInput(
                attrs={
                    "class": _INPUT_CLASS,
                    "placeholder": "https://youtu.be/... или https://drive.google.com/...",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": _INPUT_CLASS,
                    "rows": 3,
                    "placeholder": "Дополнительные характеристики растения",
                }
            ),
            "is_public": forms.CheckboxInput(
                attrs={
                    "class": "h-5 w-5 rounded text-primary focus:ring-primary/40 border-stone-300",
                }
            ),
        }


_IFRAME_SRC_RE = re.compile(r'''<iframe[^>]*\ssrc\s*=\s*["']([^"']+)["']''', re.IGNORECASE)
_EMBEDDABLE_HOSTS = (
    "yandex.ru/map-widget",
    "yandex.com/map-widget",
    "google.com/maps/embed",
    "www.google.com/maps/embed",
    "2gis.ru/widget",
    "static-maps.yandex.ru",
)


def _map_field(model_field_name):
    field = SiteSettings._meta.get_field(model_field_name)
    return forms.CharField(
        label=field.verbose_name,
        required=False,
        widget=forms.Textarea(attrs={
            "class": (
                "w-full bg-surface-container-low border-none rounded-lg p-4 "
                "focus:ring-2 focus:ring-primary/40 transition-all placeholder:text-stone-400 font-mono text-xs"
            ),
            "rows": 5,
            "placeholder": '<div ...><iframe src="https://yandex.ru/map-widget/v1/?..." ...></iframe></div>',
        }),
        help_text=field.help_text,
    )


def _clean_map_embed(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""

    if "<iframe" in raw.lower():
        m = _IFRAME_SRC_RE.search(raw)
        if not m:
            raise forms.ValidationError(
                "Не удалось найти src=\"…\" внутри вставленного кода <iframe>."
            )
        src = m.group(1).strip()
        if not any(host in src for host in _EMBEDDABLE_HOSTS):
            raise forms.ValidationError(
                "Внутри iframe должна быть ссылка на встраиваемый виджет "
                "(например, https://yandex.ru/map-widget/v1/…). Обычные страницы карт "
                "Яндекс запрещает загружать в iframe."
            )
        return raw

    if raw.startswith(("http://", "https://")):
        if not any(host in raw for host in _EMBEDDABLE_HOSTS):
            raise forms.ValidationError(
                "Это ссылка на страницу карт, а не на встраиваемый виджет — Яндекс блокирует такие URL "
                "в iframe. Откройте yandex.ru/maps → «Поделиться» → «Код карты» и скопируйте либо весь "
                "блок с <iframe>, либо URL из атрибута src=\"…\" (он начинается с https://yandex.ru/map-widget/v1/…)."
            )
        return raw

    raise forms.ValidationError(
        "Ожидается HTML-код (с <iframe>) или URL, начинающийся с https://"
    )


class SiteSettingsForm(forms.ModelForm):
    map_embed_url = _map_field("map_embed_url")
    map_embed_retail = _map_field("map_embed_retail")

    def clean_map_embed_url(self):
        return _clean_map_embed(self.cleaned_data.get("map_embed_url"))

    def clean_map_embed_retail(self):
        return _clean_map_embed(self.cleaned_data.get("map_embed_retail"))

    class Meta:
        model = SiteSettings
        fields = (
            "hero_kicker",
            "hero_title",
            "hero_title_accent",
            "address",
            "map_embed_url",
            "address_retail",
            "map_embed_retail",
            "phones",
            "email",
            "schedule",
            "footer_about",
            "footer_address_title",
            "footer_address_note",
            "legal_entity",
            "inn",
            "copyright_text",
        )
        widgets = {
            "hero_kicker": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "Питомник растений"}
            ),
            "hero_title": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "Хвойные растения"}
            ),
            "hero_title_accent": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "из нашего питомника."}
            ),
            "address": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "Оренбург, Загородное шоссе, 37/2"}
            ),
            "address_retail": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "Адрес розничной точки (можно оставить пустым)"}
            ),
            "phones": forms.Textarea(
                attrs={
                    "class": _INPUT_CLASS,
                    "rows": 4,
                    "placeholder": "+7 (912) 846-10-22\n+7 (912) 845-10-22",
                }
            ),
            "email": forms.EmailInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "info@example.ru"}
            ),
            "schedule": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "Работаем без выходных"}
            ),
            "footer_about": forms.Textarea(
                attrs={
                    "class": _INPUT_CLASS,
                    "rows": 3,
                    "placeholder": "Краткое описание питомника",
                }
            ),
            "footer_address_title": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "Штаб-квартира"}
            ),
            "footer_address_note": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "Главный кампус питомника"}
            ),
            "legal_entity": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "ИП Суслова / ООО «Ромашка»"}
            ),
            "inn": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "565100366000"}
            ),
            "copyright_text": forms.TextInput(
                attrs={"class": _INPUT_CLASS, "placeholder": "© 2024–2026 …"}
            ),
        }
