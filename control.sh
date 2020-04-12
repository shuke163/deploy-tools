#!/usr/bin/env bash

set +e
set -o noglob

# Set Colors
bold=$(tput bold)
underline=$(tput sgr 0 1)
reset=$(tput sgr0)

red=$(tput setaf 1)
green=$(tput setaf 76)
white=$(tput setaf 7)
tan=$(tput setaf 202)
blue=$(tput setaf 25)

# Headers and Logging
underline() {
    printf "${underline}${bold}%s${reset}\n" "$@"
}
h1() {
    printf "\n${underline}${bold}${blue}%s${reset}\n" "$@"
}
h2() {
    printf "\n${underline}${bold}${white}%s${reset}\n" "$@"
}
debug() {
    printf "${white}%s${reset}\n" "$@"
}
info() {
    printf "${white}➜ %s${reset}\n" "$@"
}
success() {
    printf "${green}✔ %s${reset}\n" "$@"
}
error() {
    printf "${red}✖ %s${reset}\n" "$@"
}
warn() {
    printf "${tan}➜ %s${reset}\n" "$@"
}
bold() {
    printf "${bold}%s${reset}\n" "$@"
}
note() {
    printf "\n${underline}${bold}${blue}Note:${reset} ${blue}%s${reset}\n" "$@"
}

CURRENT_PATH=$(
    cd $(dirname $0)
    pwd
)
PYTHON_PATH=/opt/python3

item=0

function help() {
    echo "Usage: bash $0 8099"
}

if [[ $# -gt 1 ]]; then
    help
    exit 127
elif [[ $# -eq 1 ]]; then
    APP_PORT=$1
else
    APP_PORT=8099
fi

# notary is not enabled by default
with_notary=$false
# clair is not enabled by default
with_clair=$false

function stop() {
    source ${CURRENT_PATH}/scripts/shutdown.sh
}

function redis() {
    if [[ ! -f ${REDIS_CONF} ]]; then
        source ${CURRENT_PATH}/scripts/install-redis.sh
        main
    fi
}

function set_python() {
    USER_ENV="/${USER}/.bashrc"
    if [[ -d "${PYTHON_PATH}" ]]; then
        rm -rf ${PYTHON_PATH} && tar -zxf ${CURRENT_PATH}/packages/python3.tar.gz -C /opt >/dev/null 2>&1
        if [[ $? -eq 0 ]]; then
            info "${PYTHON_PATH} reinstall success!"
        fi
    else
        tar -zxf ${CURRENT_PATH}/packages/python3.tar.gz -C /opt >/dev/null 2>&1
        info "${PYTHON_PATH} install success!"
    fi
#    if [[ -L /usr/bin/python ]]; then
#        rm -f /usr/bin/python && ln -s ${PYTHON_PATH}/bin/python /usr/bin/python
#    fi
    if [[ -f "${USER_ENV}" ]]; then
        sed -i "/LANG.*UTF-8$/d" ${USER_ENV}
        sed -i "/PATH.*python/d" ${USER_ENV}
        echo -e "export LANG=en_US.UTF-8\nexport PATH=${PYTHON_PATH}/bin:\$PATH" >>${USER_ENV}
        export PATH=${PYTHON_PATH}/bin:$PATH
        source ${USER_ENV}
    fi
    ${PYTHON_PATH}/bin/python -V
}

function start_app() {
    [[ ! -d ${CURRENT_PATH}/logs ]] && mkdir logs
    #    nohup /opt/python3/bin/python ${CURRENT_PATH}/run.py >/tmp/app.log 2>&1 &
    nohup python manage.py makemigrations >> ${CURRENT_PATH}/logs/app.log 2>&1 &
    nohup python manage.py migrate >> ${CURRENT_PATH}/logs/app.log 2>&1 &
    nohup python manage.py runserver 8099 >> ${CURRENT_PATH}/logs/app.log 2>&1 &

#    nohup ${PYTHON_PATH}/bin/flask run --host=0.0.0.0 -p ${APP_PORT} >${CURRENT_PATH}/logs/app.log 2>&1 &
    sleep 3

    port=$(ss -ntlp | grep ${APP_PORT} | awk '{print $4}' | awk -F: '{print $2}')
    if [[ -n ${port} ]]; then
        echo -e "\\033[1;32m[INFO] App already started and port is: ${port}\\033[0;39m"
    else
        echo -e "\\033[1;31m[ERROR] App not started!\\033[0;39m"
    fi
}

function start_celery() {
    nohup celery -B -A Door worker --concurrency=3 -l info >${CURRENT_PATH}/logs/celery.log 2>&1 &
    pids=$(ps -ef | grep "app.celery" | grep -v grep | awk '{print $2}')
    if [ "x${pids}" != "x" ]; then
        echo -e "\\033[1;32m[INFO] celery start success!\\033[0;39m"
    fi
}
    
function status() {
    port=$(ss -ntlp | grep ${APP_PORT} | awk '{print $4}' | awk -F: '{print $2}')
    if [[ -n ${port} ]]; then
        echo -e "\\033[1;32m[INFO] URL: http://0.0.0.0:${APP_PORT}\\033[0;39m"
    else
        echo -e "\\033[1;31m[Failed]\\033[0;39m"
    fi
}

function init_deploy() {
    h1 "Deploy System V0.1"
    export LANG=en_US.UTF-8
    export FLASK_APP=app
    export FLASK_ENV=development
    export FLASK_RUN_PORT=${APP_PORT}

    stop
    sleep 3

    h2 "[Step $item]: Install redis ..."
    let item+=1
    redis

    h2 "[Step $item]: Set python runtime ..."
    let item+=1
    set_python

    h2 "[Step $item]: Start App Service ..."
    let item+=1
    start_app

    h2 "[Step $item]: Start Celery Service ..."
    let item+=1
    start_celery

    h2 "[Step $item]: App Info ..."
    let item+=1
    status
}

init_deploy
