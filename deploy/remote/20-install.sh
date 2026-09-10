#!/usr/bin/env bash
# 20-install.sh - prima installazione: directory, segreti, compose.env.
# Idempotente: non sovrascrive mai un file di segreti esistente.

scrivi_segreto() {  # scrivi_segreto <percorso> <contenuto>
    [ -e "$1" ] && { log "conservo $(basename "$1") esistente"; return 0; }
    ( umask 077; printf '%s\n' "$2" > "$1" )
    log "generato $(basename "$1")"
}

genera_db_env() {
    scrivi_segreto "$SHARED/db.env" "$(cat <<EOT
MARIADB_ROOT_PASSWORD=$(rand_alnum 40)
MARIADB_DATABASE=$CLONE_DB
MARIADB_USER=universita_app
MARIADB_PASSWORD=$(rand_alnum 40)
EOT
)"
}

genera_db_cnf() {
    local root_pwd
    root_pwd="$(sed -n 's/^MARIADB_ROOT_PASSWORD=//p' "$SHARED/db.env")"
    scrivi_segreto "$SHARED/db.cnf" "$(cat <<EOT
[client]
host=db
user=root
password=$root_pwd
default-character-set=utf8mb4
EOT
)"
}

genera_api_env() {
    local app_pwd porta
    app_pwd="$(sed -n 's/^MARIADB_PASSWORD=//p' "$SHARED/db.env")"
    porta="${1:-18082}"
    scrivi_segreto "$SHARED/api.env" "$(cat <<EOT
# Runtime dell'API di collaudo. Generato da install; modificare a mano solo
# con criterio e riavviare con l'azione start. Non contiene l'indirizzo del
# database originale: il solo database raggiungibile e' il clone.
ERSAF_ENV=sviluppo
DATABASE_URL=mysql+pymysql://universita_app:${app_pwd}@db:3306/${CLONE_DB}?charset=utf8mb4
PASSWORD_RESET_TOKEN_PEPPER=$(rand_alnum 64)
SESSION_TOKEN_PEPPER=$(rand_alnum 64)
PASSWORD_RESET_TOKEN_TTL_MINUTES=60
PASSWORD_RESET_RATE_LIMIT_PER_HOUR=5
PASSWORD_RESET_BUDGET_MS=900
FRONTEND_BASE_URL=http://localhost:${porta}
CORS_ORIGINS=http://localhost:${porta}
SESSION_TTL_HOURS=12
BCRYPT_COST=12
PASSWORD_MIN_LENGTH=8
LOG_LEVEL=INFO
LOG_FILE=
EMAIL_BACKEND=file
EMAIL_FILE_DIR=/app/var/email
SMTP_FROM=ERSAF collaudo <noreply@ersaf.it>
EOT
)"
}

genera_compose_env() {
    local porta="${1:-18082}"
    [ -f "$SHARED/compose.env" ] && { log "conservo compose.env esistente"; return 0; }
    cat > "$SHARED/compose.env" <<EOT
RELEASE_TAG=none
RELEASE_DIR=$RELEASES/none
WEB_PORT=$porta
TZ=Europe/Rome
EOT
    log "creato compose.env (porta web $porta)"
}

# cmd_install [porta_web]
cmd_install() {
    local porta="${1:-18082}"
    log "installazione in $BASE"
    install -d -m 750 "$BASE" "$RELEASES" "$STATE" "$LOGS" "$INCOMING"
    install -d -m 700 "$SHARED" "$SNAPSHOTS" "$STATE/mariadb"
    install -d -m 750 -o "$APP_UID" -g "$APP_UID" "$STATE/email"
    genera_db_env
    genera_db_cnf
    genera_api_env "$porta"
    genera_compose_env "$porta"
    chmod 600 "$SHARED"/*.env "$SHARED"/*.cnf 2>/dev/null || true
    log "installazione base completata; segreti in $SHARED (solo root)"
}

# cmd_source_check: verifica che la sorgente sia configurata, senza leggerne i segreti.
cmd_source_check() {
    [ -f "$SHARED/source-db.cnf" ] && [ -f "$SHARED/source-db.env" ] \
        || die "sorgente non configurata: eseguire l'azione configure-source"
    chmod 600 "$SHARED/source-db.cnf" "$SHARED/source-db.env"
    log "sorgente configurata: $(sed -n 's/^SOURCE_DB_HOST=//p' "$SHARED/source-db.env"):$(sed -n 's/^SOURCE_DB_PORT=//p' "$SHARED/source-db.env") schema $(sed -n 's/^SOURCE_DB_NAME=//p' "$SHARED/source-db.env")"
}
