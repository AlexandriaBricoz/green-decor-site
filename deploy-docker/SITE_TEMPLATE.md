# Добавление второго/следующего сайта

Инфра одна: **Traefik** уже слушает 80/443 и выпускает сертификаты Let's Encrypt.
Каждый новый сайт — независимый compose-стек.

## Предусловия

1. Traefik уже запущен (см. `README.md`, шаги 1–2).
2. Сеть существует:
   ```bash
   docker network ls | grep traefik-public
   ```
3. У вашего домена A-запись указывает на IP этого сервера.

## Схема

Каждый сайт в отдельной директории `/srv/<name>/app/`, с собственным
`docker-compose.yml` и `.env`. Свой контейнер БД (изоляция), общий
Traefik и общая сеть `traefik-public`.

## Шаги для нового Django-сайта

### 1. Синхронизируйте код на сервер

```bash
mkdir -p /srv/<name>/app
rsync -avz --exclude '.git' --exclude '.env' \
      ./ root@YOUR_HOST:/srv/<name>/app/
```

### 2. Dockerfile

Если сайт уже с Dockerfile — оставляйте свой. Иначе возьмите
`Dockerfile` от Green Decor как образец: python + gunicorn + non-root.

### 3. docker-compose.yml

Скопируйте этот шаблон в корень своего проекта и подставьте `SERVICE_NAME`
(уникальное имя для Traefik router — латиница, без пробелов, например `mysite`):

```yaml
name: mysite

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
    networks: [internal]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 5s
      timeout: 5s
      retries: 20

  web:
    build: .
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    env_file: .env
    volumes:
      - media:/app/media
    networks: [internal, traefik-public]
    labels:
      - traefik.enable=true
      - traefik.docker.network=traefik-public
      - traefik.http.routers.mysite.rule=Host(`${SITE_DOMAIN}`) || Host(`www.${SITE_DOMAIN}`)
      - traefik.http.routers.mysite.entrypoints=web
      - traefik.http.routers.mysite-secure.rule=Host(`${SITE_DOMAIN}`) || Host(`www.${SITE_DOMAIN}`)
      - traefik.http.routers.mysite-secure.entrypoints=websecure
      - traefik.http.routers.mysite-secure.tls=true
      - traefik.http.routers.mysite-secure.tls.certresolver=le
      - traefik.http.services.mysite.loadbalancer.server.port=8000  # порт вашего web-процесса

networks:
  internal:
  traefik-public:
    external: true

volumes:
  db_data:
  media:
```

**Заменить `mysite` во всех 4 строках** роутеров/сервисов на уникальное имя.
Иначе конфликт с другим сайтом.

### 4. .env

```
SITE_DOMAIN=mysite.ru
POSTGRES_DB=mysite
POSTGRES_USER=mysite
POSTGRES_PASSWORD=<секрет>
DATABASE_URL=postgres://mysite:<секрет>@db:5432/mysite
DJANGO_SECRET_KEY=<секрет>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=mysite.ru,www.mysite.ru
DJANGO_CSRF_TRUSTED_ORIGINS=https://mysite.ru,https://www.mysite.ru
```

### 5. Запуск

```bash
cd /srv/mysite/app
docker compose build
docker compose up -d
docker compose logs -f web
```

Traefik подхватит labels в течение секунд. Первый запрос по HTTPS
инициирует выпуск сертификата (может занять до минуты).

### 6. Проверка

```bash
curl -I https://mysite.ru/
docker compose ps
docker network inspect traefik-public | grep -A2 mysite
```

## Диагностика

Если сертификат не выпускается:

```bash
# логи Traefik
docker logs traefik-traefik-1 2>&1 | grep -iE 'acme|error|greendecor|mysite'

# DNS указывает на этот сервер?
dig +short mysite.ru

# порт 80 открыт для Let's Encrypt?
ufw status | grep 'Nginx Full\|80/tcp\|443/tcp'
```

Если 502 Bad Gateway — контейнер веб-сервиса не слушает 8000 или упал:

```bash
docker compose logs web
docker compose exec web curl -I http://127.0.0.1:8000/
```

## Удаление сайта

```bash
cd /srv/mysite/app
docker compose down            # оставит volumes (данные БД, media)
# полная зачистка (данные потеряются):
docker compose down -v
```
