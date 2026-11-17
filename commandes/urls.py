from django.urls import path

from . import views

app_name = "commandes"
urlpatterns = [
    path("panier/", views.panier, name="panier"),
    path("panier/ajouter/<int:article_id>/", views.ajouter, name="ajouter"),
    path("panier/retirer/<int:article_id>/", views.retirer, name="retirer"),
    path("commande/valider/", views.valider, name="valider"),
    path("commande/<uuid:reference>/merci/", views.succes, name="succes"),
    path("commande/<uuid:reference>/annulee/", views.annule, name="annule"),
    path("commande/<uuid:reference>/paiement-test/", views.simulation, name="simulation"),
    path("stripe/webhook/", views.webhook_stripe, name="webhook"),
]
