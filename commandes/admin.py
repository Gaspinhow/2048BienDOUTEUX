from django.contrib import admin
from django.utils import timezone

from .models import Commande, LigneCommande


class LigneInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    can_delete = False
    fields = ["article", "titre", "prix"]
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ["numero", "cree_le", "statut", "nom", "email", "total", "nb_articles"]
    list_filter = ["statut", "cree_le"]
    search_fields = ["reference", "email", "nom", "lignes__titre"]
    date_hierarchy = "cree_le"
    inlines = [LigneInline]
    actions = ["marquer_expediee"]
    readonly_fields = [
        "numero", "reference", "cree_le", "payee_le", "expediee_le",
        "sous_total", "frais_port", "total",
        "email", "nom", "telephone", "adresse_livraison",
        "stripe_session_id", "stripe_payment_intent",
    ]
    fieldsets = [
        (None, {"fields": ["numero", "statut", "total", "sous_total", "frais_port"]}),
        ("Client & livraison", {"fields": ["nom", "email", "telephone", "adresse_livraison", "numero_suivi"]}),
        ("Suivi", {"fields": ["cree_le", "payee_le", "expediee_le", "note_interne"]}),
        ("Stripe", {"fields": ["reference", "stripe_session_id", "stripe_payment_intent"], "classes": ["collapse"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("lignes")

    def has_add_permission(self, request):
        return False  # les commandes naissent uniquement du site

    @admin.display(description="Articles")
    def nb_articles(self, obj):
        return len(obj.lignes.all())

    @admin.action(description="Marquer comme expédiée")
    def marquer_expediee(self, request, queryset):
        n = queryset.filter(statut=Commande.Statut.PAYEE).update(
            statut=Commande.Statut.EXPEDIEE, expediee_le=timezone.now()
        )
        self.message_user(request, f"{n} commande(s) marquée(s) expédiée(s).")
