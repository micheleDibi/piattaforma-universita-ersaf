#!/usr/bin/env bash
# 90-main.sh - dispatcher. Deve restare l'ultimo file del bundle: quando bash
# arriva qui ha gia' letto tutte le funzioni dallo stdin, e </dev/null impedisce
# ai comandi figli di consumare cio' che resta del flusso.

main() {
    local comando="${1:-}"
    shift || true
    case "$comando" in
        preflight)    cmd_preflight "$@";;
        install)      cmd_install "$@";;
        source-check) cmd_source_check;;
        deploy)       cmd_deploy "$@";;
        build)        require_installed; acquire_lock; cmd_preflight --deploy; cmd_release "$@";;
        clone)        cmd_clone "$@";;
        migrate)      require_installed; acquire_lock; db_up; cmd_migrate;;
        backup)       cmd_backup;;
        restore)      cmd_restore "$@";;
        expose)       cmd_esponi "$@";;
        unexpose)     cmd_disesponi;;
        verify)       require_installed; cmd_verify;;
        rollback)     require_installed; acquire_lock; cmd_rollback;;
        status)       cmd_status;;
        logs)         cmd_logs "$@";;
        stop)         cmd_stop;;
        start)        cmd_start;;
        *) die "comando sconosciuto: '$comando'";;
    esac
}

main "$@" </dev/null
