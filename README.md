# Boutique seconde main

Site e-commerce pour vêtements de seconde main : **Django** (site + back-office) et **Stripe Checkout** (paiement).

## Démarrer en local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser     # compte du gérant
python manage.py demo                # (optionnel) 8 articles fictifs
python manage.py runserver
```

- Boutique : http://localhost:8000/
- Back-office : http://localhost:8000/gestion/

Sans `STRIPE_SECRET_KEY` dans `.env`, le site tourne en **paiement simulé** : une fausse page de paiement remplace Stripe. Ce mode n'existe qu'avec `DJANGO_DEBUG=true`.

Tests : `python manage.py test`

## Architecture

| Dossier | Rôle |
|---|---|
| `catalogue/` | Catégories, articles, photos. Pages liste et fiche produit. |
| `commandes/panier.py` | Panier en session (liste d'ids : chaque pièce est unique). |
| `commandes/services.py` | **Toute la logique argent** : réservation, paiement, expiration, Stripe. |
| `commandes/views.py` | Panier, redirection vers Stripe, pages retour, webhook. |
| `templates/`, `static/` | HTML et CSS du site public. |

### Cycle d'une vente

```
Article DISPONIBLE ──clic "Payer"──▶ RÉSERVÉ (30 min) + Commande EN_ATTENTE
                                         │
                       page de paiement hébergée par Stripe
                         │                              │
              webhook "completed"              abandon / "expired" / annulation
                         ▼                              ▼
        Article VENDU, Commande PAYÉE        Article DISPONIBLE, Commande EXPIRÉE
                         │
         gérant : action "Marquer comme expédiée" dans le back-office
```

- La réservation (avec verrou en base) empêche de vendre deux fois la même pièce.
- Le webhook est vérifié par signature et idempotent (Stripe peut le renvoyer plusieurs fois).
- La page « merci » interroge aussi Stripe directement au cas où le webhook arrive en retard.
- Aucune donnée bancaire ne transite par le serveur : c'est Stripe qui saisit la carte et l'adresse.

## Brancher Stripe

1. Créer un compte Stripe (au nom du client, c'est lui qui encaisse) et récupérer la clé secrète de **test** (`sk_test_…`).
2. En local : `stripe listen --forward-to localhost:8000/stripe/webhook/` et copier le `whsec_…` affiché dans `STRIPE_WEBHOOK_SECRET`.
3. Payer avec la carte `4242 4242 4242 4242`, n'importe quelle date future, n'importe quel CVC.
4. En prod, déclarer l'endpoint `https://<domaine>/stripe/webhook/` dans le dashboard Stripe avec les événements
   `checkout.session.completed`, `checkout.session.expired`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed`.

## Reste à faire (selon le cahier des charges)

- [ ] Emails : confirmation au client, alerte « nouvelle commande » au gérant
- [ ] Hébergement + stockage des photos (disque persistant ou S3/Cloudflare R2), PostgreSQL si besoin
- [ ] Pages légales : CGV, mentions légales, politique de confidentialité, droit de rétractation (14 jours)
- [ ] Identité visuelle, page d'accueil, à propos
- [ ] Options de livraison (Mondial Relay, remise en main propre…)
- [ ] Redimensionnement automatique des photos à l'upload
- [ ] SEO (sitemap, balises meta, Open Graph pour Instagram)
