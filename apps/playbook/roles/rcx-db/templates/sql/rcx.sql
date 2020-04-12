use rcx_db;
drop table if exists `CC_AppRegistration`;

CREATE TABLE `CC_AppRegistration` (
  `appId` int(8) NOT NULL COMMENT 'appId',
  `secureKey` varchar(64) NOT NULL DEFAULT '' COMMENT '加密key',
  `appSecret` varchar(64) NOT NULL DEFAULT '' COMMENT '应用密钥',
  `state` enum('normal','auditing','testing','blocked','deleted') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'testing' COMMENT '应用状态',
  `createdTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `appName` varchar(64) DEFAULT NULL,
  `cluster` varchar(20) not null default 'prod' comment '集群标识，sandbox/prod',
  `bizDbAddress` varchar(128)  null ,

  PRIMARY KEY (`appId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='应用注册表 基础信息表';


drop table if exists `CC_AppKvExt`;


CREATE TABLE `CC_AppKvExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_AppKvExt_1` (`appId`,`bizType`,`attName`),
  KEY `IX_CC_AppKvExt_2` (`appId`,`bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用配置表';


drop table if exists `CC_ConfigKvExt`;


CREATE TABLE `CC_ConfigKvExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `bizType` int(11) NOT NULL DEFAULT 0,
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_ConfigKvExt_1` (`bizType`,`attName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用配置表';


drop table if exists `CC_AppKsetExt`;


CREATE TABLE `CC_AppKsetExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attItemHash` int(11) not null comment '属性key hash',
  `attItem` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_AppKsetExt_1` (`appId`,`bizType`,`attName`,`attItem`),
  KEY `IX_CC_AppKsetExt_2` (`appId`,`bizType`,`attNameHash` , `attItemHash` )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用配置扩展表';


drop table if exists `CC_AppKmapExt`;

CREATE TABLE `CC_AppKmapExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attKeyHash` int(11) not null comment '属性key hash',
  `attKey` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key值',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_AppKmapExt_1` (`appId`,`bizType`,`attName`,`attKey`),
  KEY `IX_CC_AppKmapExt_appId` (`appId`,`bizType`,`attNameHash`,`attKeyHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用配置扩展字典表';

drop table if exists `CC_ConfigKmapExt`;

CREATE TABLE `CC_ConfigKmapExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attKey` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key值',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_ConfigKmapExt_1` (`attName`,`attKey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用配置扩展字典表';

drop table if exists `CC_AppIdentifier`;

CREATE TABLE `CC_AppIdentifier` (
  `appKey` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `appIdentifier` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `upTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`appKey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


drop table if exists `CC_AppList`;

CREATE TABLE `CC_AppList` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) DEFAULT NULL,
  `appName` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '应用名',
  `createTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `APPID` (`appId`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;




drop table if exists `CC_DirtyWords`;

CREATE TABLE `CC_DirtyWords` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `word` varchar(256) CHARACTER SET utf8mb4 NOT NULL,
  `cleanWord` varchar(256) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '要替换的内容',
  `type` tinyint(1) DEFAULT '1' COMMENT '敏感词类型 1高危 0敏感',
  `appId` int(11) DEFAULT NULL,
  `createTime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `wordHash` (`word`(191))
) ENGINE=InnoDB AUTO_INCREMENT=1925 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


drop table if exists `CC_IosPushInfo`;



CREATE TABLE `CC_IosPushInfo` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) DEFAULT NULL,
  `iosPackageName` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `iosCer` blob,
  `iosCerPw` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `iosPushSound` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `hidBadgePackage` tinyint(1) NOT NULL,
  `voipCer` blob,
  `voipCerPw` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `createTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `proxyPushSwitch` tinyint(1) DEFAULT '0' COMMENT 'push 代理开关',
  `proxyPushConfig` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'push 代理配置{proxyPushUrl,proxyPushKey,proxyPushSecret}',
  PRIMARY KEY (`id`),
  KEY `IDX_APPID` (`appId`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='IOS push 配置';


drop table if exists `CC_SpecificPush`;


CREATE TABLE `CC_SpecificPush` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) DEFAULT NULL,
  `packageName` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '包名',
  `pushType` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '开通推送类型 MI HUAWEI GCM ……',
  `pushParam` varchar(1024) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '一种push参数,json格式',
  `createTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updateTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `pushKey` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '推送对应的key',
  `packageNameHash` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `packageName` (`packageName`,`appId`,`pushType`),
  KEY `IDX_APPID` (`appId`)
) ENGINE=InnoDB AUTO_INCREMENT=856 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



drop table if exists `CC_TemplatesArgs`;

CREATE TABLE `CC_TemplatesArgs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `grouping` varchar(20) DEFAULT NULL,
  `packet` varchar(20) DEFAULT NULL,
  `appId` bigint(20) NOT NULL,
  `rckey` varchar(128) NOT NULL,
  `rcval` varchar(1000) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;




drop table if exists `CC_TransmitPublicTemplates`;

CREATE TABLE `CC_TransmitPublicTemplates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `grouping` varchar(20) DEFAULT NULL,
  `packet` varchar(20) DEFAULT NULL COMMENT '模板分组',
  `alias` varchar(20) DEFAULT NULL COMMENT '模板别名',
  `templateUp` text NOT NULL COMMENT '上行模版',
  `contentDown` text COMMENT '下行内容模板',
  `channelDown` text COMMENT '下行渠道',
  `objNameDown` text COMMENT '下行消息类型',
  `targetIdDown` text,
  `fromIdDown` text,
  `contentErrorDown` text COMMENT '下行内容模板',
  `channelErrorDown` text COMMENT '下行渠道',
  `objNameErrorDown` text COMMENT '下行消息类型',
  `targetIdErrorDown` text,
  `fromIdErrorDown` text,
  `cacheParam` varchar(100) DEFAULT NULL COMMENT '缓存参数json',
  `doSendDown` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '根据返回内容决定是否继续下发',
  `desc` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4;


drop table if exists `CC_TransmitTemplate`;

CREATE TABLE `CC_TransmitTemplate` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL,
  `grouping` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '模板分组',
  `packet` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '子分组',
  `channelType` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '会话类型',
  `objectName` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '消息类型',
  `fromId` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `targetId` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `onLineSts` varchar(1) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '在线状态',
  `ruleOrder` smallint(6) NOT NULL COMMENT '规则排序',
  `matching` int(4) NOT NULL COMMENT '需要做规则匹配的项目 四位2进制表示',
  `upTemplate` text COLLATE utf8mb4_unicode_ci COMMENT '发给客户的http模板',
  `publicTemplateId` bigint(20) DEFAULT NULL COMMENT '上行公共模板ID',
  `channelDown` text COLLATE utf8mb4_unicode_ci COMMENT '下行渠道',
  `contentDown` text COLLATE utf8mb4_unicode_ci COMMENT '下行内容模板',
  `objNameDown` text COLLATE utf8mb4_unicode_ci COMMENT '下行消息类型',
  `targetIdDown` text COLLATE utf8mb4_unicode_ci,
  `fromIdDown` text COLLATE utf8mb4_unicode_ci,
  `contentErrorDown` text COLLATE utf8mb4_unicode_ci COMMENT '下行内容模板',
  `channelErrorDown` text COLLATE utf8mb4_unicode_ci COMMENT '下行渠道',
  `objNameErrorDown` text COLLATE utf8mb4_unicode_ci COMMENT '下行消息类型',
  `targetIdErrorDown` text COLLATE utf8mb4_unicode_ci,
  `fromIdErrorDown` text COLLATE utf8mb4_unicode_ci,
  `publicOrPrivate` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否用到公共模板',
  `isSyncMsg` tinyint(1) NOT NULL DEFAULT '0' COMMENT '标记此路由是否为同步路由\r\n阻塞消息发送\r\n默认非阻塞',
  `cacheParam` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '缓存参数json',
  `doSendDown` text COLLATE utf8mb4_unicode_ci COMMENT '根据返回内容决定是否继续下发',
  `rcdesc` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `createTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updatedTime` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_APPID` (`appId`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


drop table if exists `CC_DbCluster`;

CREATE TABLE `CC_DbCluster` (
  `id` int(11) NOT NULL COMMENT 'app集群id',
  `clusterName` varchar(64) NOT NULL DEFAULT '' COMMENT '集群名称',
  `moduleName` enum('Default','User','Group','MC','Chrm','Discussion') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Default' COMMENT '业务模块名称',
  `dbCount` int(11) NOT NULL COMMENT '数据库数量',
  `dbPrefix` varchar(64) NOT NULL COMMENT '数据库前缀',
  `updatedTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_CC_DbCluster_clusterName_moduleName` (`clusterName`,`moduleName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据库集群信息表';


drop table if exists `CC_DbInstance`;

CREATE TABLE `CC_DbInstance` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `clusterId` int(11) NOT NULL COMMENT '数据库集群id',
  `instanceIndex` int(11) NOT NULL COMMENT '主机在本模块的序号',
  `name` varchar(64) NOT NULL DEFAULT '' COMMENT '数据库实例名称',
  `host` varchar(64) NOT NULL COMMENT '主机ip',
  `port` int(11) NOT NULL COMMENT '主机端口',
  `connStr` varchar(2048) NOT NULL COMMENT '连接串',
  `updatedTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_CC_DbInstance_clusterId_instanceIndex` (`clusterId`,`instanceIndex`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COMMENT='数据库实例信息表';




-- 用户封禁, 单库，单表
use clusterCommon;
drop table if exists `CC_BlockUserInfo`;

CREATE TABLE `CC_BlockUserInfo` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `userId` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `appId` int(11) NOT NULL,
  `blockEndTime` bigint(20) NOT NULL,
  `createTime` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `permanentBlock` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appId` (`appId`,`userId`) USING BTREE,
  KEY `blockEndTime` (`blockEndTime`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户禁用.';

-- push 封禁
drop table if exists `CC_BlockUserPush`;

CREATE TABLE `CC_BlockUserPush` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userId` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'blockerId',
  `hashId` int(11) NOT NULL COMMENT 'hash值',
  `blockeeId` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '屏蔽的对象ID',
  `pushMsgType` int(11) NOT NULL COMMENT '1:二人,2:多人会话,3:Group消息,4:聊天室,5:客服客户端,6:系统通知,7:mc,8:mp',
  `createTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `appId` int(11) NOT NULL DEFAULT '100000',
  PRIMARY KEY (`id`) COMMENT '主键',
  UNIQUE KEY `UNIQUE_userId_blockeeId_pushMsgType` (`userId`,`blockeeId`,`pushMsgType`),
  KEY `IX_CC_BlockUserPush_hashId` (`hashId`)
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='屏蔽推送信息表';



drop table if exists `CC_ComKvExt`;

CREATE TABLE `CC_ComKvExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_ComKvExt_1` (`appId`,`bizType`,`attName`),
  KEY `IX_CC_ComKvExt_2` (`appId` ,`bizType`, `attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Appkv表';



drop table if exists `CC_ComKsetExt`;

CREATE TABLE `CC_ComKsetExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attItemHash` int(11) not null comment '属性key hash',
  `attItem` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `CC_ComKsetExt_1` (`appId`, `bizType`,`attName`,`attItem`),
  KEY `IX_CC_ComKsetExt_2` (`appId`, `bizType`,`attNameHash`,`attItemHash`),
  KEY `IX_CC_ComKsetExt_3` (`appId`, `bizType`,`attNameHash`),
  KEY `IX_CC_ComKsetExt_4` (`appId`, `bizType`,`attItemHash`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Appkset列表';


drop table if exists `CC_ComKmapExt`;

CREATE TABLE `CC_ComKmapExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attKeyHash` int(11) not null comment '属性key hash',
  `attKey` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `CC_ComKmapExt_1` (`appId`, `bizType`,`attName`,`attKey`),
  KEY `CC_ComKmapExt_2` (`appId`, `bizType`,`attNameHash`,`attKeyHash`),
  KEY `CC_ComKmapExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='kmap表';

use rcx_db_0;
-- USER

drop table if exists `CC_UserKvExt`;

CREATE TABLE `CC_UserKvExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_UserKvExt_1` (`appId`,`bizType`,`attName`),
  KEY `IX_CC_UserKvExt_2` (`appId` ,`bizType`, `attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户kv表';




drop table if exists `CC_UserKsetExt`;

CREATE TABLE `CC_UserKsetExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attItemHash` int(11) not null comment '属性key hash',
  `attItem` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_UserKsetExt_1` (`appId`, `bizType`,`attName`,`attItem`),
  KEY `IX_CC_UserKsetExt_2` (`appId`, `bizType`,`attNameHash`,`attItemHash`),
   KEY `IX_CC_UserKsetExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户属性列表';


drop table if exists `CC_UserKmapExt`;

CREATE TABLE `CC_UserKmapExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attKeyHash` int(11) not null comment '属性key hash',
  `attKey` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_UserKmapExt_1` (`appId`, `bizType`,`attName`,`attKey`),
  KEY `IX_CC_UserKmapExt_2` (`appId`, `bizType`,`attNameHash`,`attKeyHash`),
  KEY `IX_CC_UserKmapExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户配置表';



drop table if exists `CC_UserKmapBlobExt`;

CREATE TABLE `CC_UserKmapBlobExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attNameHash` int(11) not null comment '属性名字hash',
  `attKey` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `attKeyHash` int(11) not null comment '属性key hash' ,
  `attValue`  mediumblob   NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',
  `bizType` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_UserKmapExt_appId_attName_attKey` (`appId`,`attName`,`attKey`, `bizType`),
  key `IX_CC_UserKmapBlobExt_1` (`appId`,`bizType`,`attNameHash`,`attKeyHash` ),
  key `IX_CC_UserKmapBlobExt_2` (`appId`,`bizType`,`attNameHash`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户blob数据表';

--  GROUP


drop table if exists `CC_GroupKvExt`;

CREATE TABLE `CC_GroupKvExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_GroupKvExt_1` (`appId`,`bizType`,`attName`),
  KEY `IX_CC_GroupKvExt_2` (`appId` ,`bizType`, `attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群kv表';




drop table if exists `CC_GroupKsetExt`;

CREATE TABLE `CC_GroupKsetExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attItemHash` int(11) not null comment '属性key hash',
  `attItem` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_GroupKsetExt_1` (`appId`, `bizType`,`attName`,`attItem`),
  KEY `IX_CC_GroupKsetExt_2` (`appId`, `bizType`,`attNameHash`,`attItemHash`),
   KEY `IX_CC_GroupKsetExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群属性列表';


drop table if exists `CC_GroupKmapExt`;

CREATE TABLE `CC_GroupKmapExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attKeyHash` int(11) not null comment '属性key hash',
  `attKey` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_GroupKmapExt_1` (`appId`, `bizType`,`attName`,`attKey`),
  KEY `IX_CC_GroupKmapExt_2` (`appId`, `bizType`,`attNameHash`,`attKeyHash`),
  KEY `IX_CC_GroupKmapExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='群配置表';



-- MC

drop table if exists `CC_MCKvExt`;

CREATE TABLE `CC_MCKvExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_MCKvExt_1` (`appId`,`bizType`,`attName`),
  KEY `IX_CC_MCKvExt_2` (`appId` ,`bizType`, `attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MCkv表';




drop table if exists `CC_MCKsetExt`;

CREATE TABLE `CC_MCKsetExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attItemHash` int(11) not null comment '属性key hash',
  `attItem` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_MCKsetExt_1` (`appId`, `bizType`,`attName`,`attItem`),
  KEY `IX_CC_MCKsetExt_2` (`appId`, `bizType`,`attNameHash`,`attItemHash`),
   KEY `IX_CC_MCKsetExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MC属性列表';


drop table if exists `CC_MCKmapExt`;

CREATE TABLE `CC_MCKmapExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attKeyHash` int(11) not null comment '属性key hash',
  `attKey` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_MCKmapExt_1` (`appId`, `bizType`,`attName`,`attKey`),
  KEY `IX_CC_MCKmapExt_2` (`appId`, `bizType`,`attNameHash`,`attKeyHash`),
  KEY `IX_CC_MCKmapExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MC配置表';




-- CHATROOM

drop table if exists `CC_ChrmKvExt`;

CREATE TABLE `CC_ChrmKvExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_ChrmKvExt_1` (`appId`,`bizType`,`attName`),
  KEY `IX_CC_ChrmKvExt_2` (`appId` ,`bizType`, `attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chrm kv表';




drop table if exists `CC_ChrmKsetExt`;

CREATE TABLE `CC_ChrmKsetExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attItemHash` int(11) not null comment '属性key hash',
  `attItem` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_ChrmKsetExt_1` (`appId`, `bizType`,`attName`,`attItem`),
  KEY `IX_CC_ChrmKsetExt_2` (`appId`, `bizType`,`attNameHash`,`attItemHash`),
   KEY `IX_CC_ChrmKsetExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chrm属性列表';


drop table if exists `CC_ChrmKmapExt`;

CREATE TABLE `CC_ChrmKmapExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attKeyHash` int(11) not null comment '属性key hash',
  `attKey` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_ChrmKmapExt_1` (`appId`, `bizType`,`attName`,`attKey`),
  KEY `IX_CC_ChrmKmapExt_2` (`appId`, `bizType`,`attNameHash`,`attKeyHash`),
  KEY `IX_CC_ChrmKmapExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Chrm配置表';




-- discussion 讨论组


drop table if exists `CC_DiscussionKvExt`;

CREATE TABLE `CC_DiscussionKvExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_DiscussionKvExt_1` (`appId`,`bizType`,`attName`),
  KEY `IX_CC_DiscussionKvExt_2` (`appId` ,`bizType`, `attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Discussion kv表';




drop table if exists `CC_DiscussionKsetExt`;

CREATE TABLE `CC_DiscussionKsetExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attItemHash` int(11) not null comment '属性key hash',
  `attItem` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_DiscussionKsetExt_1` (`appId`, `bizType`,`attName`,`attItem`),
  KEY `IX_CC_DiscussionKsetExt_2` (`appId`, `bizType`,`attNameHash`,`attItemHash`),
   KEY `IX_CC_DiscussionKsetExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Discussion 属性列表';


drop table if exists `CC_DiscussionKmapExt`;

CREATE TABLE `CC_DiscussionKmapExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attKeyHash` int(11) not null comment '属性key hash',
  `attKey` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_DiscussionKmapExt_1` (`appId`, `bizType`,`attName`,`attKey`),
  KEY `IX_CC_DiscussionKmapExt_2` (`appId`, `bizType`,`attNameHash`,`attKeyHash`),
  KEY `IX_CC_DiscussionKmapExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Discussion 配置表';


-- 按appId 分区

drop table if exists `CC_AppUserPushTable`;

CREATE TABLE `CC_AppUserPushTable` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `userId` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '用户id',
  `userIdHash` int(11) NOT NULL COMMENT '用户id哈希code',
  `canPush` tinyint(1) NOT NULL COMMENT '能否push',
  `deviceId` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '设备Id/push的token',
  `deviceIdHash` int(11) DEFAULT NULL COMMENT '设备id哈希code',
  `deviceType` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT 'Android' COMMENT '设备类型',
  `packageName` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '包名',
  `updatedTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'update的时间',
  `flag` tinyint(1) unsigned zerofill NOT NULL COMMENT '状态位，该记录是否有效。1：有效，0：无效',
  `appId` int(11) NOT NULL DEFAULT '100000',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_AppUserPushTable_userId` (`userIdHash`,`userId`) USING BTREE,
  KEY `IX_CC_AppUserPushTable_deviceIdHash` (`deviceIdHash`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;




drop table if exists `CC_AppKvExt`;

CREATE TABLE `CC_AppKvExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_AppKvExt_1` (`appId`,`bizType`,`attName`),
  KEY `IX_CC_AppKvExt_2` (`appId` ,`bizType`, `attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Appkv表';



drop table if exists `CC_AppKsetExt`;

CREATE TABLE `CC_AppKsetExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attItemHash` int(11) not null comment '属性key hash',
  `attItem` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_AppKsetExt_1` (`appId`, `bizType`,`attName`,`attItem`),
  KEY `IX_CC_AppKsetExt_2` (`appId`, `bizType`,`attNameHash`,`attItemHash`),
  KEY `IX_CC_AppKsetExt_3` (`appId`, `bizType`,`attNameHash`),
  KEY `IX_CC_AppKsetExt_4` (`appId`, `bizType`,`attItemHash`)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Appkset列表';


drop table if exists `CC_AppKmapExt`;

CREATE TABLE `CC_AppKmapExt` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `appId` bigint(20) NOT NULL DEFAULT 0,
  `bizType` int(11) NOT NULL DEFAULT 0,
  `attNameHash` int(11) not null comment '属性名字hash',
  `attName` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性名字',
  `attKeyHash` int(11) not null comment '属性key hash',
  `attKey` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性key',
  `attValue` varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '' COMMENT '属性说明',

  PRIMARY KEY (`id`),
  UNIQUE KEY `CC_AppKmapExt_1` (`appId`, `bizType`,`attName`,`attKey`),
  KEY `CC_AppKmapExt_2` (`appId`, `bizType`,`attNameHash`,`attKeyHash`),
  KEY `CC_AppKmapExt_3` (`appId`, `bizType`,`attNameHash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='kmap表';

use management;
-- 管理后台user表
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `status` tinyint(1) DEFAULT NULL,
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `ix_auth_user_user_name` (`user_name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for action_log
-- ----------------------------
DROP TABLE IF EXISTS `action_log`;
CREATE TABLE `action_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `app_key` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` varchar(1024) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=695 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for package_info
-- ----------------------------
DROP TABLE IF EXISTS `package_info`;
CREATE TABLE `package_info` (
  `identify_id` int(11) NOT NULL AUTO_INCREMENT,
  `status` tinyint(1) DEFAULT NULL,
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `identify_name` varchar(255) NOT NULL,
  `appkey` varchar(50) NOT NULL,
  `android_package_name` varchar(255) DEFAULT NULL,
  `ios_package_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`identify_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8;



