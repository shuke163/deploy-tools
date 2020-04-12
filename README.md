## django rest demo
> `Django + logger + Swagger APi docs`


### role 排序
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

### celery 
```
$ celery -B -A Door worker --concurrency=3 -l info
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
