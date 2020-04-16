#!/usr/bin/env bash

PLATFORM=$(uname)

function stop_celery() {
    case ${PLATFORM} in
        Darwin)
            local pids=$(ps -ef | grep celery | grep -v grep | awk '{print $2}')
            ;;
        Linux)
            local pids=$(ps -ef | grep "/opt/miniconda3/bin/celery" | grep -v grep | awk '{print $2}')
            ;;
        *)
            local pids=$(ps -ef | grep "/opt/miniconda3/bin/celery" | grep -v grep | awk '{print $2}')
            ;;
    esac
    if [[ ! -z "${pids}" ]]; then
        for pid in ${pids[@]}; do
            kill ${pid}
            echo "[INFO] stop celery pid: ${pid}"
        done
    fi
}

function stop_app() {
    case ${PLATFORM} in
        Darwin)
            local pids=$(ps -ef | grep gunicorn | grep -v grep | awk '{print $2}')
            ;;
        Linux)
            local pids=$(ps -ef | grep gunicorn | grep -v grep | awk '{print $2}')
            ;;
        *)
            local pids=$(ps -ef | grep gunicorn | grep -v grep | awk '{print $2}')
            ;;
    esac
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
