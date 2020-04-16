#!/usr/bin/env bash

set +e
set -o noglob
shopt -s extglob

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

export PATH=/opt/local/bin:/opt/local/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/miniconda3/bin:/opt/python2/bin:/opt/mysql/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin
export LANG=en_US.UTF-8

CURRENT_PATH=$(
    cd $(dirname $0)
    pwd
)

APP_NAME="door"
PLATFORM=$(uname)
PYTHON_PATH=/opt/miniconda3

export ${PLATFORM}

item=0

function help() {
    echo "Usage: bash $0 8099 /opt/packages.tar.gz"
}

if [[ $# -gt 3 ]]; then
    help
    exit 127
elif [[ $# -lt 2 ]]; then
    help
    exit 127
elif [[ $# -eq 2 ]]; then
    APP_PORT=${1}
    RESOURCE_PATH=${2}
else
    APP_PORT=8099
fi

case ${PLATFORM} in
    Darwin)
        export PYTHON_PATH=/usr/local/Cellar/miniconda3/envs/door
        sed -i ""  "s/^bind.*$/bind = \'0.0.0.0:${APP_PORT}\'/" gunicorn.conf.py
        ;;
    Linux)
        export PYTHON_PATH=${PYTHON_PATH}
        sed -i "s/^bind.*$/bind = \'0.0.0.0:${APP_PORT}\'/" gunicorn.conf.py
        ;;
    *)
        export PYTHON_PATH=${PYTHON_PATH}
        ;;
esac

# notary is not enabled by default
with_notary=$false
# clair is not enabled by default
with_clair=$false

function stop() {
    source ${CURRENT_PATH}/scripts/shutdown.sh >> ${CURRENT_PATH}/logs/run.log 2>&1 &
    spid=$!
    echo "Shutdown app pid=${spid}"
    wait ${spid} 
}

function unzip_resource() {
    if [[ ! -f ${RESOURCE_PATH} ]]; then
        help
        exit 127
        echo -e "\\033[1;31m[ERROR] ${RESOURCE_PATH} Not Found!\\033[0;39m"
    else
        tar zxf ${RESOURCE_PATH} -C ${CURRENT_PATH}/apps && chown -R root.root ${CURRENT_PATH}
        if [[ $? -ne 0 ]]; then
              exit 127
        fi
    fi
}

function redis() {
    if [[ ! -f ${REDIS_CONF} ]]; then
        source ${CURRENT_PATH}/scripts/install-redis.sh >> ${CURRENT_PATH}/logs/run.log 2>&1 &
        cpid=$!
        echo "Install redis pid=${cpid}"
        sleep 3
        wait ${cpid}
#       main
    fi
}

function set_python() {
    USER_ENV="/${USER}/.bashrc"
    if [[ -d "${PYTHON_PATH}" ]]; then
        rm -rf ${PYTHON_PATH}
        tar -zxf ${CURRENT_PATH}/libs/miniconda3.tar.gz -C /opt >/dev/null 2>&1
        if [[ $? -eq 0 ]]; then
            info "${PYTHON_PATH} reinstall success!"
        fi
    else
        tar -zxf ${CURRENT_PATH}/libs/miniconda3.tar.gz -C /opt >/dev/null 2>&1
        info "${PYTHON_PATH} install success!"
    fi
    if [[ -f "${USER_ENV}" ]]; then
        sed -i "/LANG.*UTF-8$/d" ${USER_ENV}
        sed -i "/PATH.*python/d" ${USER_ENV}
        sed -i "/PATH.*miniconda3/d" ${USER_ENV}
        sed -i "/PATH.*HISTTIMEFORMAT/d" ${USER_ENV}
        sed -i "/PATH.*HISTFILESIZE/d" ${USER_ENV}
        echo -e "export HISTTIMEFORMAT=\"%Y-%m-%d %H:%M:%S \"" >>${USER_ENV}
        echo -e "export HISTFILESIZE=10000" >>${USER_ENV}
        echo -e "export LANG=en_US.UTF-8\nexport PATH=${PYTHON_PATH}/bin:\$PATH" >>${USER_ENV}
        export PATH=${PYTHON_PATH}/bin:$PATH
        source ${USER_ENV}
    fi
    export PATH=$PATH:${PYTHON_PATH}/bin
    ${PYTHON_PATH}/bin/python -V
}

function start_app() {

    if [[ -d "${CURRENT_PATH}/logs" ]]; then
        rm -fr "${CURRENT_PATH}/logs"
        mkdir "${CURRENT_PATH}/logs"
    else
        mkdir "${CURRENT_PATH}/logs"
    fi
 
    cd ${CURRENT_PATH} && rm -f celerybeat-schedule*
    [[ -d "${CURRENT_PATH}/logs" ]] && rm -fr "${CURRENT_PATH}/logs" && mkdir "${CURRENT_PATH}/logs"
    [[ -f "${CURRENT_PATH}/db.sqlite3" ]] && rm -f "${CURRENT_PATH}/db.sqlite3"
    [[ -d "${CURRENT_PATH}/apps/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/__pychche__"
    [[ -d "${CURRENT_PATH}/apps/account/migrations" ]] && rm -fr "${CURRENT_PATH}/apps/account/migrations"
    [[ -d "${CURRENT_PATH}/apps/account/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/account/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/deploy/migrations" ]] && rm -fr "${CURRENT_PATH}/apps/deploy/migrations"
    [[ -d "${CURRENT_PATH}/apps/deploy/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/deploy/__pycache__"
    [[ -d "${CURRENT_PATH}/apps/host/migrations" ]] && rm -fr "${CURRENT_PATH}/apps/host/migrations"
    [[ -d "${CURRENT_PATH}/apps/host/__pycache__" ]] && rm -fr "${CURRENT_PATH}/apps/host/__pycache__"
    
    ${PYTHON_PATH}/bin/python manage.py makemigrations deploy >> ${CURRENT_PATH}/logs/db.log 2>&1 &
    sleep 3
    ${PYTHON_PATH}/bin/python manage.py makemigrations host >> ${CURRENT_PATH}/logs/db.log 2>&1 &
    sleep 3
    ${PYTHON_PATH}/bin/python manage.py makemigrations account >> ${CURRENT_PATH}/logs/db.log 2>&1 &
    sleep 3
    ${PYTHON_PATH}/bin/python manage.py migrate >> ${CURRENT_PATH}/logs/db.log 2>&1 &
    sleep 3
    
    # start app service
    ${PYTHON_PATH}/bin/gunicorn  -c gunicorn.conf.py --worker-class=eventlet ${APP_NAME}.wsgi:application
    sleep 5
    # nohup ${PYTHON_PATH}/bin/python manage.py runserver 0.0.0.0:${APP_PORT} >> ${CURRENT_PATH}/logs/run.log 2>&1 &

    case ${PLATFORM} in 
        Darwin)
            local port=$(lsof -i:${APP_PORT} | awk '{print $9}' | uniq)
            ;;
        Linux)
            local port=$(ss -ntlp | grep ${APP_PORT} | awk '{print $4}' | awk -F: '{print $2}')
            ;;
        *)
            local port=$(ss -ntlp | grep ${APP_PORT} | awk '{print $4}' | awk -F: '{print $2}')
            ;;
    esac

    if [[ -n ${port} ]]; then
        echo -e "\\033[1;32m[INFO] App already started and port is: ${APP_PORT}\\033[0;39m"
    else
        echo -e "\\033[1;31m[ERROR] App not started!\\033[0;39m"
    fi
}

function start_celery() {
    nohup ${PYTHON_PATH}/bin/celery -B -A door worker --concurrency=4  -l info >${CURRENT_PATH}/logs/celery.log 2>&1 &
    pids=$(ps -ef | grep "celery" | grep -v grep | awk '{print $2}')
    if [ "x${pids}" != "x" ]; then
        echo -e "\\033[1;32m[INFO] celery start success!\\033[0;39m"
    fi
}

function status() {
    case ${PLATFORM} in 
        Darwin)
            local port=$(lsof -i:${APP_PORT} | awk '{print $2}')
            ;;
        Linux)
            local port=$(ss -ntlp | grep ${APP_PORT} | awk '{print $4}' | awk -F: '{print $2}')
            ;;
        *)
            local port=$(ss -ntlp | grep ${APP_PORT} | awk '{print $4}' | awk -F: '{print $2}')
            ;;
    esac
    if [[ -n ${port} ]]; then
        echo -e "\\033[1;32m[INFO] URL: http://0.0.0.0:${APP_PORT}\\033[0;39m"
    else
        echo -e "\\033[1;31m[Failed]\\033[0;39m"
    fi
}

function start_on_mac() {
    stop
    sleep 3

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

function start_on_linux() {
    unzip_resource
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

function init_deploy() {
    h1 "Deploy System V0.1"

    case ${PLATFORM} in 
        Darwin)
            start_on_mac
            ;;
        Linux)
            start_on_linux
            ;;
        *)
            echo -e "\\033[1;31m[ERROR] Unsupported operating system types!\\033[0;39m"
		    exit 127
            ;;
    esac
}

init_deploy
