# Mise en ligne sur un VPS (Debian / Ubuntu)

Un petit serveur à environ 5 €/mois (Hetzner, OVH…) suffit. Compter environ 1 h la première fois.

## 1. Préparer le serveur

```bash
sudo apt update && sudo apt install -y python3-venv git caddy
sudo adduser --system --group --home /srv/boutique boutique
sudo -u boutique git clone https://github.com/<compte>/<depot>.git /srv/boutique
cd /srv/boutique
sudo -u boutique python3 -m venv .venv
sudo -u boutique .venv/bin/pip install -r requirements.txt
```

## 2. Configurer `.env`

```bash
sudo -u boutique cp .env.example .env && sudo -u boutique nano .env
```

À remplir obligatoirement en prod :

- `DJANGO_DEBUG=false`
- `DJANGO_SECRET_KEY=` : générer avec `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `DJANGO_ALLOWED_HOSTS=exemple.fr,www.exemple.fr`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://exemple.fr,https://www.exemple.fr`
- `STRIPE_SECRET_KEY` et `STRIPE_WEBHOOK_SECRET` (clés **live** du compte Stripe du client)
- `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `EMAIL_GERANT`

## 3. Initialiser et lancer

```bash
sudo -u boutique .venv/bin/python manage.py migrate
sudo -u boutique .venv/bin/python manage.py collectstatic --noinput
sudo -u boutique .venv/bin/python manage.py createsuperuser   # compte du gérant
sudo -u boutique .venv/bin/python manage.py check --deploy

sudo cp deploy/boutique.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now boutique

sudo cp deploy/Caddyfile /etc/caddy/Caddyfile   # puis remplacer exemple.fr
sudo systemctl reload caddy
```

## 4. Stripe

Dashboard Stripe → Développeurs → Webhooks → ajouter `https://exemple.fr/stripe/webhook/` avec les événements :
`checkout.session.completed`, `checkout.session.expired`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed`.
Copier le secret de signature dans `STRIPE_WEBHOOK_SECRET`, puis `sudo systemctl restart boutique`.

Faire un vrai achat à petit prix (1 €), vérifier la commande dans le back-office et les deux emails, puis rembourser depuis Stripe.

## 5. Sauvegardes

```bash
sudo mkdir -p /srv/sauvegardes && sudo chown boutique /srv/sauvegardes
sudo -u boutique crontab -e
# ajouter : 30 3 * * * /srv/boutique/deploy/sauvegarde.sh
```

Pour restaurer : arrêter le site, remettre `db-AAAA-MM-JJ.sqlite3` à la place de `db.sqlite3`, détarer `media-…tar.gz`, relancer.

## Mises à jour

```bash
sudo -u boutique /srv/boutique/deploy/mettre-a-jour.sh
```
(l'utilisateur `boutique` doit avoir le droit `sudo systemctl restart boutique`, sinon lancer cette dernière commande à la main).
