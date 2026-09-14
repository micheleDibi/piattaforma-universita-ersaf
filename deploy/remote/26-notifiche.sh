#!/usr/bin/env bash
# Uscita dei provider reali: la rete dati resta interna, il bridge notifiche
# consente soltanto HTTPS/SMTP pubblici e non accede a LAN o servizi dell'host.

prepara_notifiche() {
    [ "$(compose_env_get NOTIFICHE_REALI)" = si ] || return 0
    local script=/usr/local/sbin/ersaf-universita-notifiche-firewall
    local unit=ersaf-universita-notifiche-firewall.service
    cp "$RELEASES/$ACTIVE_ID/deploy/compose.notifiche.yml" "$SHARED/compose.notifiche.yml"
    chmod 600 "$SHARED/compose.notifiche.yml"
    cat > "$script" <<'EOT'
#!/usr/bin/env bash
set -Eeuo pipefail
# Solo catena e bridge di questo progetto; nessuna modifica alle regole altrui.
iptables -w -N ERSAF-UNI-NOTIFY 2>/dev/null || true
iptables -w -F ERSAF-UNI-NOTIFY
iptables -w -A ERSAF-UNI-NOTIFY -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN
for rete in 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16 169.254.0.0/16 127.0.0.0/8; do
    iptables -w -A ERSAF-UNI-NOTIFY -d "$rete" -j REJECT
done
iptables -w -A ERSAF-UNI-NOTIFY -p tcp -m multiport --dports 443,465,587 -j RETURN
iptables -w -A ERSAF-UNI-NOTIFY -j REJECT
iptables -w -C DOCKER-USER -i br-uni-notify -j ERSAF-UNI-NOTIFY 2>/dev/null ||
    iptables -w -I DOCKER-USER 1 -i br-uni-notify -j ERSAF-UNI-NOTIFY
# Le connessioni ai servizi dell'host attraversano INPUT, non DOCKER-USER.
iptables -w -C INPUT -i br-uni-notify -m conntrack --ctstate NEW -j REJECT 2>/dev/null ||
    iptables -w -I INPUT 1 -i br-uni-notify -m conntrack --ctstate NEW -j REJECT
EOT
    chmod 750 "$script"
    cat > "/etc/systemd/system/$unit" <<EOT
[Unit]
Description=Uscita HTTPS e SMTP del collaudo Universita ERSAF
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
    systemctl daemon-reload
    systemctl enable "$unit" >/dev/null
    systemctl restart "$unit"
    log "notifiche reali: uscita HTTPS/SMTP attiva, LAN e host bloccati sul bridge dedicato"
}
