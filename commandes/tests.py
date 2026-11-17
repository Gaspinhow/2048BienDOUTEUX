import hashlib
import hmac
import json
import time
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from catalogue.models import Article, Categorie

from . import services
from .models import Commande

SECRET_WH = "whsec_test"


def signer(payload: bytes, secret=SECRET_WH):
    t = int(time.time())
    sig = hmac.new(secret.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
    return f"t={t},v1={sig}"


class Base(TestCase):
    def setUp(self):
        cat = Categorie.objects.create(nom="Vestes", slug="vestes")
        self.a1 = Article.objects.create(titre="Veste en jean", categorie=cat, prix=Decimal("35.00"))
        self.a2 = Article.objects.create(titre="Blazer laine", categorie=cat, prix=Decimal("48.50"))

    def statut(self, article):
        article.refresh_from_db()
        return article.statut


@override_settings(FRAIS_PORT_CENTIMES=590)
class ServicesTests(Base):
    def test_creer_commande_reserve_et_calcule(self):
        c = services.creer_commande([self.a1.id, self.a2.id])
        self.assertEqual(c.total, Decimal("89.40"))
        self.assertEqual(self.statut(self.a1), Article.Statut.RESERVE)

    def test_pas_de_double_vente(self):
        services.creer_commande([self.a1.id])
        with self.assertRaises(services.ArticlesIndisponibles):
            services.creer_commande([self.a1.id, self.a2.id])
        self.assertEqual(self.statut(self.a2), Article.Statut.DISPONIBLE)  # rien n'a été bloqué

    def test_confirmation_idempotente(self):
        c = services.creer_commande([self.a1.id])
        services.confirmer_paiement(c, email="a@b.fr")
        services.confirmer_paiement(c, email="autre@b.fr")
        c.refresh_from_db()
        self.assertEqual(c.statut, Commande.Statut.PAYEE)
        self.assertEqual(c.email, "a@b.fr")
        self.assertEqual(self.statut(self.a1), Article.Statut.VENDU)

    def test_expiration_remet_en_vente(self):
        c = services.creer_commande([self.a1.id])
        Commande.objects.filter(pk=c.pk).update(cree_le=timezone.now() - timedelta(hours=1))
        services.liberer_reservations_expirees()
        c.refresh_from_db()
        self.assertEqual(c.statut, Commande.Statut.EXPIREE)
        self.assertEqual(self.statut(self.a1), Article.Statut.DISPONIBLE)

    def test_liberer_ne_touche_pas_une_commande_payee(self):
        c = services.creer_commande([self.a1.id])
        services.confirmer_paiement(c)
        services.liberer_commande(c)
        self.assertEqual(self.statut(self.a1), Article.Statut.VENDU)


@override_settings(STRIPE_WEBHOOK_SECRET=SECRET_WH)
class WebhookTests(Base):
    def envoyer(self, type_, objet, secret=SECRET_WH):
        payload = json.dumps({"id": "evt_1", "object": "event", "type": type_, "data": {"object": objet}}).encode()
        return self.client.post(
            reverse("commandes:webhook"), payload, content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signer(payload, secret),
        )

    def test_signature_invalide_refusee(self):
        r = self.envoyer("checkout.session.completed", {}, secret="whsec_pirate")
        self.assertEqual(r.status_code, 400)

    def test_paiement_complete(self):
        c = services.creer_commande([self.a1.id])
        r = self.envoyer("checkout.session.completed", {
            "id": "cs_1", "object": "checkout.session", "client_reference_id": str(c.reference),
            "payment_status": "paid", "status": "complete", "payment_intent": "pi_1",
            "customer_details": {"email": "cliente@ex.fr", "name": "Léa", "phone": "0600000000"},
            "collected_information": {"shipping_details": {"name": "Léa M.", "address": {
                "line1": "3 rue Haute", "postal_code": "69001", "city": "Lyon", "country": "FR"}}},
        })
        self.assertEqual(r.status_code, 200)
        c.refresh_from_db()
        self.assertEqual(c.statut, Commande.Statut.PAYEE)
        self.assertEqual(c.email, "cliente@ex.fr")
        self.assertIn("69001 Lyon", c.adresse_livraison)
        self.assertEqual(self.statut(self.a1), Article.Statut.VENDU)

    def test_session_expiree(self):
        c = services.creer_commande([self.a1.id])
        self.envoyer("checkout.session.expired", {
            "id": "cs_1", "object": "checkout.session", "client_reference_id": str(c.reference),
            "payment_status": "unpaid", "status": "expired",
        })
        self.assertEqual(self.statut(self.a1), Article.Statut.DISPONIBLE)


@override_settings(DEBUG=True, PAIEMENT_SIMULE=True)
class ParcoursClientTests(Base):
    def test_parcours_complet_simule(self):
        self.client.post(reverse("commandes:ajouter", args=[self.a1.id]))
        r = self.client.post(reverse("commandes:valider"))
        c = Commande.objects.get()
        self.assertRedirects(r, reverse("commandes:simulation", args=[c.reference]))
        r = self.client.post(r.url, {"payer": "1", "email": "x@y.fr", "nom": "X"}, follow=True)
        self.assertContains(r, "Merci pour votre commande")
        self.assertEqual(self.statut(self.a1), Article.Statut.VENDU)
        self.assertEqual(self.client.session["panier"], [])

    def test_article_vendu_disparait_du_catalogue(self):
        services.confirmer_paiement(services.creer_commande([self.a1.id]))
        r = self.client.get(reverse("catalogue:liste"))
        self.assertNotContains(r, "Veste en jean")
        self.assertContains(r, "Blazer laine")
