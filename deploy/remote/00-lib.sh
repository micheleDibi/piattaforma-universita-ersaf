#!/usr/bin/env bash
# 00-lib.sh - funzioni comuni del bundle di deploy eseguito sul server.
#
# I file deploy/remote/*.sh vengono concatenati in ordine alfabetico dallo
# script Windows (scripts/deploy.ps1) e inviati via SSH a
# `bash -s -- <comando> [argomenti]`: sul server non resta installato nulla
# oltre alle release estratte. Ogni file definisce soltanto funzioni; il
# dispatcher e' in 90-main.sh. Nessuna funzione stampa segreti.
set -Eeuo pipefail
umask 027
export LANG=C.UTF-8 LC_ALL=C.UTF-8

BASE="${ERSAF_DEPLOY_BASE:-/srv/ersaf-universita}"
PROJECT="ersaf-universita-collaudo"
SHARED="$BASE/shared"
RELEASES="$BASE/releases"
STATE="$BASE/state"
SNAPSHOTS="$BASE/snapshots"
LOGS="$BASE/logs"
INCOMING="$BASE/incoming"
CLONE_DB="universita_collaudo"
APP_UID=10001
KEEP_RELEASES=3
KEEP_PRE_MIGRAZIONE=3
KEEP_SORGENTE=2
MIN_FREE_GIB_DEPLOY=4
MIN_FREE_GIB_CLONE=10
MIN_FREE_GIB_DOCKER=5
DB_CNF=/run/secrets/db.cnf
SOURCE_CNF=/run/secrets/source-db.cnf
DOCKER_DIR="${ERSAF_DEPLOY_DOCKER_DIR:-/var/lib/docker}"
# Release usata dalle funzioni compose_active: durante un deploy e' quella
# nuova, altrimenti quella registrata in shared/compose.env.
ACTIVE_ID=""

