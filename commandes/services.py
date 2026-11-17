"""Logique métier des commandes, indépendante des vues.

Cycle de vie :
    panier -> creer_commande()      articles DISPONIBLE -> RESERVE, commande EN_ATTENTE
           -> page de paiement Stripe
           -> confirmer_paiement()  (webhook)  articles -> VENDU, commande PAYEE
           ou liberer_commande()    (abandon)  articles -> DISPONIBLE, commande EXPIREE

La réservation empêche de vendre deux fois la même pièce si deux clients paient en même temps.
"""
from datetime import timedelta
from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from catalogue.models import Article

from .models import Commande, LigneCommande


class ArticlesIndisponibles(Exception):
    def __init__(self, articles):
        self.articles = articles
        super().__init__(", ".join(a.titre for a in articles))


def frais_port():
    return Decimal(settings.FRAIS_PORT_CENTIMES) / 100


@transaction.atomic
def creer_commande(article_ids):
    articles = list(Article.objects.select_for_update().filter(id__in=article_ids).order_by("id"))
    indispo = [a for a in articles if a.statut != Article.Statut.DISPONIBLE]
    if indispo or not articles:
        raise ArticlesIndisponibles(indispo)

    sous_total = sum((a.prix for a in articles), Decimal("0"))
    port = frais_port()
    commande = Commande.objects.create(sous_total=sous_total, frais_port=port, total=sous_total + port)
    LigneCommande.objects.bulk_create(
        [LigneCommande(commande=commande, article=a, titre=a.titre, prix=a.prix) for a in articles]
    )
    Article.objects.filter(id__in=[a.id for a in articles]).update(statut=Article.Statut.RESERVE)
    return commande


@transaction.atomic
def confirmer_paiement(commande, *, email="", nom="", telephone="", adresse="", payment_intent=""):
    """Idempotent : Stripe peut envoyer le même webhook plusieurs fois."""
    commande = Commande.objects.select_for_update().get(pk=commande.pk)
    if commande.statut == Commande.Statut.PAYEE:
        return commande
    # Paiement reçu même si la réservation avait expiré entre-temps : on encaisse quand même
    # et on marque les pièces vendues. Si l'une d'elles a été revendue, l'admin le verra
    # dans la note interne et remboursera.
    deja_revendus = [
        l.titre for l in commande.lignes.select_related("article")
        if l.article and l.article.statut == Article.Statut.VENDU
    ]
    commande.statut = Commande.Statut.PAYEE
    commande.payee_le = timezone.now()
    commande.email = email or commande.email
    commande.nom = nom or commande.nom
    commande.telephone = telephone or commande.telephone
    commande.adresse_livraison = adresse or commande.adresse_livraison
    commande.stripe_payment_intent = payment_intent or commande.stripe_payment_intent
    if deja_revendus:
        commande.note_interne += f"\n⚠ Déjà vendu(s) ailleurs, à rembourser : {', '.join(deja_revendus)}"
    commande.save()
    Article.objects.filter(lignes__commande=commande).update(statut=Article.Statut.VENDU)
    return commande


@transaction.atomic
def liberer_commande(commande):
    commande = Commande.objects.select_for_update().get(pk=commande.pk)
    if commande.statut != Commande.Statut.EN_ATTENTE:
        return commande
    commande.statut = Commande.Statut.EXPIREE
    commande.save(update_fields=["statut"])
    Article.objects.filter(lignes__commande=commande, statut=Article.Statut.RESERVE).update(
        statut=Article.Statut.DISPONIBLE
    )
    return commande


def liberer_reservations_expirees():
    """Filet de sécurité si le webhook 'expired' de Stripe n'arrive jamais."""
    limite = timezone.now() - timedelta(minutes=settings.RESERVATION_MINUTES + 5)
    for commande in Commande.objects.filter(statut=Commande.Statut.EN_ATTENTE, cree_le__lt=limite):
        liberer_commande(commande)


# --- Stripe -----------------------------------------------------------------

def _client():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def url_paiement(commande, request):
    """Crée la session Stripe Checkout et renvoie l'URL où rediriger le client."""
    succes = request.build_absolute_uri(reverse("commandes:succes", args=[commande.reference]))
    annule = request.build_absolute_uri(reverse("commandes:annule", args=[commande.reference]))

    if settings.PAIEMENT_SIMULE:
        return reverse("commandes:simulation", args=[commande.reference])

    line_items = [
        {
            "quantity": 1,
            "price_data": {
                "currency": "eur",
                "unit_amount": int(l.prix * 100),
                "product_data": {"name": l.titre},
            },
        }
        for l in commande.lignes.all()
    ]
    session = _client().checkout.Session.create(
        mode="payment",
        line_items=line_items,
        shipping_address_collection={"allowed_countries": settings.PAYS_LIVRAISON},
        shipping_options=[
            {
                "shipping_rate_data": {
                    "type": "fixed_amount",
                    "display_name": "Colissimo",
                    "fixed_amount": {"amount": settings.FRAIS_PORT_CENTIMES, "currency": "eur"},
                }
            }
        ],
        phone_number_collection={"enabled": True},
        client_reference_id=str(commande.reference),
        metadata={"commande": str(commande.reference)},
        # Stripe expire la session lui-même -> webhook checkout.session.expired -> pièces remises en vente.
        expires_at=int((timezone.now() + timedelta(minutes=settings.RESERVATION_MINUTES)).timestamp()),
        success_url=succes + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=annule,
        locale="fr",
    )
    commande.stripe_session_id = session.id
    commande.save(update_fields=["stripe_session_id"])
    return session.url


def _get(obj, *chemin):
    for cle in chemin:
        if obj is None:
            return None
        obj = obj.get(cle) if isinstance(obj, dict) else getattr(obj, cle, None)
    return obj


def infos_client(session):
    """Extrait nom / email / adresse d'une session Checkout (objet Stripe ou dict du webhook)."""
    details = _get(session, "customer_details") or {}
    livraison = _get(session, "collected_information", "shipping_details") or _get(session, "shipping_details") or {}
    adr = _get(livraison, "address") or {}
    lignes = [
        _get(livraison, "name"),
        _get(adr, "line1"),
        _get(adr, "line2"),
        " ".join(filter(None, [_get(adr, "postal_code"), _get(adr, "city")])),
        _get(adr, "country"),
    ]
    return {
        "email": _get(details, "email") or "",
        "nom": _get(livraison, "name") or _get(details, "name") or "",
        "telephone": _get(details, "phone") or "",
        "adresse": "\n".join(l for l in lignes if l),
        "payment_intent": _get(session, "payment_intent") or "",
    }


def traiter_session_stripe(session):
    """Appelé par le webhook et par la page de succès (si le webhook a du retard)."""
    ref = _get(session, "client_reference_id") or _get(session, "metadata", "commande")
    commande = Commande.objects.filter(reference=ref).first() if ref else None
    if commande is None:
        return None
    if _get(session, "payment_status") == "paid":
        return confirmer_paiement(commande, **infos_client(session))
    if _get(session, "status") == "expired":
        return liberer_commande(commande)
    return commande


def recuperer_session(session_id):
    return _client().checkout.Session.retrieve(session_id)


def construire_evenement(payload, signature):
    return stripe.Webhook.construct_event(payload, signature, settings.STRIPE_WEBHOOK_SECRET)
