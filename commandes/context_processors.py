from django.conf import settings


def panier(request):
    return {
        "nb_panier": len(request.session.get("panier", [])),
        "NOM_BOUTIQUE": settings.NOM_BOUTIQUE,
    }
