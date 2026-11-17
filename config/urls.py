from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = f"{settings.NOM_BOUTIQUE} — Back-office"
admin.site.site_title = "Back-office"
admin.site.index_title = "Gestion de la boutique"

urlpatterns = [
    path("gestion/", admin.site.urls),
    path("", include("commandes.urls")),
    path("", include("catalogue.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
