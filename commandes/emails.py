"""Emails envoyés quand une commande est payée. Un échec d'envoi ne doit jamais bloquer la vente."""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

log = logging.getLogger(__name__)


def _envoyer(sujet, gabarit, destinataire, commande):
    if not destinataire:
        return
    corps = render_to_string(gabarit, {"commande": commande, "NOM_BOUTIQUE": settings.NOM_BOUTIQUE})
    try:
        send_mail(sujet, corps, settings.DEFAULT_FROM_EMAIL, [destinataire])
    except Exception:
        log.exception("Envoi de l'email « %s » à %s impossible", sujet, destinataire)


def commande_payee(commande):
    _envoyer(
        f"{settings.NOM_BOUTIQUE} — confirmation de votre commande {commande.numero}",
        "emails/confirmation_client.txt", commande.email, commande,
    )
    _envoyer(
        f"Nouvelle commande {commande.numero} — {commande.total} €",
        "emails/alerte_gerant.txt", settings.EMAIL_GERANT, commande,
    )


def commande_expediee(commande):
    _envoyer(
        f"{settings.NOM_BOUTIQUE} — votre commande {commande.numero} est en route",
        "emails/expedition_client.txt", commande.email, commande,
    )
