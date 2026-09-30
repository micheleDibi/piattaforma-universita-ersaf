#!/usr/bin/env bash
# 27-edunews24.sh - uscita HTTPS dell'API verso EduNews24, attiva per difetto
# (USCITA_EDUNEWS24 assente, vuota o si in shared/compose.env; no la spegne).
#
# deploy/compose.edunews24.yml collega l'API a un bridge dedicato con uscita
# verso Internet. Le regole installate qui lo limitano a HTTPS (443/tcp) verso
# indirizzi pubblici e al DNS verso i nameserver dell'host; LAN, indirizzi
# riservati e servizi dell'host restano bloccati. Solo IPv4: l'overlay
# dichiara enable_ipv6: false.
#
# Ordine voluto, diverso da 26-notifiche.sh: l'overlay si copia in shared/
# solo dopo che l'unita' del firewall e' ripartita senza errori, e compose_rel
# (00-lib.sh) collega la rete solo se quella copia esiste. Overlay assente o
# su un altro bridge, o regole non applicate, non fermano mai il deploy: la
# rete resta scollegata e un avviso lo dice.

# Nameserver IPv4 non loopback che Docker passa al DNS dei container, uno per
# riga: quelli del resolv.conf dell'host, oppure quelli di systemd-resolved
# quando l'host ha come unico nameserver lo stub locale 127.0.0.53.
edunews24_nameserver() {  # [resolv.conf dell'host] [resolv.conf di systemd-resolved]
    local file="${1:-/etc/resolv.conf}" resolved="${2:-/run/systemd/resolve/resolv.conf}" tutti
    [ -r "$file" ] || return 0
    tutti="$(awk '$1 == "nameserver" { printf "%s ", $2 }' "$file")"
    if [ "$tutti" = "127.0.0.53 " ]; then
        [ -r "$resolved" ] || return 0
        file="$resolved"
    fi
    awk '$1 == "nameserver" && $2 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/ {
        split($2, o, ".")
        if (o[1] + 0 != 127 && o[1] + 0 <= 255 && o[2] + 0 <= 255 && o[3] + 0 <= 255 && o[4] + 0 <= 255) print $2
    }' "$file" | sort -u
}

# Testo dello script del firewall, su stdout: prepara_edunews24 lo installa e
# i test lo eseguono con un iptables finto. Gli argomenti facoltativi dello
# script generato passano a edunews24_nameserver (servono solo ai test).
edunews24_script_firewall() {
    printf '%s\n' '#!/usr/bin/env bash' \
        '# Generato da deploy/remote/27-edunews24.sh a ogni deploy: non modificare a mano.' \
        'set -Eeuo pipefail'
    declare -f edunews24_nameserver
    cat <<'EOT'
BRIDGE=br-uni-edu24
CATENA=ERSAF-UNI-EDU24
# Solo catena e bridge di questo progetto; nessuna modifica alle regole altrui.
iptables -w -N DOCKER-USER 2>/dev/null || true
# Cancello: finche' la catena non e' completa il bridge non esce. Se lo script
# si interrompe il cancello resta, e l'uscita resta chiusa.
iptables -w -I DOCKER-USER 1 -i "$BRIDGE" -j REJECT
# Senza il salto da FORWARD a DOCKER-USER (per esempio con il backend nftables
# di Docker) le regole non avrebbero effetto: l'unita' fallisce.
if ! iptables -w -C FORWARD -j DOCKER-USER 2>/dev/null; then
    echo "FORWARD non passa da DOCKER-USER: regole EduNews24 non applicabili" >&2
    exit 1
fi
iptables -w -N "$CATENA" 2>/dev/null || true
iptables -w -F "$CATENA"
iptables -w -A "$CATENA" -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN
# DNS verso i nameserver dell'host, prima dei blocchi: prima di Docker 28 le
# query verso quelli non di loopback partono dal container; dalla 28 partono
# dall'host e queste eccezioni restano innocue.
for ns in $(edunews24_nameserver "$@"); do
    iptables -w -A "$CATENA" -d "$ns/32" -p udp --dport 53 -j RETURN
    iptables -w -A "$CATENA" -d "$ns/32" -p tcp --dport 53 -j RETURN
done
for rete in 0.0.0.0/8 10.0.0.0/8 100.64.0.0/10 127.0.0.0/8 169.254.0.0/16 172.16.0.0/12 \
        192.0.0.0/24 192.168.0.0/16 198.18.0.0/15 224.0.0.0/4 240.0.0.0/4; do
    iptables -w -A "$CATENA" -d "$rete" -j REJECT
done
iptables -w -A "$CATENA" -p tcp --dport 443 -j RETURN
iptables -w -A "$CATENA" -j REJECT
iptables -w -C DOCKER-USER -i "$BRIDGE" -j "$CATENA" 2>/dev/null ||
    iptables -w -I DOCKER-USER 2 -i "$BRIDGE" -j "$CATENA"
# Le connessioni ai servizi dell'host attraversano INPUT, non DOCKER-USER.
iptables -w -C INPUT -i "$BRIDGE" -m conntrack --ctstate NEW -j REJECT 2>/dev/null ||
    iptables -w -I INPUT 1 -i "$BRIDGE" -m conntrack --ctstate NEW -j REJECT
# Catena completa: via il cancello, compresi quelli rimasti da avvii interrotti.
while iptables -w -D DOCKER-USER -i "$BRIDGE" -j REJECT 2>/dev/null; do :; done
EOT
}

