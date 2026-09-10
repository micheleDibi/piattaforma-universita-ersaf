#!/usr/bin/env bash
# 50-migrate.sh - migrazioni SQL sul solo clone, con registro delle applicate.
#
# I file db/migrations/*.sql sono idempotenti (vedi db/README.md); qui si
# applicano una sola volta e si registrano in _deploy_migrazioni, tabella di
# servizio presente solo nel clone. Prima di applicare migrazioni nuove si
# salva un backup del clone: la 009 modifica dati e i DDL MariaDB fanno
# commit implicito, quindi il ripristino affidabile e' lo snapshot.

TABELLA_MIGRAZIONI="_deploy_migrazioni"

crea_registro() {
    db_query "CREATE TABLE IF NOT EXISTS \`$TABELLA_MIGRAZIONI\` (
        nome VARCHAR(255) NOT NULL PRIMARY KEY,
        sha256 CHAR(64) NOT NULL,
        applicata_il DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci" >/dev/null
}

sha_file() { sha256sum "$1" | cut -d' ' -f1; }

# Stampa i percorsi delle migrazioni non ancora registrate, in ordine.
migrazioni_pendenti() {
    local dir="$1" registrate f nome sha riga
    registrate="$(db_query "SELECT CONCAT(nome, ' ', sha256) FROM \`$TABELLA_MIGRAZIONI\`")"
    for f in "$dir"/*.sql; do
        nome="$(basename "$f")"; sha="$(sha_file "$f")"
        riga="$(printf '%s\n' "$registrate" | grep "^$nome " || true)"
        if [ -z "$riga" ]; then printf '%s\n' "$f"; continue; fi
        [ "$riga" = "$nome $sha" ] || die "la migrazione $nome risulta gia' applicata con contenuto diverso: verificare prima di procedere"
    done
}

applica_migrazione() {  # <file>
    local nome; nome="$(basename "$1")"
    log "applico $nome"
    db_tools mariadb --defaults-extra-file="$DB_CNF" --default-character-set=utf8mb4 \
        --database="$CLONE_DB" < "$1"
    db_query "INSERT INTO \`$TABELLA_MIGRAZIONI\` (nome, sha256) VALUES ('$nome', '$(sha_file "$1")')" >/dev/null
}

# cmd_migrate: usa le migrazioni della release attiva.
cmd_migrate() {
    local dir pendenti backup f
    dir="$RELEASES/${ACTIVE_ID:-$(current_release_id)}/db/migrations"
    [ -d "$dir" ] || die "cartella migrazioni assente: $dir"
    clone_present || die "clone assente: nessuna migrazione applicabile"
    crea_registro
    pendenti="$(migrazioni_pendenti "$dir")"
    if [ -z "$pendenti" ]; then log "migrazioni: nessuna da applicare"; return 0; fi
    log "migrazioni da applicare: $(printf '%s\n' "$pendenti" | xargs -n1 basename | tr '\n' ' ')"
    backup="$(dump_clone clone-pre-migrazione)"
    log "backup pre-migrazione: $(basename "$backup")"
    for f in $pendenti; do applica_migrazione "$f"; done
    prune_files "$SNAPSHOTS/clone-pre-migrazione-*.sql.gz" "$KEEP_PRE_MIGRAZIONE"
    log "migrazioni completate"
}
