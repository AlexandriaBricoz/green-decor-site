# Green Decor — Docker deploy

Каждый сайт живёт в своём compose-стеке (свой `web`, свой `db`).
Единый `traefik` обслуживает 80/443 и автоматически выпускает сертификаты
Let's Encrypt для каждого домена. Второй, третий, N-й сайт подключается
к общей сети `traefik-public` и регистрируется через labels — правки
Traefik не требуются.

## Схема

```
    Internet :80/:443
           │
      ┌────▼────┐
      │ Traefik │   (docker container, ACME HTTP-01)
      └────┬────┘
           │  network: traefik-public
   ┌───────┼───────────┐
┌──▼──┐ ┌──▼──┐    ┌──▼──┐
│site1│ │site2│... │siteN│  (каждый сайт = свой compose-stack)
└──┬──┘ └──┬──┘    └──┬──┘
   │       │          │      network: internal (у каждого свой db)
```

## 0. Подготовка сервера (одноразово)

```bash
ssh root@YOUR_HOST
apt-get update && apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
```

**Если на сервере уже слушает `nginx` на 80/443 (текущий деплой Green Decor через systemd) —
остановите его, чтобы освободить порты:**

```bash
systemctl disable --now nginx
systemctl disable --now green-decor.socket green-decor.service    # если запускали
```

Данные PostgreSQL из старого деплоя останутся в хостовом Postgres — при желании
можно снять дамп и залить в новый контейнерный:
```bash
sudo -u postgres pg_dump -Fc green_decor > /root/gd.dump
# позже, когда Docker-стек поднят:
docker exec -i green-decor-db-1 pg_restore -U green_decor -d green_decor -c < /root/gd.dump
```

## 1. Общая сеть

```bash
docker network create traefik-public
```

## 2. Запуск Traefik

```bash
mkdir -p /srv/traefik
# скопируйте на сервер файлы deploy-docker/traefik/{compose.yml,.env.example}
cp deploy-docker/traefik/.env.example /srv/traefik/.env
nano /srv/traefik/.env     # укажите ACME_EMAIL
cp deploy-docker/traefik/compose.yml /srv/traefik/compose.yml

cd /srv/traefik
docker compose up -d
docker compose logs -f traefik
```

## 3. Первый сайт (Green Decor)

Подготовьте `.env` из шаблона:

```bash
mkdir -p /srv/greendecor
# скопируйте на сервер весь проект green_decor_site → /srv/greendecor/app
rsync -avz --exclude '.git' --exclude '.env' --exclude 'db.sqlite3' \
    --exclude 'staticfiles/' --exclude 'media/' \
    ./ root@YOUR_HOST:/srv/greendecor/app/

# на сервере
cd /srv/greendecor/app
cp .env.docker.example .env
nano .env       # заполните SITE_DOMAIN, DJANGO_SECRET_KEY, POSTGRES_PASSWORD, DATABASE_URL

# сгенерировать SECRET_KEY
python3 -c 'import secrets; print(secrets.token_urlsafe(64))'
# сгенерировать пароль БД
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```

Запуск:

```bash
docker compose build
docker compose up -d
docker compose logs -f web
```

Первый суперпользователь:
```bash
docker compose exec web python manage.py createsuperuser
```

Проверка:
```bash
curl -I https://greendecor056.ru/
```

## 4. Второй сайт

См. **SITE_TEMPLATE.md** — там пошагово.

Кратко:
1. Скопируйте свой проект в `/srv/<name>/app/`.
2. Возьмите его `docker-compose.yml` (по образцу этого) и `.env`.
3. `docker compose up -d`.
4. Traefik автоматически подхватит по labels и выпустит сертификат.

## Обновление сайта

```bash
cd /srv/greendecor/app
# синхронизируйте новую версию кода
docker compose build web
docker compose up -d web
docker compose exec web python manage.py migrate --noinput
```

## Резервные копии

```bash
# БД конкретного сайта
docker exec green-decor-db-1 pg_dump -U green_decor -d green_decor -Fc > backup_$(date +%F).dump

# Загружаемые фото
docker run --rm -v green-decor_media:/data -v /root/backups:/backup alpine \
    tar czf /backup/media_$(date +%F).tgz -C /data .
```