# prepara_edunews24: chiamata da cmd_deploy (70-deploy.sh) dopo prepara_notifiche,
# con ACTIVE_ID uguale alla release nuova; con l'uscita spenta non fa nulla.
# Con NOTIFICHE_REALI=si installa e copia comunque: compose_rel non collega la
# rete, ma spegnendo le notifiche la trova gia' protetta. Con gli SMS reali e
# senza NOTIFICHE_REALI=si non installa nulla e toglie la copia.
prepara_edunews24() {
    uscita_edunews24_attiva || return 0
    local overlay="$RELEASES/$ACTIVE_ID/deploy/compose.edunews24.yml"
    local copia="$SHARED/compose.edunews24.yml"
    local script=/usr/local/sbin/ersaf-universita-edunews24-firewall
    local unit=ersaf-universita-edunews24-firewall.service
    # SMS_BACKEND=skebby in api.env senza NOTIFICHE_REALI=si: dalla 443 del
    # bridge partirebbero gli SMS reali. compose_rel gia' non collega la rete;
    # qui si toglie anche la copia, invece di lasciare quella di un deploy
    # precedente: e' la forma piu' conservativa, perche' la rete non si
    # ricollega con una semplice modifica di api.env seguita da start, ne' con
    # gli script di una versione precedente a questo controllo, ma solo con un
    # nuovo deploy, che ripete la verifica. Regole esistenti non toccate:
    # valgono solo per il bridge. Nessun die: il deploy prosegue.
    if [ "$(compose_env_get NOTIFICHE_REALI)" != si ] && sms_reali_in_api_env; then
        rm -f "$copia"
        avviso_sms_edunews24
        log "EduNews24: regole non aggiornate e copia in shared/ rimossa, per gli SMS reali senza NOTIFICHE_REALI=si"
        return 0
    fi
    if [ ! -f "$overlay" ]; then
        warn "uscita EduNews24 attiva (USCITA_EDUNEWS24 assente, vuota o si) ma la release $ACTIVE_ID non contiene deploy/compose.edunews24.yml: regole e copia in shared/ restano come sono"
        return 0
    fi
    # Al primo deploy cmd_release non vede l'overlay (la copia in shared/ non
    # esiste ancora): lo si valida qui, prima di installare e copiare.
    RELEASE_TAG="$ACTIVE_ID" RELEASE_DIR="$RELEASES/$ACTIVE_ID" docker compose \
        -p "$PROJECT" --project-directory "$BASE" --env-file "$SHARED/compose.env" \
        -f "$RELEASES/$ACTIVE_ID/deploy/compose.yml" -f "$overlay" config --quiet \
        || die "deploy/compose.edunews24.yml della release non valido"
    # Le regole vengono da questi script, l'overlay dalla release, che con -Ref
    # puo' essere di un'altra versione, e compose_rel preferisce l'overlay della
    # release alla copia: con un bridge diverso l'API uscirebbe senza regole.
    # Stessa reazione delle regole non applicate; regole esistenti non toccate.
    if ! edunews24_overlay_sul_bridge "$overlay"; then
        rm -f "$copia"
        warn "deploy/compose.edunews24.yml della release non crea il bridge filtrato dalle regole di questi script: l'API resta senza rete EduNews24"
        return 0
    fi
    # Elenco vuoto: con soli IPv6, o senza nameserver (Docker ricade su resolver
    # pubblici), prima della 28 il DNS del container resta bloccato. Con soli
    # nameserver di loopback Docker li interroga dall'host: avviso innocuo.
    if [ -z "$(edunews24_nameserver)" ]; then
        warn "nessun nameserver IPv4 non loopback sull'host: con Docker precedente alla 28 l'API potrebbe non risolvere i nomi"
    fi
    edunews24_script_firewall > "$script.nuovo"
    chmod 750 "$script.nuovo"
    mv -f "$script.nuovo" "$script"
    cat > "/etc/systemd/system/$unit" <<EOT
[Unit]
Description=Uscita HTTPS verso EduNews24 del collaudo Universita ERSAF
Requires=docker.service
After=docker.service
PartOf=docker.service

[Service]
Type=oneshot
ExecStart=$script
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT
    if ! { systemctl daemon-reload && systemctl enable "$unit" >/dev/null && systemctl restart "$unit"; }; then
        # Senza regole la rete non deve collegarsi: compose_rel guarda la copia.
        rm -f "$copia"
        warn "regole EduNews24 non applicate (journalctl -u $unit): l'API resta senza rete EduNews24"
        return 0
    fi
    cp "$overlay" "$copia"
    chmod 600 "$copia"
    if [ "$(compose_env_get NOTIFICHE_REALI)" = si ]; then
        log "EduNews24: regole installate; con NOTIFICHE_REALI=si l'API esce dal bridge delle notifiche e la rete EduNews24 resta scollegata"
    else
        log "EduNews24: uscita HTTPS attiva sul bridge dedicato, LAN e host bloccati"
    fi
}

# Vero se l'overlay crea proprio il bridge filtrato dallo script del firewall
# di questo bundle. Il nome si legge dallo script generato, per tenerlo scritto
# in un posto solo; una forma diversa da quella di deploy/compose.edunews24.yml
# (per esempio il valore fra apici) conta come bridge diverso.
edunews24_overlay_sul_bridge() {  # <overlay>
    local bridge
    bridge="$(edunews24_script_firewall | sed -n 's/^BRIDGE=//p')"
    [ -n "$bridge" ] || return 1
    grep -Eq "^[[:space:]]+com\.docker\.network\.bridge\.name:[[:space:]]+${bridge}[[:space:]]*\$" "$1"
}
