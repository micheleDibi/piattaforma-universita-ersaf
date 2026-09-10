#!/usr/bin/env bash
# 25-esposizione.sh - pubblicazione del collaudo su un dominio servito da un
# reverse proxy esterno (Nginx Proxy Manager su un altro host della LAN).
#
# La porta del web resta chiusa a tutta la rete tranne l'host del proxy: il
# binding sull'indirizzo LAN e' accompagnato da due regole DOCKER-USER
# (ACCEPT dal proxy, DROP per tutti gli altri), lo stesso schema gia' usato dal
# servizio realtime presente sulla macchina. Una unit systemd le riapplica al
# riavvio, perche' iptables non le conserva.
#
# Nessuna regola preesistente viene modificata: le due regole sono aggiunte in
# coda e riguardano soltanto la porta di questo stack.

SCRIPT_FIREWALL=/usr/local/sbin/ersaf-universita-firewall
UNIT_FIREWALL=ersaf-universita-firewall.service

esposizione_get() { sed -n "s/^$1=//p" "$SHARED/esposizione.env" 2>/dev/null | tail -n 1; }

# Sostituisce una chiave in un file di configurazione conservandone i permessi.
env_file_set() {
    local file="$1" chiave="$2" valore="$3" tmp
    tmp="$(mktemp)"
    { grep -v "^${chiave}=" "$file" || true; printf '%s=%s\n' "$chiave" "$valore"; } > "$tmp"
    cat "$tmp" > "$file"
    rm -f "$tmp"
}

ip_lan_verso() {
    ip -4 route get "$1" 2>/dev/null | awk '{for (i = 1; i < NF; i++) if ($i == "src") { print $(i + 1); exit }}'
}

scrivi_script_firewall() {  # <ip_server> <ip_proxy> <porta>
    cat > "$SCRIPT_FIREWALL" <<EOT
#!/usr/bin/env bash
# Generato da deploy/remote/25-esposizione.sh. Ammette il solo reverse proxy
# sulla porta del collaudo Universita e nega tutto il resto della rete.
set -Eeuo pipefail
iptables -w -N DOCKER-USER 2>/dev/null || true
iptables -w -C DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || \\
    iptables -w -I DOCKER-USER 1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -w -C DOCKER-USER -p tcp -s $2/32 \\
    -m conntrack --ctorigdst $1 --ctorigdstport $3 -j ACCEPT 2>/dev/null || \\
    iptables -w -A DOCKER-USER -p tcp -s $2/32 \\
        -m conntrack --ctorigdst $1 --ctorigdstport $3 -j ACCEPT
iptables -w -C DOCKER-USER -p tcp \\
    -m conntrack --ctorigdst $1 --ctorigdstport $3 -j DROP 2>/dev/null || \\
    iptables -w -A DOCKER-USER -p tcp \\
        -m conntrack --ctorigdst $1 --ctorigdstport $3 -j DROP
EOT
    chmod 750 "$SCRIPT_FIREWALL"
}

scrivi_unit_firewall() {
    cat > "/etc/systemd/system/$UNIT_FIREWALL" <<EOT
[Unit]
Description=Firewall del collaudo Universita ERSAF (accesso dal solo reverse proxy)
Requires=docker.service
After=docker.service
PartOf=docker.service

[Service]
Type=oneshot
ExecStart=$SCRIPT_FIREWALL
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT
    systemctl daemon-reload
    systemctl enable --now "$UNIT_FIREWALL" >/dev/null
    log "regole firewall attive e riapplicate al riavvio ($UNIT_FIREWALL)"
}

