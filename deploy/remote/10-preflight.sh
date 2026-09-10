#!/usr/bin/env bash
# 10-preflight.sh - controlli in sola lettura sul server. Non crea file.

_pf_ko=0
pf_ok() { printf '  OK  %s\n' "$*"; }
pf_ko() { printf '  KO  %s\n' "$*"; _pf_ko=$((_pf_ko + 1)); }
pf_wa() { printf '  !!  %s\n' "$*"; }

pf_docker() {
    if docker info >/dev/null 2>&1; then
        pf_ok "Docker $(docker version -f '{{.Server.Version}}'), Compose $(docker compose version --short)"
    else
        pf_ko "Docker non raggiungibile (daemon fermo o permessi)"
    fi
}

pf_spazio() {
    local base_fs liberi
    base_fs="$BASE"; [ -d "$base_fs" ] || base_fs="$(dirname "$BASE")"
    liberi="$(free_gib "$base_fs")"
    if [ "${liberi:-0}" -ge "$1" ]; then pf_ok "spazio su $base_fs: ${liberi} GiB liberi"
    else pf_ko "spazio su $base_fs: ${liberi} GiB liberi, minimo $1 GiB"; fi
    liberi="$(free_gib "$DOCKER_DIR")"
    if [ "${liberi:-0}" -ge "$MIN_FREE_GIB_DOCKER" ]; then pf_ok "spazio Docker ($DOCKER_DIR): ${liberi} GiB liberi"
    else pf_ko "spazio Docker: ${liberi} GiB liberi, minimo $MIN_FREE_GIB_DOCKER GiB"; fi
}

pf_memoria() {
    local disp
    disp="$(free -g | awk '/^Mem:/ {print $7}')"
    if [ "${disp:-0}" -ge 4 ]; then pf_ok "memoria disponibile: ${disp} GiB"
    else pf_ko "memoria disponibile: ${disp:-?} GiB, minimo 4 GiB"; fi
}

pf_porta() {
    local porta="$1" nostro
    if ! ss -ltnH "sport = :$porta" | grep -q .; then pf_ok "porta $porta libera"; return; fi
    nostro="$(docker ps --filter "label=com.docker.compose.project=$PROJECT" --filter "publish=$porta" -q 2>/dev/null)"
    if [ -n "$nostro" ]; then pf_ok "porta $porta usata dal nostro container web"
    else pf_ko "porta $porta occupata da un altro processo"; fi
}

pf_internet() {
    local url codice
    for url in https://registry-1.docker.io/v2/ https://pypi.org/simple/ https://registry.npmjs.org/; do
        codice="$(curl -sS -m 10 -o /dev/null -w '%{http_code}' "$url" 2>/dev/null || true)"
        case "$codice" in
            2*|3*|401) pf_ok "raggiungibile: $url";;
            *) pf_ko "non raggiungibile: $url (serve per immagini e pacchetti)";;
        esac
    done
}

pf_sorgente() {
    [ -f "$SHARED/source-db.env" ] || { pf_wa "sorgente non configurata (source-db.env assente): richiesta per la clonazione"; return; }
    local host porta
    host="$(sed -n 's/^SOURCE_DB_HOST=//p' "$SHARED/source-db.env")"
    porta="$(sed -n 's/^SOURCE_DB_PORT=//p' "$SHARED/source-db.env")"
    if timeout 5 bash -c "</dev/tcp/$host/${porta:-3306}" 2>/dev/null; then pf_ok "sorgente $host:${porta:-3306} raggiungibile (solo TCP)"
    else pf_ko "sorgente $host:${porta:-3306} non raggiungibile dal server"; fi
}

pf_altri_servizi() {
    local altri
    altri="$(docker ps --format '{{.Names}}' | grep -v "^${PROJECT}-" || true)"
    [ -z "$altri" ] || pf_ok "servizi preesistenti che non vengono toccati: $(printf '%s' "$altri" | tr '\n' ' ')"
}

# cmd_preflight [--install|--deploy|--auto]
cmd_preflight() {
    local modo="${1:---auto}" porta
    if [ "$modo" = "--auto" ]; then installed && modo="--deploy" || modo="--install"; fi
    log "preflight ($modo) su $(hostname), base $BASE"
    pf_docker
    if [ "$modo" = "--deploy" ]; then
        if installed; then pf_ok "ambiente installato in $BASE"; else pf_ko "ambiente non installato: eseguire install"; fi
        pf_spazio "$MIN_FREE_GIB_DEPLOY"
    else
        [ -d "$BASE" ] && pf_wa "$BASE esiste gia': install e' idempotente e non sovrascrive segreti" || pf_ok "$BASE assente, verra' creata"
        pf_spazio "$MIN_FREE_GIB_CLONE"
    fi
    pf_memoria
    porta="$( [ -f "$SHARED/compose.env" ] && compose_env_get WEB_PORT || true )"
    pf_porta "${porta:-18082}"
    pf_internet
    pf_sorgente
    pf_altri_servizi
    [ "$_pf_ko" -eq 0 ] || die "preflight fallito: $_pf_ko controlli KO"
    log "preflight superato"
}
