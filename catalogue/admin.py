from django.contrib import admin
from django.utils.html import format_html

from .models import Article, Categorie, Photo


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ["nom", "ordre", "nb_en_vente"]
    list_editable = ["ordre"]
    prepopulated_fields = {"slug": ["nom"]}

    @admin.display(description="En vente")
    def nb_en_vente(self, obj):
        return obj.articles.en_vente().count()


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 3
    fields = ["apercu", "image", "ordre"]
    readonly_fields = ["apercu"]

    @admin.display(description="Aperçu")
    def apercu(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="height:80px;border-radius:4px">', obj.image.url)
        return "—"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["miniature", "titre", "categorie", "taille", "prix", "statut", "mis_en_avant", "cree_le"]
    list_display_links = ["miniature", "titre"]
    list_editable = ["prix", "statut", "mis_en_avant"]
    list_filter = ["statut", "categorie", "etat", "mis_en_avant"]
    search_fields = ["titre", "marque", "description"]
    list_per_page = 50
    inlines = [PhotoInline]
    actions = ["mettre_en_vente", "retirer_de_la_vente"]
    fieldsets = [
        (None, {"fields": ["titre", "categorie", "prix", "statut", "mis_en_avant"]}),
        ("Détails", {"fields": ["marque", "taille", "etat", "description"]}),
        ("Avancé", {"fields": ["slug"], "classes": ["collapse"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("categorie").prefetch_related("photos")

    @admin.display(description="")
    def miniature(self, obj):
        photo = obj.photo_principale
        if photo:
            return format_html('<img src="{}" style="height:48px;width:48px;object-fit:cover;border-radius:4px">', photo.image.url)
        return "—"

    @admin.action(description="Mettre en vente")
    def mettre_en_vente(self, request, queryset):
        n = queryset.exclude(statut=Article.Statut.VENDU).update(statut=Article.Statut.DISPONIBLE)
        self.message_user(request, f"{n} article(s) mis en vente.")

    @admin.action(description="Retirer de la vente (brouillon)")
    def retirer_de_la_vente(self, request, queryset):
        n = queryset.filter(statut=Article.Statut.DISPONIBLE).update(statut=Article.Statut.BROUILLON)
        self.message_user(request, f"{n} article(s) retiré(s).")
