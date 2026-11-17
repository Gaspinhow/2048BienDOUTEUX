from django.shortcuts import get_object_or_404, render

from commandes.services import liberer_reservations_expirees

from .models import Article, Categorie


def liste(request, categorie_slug=None):
    liberer_reservations_expirees()
    articles = Article.objects.en_vente().select_related("categorie").prefetch_related("photos")
    categorie = None
    if categorie_slug:
        categorie = get_object_or_404(Categorie, slug=categorie_slug)
        articles = articles.filter(categorie=categorie)
    taille = request.GET.get("taille")
    if taille:
        articles = articles.filter(taille__iexact=taille)
    tailles = (
        Article.objects.en_vente().exclude(taille="").values_list("taille", flat=True).distinct().order_by("taille")
    )
    return render(
        request,
        "catalogue/liste.html",
        {
            "articles": articles,
            "categories": Categorie.objects.all(),
            "categorie": categorie,
            "tailles": tailles,
            "taille": taille,
        },
    )


def detail(request, slug):
    article = get_object_or_404(
        Article.objects.exclude(statut=Article.Statut.BROUILLON).prefetch_related("photos"), slug=slug
    )
    return render(request, "catalogue/detail.html", {"article": article})
