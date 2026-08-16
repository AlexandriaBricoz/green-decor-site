from django.db import models


class SiteSettings(models.Model):
    """Одна запись на весь сайт — контакты, адрес, карта, футер."""

    hero_kicker = models.CharField(
        "Главная — маленькая подпись сверху",
        max_length=100,
        blank=True,
        default="Питомник растений",
        help_text="Тонкая надпись капсом над главным заголовком (обычно 2-3 слова).",
    )
    hero_title = models.CharField(
        "Главная — заголовок, первая строка",
        max_length=200,
        blank=True,
        default="Хвойные растения",
        help_text="Большая надпись на главной. Первая строка отображается обычным цветом.",
    )
    hero_title_accent = models.CharField(
        "Главная — заголовок, вторая строка (зелёный курсив)",
        max_length=200,
        blank=True,
        default="из нашего питомника.",
        help_text="Продолжение заголовка на новой строке, выделено зелёным курсивом.",
    )

    address = models.CharField(
        "Адрес оптового питомника",
        max_length=300,
        default="Оренбург, Загородное шоссе, 37/2",
    )
    map_embed_url = models.TextField(
        "Код карты оптового питомника",
        blank=True,
        default="",
        help_text=(
            "Откройте yandex.ru/maps → «Поделиться» → «Код карты» → «Скопировать» и "
            "вставьте полученный HTML-блок целиком (или только URL из src=\"…\")."
        ),
    )
    address_retail = models.CharField(
        "Адрес розничного питомника",
        max_length=300,
        blank=True,
        default="",
        help_text="Оставьте пустым, если розничного питомника нет — блок скроется.",
    )
    map_embed_retail = models.TextField(
        "Код карты розничного питомника",
        blank=True,
        default="",
        help_text="Инструкция та же, что и для оптового.",
    )
    phones = models.TextField(
        "Телефоны",
        blank=True,
        default="+7 (912) 846-10-22\n+7 (912) 845-10-22\n+7 (912) 066-38-08",
        help_text="По одному номеру на строку.",
    )
    email = models.EmailField("Email", blank=True, default="suslova_1983@mail.ru")
    schedule = models.CharField(
        "Режим работы",
        max_length=200,
        blank=True,
        default="Работаем без выходных",
    )
    legal_entity = models.CharField(
        "Юридическое лицо / ИП",
        max_length=200,
        blank=True,
        default="ИП Суслова",
        help_text="Например: «ИП Суслова» или «ООО \"Ромашка\"». Показывается в футере рядом с ИНН.",
    )
    inn = models.CharField("ИНН", max_length=20, blank=True, default="565100366000")
    footer_about = models.TextField(
        "Описание в футере",
        blank=True,
        default="Питомник хвойных и декоративных растений. Для дач, садов, парков и городских проектов.",
    )
    footer_address_title = models.CharField(
        "Заголовок блока адреса в футере",
        max_length=100,
        blank=True,
        default="Штаб-квартира",
    )
    footer_address_note = models.CharField(
        "Подпись под адресом в футере",
        max_length=200,
        blank=True,
        default="Главный кампус питомника",
    )
    copyright_text = models.CharField(
        "Копирайт",
        max_length=200,
        blank=True,
        default="© 2024–2026 Green Decor · ИП Суслова · ИНН: 565100366000. Все права защищены.",
    )
    telegram_chat_id = models.CharField(
        "Telegram chat ID",
        max_length=50,
        blank=True,
        default="",
        help_text=(
            "Заполняется автоматически, когда вы напишете боту команду /start в группе. "
            "Пока пусто — уведомления не отправляются."
        ),
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def phones_list(self) -> list[dict]:
        result = []
        for line in (self.phones or "").splitlines():
            phone = line.strip()
            if not phone:
                continue
            href = "tel:" + "".join(ch for ch in phone if ch.isdigit() or ch == "+")
            result.append({"label": phone, "href": href})
        return result


class Plant(models.Model):
    LOW_STOCK_THRESHOLD = 10

    name = models.CharField("Наименование", max_length=200)
    sku = models.CharField("Артикул", max_length=50, unique=True)
    age_years = models.PositiveIntegerField("Возраст (лет)")
    size_cm = models.CharField(
        "Размер (см)",
        max_length=50,
        help_text="Например, 60-80 или 120",
    )
    quantity = models.PositiveIntegerField("Количество (шт)", default=0)
    price = models.DecimalField("Цена (₽/шт)", max_digits=10, decimal_places=2)
    photo = models.ImageField("Фото", upload_to="plants/", blank=True, null=True)
    external_url = models.URLField(
        "Ссылка на медиа",
        max_length=500,
        blank=True,
        default="",
        help_text="Ссылка на видео, фотогалерею или другой материал. Попадёт в Excel-прайс.",
    )
    description = models.TextField("Описание", blank=True)
    is_public = models.BooleanField(
        "Показывать в публичном прайс-листе",
        default=True,
        help_text="Если выключено — позиция скрыта от клиентов и в Excel-прайсе.",
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Растение"
        verbose_name_plural = "Растения"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.LOW_STOCK_THRESHOLD

    @property
    def total_value(self):
        return self.quantity * self.price
