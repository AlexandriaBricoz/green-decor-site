from django import forms

from .models import ContactRequest


_FIELD_CLASS = (
    "w-full bg-surface-container-high border-none rounded-md px-6 py-4 "
    "focus:ring-2 focus:ring-primary/40 text-on-surface placeholder:text-stone-400"
)


class ContactForm(forms.ModelForm):
    # Honeypot: скрытое поле, реальные пользователи оставляют пустым.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
                "style": "position:absolute;left:-10000px;height:0;width:0;opacity:0;",
            }
        ),
        label="",
    )
    consent_given = forms.BooleanField(
        required=True,
        label="Я ознакомился и согласен со следующими документами:",
        error_messages={
            "required": (
                "Для отправки заявки необходимо ознакомиться и согласиться "
                "с Политикой конфиденциальности и Согласием на обработку персональных данных."
            )
        },
    )
    marketing_consent = forms.BooleanField(
        required=False,
        label="Я хочу получать от вас информационную рассылку со специальными предложениями",
    )

    class Meta:
        model = ContactRequest
        fields = ("name", "contact", "company", "consent_given", "marketing_consent")
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Иван Иванов", "class": _FIELD_CLASS, "autocomplete": "name"}
            ),
            "contact": forms.TextInput(
                attrs={
                    "placeholder": "+7 (900) 123-45-67",
                    "class": _FIELD_CLASS,
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "type": "tel",
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "placeholder": "ООО «Пример» / ИНН",
                    "class": _FIELD_CLASS,
                    "autocomplete": "organization",
                }
            ),
        }
        labels = {
            "contact": "Телефон",
            "company": "Компания / ИНН",
        }

    def is_spam(self) -> bool:
        return bool(self.data.get("website", "").strip())
