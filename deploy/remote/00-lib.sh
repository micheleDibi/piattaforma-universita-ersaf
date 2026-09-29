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

# Vero se shared/api.env esiste e la sua ultima riga con SMS_BACKEND vale skebby.
# Riga cercata come la legge Docker Compose (rientro, export, spazi, = o :) e con
# maiuscole qualunque, come l'API; dal valore si tolgono apici, spazi, CR e
# commento in coda. Legge solo quella chiave e non ne stampa il valore.
sms_reali_in_api_env() {
    local valore
    [ -f "$SHARED/api.env" ] || return 1
    valore="$(sed -nE 's/^[[:space:]]*(export[[:space:]]+)?[Ss][Mm][Ss]_[Bb][Aa][Cc][Kk][Ee][Nn][Dd][[:space:]]*[=:]//p' \
        "$SHARED/api.env" 2>/dev/null | tail -n 1 | sed 's/[[:space:]]#.*$//' | tr -d "\r\t\"' " || true)"
    [ "$valore" = skebby ]
}

# Avviso della rete EduNews24 lasciata scollegata per gli SMS reali: una volta
# per shell, anche se lo chiedono sia compose_rel sia prepara_edunews24.
avviso_sms_edunews24() {
    [ -z "${_avviso_sms_edunews24:-}" ] || return 0
    _avviso_sms_edunews24=1
    warn "uscita EduNews24 attiva (USCITA_EDUNEWS24 assente, vuota o si) ma shared/api.env ha SMS_BACKEND=skebby senza NOTIFICHE_REALI=si: l'API resta senza rete EduNews24, perche' dalla sua porta HTTPS partirebbero gli SMS reali. Per collegarla: SMS_BACKEND diverso da skebby, poi -Action deploy; per spegnerla e togliere l'avviso: USCITA_EDUNEWS24=no"
}

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
    if [ -f "$SHARED/db-tls/server.cnf" ] && [ -f "$RELEASES/$id/deploy/compose.tls.yml" ]; then
        file+=(-f "$RELEASES/$id/deploy/compose.tls.yml")
    fi
    if [ -f "$SHARED/compose.env" ] && [ "$(compose_env_get CHAT_NATIVA)" = "si" ]; then
        # Overlay presente solo nelle release native; non ostacola il rollback.
        if [ -f "$RELEASES/$id/deploy/compose.chat.yml" ]; then
            [ -d "$SHARED/chat-secrets" ] || die "cartella segreti chat assente"
            file+=(-f "$RELEASES/$id/deploy/compose.chat.yml")
        fi
    fi
    # Quando il collaudo e' pubblicato su un dominio si aggiunge la seconda
    # pubblicazione della porta web sull'indirizzo LAN (25-esposizione.sh).
    if [ -f "$SHARED/compose.env" ] && [ "$(compose_env_get ESPOSIZIONE)" = "si" ]; then
        file+=(-f "$RELEASES/$id/deploy/compose.esposizione.yml")
    fi
    if [ -f "$SHARED/compose.env" ] && [ "$(compose_env_get NOTIFICHE_REALI)" = "si" ]; then
        # Il fallback mantiene disponibile il rollback alle release precedenti
        # all'introduzione dei provider reali.
        local notifiche="$RELEASES/$id/deploy/compose.notifiche.yml"
        [ -f "$notifiche" ] || notifiche="$SHARED/compose.notifiche.yml"
        [ -f "$notifiche" ] || die "configurazione rete notifiche assente"
        file+=(-f "$notifiche")
    fi
    # Uscita verso EduNews24 (27-edunews24.sh), solo se valgono tutte e quattro:
    # - USCITA_EDUNEWS24 assente, vuota o si (uscita_edunews24_attiva, piu' sotto);
    # - notifiche reali spente: con due reti non interne l'API avrebbe un solo
    #   gateway, scelto da Docker, e l'SMTP potrebbe finire sul bridge EduNews24,
    #   che ammette solo la 443 (quello delle notifiche la ammette gia');
    # - SMS reali non configurati (sms_reali_in_api_env): la 443 del bridge vale
    #   per tutta l'API e farebbe partire gli SMS senza NOTIFICHE_REALI=si;
    # - copia in shared/ presente: la crea solo il deploy, dopo aver installato
    #   le regole, quindi nessuna azione collega la rete senza firewall.
    # Senza copia o con gli SMS reali si avvisa su stderr, una volta per shell
    # (verify, che chiama compose da sottoshell, puo' ripeterlo): lo stdout di
    # compose_active e' letto da altre funzioni, e die bloccherebbe anche status
    # e rollback.
    if [ -f "$SHARED/compose.env" ] && uscita_edunews24_attiva \
        && [ "$(compose_env_get NOTIFICHE_REALI)" != "si" ]; then
        if sms_reali_in_api_env; then
            avviso_sms_edunews24
        elif [ -f "$SHARED/compose.edunews24.yml" ]; then
            local edunews24="$RELEASES/$id/deploy/compose.edunews24.yml"
            [ -f "$edunews24" ] || edunews24="$SHARED/compose.edunews24.yml"
            file+=(-f "$edunews24")
        elif [ -z "${_avviso_edunews24:-}" ]; then
            _avviso_edunews24=1
            warn "uscita EduNews24 attiva (USCITA_EDUNEWS24 assente, vuota o si) ma le regole non sono installate: l'API resta senza rete EduNews24 finche' un deploy non le installa; per spegnerla: USCITA_EDUNEWS24=no"
        fi
    fi
    RELEASE_TAG="$id" RELEASE_DIR="$RELEASES/$id" docker compose \
        -p "$PROJECT" --project-directory "$BASE" --env-file "$SHARED/compose.env" \
        "${file[@]}" "$@"
}

compose_active() { compose_rel "${ACTIVE_ID:-$(current_release_id)}" "$@"; }

# Vero se l'uscita verso EduNews24 e' attiva. Lo e' per difetto: con
# USCITA_EDUNEWS24 assente o vuota in shared/compose.env (vale l'ultima riga,
# come per le altre chiavi) e con si. La spegne solo un valore diverso, per
# esempio no; anche "si" fra apici, SI o si con spazi la spengono.
uscita_edunews24_attiva() {
    local valore
    valore="$(compose_env_get USCITA_EDUNEWS24)"
    [ -z "$valore" ] || [ "$valore" = si ]
}

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
