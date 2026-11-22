#!/usr/bin/env bash
# À lancer sur le serveur après chaque modification du code : ./deploy/mettre-a-jour.sh
set -euo pipefail
cd /srv/boutique
git pull --ff-only
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput -v0
.venv/bin/python manage.py check --deploy --fail-level ERROR
sudo systemctl restart boutique
echo "Site mis à jour."
