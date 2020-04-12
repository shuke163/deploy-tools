#!/usr/bin/env bash

function stop_celery() {
    celery_pid=$(ps -ef | grep "/opt/miniconda3/bin/celery" | grep -v grep | awk '{print $2}')
    if [[ ! -z "${celery_pid}" ]]; then
        for pid in ${celery_pid[@]}; do
            kill ${pid}
            echo "[INFO] stop celery pid: ${pid}"
        done
    fi
}

function stop_app() {
    pids=$(ps aux | grep "/opt/miniconda3/bin/python" | grep -v grep | awk '{print $2}')
    if [ "x${pids}" != "x" ]; then
        echo "[INFO] Kill the app: "
        echo "[INFO] ${pids}"
        kill -9 ${pids}
    else
        echo "[INFO] App not running!"
    fi
}

function shutdown() {
    stop_celery
    stop_app
}
shutdown
