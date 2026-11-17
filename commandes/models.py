import uuid

from django.db import models


class Commande(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "en_attente", "En attente de paiement"
        PAYEE = "payee", "Payée — à expédier"
        EXPEDIEE = "expediee", "Expédiée"
        EXPIREE = "expiree", "Abandonnée / expirée"
        REMBOURSEE = "remboursee", "Remboursée"

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.EN_ATTENTE, db_index=True)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frais_port = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Rempli après paiement à partir des infos saisies sur la page Stripe.
    email = models.EmailField(blank=True)
    nom = models.CharField(max_length=150, blank=True)
    telephone = models.CharField(max_length=40, blank=True)
    adresse_livraison = models.TextField(blank=True)

    stripe_session_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    numero_suivi = models.CharField("n° de suivi colis", max_length=100, blank=True)
    note_interne = models.TextField(blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    payee_le = models.DateTimeField(null=True, blank=True)
    expediee_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-cree_le"]

    def __str__(self):
        return f"Commande {self.numero}"

    @property
    def numero(self):
        return str(self.reference)[:8].upper()


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes")
    # SET_NULL : si l'article est supprimé un jour, la commande garde titre et prix.
    article = models.ForeignKey("catalogue.Article", on_delete=models.SET_NULL, null=True, related_name="lignes")
    titre = models.CharField(max_length=150)
    prix = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "ligne de commande"
        verbose_name_plural = "lignes de commande"

    def __str__(self):
        return self.titre
