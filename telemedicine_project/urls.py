from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.urls')),
    # Ajoutez ici les URLs pour vos autres applications API si vous en avez
    # path('api/', include('votre_autre_app.urls')),
]

# Cette configuration est cruciale pour servir les fichiers médias en environnement de développement.
# Elle ne doit PAS être utilisée en production.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)