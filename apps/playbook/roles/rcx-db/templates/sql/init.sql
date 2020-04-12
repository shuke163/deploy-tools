use rcx_db;

delete from CC_ConfigKvExt;
insert into CC_ConfigKvExt(attName, attValue, bizType) values('apiThreadPool', '{"threadPoolConfig":[{"name":"common","coreSize":4},{"name":"Actors_Pools","coreSize":8},{"name":"dataPersistence","coreSize":8}]}', '0');

insert into CC_ConfigKvExt(attName, attValue, bizType) values('fileStorageUrl', 'http://{{ mysql_host }}:{{ fileserver_port }}/getToken?namespace=message', '0');

insert into CC_ConfigKvExt(attName, attValue, bizType) values('license', '{{ license }}', '0');
insert into CC_ConfigKvExt(attName, attValue, bizType) values('runtime.threadpool.model', 'apiThreadPool', '0');
insert into CC_ConfigKvExt(attName, attValue, bizType) values('runtime.agent.rpc.port', '10001', '0');
insert into CC_ConfigKvExt(attName, attValue, bizType) values('runtime.agent.data.port', '10002', '0');
insert into CC_ConfigKvExt(attName, attValue, bizType) values('runtime.service.host', '127.0.0.1', '0');
insert into CC_ConfigKvExt(attName, attValue, bizType) values('runtime.' ||
 '.port', '8899', '0');

insert into CC_ConfigKvExt(attName, attValue, bizType) values('runtime.rmtp.port', '{{ rmtp_public_port }}', '0');
insert into CC_ConfigKvExt(attName, attValue, bizType) values('runtime.websocket.port', '{{ rmtp_ws_public_port }}', '0');
insert into CC_ConfigKvExt(attName, attValue, bizType) values('runtime.androidpush.port', '{{ apush_public_port }}', '0');
insert into CC_ConfigKvExt(attName, attValue, bizType) values('env.zookeeper.clusters', '{{ zkString }}', '0');
insert into CC_ConfigKvExt(attName, attValue, bizType) values('env.es.clusters', '{{ esString }}', '0');
select * from CC_ConfigKvExt;


delete from  CC_DbCluster where clusterName in ('sandbox','production','special');
insert into CC_DbCluster (id,clusterName,moduleName,dbCount,dbPrefix)
values ('1','prod','Default',1,'rcx_db_');
select * from CC_DbCluster;



delete from CC_DbInstance;

insert into CC_DbInstance(clusterId,instanceIndex,name,host,port,connStr)
values ('1','0','rcx-im','{{ mysql_host }}','{{ mysql_port }}','jdbcUrl=jdbc:mysql://{{ mysql_host }}:{{ mysql_port }}/db_proxy?useUnicode=true&characterEncoding=utf8&autoReconnect=true\nusername={{ mysql_user }}\npassword={{ mysql_password }}\nmaximumPoolSize=5');
select * from CC_DbInstance;


-- ----------------------------
-- Records of users
-- ----------------------------
use management;
INSERT INTO `users` VALUES ('1', null, '2018-11-29 09:49:15', '2018-12-17 09:58:08', 'admin', '+giPWTh2EC4l9bH8hPB1zQ==', '1', null);

