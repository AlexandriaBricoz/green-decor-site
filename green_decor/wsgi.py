import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "green_decor.settings")

application = get_wsgi_application()

# Whitenoise отдаёт /static/ через middleware, а загружаемые /media/
# оборачиваем здесь: в проде nginx/traefik могут быть без static-хендлера.
_media_root = os.environ.get("DJANGO_MEDIA_ROOT")
if _media_root and os.path.isdir(_media_root):
    from whitenoise import WhiteNoise

    application = WhiteNoise(application, root=_media_root, prefix="/media/")
