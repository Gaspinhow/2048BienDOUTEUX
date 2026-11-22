import io
from pathlib import Path
import shutil
import tempfile
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from .models import TAILLE_MAX_PHOTO, Article, Categorie, Photo

MEDIA_TMP = tempfile.mkdtemp()


def fausse_photo(largeur, hauteur, fmt="JPEG", mode="RGB", orientation=None):
    img = Image.new(mode, (largeur, hauteur), "red" if mode == "RGB" else (255, 0, 0, 128))
    buf = io.BytesIO()
    kwargs = {}
    if orientation:
        exif = Image.Exif()
        exif[0x0112] = orientation
        kwargs["exif"] = exif
    img.save(buf, fmt, **kwargs)
    return SimpleUploadedFile(f"photo.{fmt.lower()}", buf.getvalue())


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class PhotoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cat = Categorie.objects.create(nom="Hauts", slug="hauts")
        self.article = Article.objects.create(titre="Pull", categorie=cat, prix=Decimal("20"))

    def test_grande_photo_reduite_en_jpeg(self):
        p = Photo.objects.create(article=self.article, image=fausse_photo(4000, 3000, "PNG"))
        self.assertTrue(p.image.name.endswith(".jpg"))
        with Image.open(p.image.path) as img:
            self.assertEqual(max(img.size), TAILLE_MAX_PHOTO)
            self.assertEqual(img.format, "JPEG")

    def test_photo_telephone_redressee(self):
        # Orientation EXIF 6 = photo prise en portrait, stockée couchée.
        p = Photo.objects.create(article=self.article, image=fausse_photo(1200, 900, orientation=6))
        with Image.open(p.image.path) as img:
            self.assertEqual(img.size, (900, 1200))

    def test_png_transparent(self):
        p = Photo.objects.create(article=self.article, image=fausse_photo(500, 500, "PNG", mode="RGBA"))
        with Image.open(p.image.path) as img:
            self.assertEqual(img.mode, "RGB")

    def test_suppression_efface_le_fichier(self):
        p = Photo.objects.create(article=self.article, image=fausse_photo(300, 300))
        chemin = p.image.path
        p.delete()
        self.assertFalse(Path(chemin).exists())

    def test_changer_ordre_ne_retraite_pas(self):
        p = Photo.objects.create(article=self.article, image=fausse_photo(300, 300))
        nom = p.image.name
        p.ordre = 3
        p.save()
        self.assertEqual(p.image.name, nom)



