"""Panier stocké en session. Chaque pièce est unique : on garde juste une liste d'ids, sans quantité."""
from decimal import Decimal

from catalogue.models import Article

CLE = "panier"


class Panier:
    def __init__(self, request):
        self.session = request.session
        self.ids = [int(i) for i in self.session.get(CLE, [])]

    def _sauver(self):
        self.session[CLE] = self.ids
        self.session.modified = True

    def ajouter(self, article_id):
        if article_id not in self.ids:
            self.ids.append(article_id)
            self._sauver()

    def retirer(self, article_id):
        if article_id in self.ids:
            self.ids.remove(article_id)
            self._sauver()

    def vider(self):
        self.ids = []
        self._sauver()

    def articles(self):
        """Articles encore en vente. Ceux vendus entre-temps sont retirés silencieusement."""
        dispo = list(Article.objects.en_vente().filter(id__in=self.ids).prefetch_related("photos"))
        ids_dispo = [a.id for a in dispo]
        if ids_dispo != self.ids and set(ids_dispo) != set(self.ids):
            self.ids = [i for i in self.ids if i in ids_dispo]
            self._sauver()
        return dispo

    def __len__(self):
        return len(self.ids)

    @staticmethod
    def total(articles):
        return sum((a.prix for a in articles), Decimal("0"))
