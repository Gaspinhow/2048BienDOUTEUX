"""python manage.py demo : remplit la base avec quelques pièces fictives (photos générées)."""
import io
import random
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw

from catalogue.models import Article, Categorie, Photo

PIECES = [
    ("Vestes", "Veste en jean délavée", "Levi's", "M", "35"),
    ("Vestes", "Blazer en laine chevrons", "Zara", "38", "48.50"),
    ("Hauts", "Pull marin rayé", "Saint James", "S", "42"),
    ("Hauts", "Chemise lin blanche", "", "L", "18"),
    ("Bas", "Jean 501 brut", "Levi's", "W30", "39"),
    ("Bas", "Jupe plissée vintage", "", "36", "22"),
    ("Chaussures", "Derbies cuir marron", "Paraboot", "42", "95"),
    ("Accessoires", "Foulard soie imprimé", "", "", "15"),
]
COULEURS = ["#c9b79c", "#7d8f7a", "#b5654a", "#3e5c76", "#d9c5b2", "#8a6f5a"]


def image(couleur, texte):
    """Aplat de couleur avec un léger dégradé (pas de texte : la police par défaut gère mal les accents)."""
    img = Image.new("RGB", (600, 800), couleur)
    calque = ImageDraw.Draw(img, "RGBA")
    for y in range(0, 800, 4):
        calque.rectangle([0, y, 600, y + 4], fill=(255, 255, 255, int(40 * (1 - y / 800))))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=80)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = "Crée des catégories et articles de démonstration."

    def handle(self, *args, **opts):
        for i, (cat_nom, titre, marque, taille, prix) in enumerate(PIECES):
            cat, _ = Categorie.objects.get_or_create(nom=cat_nom, defaults={"slug": cat_nom.lower(), "ordre": i})
            if Article.objects.filter(titre=titre).exists():
                continue
            a = Article.objects.create(
                titre=titre, categorie=cat, marque=marque, taille=taille, prix=Decimal(prix),
                etat=random.choice(Article.Etat.values), mis_en_avant=(i == 0),
                description="Pièce de démonstration.\nTrès bon état, aucun défaut visible.",
            )
            p = Photo(article=a)
            p.image.save(f"{a.slug}.jpg", image(random.choice(COULEURS), titre), save=True)
        self.stdout.write(self.style.SUCCESS(f"{Article.objects.count()} articles en base."))
