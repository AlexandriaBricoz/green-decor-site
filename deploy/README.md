# Green Decor — Deploy

Инструкция для деплоя на VPS с Ubuntu 22.04/24.04.
Все шаги идемпотентны и могут повторяться при апдейтах.

## 0. Предпосылки

- Домен указывает A/AAAA-записями на IP сервера.
- SSH-доступ под пользователем с sudo.
- Порты 80 и 443 открыты в фаерволе (`ufw allow 'Nginx Full'`).

Замените в командах:
- `YOUR_DOMAIN` → ваш домен (например, `green-decor.ru`).
- `STRONG_PASSWORD_HERE` → случайный пароль (не менее 24 символов).

## 1. Установка системных пакетов (одноразово)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip \
    postgresql postgresql-contrib \
    nginx certbot python3-certbot-nginx \
    git
```

## 2. Создание пользователя базы и БД

```bash
sudo -u postgres psql <<SQL
CREATE USER green_decor WITH PASSWORD 'STRONG_PASSWORD_HERE';
CREATE DATABASE green_decor OWNER green_decor ENCODING 'UTF8' LC_COLLATE 'ru_RU.UTF-8' LC_CTYPE 'ru_RU.UTF-8' TEMPLATE template0;
GRANT ALL PRIVILEGES ON DATABASE green_decor TO green_decor;
SQL
```

Если локали `ru_RU.UTF-8` нет: `sudo locale-gen ru_RU.UTF-8` и повторите.

## 3. Каталоги приложения

```bash
sudo mkdir -p /srv/green-decor /var/lib/green-decor/media
sudo chown -R www-data:www-data /srv/green-decor /var/lib/green-decor
```

## 4. Код приложения

Есть два способа: git clone (если репо есть) или rsync с локальной машины.

**Вариант A — с локальной машины:**
```bash
# из корня локального проекта green_decor_site
rsync -av --delete \
  --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude '.env' --exclude 'db.sqlite3' --exclude 'media/' \
  --exclude 'staticfiles/' --exclude '.venv/' \
  ./ user@YOUR_HOST:/tmp/green-decor-src/

# на сервере
sudo rsync -av --delete /tmp/green-decor-src/ /srv/green-decor/app/
sudo chown -R www-data:www-data /srv/green-decor/app
```

## 5. Виртуальное окружение и зависимости

```bash
sudo -u www-data python3 -m venv /srv/green-decor/venv
sudo -u www-data /srv/green-decor/venv/bin/pip install --upgrade pip
sudo -u www-data /srv/green-decor/venv/bin/pip install -r /srv/green-decor/app/requirements.txt
```

## 6. .env

```bash
sudo cp /srv/green-decor/app/.env.example /srv/green-decor/app/.env
sudo nano /srv/green-decor/app/.env    # заполните
sudo chown www-data:www-data /srv/green-decor/app/.env
sudo chmod 640 /srv/green-decor/app/.env
```

Сгенерировать `DJANGO_SECRET_KEY`:
```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(64))'
```

## 7. Миграции, статика, суперпользователь

```bash
cd /srv/green-decor/app
sudo -u www-data /srv/green-decor/venv/bin/python manage.py migrate --noinput
sudo -u www-data /srv/green-decor/venv/bin/python manage.py collectstatic --noinput
sudo -u www-data /srv/green-decor/venv/bin/python manage.py createsuperuser
```

## 8. systemd

```bash
sudo cp /srv/green-decor/app/deploy/gunicorn.socket /etc/systemd/system/green-decor.socket
sudo cp /srv/green-decor/app/deploy/gunicorn.service /etc/systemd/system/green-decor.service
sudo systemctl daemon-reload
sudo systemctl enable --now green-decor.socket
sudo systemctl start green-decor.service
sudo systemctl status green-decor.service
```

## 9. nginx

```bash
sudo cp /srv/green-decor/app/deploy/nginx.conf /etc/nginx/sites-available/green-decor
sudo sed -i 's/YOUR_DOMAIN/'"$YOUR_DOMAIN"'/g' /etc/nginx/sites-available/green-decor

# Первый раз — HTTP-only, чтобы certbot смог провалидировать домен.
# Закомментируйте блок server 443 и ssl-строки в HTTP, а затем:
sudo ln -sf /etc/nginx/sites-available/green-decor /etc/nginx/sites-enabled/green-decor
sudo mkdir -p /var/www/certbot
sudo nginx -t && sudo systemctl reload nginx
```

## 10. HTTPS (Let's Encrypt)

```bash
sudo certbot --nginx -d YOUR_DOMAIN -d www.YOUR_DOMAIN --agree-tos -m admin@YOUR_DOMAIN --no-eff-email
# После этого certbot сам поправит nginx.conf под HTTPS.
# Если certbot не подхватил наш конфиг — раскомментируйте блок 443 из deploy/nginx.conf.
sudo systemctl reload nginx
```

Автообновление сертификата:
```bash
sudo systemctl status certbot.timer    # активен по умолчанию
```

## 11. Проверки

```bash
curl -I https://YOUR_DOMAIN/
curl -I https://YOUR_DOMAIN/price-list.xlsx
sudo journalctl -u green-decor.service -n 100
```

## 12. Обновление кода в будущем

```bash
# с локальной машины
rsync -av --delete \
  --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
  --exclude '.env' --exclude 'db.sqlite3' --exclude 'media/' \
  --exclude 'staticfiles/' --exclude '.venv/' \
  ./ user@YOUR_HOST:/tmp/green-decor-src/

# на сервере
sudo rsync -av --delete /tmp/green-decor-src/ /srv/green-decor/app/
sudo chown -R www-data:www-data /srv/green-decor/app
sudo -u www-data /srv/green-decor/venv/bin/pip install -r /srv/green-decor/app/requirements.txt
sudo -u www-data /srv/green-decor/venv/bin/python /srv/green-decor/app/manage.py migrate --noinput
sudo -u www-data /srv/green-decor/venv/bin/python /srv/green-decor/app/manage.py collectstatic --noinput
sudo systemctl restart green-decor.service
```

## 13. Резервные копии

```bash
# БД
sudo -u postgres pg_dump -Fc green_decor > /var/backups/green_decor_$(date +%F).dump

# Media
sudo tar czf /var/backups/green_decor_media_$(date +%F).tgz -C /var/lib/green-decor media
```

Пропишите оба в cron/systemd-timer.
