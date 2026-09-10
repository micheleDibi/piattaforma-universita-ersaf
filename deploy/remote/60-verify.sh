#!/usr/bin/env bash
# 60-verify.sh - verifica funzionale dopo deploy, rollback o ripristino.

_vf_ko=0
vf_ok() { printf '  OK  %s\n' "$*"; }
vf_ko() { printf '  KO  %s\n' "$*"; _vf_ko=$((_vf_ko + 1)); }

http_code() { curl -s -o /dev/null -m 10 -w '%{http_code}' "$@" 2>/dev/null || printf '000'; }

vf_http_base() {
    local base="$1" codice
    if curl -fsS -m 5 "$base/healthz" 2>/dev/null | grep -q ok; then vf_ok "web risponde su $base"; else vf_ko "web non risponde su $base/healthz"; fi
    if curl -fsS -m 10 "$base/api/salute" 2>/dev/null | grep -q '"stato"'; then vf_ok "API raggiunta tramite /api/salute"; else vf_ko "API non raggiunta tramite /api/salute"; fi
    if curl -fsS -m 5 "$base/" 2>/dev/null | grep -q 'id="root"'; then vf_ok "pagina della SPA servita"; else vf_ko "index.html non servito"; fi
    codice="$(http_code "$base/elenco")"
    [ "$codice" = 200 ] && vf_ok "fallback SPA sui deep link ($codice)" || vf_ko "fallback SPA non funziona (/elenco -> $codice)"
}

# Un login con utente inesistente attraversa API e database: 401 dimostra il
# giro completo senza creare sessioni. Un 5xx indica che il DB non risponde.
vf_login_db() {
    local codice
    codice="$(http_code -X POST -H 'Content-Type: application/json' \
        --data '{"utente_username":"verifica.deploy.inesistente","utente_password":"non-valida"}' "$1/api/auth/login")"
    case "$codice" in
        401) vf_ok "login di prova respinto con 401: API e database collegati";;
        5*|000) vf_ko "login di prova fallito con $codice: API o database non funzionanti";;
        *) vf_ok "login di prova risposto $codice (atteso 401): controllare i log api";;
    esac
}

vf_db() {
    local n
    if ! clone_present; then vf_ko "clone assente"; return; fi
    n="$(db_query 'SELECT COUNT(*) FROM utenti' | tr -dc '0-9')"
    [ "${n:-0}" -gt 0 ] && vf_ok "clone con $n utenti" || vf_ko "tabella utenti vuota nel clone"
}

vf_log_api() {
    local cid
    cid="$(container_id api)"
    [ -n "$cid" ] || return 0
    if docker logs --since 10m "$cid" 2>&1 | grep -qi "startup failed\|Configurazione non valida"; then
        vf_ko "l'API segnala configurazione non valida (vedi logs api)"
    else
        vf_ok "nessun errore di avvio nei log api"
    fi
}

cmd_verify() {
    local base="http://127.0.0.1:$(web_port)"
    _vf_ko=0
    log "verifica dello stack ($base)"
    wait_healthy api 150
    wait_healthy web 90
    vf_http_base "$base"
    vf_login_db "$base"
    vf_db
    vf_log_api
    [ "$_vf_ko" -eq 0 ] || die "verifica fallita: $_vf_ko controlli KO"
    log "verifica superata"
}
