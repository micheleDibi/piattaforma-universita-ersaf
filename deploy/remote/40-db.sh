#!/usr/bin/env bash
# 40-db.sh - clone del database originale, backup e ripristino del clone.
#
# REGOLE VINCOLANTI
# - Verso la sorgente (192.168.40.11) si esegue soltanto mariadb-dump in sola
#   lettura, con snapshot consistente (--single-transaction) e senza lock
#   globali, FLUSH o opzioni di replica. Nessuna GRANT, nessuna scrittura.
# - L'API non conosce la sorgente: il solo servizio con uscita di rete e'
#   dbclone, avviato qui e rimosso alla fine (--rm).
# - Il clone contiene dati personali: i dump restano in $SNAPSHOTS (solo root)
#   e non vengono mai copiati sul PC.

DUMP_OPZIONI=(--single-transaction --quick --hex-blob --triggers --skip-routines
    --skip-events --no-tablespaces --default-character-set=utf8mb4
    --max-allowed-packet=64M --skip-comments)

source_var() { sed -n "s/^$1=//p" "$SHARED/source-db.env"; }

dump_sorgente() {  # dump_sorgente <file.sql.gz>
    local out="$1" nome
    nome="$(source_var SOURCE_DB_NAME)"
    log "export dalla sorgente $(source_var SOURCE_DB_HOST):$(source_var SOURCE_DB_PORT)/$nome (sola lettura, snapshot consistente)"
    compose_active run --rm -T dbclone mariadb-dump --defaults-extra-file="$SOURCE_CNF" \
        "${DUMP_OPZIONI[@]}" "$nome" | gzip -1 > "$out"
    gzip -t "$out" || die "archivio del dump corrotto: $out"
    (cd "$SNAPSHOTS" && sha256sum "$(basename "$out")" > "$(basename "$out").sha256")
    log "dump completato: $(du -h "$out" | cut -f1), $(conta_tabelle_dump "$out") tabelle"
}

conta_tabelle_dump() { zcat "$1" | grep -c '^CREATE TABLE' || true; }

dump_clone() {  # dump_clone <prefisso>  -> stampa il percorso creato
    local out="$SNAPSHOTS/$1-$(timestamp).sql.gz"
    db_tools mariadb-dump --defaults-extra-file="$DB_CNF" --single-transaction --quick --hex-blob \
        --triggers --events --routines --default-character-set=utf8mb4 --max-allowed-packet=256M \
        "$CLONE_DB" | gzip -1 > "$out"
    gzip -t "$out" || die "backup del clone corrotto: $out"
    printf '%s' "$out"
}

ricrea_schema_clone() {
    log "svuoto lo schema $CLONE_DB"
    db_sql -e "DROP DATABASE IF EXISTS \`$CLONE_DB\`; CREATE DATABASE \`$CLONE_DB\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
}

importa_nel_clone() {  # importa_nel_clone <file.sql.gz>
    log "import di $(basename "$1") in $CLONE_DB (puo' richiedere diversi minuti)"
    zcat "$1" | db_tools mariadb --defaults-extra-file="$DB_CNF" --default-character-set=utf8mb4 \
        --max-allowed-packet=256M "$CLONE_DB"
    log "import terminato: $(db_tables_count) tabelle nel clone"
}

verifica_clone() {  # verifica_clone <tabelle_attese>
    local tabelle
    tabelle="$(db_tables_count)"
    [ "$tabelle" -eq "$1" ] || die "tabelle nel clone ($tabelle) diverse da quelle nel dump ($1)"
    log "verifica clone: $tabelle tabelle; utenti=$(db_query 'SELECT COUNT(*) FROM utenti') clienti=$(db_query 'SELECT COUNT(*) FROM clienti')"
}

# do_clone <refresh:0|1>
do_clone() {
    local refresh="$1" dump backup
    cmd_source_check
    require_free_gib "$SNAPSHOTS" "$MIN_FREE_GIB_CLONE"
    db_up
    if clone_present; then
        [ "$refresh" = 1 ] || die "il clone contiene gia' $(db_tables_count) tabelle: per ricrearlo usare refresh-clone"
        stop_app
        backup="$(dump_clone clone-pre-refresh)"
        log "copia di sicurezza del clone attuale: $(basename "$backup")"
        ricrea_schema_clone
    fi
    dump="$SNAPSHOTS/sorgente-$(timestamp).sql.gz"
    dump_sorgente "$dump"
    importa_nel_clone "$dump"
    verifica_clone "$(conta_tabelle_dump "$dump")"
    printf 'data=%s\ndump=%s\ntabelle=%s\n' "$(date -Is)" "$(basename "$dump")" "$(db_tables_count)" > "$SNAPSHOTS/clone.info"
    prune_files "$SNAPSHOTS/sorgente-*.sql.gz" "$KEEP_SORGENTE"
    log "clone pronto; le migrazioni vengono applicate dal deploy"
}

# cmd_clone --confermato [--refresh]
cmd_clone() {
    local confermato=0 refresh=0 a
    for a in "$@"; do case "$a" in --confermato) confermato=1;; --refresh) refresh=1;; esac; done
    [ "$confermato" = 1 ] || die "clonazione non confermata"
    require_installed
    acquire_lock
    exec > >(tee -a "$LOGS/clone-$(timestamp).log") 2>&1
    do_clone "$refresh"
    if [ "$refresh" = 1 ]; then
        cmd_migrate
        compose_active up -d --no-build api web
        cmd_verify
    fi
}

cmd_backup() {
    require_installed
    db_up
    log "backup del clone: $(basename "$(dump_clone clone-backup)")"
}

# cmd_restore <nome_snapshot> --confermato
cmd_restore() {
    local file="$SNAPSHOTS/$(basename "${1:-}")"
    [ "${2:-}" = "--confermato" ] || die "ripristino non confermato"
    [ -f "$file" ] || die "snapshot non trovato: $file"
    require_installed
    acquire_lock
    exec > >(tee -a "$LOGS/restore-$(timestamp).log") 2>&1
    db_up
    stop_app
    ricrea_schema_clone
    importa_nel_clone "$file"
    cmd_migrate
    compose_active up -d --no-build api web
    cmd_verify
}
