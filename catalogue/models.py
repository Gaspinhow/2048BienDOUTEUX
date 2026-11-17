from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Categorie(models.Model):
    nom = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage dans le menu.")

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "catégorie"

    def __str__(self):
        return self.nom


class ArticleQuerySet(models.QuerySet):
    def en_vente(self):
        return self.filter(statut=Article.Statut.DISPONIBLE)


class Article(models.Model):
    """Une pièce de seconde main : chaque article est unique (stock = 1)."""

    class Statut(models.TextChoices):
        BROUILLON = "brouillon", "Brouillon (invisible)"
        DISPONIBLE = "disponible", "En vente"
        RESERVE = "reserve", "Réservé (paiement en cours)"
        VENDU = "vendu", "Vendu"

    class Etat(models.TextChoices):
        NEUF = "neuf", "Neuf avec étiquette"
        TRES_BON = "tres_bon", "Très bon état"
        BON = "bon", "Bon état"
        CORRECT = "correct", "État correct"

    titre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT, related_name="articles", verbose_name="catégorie")
    marque = models.CharField(max_length=80, blank=True)
    taille = models.CharField(max_length=20, blank=True, help_text="Ex. : S, M, 38, 42…")
    etat = models.CharField("état", max_length=10, choices=Etat.choices, default=Etat.TRES_BON)
    prix = models.DecimalField(max_digits=8, decimal_places=2)
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.DISPONIBLE, db_index=True)
    mis_en_avant = models.BooleanField("mis en avant", default=False, help_text="Affiché en premier sur l'accueil.")
    cree_le = models.DateTimeField("ajouté le", auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-mis_en_avant", "-cree_le"]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titre)[:150] or "article"
            slug, n = base, 2
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalogue:detail", args=[self.slug])

    @property
    def prix_centimes(self):
        return int(self.prix * 100)

    @property
    def photo_principale(self):
        photos = list(self.photos.all())  # profite du prefetch_related
        return photos[0] if photos else None


class Photo(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="articles/%Y/%m/")
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "id"]

    def __str__(self):
        return f"Photo de {self.article}"
