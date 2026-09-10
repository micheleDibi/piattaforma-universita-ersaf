#!/usr/bin/env bash
# 30-release.sh - estrazione dell'archivio e build delle immagini.

normalizza_fine_riga() {
    # Il checkout Windows puo' avere CRLF: Dockerfile, script e SQL vanno in LF.
    find "$1" -type f \( -name '*.sh' -o -name 'Dockerfile' -o -name '*.conf' \
        -o -name '*.yml' -o -name '.dockerignore' -o -name '*.sql' -o -name '*.env*' \) \
        -exec sed -i 's/\r$//' {} +
}

scrivi_release_info() {  # <dir> <id> <sha> <dirty>
    cat > "$1/RELEASE_INFO" <<EOT
release=$2
git_sha=$3
albero_modificato=$4
data=$(date -Is)
operatore=${SUDO_USER:-$(id -un)}@$(hostname)
EOT
}

# cmd_release <archivio> <id> <sha> <dirty>
cmd_release() {
    local archivio="$1" id="$2" sha="$3" dirty="$4" dir
    dir="$RELEASES/$id"
    [ -f "$archivio" ] || die "archivio non trovato: $archivio"
    [ -e "$dir" ] && die "la release $id esiste gia'"
    mkdir -p "$dir"
    tar -xzf "$archivio" -C "$dir"
    rm -f "$archivio"
    [ -f "$dir/deploy/compose.yml" ] || die "archivio incompleto: manca deploy/compose.yml"
    normalizza_fine_riga "$dir"
    scrivi_release_info "$dir" "$id" "$sha" "$dirty"
    log "release $id estratta (git $sha, albero modificato: $dirty)"
    compose_rel "$id" config --quiet || die "compose.yml della release non valido"
    log "build delle immagini api e web (alcuni minuti alla prima esecuzione)"
    compose_rel "$id" build --pull api web
    log "immagini pronte: ersaf-universita/api:$id, ersaf-universita/web:$id"
}

# Conserva le ultime KEEP_RELEASES release oltre a quelle attiva e precedente.
cmd_prune() {
    local attuale precedente id i=0
    attuale="$(compose_env_get RELEASE_TAG)"
    precedente="$(cat "$SHARED/previous_release" 2>/dev/null || true)"
    for id in $(ls -1 "$RELEASES" 2>/dev/null | sort -r); do
        [ "$id" = "$attuale" ] || [ "$id" = "$precedente" ] && continue
        i=$((i + 1))
        [ "$i" -le "$KEEP_RELEASES" ] && continue
        log "rimuovo release vecchia $id e le sue immagini"
        rm -rf "$RELEASES/$id"
        docker image rm "ersaf-universita/api:$id" "ersaf-universita/web:$id" >/dev/null 2>&1 || true
    done
}
