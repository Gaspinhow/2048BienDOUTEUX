#!/usr/bin/env bash
# Sauvegarde quotidienne de la base et des photos. Garde les 14 derniers jours.
# Cron (crontab -e de l'utilisateur boutique) : 30 3 * * * /srv/boutique/deploy/sauvegarde.sh
set -euo pipefail
APP=/srv/boutique
DEST=${DEST:-/srv/sauvegardes}
JOUR=$(date +%F)
mkdir -p "$DEST"
# Copie cohérente de SQLite même si le site tourne.
"$APP/.venv/bin/python" -c "import sqlite3; s=sqlite3.connect('$APP/db.sqlite3'); d=sqlite3.connect('$DEST/db-$JOUR.sqlite3'); s.backup(d); d.close()"
tar -czf "$DEST/media-$JOUR.tar.gz" -C "$APP" media
find "$DEST" -type f -mtime +14 -delete
# Conseil : copier aussi $DEST hors du serveur (rclone vers un stockage externe, ou snapshot de l'hébergeur).