log()  { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
warn() { printf '[%s] ATTENZIONE: %s\n' "$(date +%H:%M:%S)" "$*" >&2; }
die()  { printf '\n[%s] ERRORE: %s\n' "$(date +%H:%M:%S)" "$1" >&2; exit "${2:-1}"; }
trap 'printf "\n[%s] ERRORE: comando fallito (riga %s): %s\n" "$(date +%H:%M:%S)" "$LINENO" "$BASH_COMMAND" >&2' ERR

timestamp() { date +%Y%m%d-%H%M%S; }

# GiB liberi sul filesystem del percorso; 0 se il percorso non e' misurabile.
free_gib() {
    local liberi
    liberi="$(df -BG --output=avail "$1" 2>/dev/null | tail -n 1 | tr -dc '0-9')" || true
    printf '%s' "${liberi:-0}"
}

require_free_gib() {
    local percorso="$1" minimo="$2" liberi
    liberi="$(free_gib "$percorso")"
    [ "${liberi:-0}" -ge "$minimo" ] \
        || die "spazio insufficiente su $percorso: ${liberi:-0} GiB liberi, minimo ${minimo} GiB"
    log "spazio su $percorso: ${liberi} GiB liberi"
}

installed() { [ -f "$SHARED/compose.env" ]; }

require_installed() {
    installed || die "ambiente non installato in $BASE: eseguire prima l'azione install"
}

compose_env_get() { sed -n "s/^$1=//p" "$SHARED/compose.env" | tail -n 1; }

compose_env_set() {
    local chiave="$1" valore="$2" tmp
    tmp="$(mktemp)"
    { grep -v "^${chiave}=" "$SHARED/compose.env" || true; printf '%s=%s\n' "$chiave" "$valore"; } > "$tmp"
    cat "$tmp" > "$SHARED/compose.env"
    rm -f "$tmp"
}

web_port() { local p; p="$(compose_env_get WEB_PORT)"; printf '%s' "${p:-18082}"; }

current_release_id() {
    local id
    id="$(compose_env_get RELEASE_TAG)"
    { [ -n "$id" ] && [ "$id" != none ]; } || die "nessuna release attiva: eseguire prima install"
    printf '%s' "$id"
}

# docker compose sulla release indicata. RELEASE_TAG/RELEASE_DIR passate come
# ambiente prevalgono sul file --env-file: cosi' si costruisce e si avvia una
# release nuova senza toccare compose.env finche' la verifica non passa.
compose_rel() {
    local id="$1"; shift
    local file=(-f "$RELEASES/$id/deploy/compose.yml")
    # Quando il collaudo e' pubblicato su un dominio si aggiunge la seconda
    # pubblicazione della porta web sull'indirizzo LAN (25-esposizione.sh).
    if [ -f "$SHARED/compose.env" ] && [ "$(compose_env_get ESPOSIZIONE)" = "si" ]; then
        file+=(-f "$RELEASES/$id/deploy/compose.esposizione.yml")
    fi
    RELEASE_TAG="$id" RELEASE_DIR="$RELEASES/$id" docker compose \
        -p "$PROJECT" --project-directory "$BASE" --env-file "$SHARED/compose.env" \
        "${file[@]}" "$@"
}

compose_active() { compose_rel "${ACTIVE_ID:-$(current_release_id)}" "$@"; }

acquire_lock() {
    mkdir -p "$BASE"
    exec 9>"$BASE/.lock"
    if command -v flock >/dev/null 2>&1; then
        flock -n 9 || die "un'altra operazione e' in corso su $BASE (file .lock)"
    fi
}

container_id() { compose_active ps -q "$1" 2>/dev/null | head -n 1; }

container_health() {
    local cid
    cid="$(container_id "$1")"
    [ -n "$cid" ] || { printf 'assente'; return; }
    docker inspect -f '{{.State.Status}}{{if .State.Health}}/{{.State.Health.Status}}{{end}}' "$cid"
}

wait_healthy() {
    # Le variabili ERSAF_DEPLOY_WAIT_* servono solo al banco di prova locale.
    local servizio="$1" limite="${ERSAF_DEPLOY_WAIT_LIMIT:-${2:-180}}" passo="${ERSAF_DEPLOY_WAIT_STEP:-5}" atteso=0 stato
    while :; do
        stato="$(container_health "$servizio")"
        if [ "$stato" = "running/healthy" ]; then log "$servizio: $stato"; return 0; fi
        [ "$atteso" -lt "$limite" ] || die "$servizio non e' healthy dopo ${limite}s (stato: $stato)"
        sleep "$passo"; atteso=$((atteso + passo))
    done
}

# Client MariaDB usa-e-getta sulla rete interna; credenziali dal file montato.
db_tools() { compose_active run --rm -T dbtools "$@"; }
db_sql()   { db_tools mariadb --defaults-extra-file="$DB_CNF" --batch --skip-column-names "$@"; }
db_query() { db_sql --database="$CLONE_DB" -e "$1" | tr -d '\r'; }

db_tables_count() {
    db_sql -e "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA='$CLONE_DB'" | tr -dc '0-9'
}

clone_present() { local n; n="$(db_tables_count)"; [ "${n:-0}" -gt 0 ]; }

db_up() {
    log "avvio del database del clone"
    compose_active up -d --no-build db
    wait_healthy db 240
}

stop_app() { compose_active stop api web; }

rand_alnum() {
    local n="$1" s
    s="$(openssl rand -base64 192 | tr -dc 'A-Za-z0-9')"
    printf '%s' "${s:0:n}"
}

# Elimina i file piu' vecchi oltre i primi N (per nome, che inizia col timestamp).
prune_files() {
    local pattern="$1" tieni="$2" f i=0
    for f in $(ls -1 $pattern 2>/dev/null | sort -r || true); do
        i=$((i + 1))
        [ "$i" -le "$tieni" ] && continue
        log "rimuovo snapshot vecchio: $(basename "$f")"
        rm -f "$f" "$f.sha256"
    done
}