rimuovi_regole_firewall() {  # <ip_server> <porta>
    local s="$1" p="$2"
    while iptables -w -C DOCKER-USER -p tcp -m conntrack --ctorigdst "$s" --ctorigdstport "$p" -j DROP 2>/dev/null; do
        iptables -w -D DOCKER-USER -p tcp -m conntrack --ctorigdst "$s" --ctorigdstport "$p" -j DROP
    done
    local proxy; proxy="$(esposizione_get PROXY_IP)"
    while [ -n "$proxy" ] && iptables -w -C DOCKER-USER -p tcp -s "$proxy/32" -m conntrack --ctorigdst "$s" --ctorigdstport "$p" -j ACCEPT 2>/dev/null; do
        iptables -w -D DOCKER-USER -p tcp -s "$proxy/32" -m conntrack --ctorigdst "$s" --ctorigdstport "$p" -j ACCEPT
    done
}

aggiorna_url_api() {  # <url_pubblico>
    local porta; porta="$(web_port)"
    env_file_set "$SHARED/api.env" FRONTEND_BASE_URL "$1"
    env_file_set "$SHARED/api.env" CORS_ORIGINS "$1,http://localhost:$porta"
    chmod 600 "$SHARED/api.env"
    log "URL pubblico dell'applicazione: $1 (il tunnel su localhost resta valido)"
}

verifica_esposizione() {  # <ip_server> <porta>
    ss -ltnH "sport = :$2" | grep -q "$1" || die "la porta $2 non risulta in ascolto su $1"
    iptables -S DOCKER-USER | grep -q "ctorigdstport $2 -j DROP" || die "regola DROP assente per la porta $2"
    curl -fsS -m 10 "http://$1:$2/healthz" >/dev/null || die "il web non risponde su http://$1:$2/healthz"
    log "verifica: porta in ascolto su $1:$2, regole attive, web raggiungibile dal server"
}

# cmd_esponi <dominio> <ip_proxy>
cmd_esponi() {
    local dominio="${1:-}" proxy="${2:-}" porta ip_server
    [ -n "$dominio" ] && [ -n "$proxy" ] || die "uso: esponi <dominio> <ip_del_reverse_proxy>"
    require_installed
    porta="$(web_port)"
    ip_server="$(ip_lan_verso "$proxy")"
    [ -n "$ip_server" ] || die "non riesco a determinare l'indirizzo LAN verso $proxy"
    log "pubblicazione di https://$dominio tramite il proxy $proxy verso $ip_server:$porta"
    ( umask 077; printf 'DOMINIO=%s\nPROXY_IP=%s\nWEB_LAN_IP=%s\nPORTA=%s\n' \
        "$dominio" "$proxy" "$ip_server" "$porta" > "$SHARED/esposizione.env" )
    compose_env_set ESPOSIZIONE si
    compose_env_set WEB_LAN_IP "$ip_server"
    scrivi_script_firewall "$ip_server" "$proxy" "$porta"
    scrivi_unit_firewall
    aggiorna_url_api "https://$dominio"
    compose_active up -d --no-build --force-recreate web api
    wait_healthy api 150
    wait_healthy web 90
    verifica_esposizione "$ip_server" "$porta"
    log "sul reverse proxy configurare: $dominio -> http://$ip_server:$porta"
}

# cmd_disesponi: torna al solo tunnel SSH.
cmd_disesponi() {
    require_installed
    local porta ip_server
    porta="$(web_port)"
    ip_server="$(esposizione_get WEB_LAN_IP)"
    [ -n "$ip_server" ] || die "esposizione non attiva"
    systemctl disable --now "$UNIT_FIREWALL" >/dev/null 2>&1 || true
    rm -f "/etc/systemd/system/$UNIT_FIREWALL" "$SCRIPT_FIREWALL"
    systemctl daemon-reload
    rimuovi_regole_firewall "$ip_server" "$porta"
    compose_env_set ESPOSIZIONE no
    aggiorna_url_api "http://localhost:$porta"
    rm -f "$SHARED/esposizione.env"
    compose_active up -d --no-build --force-recreate web api
    wait_healthy web 90
    log "esposizione rimossa: la porta $porta torna al solo loopback"
}
