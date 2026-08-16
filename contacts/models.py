from django.db import models


class ContactRequest(models.Model):
    SUBJECT_WHOLESALE = "wholesale"
    SUBJECT_LOGISTICS = "logistics"
    SUBJECT_CATALOG = "catalog"
    SUBJECT_CHOICES = (
        (SUBJECT_WHOLESALE, "Оптовый запрос"),
        (SUBJECT_LOGISTICS, "Логистическая поддержка"),
        (SUBJECT_CATALOG, "Технический каталог"),
    )

    name = models.CharField("Имя", max_length=120)
    contact = models.CharField("Телефон", max_length=200)
    company = models.CharField("Компания", max_length=200, blank=True, default="")
    volume = models.CharField(
        "Планируемый объём заказа",
        max_length=200,
        blank=True,
        default="",
        help_text="Например, «50–100 растений» или «на объект 2 га».",
    )
    subject = models.CharField(
        "Тема",
        max_length=20,
        choices=SUBJECT_CHOICES,
        default=SUBJECT_WHOLESALE,
        blank=True,
    )
    message = models.TextField("Сообщение", blank=True, default="")
    consent_given = models.BooleanField(
        "Согласие на обработку персональных данных (152-ФЗ)",
        default=False,
    )
    consent_at = models.DateTimeField("Дата согласия", null=True, blank=True)
    source_ip = models.GenericIPAddressField("IP отправителя", null=True, blank=True)
    user_agent = models.CharField("User-Agent", max_length=500, blank=True, default="")
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    processed = models.BooleanField("Обработана", default=False)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.get_subject_display()}"
