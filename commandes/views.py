import logging

from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from catalogue.models import Article

from . import services
from .models import Commande
from .panier import Panier

log = logging.getLogger(__name__)


def panier(request):
    p = Panier(request)
    articles = p.articles()
    sous_total = Panier.total(articles)
    port = services.frais_port() if articles else 0
    return render(
        request,
        "commandes/panier.html",
        {"articles": articles, "sous_total": sous_total, "frais_port": port, "total": sous_total + port},
    )


@require_POST
def ajouter(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if article.statut != Article.Statut.DISPONIBLE:
        messages.error(request, "Désolé, cette pièce n'est plus disponible.")
        return redirect(article)
    Panier(request).ajouter(article.id)
    messages.success(request, f"« {article.titre} » ajouté au panier.")
    return redirect("commandes:panier")


@require_POST
def retirer(request, article_id):
    Panier(request).retirer(article_id)
    return redirect("commandes:panier")


@require_POST
def valider(request):
    p = Panier(request)
    try:
        commande = services.creer_commande(p.ids)
    except services.ArticlesIndisponibles as e:
        for a in e.articles:
            p.retirer(a.id)
        messages.error(request, f"Plus disponible : {e}. Votre panier a été mis à jour." if e.articles else "Panier vide.")
        return redirect("commandes:panier")
    try:
        url = services.url_paiement(commande, request)
    except Exception:
        log.exception("Création de la session Stripe impossible")
        services.liberer_commande(commande)
        messages.error(request, "Le paiement est momentanément indisponible, réessayez dans un instant.")
        return redirect("commandes:panier")
    request.session["commande_en_cours"] = str(commande.reference)
    return redirect(url)


def succes(request, reference):
    commande = get_object_or_404(Commande, reference=reference)
    # Le webhook peut arriver après le retour du client : on vérifie directement auprès de Stripe.
    session_id = request.GET.get("session_id")
    if commande.statut == Commande.Statut.EN_ATTENTE and session_id and session_id == commande.stripe_session_id:
        try:
            services.traiter_session_stripe(services.recuperer_session(session_id))
            commande.refresh_from_db()
        except Exception:
            log.exception("Vérification de la session Stripe impossible")
    if commande.statut == Commande.Statut.PAYEE:
        Panier(request).vider()
    return render(request, "commandes/succes.html", {"commande": commande})


def annule(request, reference):
    commande = get_object_or_404(Commande, reference=reference)
    services.liberer_commande(commande)  # pièces remises en vente tout de suite
    messages.info(request, "Paiement annulé. Vos articles sont toujours dans le panier.")
    return redirect("commandes:panier")


def simulation(request, reference):
    """Fausse page de paiement pour développer sans compte Stripe. Désactivée en prod."""
    if not (settings.DEBUG and settings.PAIEMENT_SIMULE):
        raise Http404
    commande = get_object_or_404(Commande, reference=reference, statut=Commande.Statut.EN_ATTENTE)
    if request.method == "POST":
        if "payer" in request.POST:
            services.confirmer_paiement(
                commande,
                email=request.POST.get("email", "test@example.com"),
                nom=request.POST.get("nom", "Client Test"),
                adresse=request.POST.get("adresse", ""),
            )
            return redirect("commandes:succes", reference=commande.reference)
        return redirect("commandes:annule", reference=commande.reference)
    return render(request, "commandes/simulation.html", {"commande": commande})


@csrf_exempt
@require_POST
def webhook_stripe(request):
    try:
        event = services.construire_evenement(request.body, request.headers.get("Stripe-Signature", ""))
    except Exception:
        return HttpResponseBadRequest("signature invalide")

    if event["type"] in (
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
        "checkout.session.expired",
    ):
        services.traiter_session_stripe(event["data"]["object"])
    elif event["type"] == "checkout.session.async_payment_failed":
        ref = event["data"]["object"].get("client_reference_id")
        commande = Commande.objects.filter(reference=ref).first()
        if commande:
            services.liberer_commande(commande)
    return HttpResponse(status=200)
