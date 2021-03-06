## django rest demo
> `Django + logger + Swagger APi docs`

### role sort
{
"base": all
"service": ["install-python","systemconf","supervisord","openssl","jre"],
"sort": 1
}

{
"business": base
"service": ["mysql","redis","rcdb","elasticsearch","zookeeper"],
"sort": 10
}

{
"business": rcx
"service": ["rcx-management","fastdfs","rcx-fileserver","rcx-server","tproxy-rcx-server"],
"sort": 101
}

{
"business": rce
"service": ["rce-server","rce-moments","rce-slp2p",],
"sort": 201
}

{
"business": rtc
"service": ["rtc","openresty","sealrtc-server","sealrtc-web"],
"sort": 301
}

{
"business": record
"service": ["record",],
"sort": 301
}

## scan dir for `requirements.txt`
```
# pipreqs ./ --force --encoding=utf8
```

### celery 
```
$ celery -B -A door worker --concurrency=3 -l info
```

### ansible BUG
在`/Users/shuke/opt/anaconda3/envs/Door/lib/python3.7/site-packages/ansible/plugins/connection/ssh.py`文件584行处修改
```python
if self._play_context.verbosity and self._play_context.verbosity > 3:
    b_command.append(b'-vvv')
```
在`/Users/shuke/opt/anaconda3/envs/Door/lib/python3.7/site-packages/ansible/executor/playbook_executor.py` 152行修改如下
```python
if "syntax" in context.CLIARGS.keys():
    continue
```

### 项目目录结构
```
.
├── door
│   ├── __init__.py
│   ├── celery.py      # celery配置文件
│   ├── settings.py    # 项目配置文件
│   ├── urls.py
│   └── wsgi.py
├── Makefile            # 编译构建时使用
├── README.md           # Readme
├── apps
│   ├── __init__.py
│   ├── account         # 账号model
│   ├── core            # core代码
│   ├── dashboard       # dashboard模块
│   ├── deploy          # 部署模块
│   ├── host            # 主机相关模块
│   ├── middleware      # 中间件
│   └── playbook        # ansible playbook
├── clean.sh            # 打包使用脚本
├── config              # 配置相关模块
│   ├── __init__.py
│   ├── config.yaml     # 项目区分环境配置文件
│   └── vars.yaml       # ansible全局配置及各业务线配置参数
├── control.sh          # 服务操作脚本
├── manage.py
├── requirements.txt
├── run.sh              # 服务启停脚本
├── scripts
│   ├── delete_hidden_file.py
│   ├── install-redis.sh # install redis 脚本
│   ├── redis_6380       # redis脚本
│   ├── shutdown.sh      # service 停止脚本
│   └── ssh-login.sh
└── utils
    ├── HandleExcel.py   # 处理excel脚本
    ├── HandlerLogs.py  
    ├── HandlerVars.py
    ├── __init__.py
    ├── ansible_api_v2.py
    ├── ansible_cmdb_api.py  # ansible cmdb api
```

## uwsgi service crontrol
1. start
```
# uwsgi --ini uwsgi.ini
```
2. reload
```
# uwsgi --reload uwsgi/uwsgi.pid
```
3. connect and read
```
# uwsgi --connect-and-read uwsgi/uwsgi.status
```
4. stop
```
# kill -INT `cat uwsgi/uwsgi.pid`
# or for convenience...
# uwsgi --stop uwsgi/uwsgi.pid
```

## gunicorn

1. 启动`gunicorn`
```
# gunicorn  -c gunicorn.conf.py --worker-class=eventlet door.wsgi:application
```
2. 查找`masterpid`
```
# pstree -ap | grep gunicorn
```
3. 重启`gunicorn`任务
```
# kill -HUP $(cat var/gunicorn.pid)
```
4. 退出`gunicorn`任务
```
# kill -9 $(cat var/gunicorn.pid)
```
⚠️: 启动方式可以采用`gunicorn`或者`uwsgi`两种方式，该项目采用`gunicorn`方式启动
