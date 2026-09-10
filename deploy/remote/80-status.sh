#!/usr/bin/env bash
# 80-status.sh - stato, log, arresto e riavvio del solo stack di collaudo.

cmd_status() {
    installed || { log "ambiente non installato in $BASE"; return 0; }
    log "release attiva: $(compose_env_get RELEASE_TAG); precedente: $(cat "$SHARED/previous_release" 2>/dev/null || echo nessuna)"
    log "release presenti: $(ls -1 "$RELEASES" 2>/dev/null | tr '\n' ' ')"
    if [ "$(compose_env_get RELEASE_TAG)" != none ]; then
        compose_active ps --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}' || true
    fi
    log "spazio: base $(free_gib "$BASE") GiB liberi; docker $(free_gib "$DOCKER_DIR") GiB liberi"
    log "snapshot in $SNAPSHOTS:"
    ls -lh "$SNAPSHOTS" 2>/dev/null | awk 'NR>1 {print "      " $5 "  " $9}' || true
    [ -f "$SNAPSHOTS/clone.info" ] && log "clone: $(tr '\n' ' ' < "$SNAPSHOTS/clone.info")"
    log "email su file: $(ls -1 "$STATE/email" 2>/dev/null | wc -l) messaggi in $STATE/email"
}

# cmd_logs <servizio> [righe]
cmd_logs() {
    require_installed
    compose_active logs --no-color --tail "${2:-200}" "${1:-api}"
}

cmd_stop() {
    require_installed
    log "arresto dei soli container di $PROJECT"
    compose_active stop
}

cmd_start() {
    require_installed
    acquire_lock
    db_up
    compose_active up -d --no-build api web
    cmd_verify
}
