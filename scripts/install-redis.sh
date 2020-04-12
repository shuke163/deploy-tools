#!/usr/bin/env bash

set -e

REDIS_TAR_PKG="./libs/redis.tar.gz"
REDIS_CONF_PATH="/etc/redis"
REDIS_CONF="${REDIS_CONF_PATH}/6380.conf"
REDIS_INIT_SCRIPTS="/etc/init.d/redis_6380"
DEST_PATH="/usr/local/src"

function init_redis_conf() {
    [[ ! -d ${REDIS_CONF_PATH} ]] && mkdir -pv ${REDIS_CONF_PATH}
    if [[ ! -f ${REDIS_CONF} ]]; then
        cat <<-EOF >${REDIS_CONF}
bind 127.0.0.1
protected-mode yes
port 6380
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize yes
supervised no
pidfile /var/run/redis_6380.pid
loglevel notice
logfile "/tmp/redis_6380.log"
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /tmp
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
requirepass RongCloud
appendonly no
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
activerehashing yes
client-output-buffer-limit normal 0 0 0
hz 10
EOF
    fi
}

function install_redis() {

    [[ ! -d "/usr/local/src/redis" ]] && tar zxf ${REDIS_TAR_PKG} -C ${DEST_PATH}
    [[ ! -L "/usr/local/bin/redis-server" ]] && ln -sv ${DEST_PATH}/redis/redis-server /usr/local/bin/redis-server
    [[ ! -L "/usr/local/bin/redis-cli" ]] && ln -sv ${DEST_PATH}/redis/redis-cli /usr/local/bin/redis-cli

    if [[ ! -f ${REDIS_INIT_SCRIPTS} ]]; then
        mv scripts/redis_6380 ${REDIS_INIT_SCRIPTS} && chmod +x ${REDIS_INIT_SCRIPTS}
    fi
}

function start() {
    if [[ -f "/var/run/redis_6380.pid" ]]; then
        ${REDIS_INIT_SCRIPTS} stop
        ${REDIS_INIT_SCRIPTS} start
    else
        ${REDIS_INIT_SCRIPTS} start
    fi
}

function main() {
    init_redis_conf
    install_redis
    start
}

main
