#!/usr/bin/env bash
# 20-install.sh - prima installazione: directory, segreti, compose.env.
# Idempotente: non sovrascrive mai un file di segreti esistente; ad api.env
# aggiunge soltanto le chiavi comparse dopo (completa_api_env, usata anche da
# deploy e start).

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
TOTP_CHIAVE=$(rand_alnum 64)
PASSWORD_RESET_TOKEN_TTL_MINUTES=60
PASSWORD_RESET_RATE_LIMIT_PER_HOUR=5
PASSWORD_RESET_BUDGET_MS=900
FRONTEND_BASE_URL=http://localhost:${porta}
CORS_ORIGINS=http://localhost:${porta}
WEBAUTHN_RP_ID=localhost
WEBAUTHN_ORIGINI=http://localhost:${porta}
SESSION_INATTIVITA_GIORNI=14
SESSION_DURATA_MASSIMA_GIORNI=90
BCRYPT_COST=12
PASSWORD_MIN_LENGTH=8
LOG_LEVEL=INFO
LOG_FILE=
EMAIL_BACKEND=file
EMAIL_FILE_DIR=/app/var/email
SMS_BACKEND=file
SMS_FILE_DIR=/app/var/email/sms
SMTP_FROM=ERSAF collaudo <noreply@ersaf.it>
EOT
)"
}

# Chiavi nate dopo la prima installazione: un api.env esistente non si
# riscrive (scrivi_segreto lo conserva), ma senza TOTP_CHIAVE l'API rifiuta di
# partire e senza RP ID e origini WebAuthn le passkey non funzionano sul
# dominio. Si aggiungono in coda solo le chiavi mancanti, senza toccare le
# altre; i valori WebAuthn vengono da FRONTEND_BASE_URL, cio' che il browser vede.
completa_api_env() {  # [porta_web]
    local env="$SHARED/api.env" base host_porta
    [ -f "$env" ] || return 0
    base="$(sed -n 's/^FRONTEND_BASE_URL=//p' "$env" | tail -n 1)"
    base="${base%%[?#]*}"; base="${base%/}"
    [ -n "$base" ] || base="http://localhost:${1:-$(web_port)}"
    host_porta="${base#*://}"; host_porta="${host_porta%%/*}"
    aggiungi_chiave_mancante "$env" TOTP_CHIAVE "$(rand_alnum 64)"
    aggiungi_chiave_mancante "$env" WEBAUTHN_RP_ID "${host_porta%%:*}"
    aggiungi_chiave_mancante "$env" WEBAUTHN_ORIGINI "${base%%://*}://$host_porta"
    chmod 600 "$env"
}

aggiungi_chiave_mancante() {  # <file> <chiave> <valore>
    grep -q "^$2=" "$1" && return 0
    printf '%s=%s\n' "$2" "$3" >> "$1"
    log "api.env: aggiunta la chiave $2"
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

# cmd_install [porta_web]: esce con 10 se la sorgente non e' ancora configurata.
cmd_install() {
    local porta="${1:-18082}"
    cmd_preflight --install
    log "installazione in $BASE"
    install -d -m 750 "$BASE" "$RELEASES" "$STATE" "$LOGS" "$INCOMING"
    install -d -m 700 "$SHARED" "$SNAPSHOTS" "$STATE/mariadb"
    install -d -m 750 -o "$APP_UID" -g "$APP_UID" "$STATE/email"
    genera_db_env
    genera_db_cnf
    genera_api_env "$porta"
    genera_compose_env "$porta"
    completa_api_env "$porta"
    chmod 600 "$SHARED"/*.env "$SHARED"/*.cnf 2>/dev/null || true
    log "installazione base completata; segreti in $SHARED (solo root)"
    if [ -f "$SHARED/source-db.cnf" ] && [ -f "$SHARED/source-db.env" ]; then cmd_source_check; else
        warn "sorgente non configurata: servono le credenziali di lettura del database originale"; exit 10; fi
}

# cmd_source_check: verifica che la sorgente sia configurata, senza leggerne i segreti.
cmd_source_check() {
    [ -f "$SHARED/source-db.cnf" ] && [ -f "$SHARED/source-db.env" ] \
        || die "sorgente non configurata: eseguire l'azione configure-source"
    chmod 600 "$SHARED/source-db.cnf" "$SHARED/source-db.env"
    log "sorgente configurata: $(sed -n 's/^SOURCE_DB_HOST=//p' "$SHARED/source-db.env"):$(sed -n 's/^SOURCE_DB_PORT=//p' "$SHARED/source-db.env") schema $(sed -n 's/^SOURCE_DB_NAME=//p' "$SHARED/source-db.env")"
}
