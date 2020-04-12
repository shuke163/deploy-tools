/* {{ ansible_managed }} */

use management;

INSERT INTO `users` VALUES ('1', null, '2018-11-29 09:49:15', '2018-12-17 09:58:08', 'admin', 'JP0R7aizG7XTa9XARIOzbA==', '1', null);


use comcloud_x;

DELETE FROM CC_ConfigKvExt WHERE attName in ('apiThreadPool','fileStorageUrl','license');

INSERT INTO CC_ConfigKvExt(attName, attValue, bizType) VALUES ('apiThreadPool', '{"threadPoolConfig":[{"name":"common","coreSize":4},{"name":"Actors_Pools","coreSize":8},{"name":"dataPersistence","coreSize":8}]}', '0');
INSERT INTO CC_ConfigKvExt(attName, attValue, bizType) VALUES ('fileStorageUrl', 'http://{{ mysql_host }}:{{ rcx.FILE_PORT }}/getToken?namespace=message', '0');
INSERT INTO CC_ConfigKvExt(attName, attValue, bizType) VALUES ('license', '{{ license }}', '0');

/* 删除配置信息*/
DELETE FROM CC_PublicIp WHERE type in ("cmp","android_push");

{% for host in groups['rcx_server'] %}
INSERT INTO CC_PublicIp (type, nodeName, publicIps, updatedTime) VALUES ('cmp', '{{ hostvars[host]["private_ip"] }}', '{"publicIps":[{"ip": {{ hostvars[host]["public_ip"] }},"rmtpPort":{{ rcx.CMP_NET_PORT }},"order":1,"wsPort":{{ rcx.WS_LISTEN_PORT }},"wssPort":{{ rcx.WS_LISTEN_PORT }}}]}', now()),( 'android_push', '{{ hostvars[host]["private_ip"] }}', '{"publicIps":[{"ip": {{ hostvars[host]["public_ip"] }},"order":1,"port":{{ rcx.PUSH_LISTEN_PORT }}}]}', now());
{% endfor %}

INSERT INTO CC_ConfigKvExt(attName,attValue,bizType,updatedTime,description) VALUES ('chatroom-redis', '{"list":[{"timeout":3000,"host":"{{ redis_host }}","port":{{ redis_port }},"password":"{{ redis_password }}","name":"name1","weight":1}],"maxIdle":8,"minIdle":0,"maxActive":8,"maxWait":-1,"whenExhaustedAction":1,"testOnBorrow":false,"testOnReturn":false,"testWhileIdle":true,"timeBetweenEvictionRunsMillis":30000,"numTestsPerEvictionRun":-1,"minEvictableIdleTimeMillis":60000,"softMinEvictableIdleTimeMillis":-1,"lifo":true}', 0, now(), '');

