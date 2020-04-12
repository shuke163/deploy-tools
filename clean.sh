#!/usr/bin/env bash

CURRENT_PATH=$(
    cd $(dirname $0)
    pwd
)

function clean() {
    cd ${CURRENT_PATH} && rm -f celerybeat-schedule*
    [[ -d "${CURRENT_PATH}/apps/playbook/inventory" ]] && rm -fr "${CURRENT_PATH}/apps/playbook/inventory"
    [[ -f "${CURRENT_PATH}/db.sqlite3" ]] && rm -rf "${CURRENT_PATH}/db.sqlite3"
    [[ -d "${CURRENT_PATH}/apps/packages" ]] && rm -rf "${CURRENT_PATH}/apps/packages"
    [[ -d "${CURRENT_PATH}/logs" ]] && rm -fr "${CURRENT_PATH}/logs" && mkdir "${CURRENT_PATH}/logs"
    [[ -f "${CURRENT_PATH}/db.sqlite3" ]] && rm -f "${CURRENT_PATH}/db.sqlite3"
    [[ -d "${CURRENT_PATH}/apps/__pycache__" ]] && rm -fr ${CURRENT_PATH}/apps/__pycache__/
    [[ -d "${CURRENT_PATH}/apps/account/migrations" ]] && rm -fr "${CURRENT_PATH}/apps/account/migrations"
    [[ -d "${CURRENT_PATH}/apps/account/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/account/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/deploy/migrations" ]] && rm -fr "${CURRENT_PATH}/apps/deploy/migrations"
    [[ -d "${CURRENT_PATH}/apps/deploy/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/deploy/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/host/migrations" ]] && rm -fr "${CURRENT_PATH}/apps/host/migrations"
    [[ -d "${CURRENT_PATH}/apps/host/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/host/__pycache__"
    [[ -d "${CURRENT_PATH}/utils/__pycache__" ]] && rm -fr "${CURRENT_PATH}/utils/__pycache__"
    [[ -d "${CURRENT_PATH}/uploads" ]] && rm -fr "${CURRENT_PATH}/uploads"
    [[ -d "${CURRENT_PATH}/Door/__pycache__" ]] && rm -fr "${CURRENT_PATH}/Door/__pycache__"
    [[ -f "${CURRENT_PATH}/config/ports.json" ]] && rm -fr "${CURRENT_PATH}/config/ports.json"
    [[ -d "${CURRENT_PATH}/docs" ]] && rm -fr "${CURRENT_PATH}/docs"
    [[ -d "${CURRENT_PATH}/config/__pycache__" ]] && rm -fr "${CURRENT_PATH}/config/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/core/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/core/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/dashbord/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/dashbord/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/deploy/task/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/deploy/task/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/deploy/views/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/deploy/views/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/deploy/conf/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/deploy/conf/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/host/task/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/host/task/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/host/views/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/host/views/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/dashboard/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/dashboard/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/middleware/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/middleware/__pycache__"
}

clean
