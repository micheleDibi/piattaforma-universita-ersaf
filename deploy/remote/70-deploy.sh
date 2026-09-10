#!/usr/bin/env bash
# 70-deploy.sh - orchestrazione del deploy con rollback automatico.

attiva_release() {  # <id>
    local attuale
    attuale="$(compose_env_get RELEASE_TAG)"
    if [ -n "$attuale" ] && [ "$attuale" != none ] && [ "$attuale" != "$1" ]; then
        printf '%s\n' "$attuale" > "$SHARED/previous_release"
    fi
    compose_env_set RELEASE_TAG "$1"
    compose_env_set RELEASE_DIR "$RELEASES/$1"
    ln -sfn "$RELEASES/$1" "$BASE/current"
    log "release attiva: $1"
}

avvia_app() { compose_active up -d --no-build api web; }

deploy_fallito() {  # <precedente>
    warn "deploy fallito"
    if [ -n "$1" ] && [ "$1" != none ]; then
        warn "ripristino della release precedente $1"
        # Subshell: die dentro cmd_rollback non deve saltare i messaggi finali.
        if ( cmd_rollback ); then
            die "deploy annullato: ripristinata la release $1 (le migrazioni gia' applicate restano; snapshot in $SNAPSHOTS)" 3
        fi
        die "deploy fallito e rollback non riuscito: intervento manuale (azioni status e logs)" 4
    fi
    die "primo deploy fallito: correggere e ripetere; per diagnosi usare le azioni status e logs" 3
}

# cmd_deploy <archivio> <id> <sha> <dirty> [--primo-clone] [--senza-clone]
cmd_deploy() {
    local archivio="$1" id="$2" sha="$3" dirty="$4" primo_clone=0 senza_clone=0 a precedente
    shift 4
    for a in "$@"; do case "$a" in --primo-clone) primo_clone=1;; --senza-clone) senza_clone=1;; esac; done
    require_installed
    acquire_lock
    mkdir -p "$LOGS"
    exec > >(tee -a "$LOGS/deploy-$id.log") 2>&1
    log "deploy della release $id"
    cmd_preflight --deploy
    require_free_gib "$BASE" "$MIN_FREE_GIB_DEPLOY"
    precedente="$(compose_env_get RELEASE_TAG)"
    ACTIVE_ID="$id"
    cmd_release "$archivio" "$id" "$sha" "$dirty"
    db_up
    if [ "$primo_clone" = 1 ]; then
        if clone_present; then log "clone gia' presente: la clonazione non viene ripetuta"; else do_clone 0; fi
    fi
    if ! clone_present; then
        [ "$senza_clone" = 1 ] || die "clone del database assente: eseguire install (con clonazione) o clone-db"
        warn "avvio senza clone: solo per prova del packaging"
    else
        cmd_migrate
    fi
    attiva_release "$id"
    # cmd_verify termina con die: in subshell il fallimento torna qui e scatta il rollback.
    if avvia_app && ( cmd_verify ); then
        cmd_prune
        log "deploy completato: release $id (git $sha)"
        return 0
    fi
    deploy_fallito "$precedente"
}

cmd_rollback() {
    local precedente attuale
    precedente="$(cat "$SHARED/previous_release" 2>/dev/null || true)"
    [ -n "$precedente" ] || die "nessuna release precedente registrata"
    [ -d "$RELEASES/$precedente" ] || die "cartella della release precedente assente: $precedente"
    docker image inspect "ersaf-universita/api:$precedente" "ersaf-universita/web:$precedente" >/dev/null 2>&1 \
        || die "immagini della release $precedente non piu' presenti"
    attuale="$(compose_env_get RELEASE_TAG)"
    log "rollback da $attuale a $precedente"
    ACTIVE_ID="$precedente"
    avvia_app
    compose_env_set RELEASE_TAG "$precedente"
    compose_env_set RELEASE_DIR "$RELEASES/$precedente"
    ln -sfn "$RELEASES/$precedente" "$BASE/current"
    printf '%s\n' "$attuale" > "$SHARED/previous_release"
    cmd_verify
    warn "le migrazioni applicate dalla release $attuale non vengono annullate: db/rollback e gli snapshot pre-migrazione sono in $SNAPSHOTS"
}
