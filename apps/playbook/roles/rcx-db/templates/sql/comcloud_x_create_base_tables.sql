use comcloud_x;

-- Create syntax for TABLE 'CC_AppExtConfig'
CREATE TABLE `CC_AppExtConfig`
(
  `id`          int(11)                                  NOT NULL AUTO_INCREMENT,
  `attName`     varchar(50)                              NOT NULL COMMENT '属性名字',
  `attValue`    varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp                                NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `appId`       bigint(20)                               NOT NULL DEFAULT 0 comment 'appId',
  `description` varchar(200) COLLATE utf8mb4_unicode_ci           DEFAULT '' COMMENT '属性说明',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_AppExtConfig_appId_attName` (`appId`, `attName`),
  KEY `IX_CC_AppExtConfig_appId` (`appId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='应用注册表 信息扩展表';

-- Create syntax for TABLE 'CC_AppIdentifier'
CREATE TABLE `CC_AppIdentifier`
(
  `appKey`        varchar(32) COLLATE utf8mb4_unicode_ci  NOT NULL DEFAULT '',
  `appIdentifier` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `upTime`        timestamp                               NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`appKey`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_AppList'
CREATE TABLE `CC_AppList`
(
  `id`         int(11)    NOT NULL AUTO_INCREMENT,
  `appId`      bigint(20) NOT NULL                     DEFAULT 0 comment 'appId',
  `appName`    varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '应用名',
  `createTime` timestamp  NOT NULL                     DEFAULT current_timestamp() COMMENT '创建时间',
  `updateTime` timestamp  NOT NULL                     DEFAULT current_timestamp() COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `APPID` (`appId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_AppRegistration'
CREATE TABLE `CC_AppRegistration`
(
  `appId`       bigint(20)                                                                                                NOT NULL DEFAULT 0 comment 'appId',
  `secureKey`   varchar(64)                                                                                               NOT NULL DEFAULT '' COMMENT '加密key',
  `appSecret`   varchar(64)                                                                                               NOT NULL DEFAULT '' COMMENT '应用密钥',
  `state`       enum ('normal','auditing','testing','blocked','deleted') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'testing' COMMENT '应用状态',
  `createdTime` timestamp                                                                                                 NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `appName`     varchar(64)                                                                                                        DEFAULT NULL,
  PRIMARY KEY (`appId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='应用注册表 基础信息表';

-- Create syntax for TABLE 'CC_AppUserBlackList'
CREATE TABLE `CC_AppUserBlackList`
(
  `id`            int(11)                                NOT NULL AUTO_INCREMENT,
  `userId`        varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `userIdHash`    int(11)                                NOT NULL,
  `blackedUserId` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `appId`         bigint(20)                             NOT NULL DEFAULT 0 comment 'appId',
  `reason`        int(11)                                         DEFAULT 405,
  `createdTime`   timestamp                              NULL     DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `IX_CC_AppUserBlackList_userIdHash` (`userIdHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_BlockUserInfo'
CREATE TABLE `CC_BlockUserInfo`
(
  `id`             bigint(20)                             NOT NULL AUTO_INCREMENT,
  `userId`         varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `appId`          bigint(20)                             NOT NULL DEFAULT 0 comment 'appId',
  `blockEndTime`   bigint(20)                             NOT NULL,
  `createTime`     timestamp                              NULL     DEFAULT current_timestamp(),
  `permanentBlock` int(11)                                         DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `appId` (`appId`, `userId`) USING BTREE,
  KEY `blockEndTime` (`blockEndTime`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='用户禁用.';

-- Create syntax for TABLE 'CC_DeviceTokenMap'
CREATE TABLE `CC_DeviceTokenMap`
(
  `id`           int(11) unsigned                        NOT NULL AUTO_INCREMENT,
  `deviceId`     varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT 'RongDeviceId 根据AppId、PackageName、和Mac地址MD5获得唯一',
  `token`        varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '第三方Push Token，用来推送第三方Push',
  `pushType`     varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '第三方Push类型（MI、HY、GCM）',
  `createTime`   timestamp                               NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `updatedTime`  timestamp                               NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '更新时间',
  `deviceIdHash` int(11)                                 NOT NULL,
  `appId`        bigint(20)                              NOT NULL DEFAULT 0 comment 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_uniqueKey` (`deviceIdHash`, `appId`),
  KEY `IX_CC_deviceTokenMap_deviceIdHash` (`deviceIdHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_DirtyWords'
CREATE TABLE `CC_DirtyWords`
(
  `id`         int(10) unsigned                   NOT NULL AUTO_INCREMENT,
  `word`       varchar(256) CHARACTER SET utf8mb4 NOT NULL,
  `cleanWord`  varchar(256) CHARACTER SET utf8mb4          DEFAULT NULL COMMENT '要替换的内容',
  `type`       tinyint(1)                                  DEFAULT 1 COMMENT '敏感词类型 1高危 0敏感',
  `appId`      bigint(20)                         NOT NULL DEFAULT 0 comment 'appId',
  `createTime` timestamp                          NULL     DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `wordHash` (`word`(191))
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_GroupForbiddenMember'
CREATE TABLE `CC_GroupForbiddenMember`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT COMMENT '主键',
  `userId`      varchar(64) CHARACTER SET utf8mb4      NOT NULL COMMENT '用户id',
  `userIdHash`  int(11)                                NOT NULL COMMENT 'userId的hashcode，索引',
  `groupId`     varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群id',
  `groupIdHash` int(11)                                NOT NULL COMMENT 'groupid的hashcode,索引',
  `createTime`  timestamp                              NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `endTime`     bigint(20)                                      DEFAULT NULL COMMENT '禁言结束时间',
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 comment 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_GroupForbiddenMember_userId_groupId` (`userId`, `groupId`, `appId`),
  KEY `IX_CC_GroupForbiddenMember_groupIdHash` (`groupIdHash`),
  KEY `IX_CC_GroupForbiddenMember_userIdHash` (`userIdHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_GroupInfo'
CREATE TABLE `CC_GroupInfo`
(
  `id`            int(11)                                 NOT NULL AUTO_INCREMENT COMMENT '主键',
  `groupId`       varchar(64) COLLATE utf8mb4_unicode_ci  NOT NULL COMMENT '群id',
  `groupIdHash`   int(11)                                 NOT NULL COMMENT 'groupid的hashcode,索引',
  `name`          varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'name',
  `createTime`    timestamp                               NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `updatedTime`   timestamp                               NOT NULL DEFAULT current_timestamp(),
  `groupCapacity` smallint(6)                             NOT NULL,
  `appId`         bigint(20)                              NOT NULL DEFAULT 0 comment 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_GroupInfo_groupId` (`groupId`, `appId`),
  KEY `IX_CC_GroupInfo_groupIdHash` (`groupIdHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_GroupPerson'
CREATE TABLE `CC_GroupPerson`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT COMMENT '主键',
  `userId`      varchar(64) CHARACTER SET utf8mb4      NOT NULL COMMENT '用户id',
  `userIdHash`  int(11)                                NOT NULL COMMENT 'userid的hashcode,索引',
  `groupId`     varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '群id',
  `groupIdHash` int(11)                                NOT NULL COMMENT 'groupid的hashcode,索引',
  `createTime`  timestamp                              NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `flag`        tinyint(4)                             NOT NULL,
  `ptName`      varchar(64) COLLATE utf8mb4_unicode_ci          DEFAULT NULL COMMENT '昵称',
  `joinTime`    timestamp                              NULL     DEFAULT NULL COMMENT '加入时间',
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 comment 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_GroupPerson_userId_groupId` (`userId`, `groupId`, `appId`),
  KEY `IX_CC_GroupPerson_userIdHash` (`userIdHash`),
  KEY `IX_CC_GroupPerson_groupIdHash` (`groupIdHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_IosPushInfo'

CREATE TABLE `CC_IosPushInfo`
(
  `id`              int(8)     NOT NULL AUTO_INCREMENT,
  `appId`           bigint(20) NOT NULL                     DEFAULT 0 comment 'appId',
  `iosPackageName`  varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT ' ios 包名',
  `iosCer`          blob COMMENT ' 推送证书',
  `iosCerPw`        varchar(32) COLLATE utf8mb4_unicode_ci  DEFAULT NULL COMMENT ' 推送证书密码',
  `iosPushSound`    varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `hidBadgePackage` tinyint(1) NOT NULL,
  `voipCer`         blob COMMENT 'voip 证书',
  `voipCerPw`       varchar(32) COLLATE utf8mb4_unicode_ci  DEFAULT NULL COMMENT 'voip 证书密码',
  `createTime`      timestamp  NOT NULL                     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updateTime`      timestamp  NOT NULL                     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `proxyPushSwitch` tinyint(1)                              DEFAULT '0' COMMENT 'push 代理开关',
  `proxyPushConfig` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'push 代理配置{proxyPushUrl,proxyPushKey,proxyPushSecret}',
  PRIMARY KEY (`id`),
  KEY `IDX_APPID` (`appId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='IOS push 配置';

-- Create syntax for TABLE 'CC_MsgRelations'
CREATE TABLE `CC_MsgRelations`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `userId`      varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `userIdHash`  int(11)                                         DEFAULT NULL,
  `fromId`      varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fromIdHash`  int(11)                                         DEFAULT NULL,
  `channelType` int(11)                                NOT NULL,
  `createTime`  timestamp                              NOT NULL DEFAULT current_timestamp(),
  `sendMsgTime` bigint(11)                                      DEFAULT NULL,
  `dataHash`    char(32) COLLATE utf8mb4_unicode_ci             DEFAULT NULL COMMENT '数据hash（userId+fromId+channelType）',
  `objectName`  varchar(32) COLLATE utf8mb4_unicode_ci          DEFAULT NULL COMMENT '消息类型',
  `msgContent`  mediumblob                                      DEFAULT NULL COMMENT '最后一条消息',
  `direction`   tinyint(3)                                      DEFAULT NULL COMMENT '发送为0，接收为1',
  `sendUserId`  varchar(64) COLLATE utf8mb4_unicode_ci          DEFAULT NULL COMMENT '发送者',
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 comment 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `dataHash` (`dataHash`, `appId`),
  KEY `IX_CC_MsgRelations_userIdHash` (`userIdHash`),
  KEY `IX_CC_MsgRelations_fromIdHash` (`fromIdHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_SpecificPush'
CREATE TABLE `CC_SpecificPush`
(
  `id`              int(11)                                  NOT NULL AUTO_INCREMENT,
  `appId`           bigint(20)                               NOT NULL DEFAULT 0 COMMENT 'appId',
  `packageName`     varchar(128) COLLATE utf8mb4_unicode_ci           DEFAULT NULL COMMENT '包名',
  `pushType`        varchar(32) COLLATE utf8mb4_unicode_ci            DEFAULT NULL COMMENT '开通推送类型 MI HUAWEI GCM ……',
  `pushParam`       varchar(1024) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '一种push参数,json格式',
  `createTime`      timestamp                                NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `updateTime`      timestamp                                NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `pushKey`         varchar(255) COLLATE utf8mb4_unicode_ci  NOT NULL DEFAULT '' COMMENT '推送对应的key',
  `packageNameHash` int(11)                                           DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `packageName` (`packageName`, `appId`, `pushType`),
  KEY `IDX_APPID` (`appId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_UserDeviceMap'
CREATE TABLE `CC_UserDeviceMap`
(
  `id`           int(11) unsigned                        NOT NULL AUTO_INCREMENT,
  `deviceId`     varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT 'deviceId',
  `deviceIdHash` int(11)                                 NOT NULL,
  `packageName`  varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '第三方Push Token，用来推送第三方Push',
  `userId`       varchar(64) CHARACTER SET utf8mb4       NOT NULL COMMENT '用户id',
  `createTime`   timestamp                               NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '创建时间',
  `appId`        bigint(20)                              NOT NULL DEFAULT 0 COMMENT 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_uniqueKey` (`deviceIdHash`, `appId`),
  KEY `IX_CC_deviceTokenMap_deviceIdHash` (`deviceIdHash`),
  KEY `packageName` (`packageName`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_UserInfo'
CREATE TABLE `CC_UserInfo`
(
  `id`           int(10) unsigned NOT NULL AUTO_INCREMENT,
  `userId`       varchar(64)      NOT NULL                                    DEFAULT '',
  `userName`     varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '',
  `hashId`       int(11)          NOT NULL,
  `userPortrait` varchar(1024)                                                DEFAULT '',
  `extension`    mediumblob                                                   DEFAULT NULL,
  `updatedTime`  timestamp        NOT NULL                                    DEFAULT current_timestamp(),
  `regTime`      timestamp        NOT NULL                                    DEFAULT current_timestamp(),
  `state`        enum ('normal','locked','deleted')                           DEFAULT 'normal',
  `userAgent`    varchar(256)                                                 DEFAULT NULL COMMENT '设备信息',
  `appId`        bigint(20)       NOT NULL                                    DEFAULT 0 comment 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_UserInfo_appId_userId` (`userId`, `appId`),
  KEY `IX_CC_UserInfo_hashId_domainId` (`hashId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;


-- Create syntax for TABLE 'CC_UserPushTable'
CREATE TABLE `CC_UserPushTable`
(
  `id`           int(11) unsigned                                             NOT NULL AUTO_INCREMENT COMMENT '主键',
  `userId`       varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户id',
  `userIdHash`   int(11)                                                      NOT NULL COMMENT '用户id哈希code',
  `canPush`      tinyint(1)                                                   NOT NULL COMMENT '能否push',
  `deviceId`     varchar(255) COLLATE utf8mb4_unicode_ci                               DEFAULT NULL COMMENT '设备Id/push的token',
  `deviceIdHash` int(11)                                                               DEFAULT NULL COMMENT '设备id哈希code',
  `deviceType`   varchar(32) COLLATE utf8mb4_unicode_ci                                DEFAULT 'Android' COMMENT '设备类型',
  `packageName`  varchar(255) COLLATE utf8mb4_unicode_ci                               DEFAULT NULL COMMENT '包名',
  `updatedTime`  timestamp                                                    NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'update的时间',
  `flag`         tinyint(1) unsigned zerofill                                 NOT NULL COMMENT '状态位，该记录是否有效。1：有效，0：无效',
  `appId`        bigint(20)                                                   NOT NULL DEFAULT 0 COMMENT 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_UserPushTable_userId` (`userIdHash`, `userId`, `appId`) USING BTREE,
  KEY `IX_CC_UserPushTable_deviceIdHash` (`deviceIdHash`) USING BTREE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- Create syntax for TABLE 'CC_UserSetting'
CREATE TABLE `CC_UserSetting`
(
  `id`          int(11)      NOT NULL AUTO_INCREMENT,
  `md5v`        varchar(50)  NOT NULL,
  `userId`      varchar(64)  NOT NULL,
  `userIdHash`  int(11)      NOT NULL,
  `itemKey`     varchar(20)  NOT NULL,
  `itemValue`   varchar(200) NOT NULL,
  `itemStatus`  int(11)      NOT NULL COMMENT '1：add 2：update 3：delete',
  `itemVersion` bigint(20)   NOT NULL,
  `appId`       bigint(20)   NOT NULL DEFAULT 0 COMMENT 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `Index_md5` (`md5v`),
  KEY `Index_userIdHash_itemVersion` (`userIdHash`, `itemVersion`),
  KEY `ix_CC_UserSetting_2` (`appId`, `userIdHash`,`itemKey`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- Create syntax for TABLE 'CC_VoipTokenTable'
CREATE TABLE `CC_VoipTokenTable`
(
  `id`           int(11) unsigned NOT NULL AUTO_INCREMENT,
  `appId`        bigint(20)       NOT NULL DEFAULT 0 COMMENT 'appId',
  `deviceId`     varchar(255)              DEFAULT NULL COMMENT 'deviceId',
  `deviceIdHash` int(11)                   DEFAULT NULL COMMENT 'deviceIdCode',
  `voipToken`    varchar(255)              DEFAULT NULL COMMENT 'voipToken',
  `createTime`   timestamp        NULL     DEFAULT current_timestamp() COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_VoipTokenTable_nuiqueKey` (`appId`, `deviceIdHash`),
  KEY `IX_CC_VoipTokenTable_deviceIdCode` (`deviceIdHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;


CREATE TABLE `CC_ConfigBean`
(
  `id`            int(11)                                  NOT NULL AUTO_INCREMENT,
  `beanName`      varchar(64) COLLATE utf8mb4_unicode_ci   NOT NULL COMMENT '配置 bean 的名称',
  `propertyName`  varchar(128) COLLATE utf8mb4_unicode_ci  NOT NULL DEFAULT '' COMMENT '配置 bean 属性名称',
  `propertyValue` varchar(1024) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '配置 bean 属性值',
  `dataType`      varchar(32) COLLATE utf8mb4_unicode_ci            DEFAULT '' COMMENT '配置参数类型',
  `description`   varchar(1024) COLLATE utf8mb4_unicode_ci          DEFAULT '' COMMENT ' 说明',
  `updatedTime`   timestamp                                NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_ConfigBean_beanName_propertyName` (`beanName`, `propertyName`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='mbean 配置表';


CREATE TABLE `CC_BlockUserPush`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `userId`      varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'blockerId',
  `hashId`      int(11)                                NOT NULL COMMENT 'hash值',
  `blockeeId`   varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '屏蔽的对象ID',
  `pushMsgType` int(11)                                NOT NULL COMMENT '1:二人,2:多人会话,3:Group消息,4:聊天室,5:客服客户端,6:系统通知,7:mc,8:mp',
  `createTime`  timestamp                              NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 COMMENT 'appId',
  PRIMARY KEY (`id`) COMMENT '主键',
  UNIQUE KEY `UNIQUE_userId_blockeeId_pushMsgType` (`userId`, `blockeeId`, `pushMsgType`, `appId`),
  KEY `IX_CC_BlockUserPush_hashId` (`hashId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='屏蔽推送信息表';


CREATE TABLE `CC_TransmitTemplate`
(
  `id`                bigint(20)  NOT NULL AUTO_INCREMENT,
  `appId`             bigint(20)  NOT NULL                    DEFAULT 0 COMMENT 'appId',
  `grouping`          varchar(20) COLLATE utf8mb4_unicode_ci  DEFAULT NULL COMMENT '模板分组',
  `packet`            varchar(20) COLLATE utf8mb4_unicode_ci  DEFAULT NULL COMMENT '子分组',
  `channelType`       varchar(64) COLLATE utf8mb4_unicode_ci  DEFAULT NULL COMMENT '会话类型',
  `objectName`        varchar(64) COLLATE utf8mb4_unicode_ci  DEFAULT NULL COMMENT '消息类型',
  `fromId`            varchar(64) COLLATE utf8mb4_unicode_ci  DEFAULT NULL,
  `targetId`          varchar(64) COLLATE utf8mb4_unicode_ci  DEFAULT NULL,
  `onLineSts`         varchar(1) COLLATE utf8mb4_unicode_ci   DEFAULT NULL COMMENT '在线状态',
  `ruleOrder`         smallint(6) NOT NULL COMMENT '规则排序',
  `matching`          int(4)      NOT NULL COMMENT '需要做规则匹配的项目 四位2进制表示',
  `upTemplate`        text COLLATE utf8mb4_unicode_ci COMMENT '发给客户的http模板',
  `publicTemplateId`  bigint(20)                              DEFAULT NULL COMMENT '上行公共模板ID',
  `channelDown`       text COLLATE utf8mb4_unicode_ci COMMENT '下行渠道',
  `contentDown`       text COLLATE utf8mb4_unicode_ci COMMENT '下行内容模板',
  `objNameDown`       text COLLATE utf8mb4_unicode_ci COMMENT '下行消息类型',
  `targetIdDown`      text COLLATE utf8mb4_unicode_ci,
  `fromIdDown`        text COLLATE utf8mb4_unicode_ci,
  `contentErrorDown`  text COLLATE utf8mb4_unicode_ci COMMENT '下行内容模板',
  `channelErrorDown`  text COLLATE utf8mb4_unicode_ci COMMENT '下行渠道',
  `objNameErrorDown`  text COLLATE utf8mb4_unicode_ci COMMENT '下行消息类型',
  `targetIdErrorDown` text COLLATE utf8mb4_unicode_ci,
  `fromIdErrorDown`   text COLLATE utf8mb4_unicode_ci,
  `publicOrPrivate`   tinyint(1)  NOT NULL                    DEFAULT '0' COMMENT '是否用到公共模板',
  `isSyncMsg`         tinyint(1)  NOT NULL                    DEFAULT '0' COMMENT '标记此路由是否为同步路由\r\n阻塞消息发送\r\n默认非阻塞',
  `cacheParam`        varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '缓存参数json',
  `doSendDown`        text COLLATE utf8mb4_unicode_ci COMMENT '根据返回内容决定是否继续下发',
  `rcdesc`            varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `createTime`        timestamp   NOT NULL                    DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updatedTime`       timestamp   NULL                        DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IDX_APPID` (`appId`) USING BTREE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE `CC_TransmitPublicTemplates`
(
  `id`                int(11) NOT NULL AUTO_INCREMENT,
  `grouping`          varchar(20)  DEFAULT NULL,
  `packet`            varchar(20)  DEFAULT NULL COMMENT '模板分组',
  `alias`             varchar(20)  DEFAULT NULL COMMENT '模板别名',
  `templateUp`        text    NOT NULL COMMENT '上行模版',
  `contentDown`       text COMMENT '下行内容模板',
  `channelDown`       text COMMENT '下行渠道',
  `objNameDown`       text COMMENT '下行消息类型',
  `targetIdDown`      text,
  `fromIdDown`        text,
  `contentErrorDown`  text COMMENT '下行内容模板',
  `channelErrorDown`  text COMMENT '下行渠道',
  `objNameErrorDown`  text COMMENT '下行消息类型',
  `targetIdErrorDown` text,
  `fromIdErrorDown`   text,
  `cacheParam`        varchar(100) DEFAULT NULL COMMENT '缓存参数json',
  `doSendDown`        text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci COMMENT '根据返回内容决定是否继续下发',
  `desc`              varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE `CC_TemplatesArgs`
(
  `id`       int(11)       NOT NULL AUTO_INCREMENT,
  `grouping` varchar(20)            DEFAULT NULL,
  `packet`   varchar(20)            DEFAULT NULL,
  `appId`    bigint(20)    NOT NULL DEFAULT 0 COMMENT 'appId',
  `rckey`    varchar(128)  NOT NULL,
  `rcval`    varchar(1000) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8;

CREATE TABLE `CC_McInfo`
(
  `id`          int(11)                                 NOT NULL AUTO_INCREMENT,
  `mcId`        varchar(64) COLLATE utf8mb4_unicode_ci  NOT NULL COMMENT '公众号id',
  `mcIdHash`    int(11)                                 NOT NULL DEFAULT 0 COMMENT '公众号id hashcode',
  `attName`     varchar(50) COLLATE utf8mb4_unicode_ci  NOT NULL COMMENT '属性名称',
  `attValue`    varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `createdTime` timestamp                               NOT NULL DEFAULT current_timestamp() COMMENT '公众号创建时间',
  `appId`       bigint(20)                              NOT NULL DEFAULT 0 COMMENT 'appId',
  PRIMARY KEY (`id`),
  key ix_CC_McInfo_1 ( `mcIdHash`, `appId`),
  key ix_CC_McInfo_2 ( `mcIdHash`, `appId`,`attName`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='公众号表 信息扩展表';


-- Create syntax for TABLE 'CC_McRelation'
CREATE TABLE `CC_McRelation`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `mcId`        varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '公众号id',
  `mcIdHash`    int(11)                                NOT NULL DEFAULT 0 COMMENT '公众号id hashcode',
  `userId`      varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'uid',
  `userIdHash`  int(11)                                NOT NULL COMMENT 'uid hashcode',
  `createdTime` timestamp                              NOT NULL DEFAULT current_timestamp() COMMENT '关系创建时间',
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 COMMENT 'appId',
  `tagbitmap`   int(11) COMMENT '标签标识',
  PRIMARY KEY (`id`),
  key ix_CC_McRelation_1 ( `mcIdHash`, `userIdHash`,`appId`),
  key ix_CC_McRelation_2 ( `mcIdHash`, `appId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='公众号用户关系表';


drop table if exists `CC_AppKmapExt`;
-- Limit config

CREATE TABLE `CC_AppKmapExt`
(
  `id`          int(11)                                  NOT NULL AUTO_INCREMENT,
  `appId`       bigint(20)                               NOT NULL DEFAULT 0 COMMENT 'appId',
  `bizType`     int(11)                                  NOT NULL DEFAULT 0,
  `attNameHash` int(11)                                  not null comment '属性名字hash',
  `attName`     varchar(80) COLLATE utf8mb4_unicode_ci   NOT NULL COMMENT '属性名字',
  `attKeyHash`  int(11)                                  not null comment '属性key hash',
  `attKey`      varchar(100) COLLATE utf8mb4_unicode_ci  NOT NULL COMMENT '属性key值',
  `attValue`    varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `updatedTime` timestamp                                NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci            DEFAULT '' COMMENT '属性说明',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_AppKmapExt_1` (`appId`, `bizType`, `attName`, `attKey`),
  KEY `IX_CC_AppKmapExt_appId` (`appId`, `bizType`, `attNameHash`, `attKeyHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='应用配置扩展字典表';


-- global config
drop table if exists `CC_ConfigKvExt`;

CREATE TABLE `CC_ConfigKvExt`
(
  `id`          int(11)                                  NOT NULL AUTO_INCREMENT,
  `attName`     varchar(80) COLLATE utf8mb4_unicode_ci   NOT NULL COMMENT '属性名字',
  `attValue`    varchar(2048) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '属性值',
  `bizType`     int(11)                                  NOT NULL DEFAULT 0,
  `updatedTime` timestamp                                NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  `description` varchar(50) COLLATE utf8mb4_unicode_ci            DEFAULT '' COMMENT '属性说明',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_ConfigKvExt_1` (`bizType`, `attName`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='应用配置表';



drop table if exists `CC_AppUserWhiteList`;

CREATE TABLE `CC_AppUserWhiteList`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `userId`      varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `userIdHash`  int(11)                                NOT NULL,
  `whiteUserId` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 COMMENT 'appId',
  `reason`      int(11)                                         DEFAULT '405',
  `createdTime` timestamp                              NULL     DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `IX_CC_AppUserWhiteList_userIdHash` (`userIdHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


drop table if exists `CC_GroupSetting`;
CREATE TABLE `CC_GroupSetting`
(
  `id`          int(11)      NOT NULL AUTO_INCREMENT,
  `md5v`        varchar(50)  NOT NULL,
  `groupId`     varchar(64)  NOT NULL,
  `groupIdHash` int(11)      NOT NULL,
  `itemKey`     varchar(20)  NOT NULL,
  `itemValue`   varchar(200) NOT NULL,
  `itemStatus`  int(11)      NOT NULL COMMENT '1:add 2:update 3:delete',
  `itemVersion` bigint(20)   NOT NULL,
  `appId`       bigint(20)   NOT NULL DEFAULT 0 COMMENT 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `Index_md5` (`md5v`),
  KEY `Index_groupIdHash_itemVersion` (`appId`, `groupIdHash`,`itemVersion`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;


drop table if exists `CC_RtcSpecialDevice`;

CREATE TABLE `CC_RtcSpecialDevice`
(
  `id`            int(11)                                NOT NULL AUTO_INCREMENT,
  `deviceModel`   varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `osType`        varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `minOsVersion`  int(11)                                 DEFAULT NULL,
  `maxOsVersion`  int(11)                                 DEFAULT NULL,
  `minSdkVersion` int(11)                                 DEFAULT NULL,
  `maxSdkVersion` int(11)                                 DEFAULT NULL,
  `suportConfig`  varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `createTime`    datetime                                DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


drop table if exists `CC_PushPeriodSetting`;

CREATE TABLE `CC_PushPeriodSetting`
(
  `id`          int(11)     NOT NULL AUTO_INCREMENT,
  `appId`       bigint(20)  NOT NULL DEFAULT 0 COMMENT 'appId',
  `userId`      varchar(64) NOT NULL DEFAULT '',
  `startTime`   varchar(32) NULL     DEFAULT '',
  `period`      int(11)     not null DEFAULT '0',
  `timeZone`    varchar(32) not null DEFAULT '',
  `updatedTime` timestamp   NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_PushPeriodSetting` (`appId`, `userId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='push 免打扰时间段设置';


drop table if exists `CC_AppUserConfig`;

CREATE TABLE `CC_AppUserConfig`
(
  `id`          int(11)     NOT NULL AUTO_INCREMENT,
  `appId`       bigint(20)  NOT NULL,
  `userId`      varchar(64) NOT NULL DEFAULT '',
  `logType`     int         NOT NULL DEFAULT '0',
  `startTime`   bigint(20)  not null,
  `updatedTime` timestamp   NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',

  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_AppUserConfig` (`appId`, `userId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='CC_AppUserConfig';


drop table if exists `CC_BanGroup`;

CREATE TABLE `CC_BanGroup`
(
  `id`          int(11)     NOT NULL AUTO_INCREMENT,
  `appId`       bigint(20)  NOT NULL DEFAULT 0 COMMENT 'appId',
  `groupId`     varchar(64) NOT NULL DEFAULT '',
  `groupIdHash` int(11)     NOT NULL COMMENT 'hashcode,索引',
  `updatedTime` timestamp   NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',

  PRIMARY KEY (`id`),
  KEY `IX_CC_BanGroup` (`appId`, `groupId`),
  UNIQUE KEY `IX_CC_BanGroup_1` (`appId`, `groupIdHash`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci COMMENT ='CC_BanGroup';


drop table if exists `CC_GroupWhiteList`;

CREATE TABLE `CC_GroupWhiteList`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `appId`       int(11)                                NOT NULL,
  `groupId`     varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `groupIdHash` int(11)                                NOT NULL COMMENT 'hashcode,索引',
  `userId`      varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `userIdHash`  int(11)                                NOT NULL,
  `updatedTime` timestamp                              NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  PRIMARY KEY (`id`),
  KEY `IX_CC_GroupWhiteList` (`appId`, `groupIdHash`, `userIdHash`),
  UNIQUE KEY `IX_CC_GroupWhiteList_1` (`appId`, `groupId`, `userId`)


) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


drop table if exists `CC_App_GroupWhiteList`;

CREATE TABLE `CC_App_GroupWhiteList`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 COMMENT 'appId',
  `userId`      varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `userIdHash`  int(11)                                NOT NULL COMMENT 'hashcode,索引',
  `updatedTime` timestamp                              NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',

  PRIMARY KEY (`id`),
  KEY `IX_CC_App_GroupWhiteList` (`appId`, `userIdHash`),
  UNIQUE KEY `IX_CC_App_GroupWhiteList_1` (`appId`, `userId`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


drop table if exists `CC_GroupMsgTypeWhiteList`;

CREATE TABLE `CC_GroupMsgTypeWhiteList`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 COMMENT 'appId',
  `groupId`     varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `groupIdHash` int(11)                                NOT NULL COMMENT 'hashcode,索引',
  `msgType`     varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `msgTypeHash` int(11)                                NOT NULL COMMENT 'hashcode,索引',
  `updatedTime` timestamp                              NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',
  PRIMARY KEY (`id`),
  KEY `IX_CC_GroupWhiteList` (`appId`, `groupIdHash`, `msgTypeHash`),
  UNIQUE KEY `IX_CC_GroupWhiteList_1` (`appId`, `groupId`, `msgType`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


drop table if exists `CC_App_GroupMsgTypeWhiteList`;

CREATE TABLE `CC_App_GroupMsgTypeWhiteList`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 COMMENT 'appId',
  `msgType`     varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `msgTypeHash` int(11)                                NOT NULL COMMENT 'hashcode,索引',
  `updatedTime` timestamp                              NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '当前属性修改时间',

  PRIMARY KEY (`id`),
  KEY `IX_CC_App_GroupWhiteList` (`appId`, `msgTypeHash`),
  UNIQUE KEY `IX_CC_App_GroupWhiteList_1` (`appId`, `msgType`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


drop table if exists `CC_PushAppTag`;

CREATE TABLE `CC_PushAppTag`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `appId`       bigint(20)                             NOT NULL DEFAULT 0 COMMENT 'appId',
  `tag`         varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tagHash`     int(11)                                NOT NULL,
  `updatedTime` timestamp                              NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '当前属性修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `CC_PushAppTag_1` (`appId`, `tag`),
  KEY `CC_PushAppTag_2` (`appId`, `tagHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- for management config
drop table if exists `CC_PublicIp`;

CREATE TABLE `CC_PublicIp`
(
  `id`          int(11)                                NOT NULL AUTO_INCREMENT,
  `type`        varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nodeName`    varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `publicIps`   TEXT COLLATE utf8mb4_unicode_ci        NOT NULL,
  `updatedTime` timestamp                              NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '当前属性修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `CC_PublicIp_1` (`type`, `nodeName`)

) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


drop table if exists `CC_FdfsIndex`;
CREATE TABLE `CC_FdfsIndex`
(
  `uniqueId`   varchar(40)  NOT NULL,
  `fileId`     varchar(256) NULL,
  `thumbId`    varchar(128)          DEFAULT NULL,
  `fileSize`   bigint(8)    NOT NULL,
  `uploadTime` timestamp    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `namespace`  varchar(64)           DEFAULT NULL,
  `isDelete`   tinyint(1)   NOT NULL DEFAULT '0',
  PRIMARY KEY (`uniqueId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='文件服务器索引';

DROP TABLE IF EXISTS `CC_UserRtcAuthInfo`;
CREATE TABLE `CC_UserRtcAuthInfo`
(
  `id`         int(10) unsigned                  NOT NULL AUTO_INCREMENT,
  `userId`     varchar(64) CHARACTER SET utf8mb4 NOT NULL COMMENT '用户id',
  `hashId`     int(11)                           NOT NULL,
  `updateTime` timestamp                         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `createTime` timestamp                         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `rtcState`   int(8)                                     DEFAULT 0,
  `appId`      bigint(20)                        NOT NULL DEFAULT 0 COMMENT 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_UserRtcAuthInfo_appId_userId` (`appId`, `userId`),
  KEY `IX_CC_UserRtcAuthInfo_appId` (`appId`),
  KEY `IX_CC_UserRtcAuthInfo_hashId_domainId` (`hashId`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

CREATE TABLE `CC_ChatroomForbiddenMember`
(
  `id`         int(11)                                NOT NULL AUTO_INCREMENT COMMENT '主键',
  `userId`     varchar(64) CHARACTER SET utf8mb4      NOT NULL COMMENT '用户id',
  `userIdHash` int(11)                                NOT NULL COMMENT 'userId的hashcode，索引',
  `chrmId`     varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '聊天室id',
  `chrmIdHash` int(11)                                NOT NULL COMMENT 'chrmid的hashcode,索引',
  `status`     tinyint(4)                                      DEFAULT '0' COMMENT '状态，1禁言，2封禁',
  `createTime` timestamp                              NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `endTime`    bigint(20)                                      DEFAULT NULL COMMENT '禁言／封禁结束时间',
  `appId`      bigint(20)                             NOT NULL DEFAULT 0 COMMENT 'appId',
  PRIMARY KEY (`id`),
  UNIQUE KEY `IX_CC_GroupForbiddenMember_userId_chrmId` (`userId`, `chrmId`, `appId`),
  KEY `IX_CC_ChatroomForbiddenMember_chrmIdHash` (`chrmIdHash`),
  KEY `IX_CC_ChatroomForbiddenMember_userIdHash` (`userIdHash`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;


CREATE DATABASE if not exists management;
use management;
-- 管理后台user表
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`
(
  `user_id`   int(11)      NOT NULL AUTO_INCREMENT,
  `status`    tinyint(1)        DEFAULT NULL,
  `created`   timestamp    NULL DEFAULT CURRENT_TIMESTAMP,
  `modified`  timestamp    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_name` varchar(255) NOT NULL,
  `password`  varchar(255) NOT NULL,
  `role`      varchar(255) NOT NULL,
  `comment`   varchar(255)      DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `ix_auth_user_user_name` (`user_name`) USING BTREE
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

-- ----------------------------
-- Table structure for action_log
-- ----------------------------
DROP TABLE IF EXISTS `action_log`;
CREATE TABLE `action_log`
(
  `id`        int(11)                                 NOT NULL AUTO_INCREMENT,
  `created`   timestamp                               NULL DEFAULT CURRENT_TIMESTAMP,
  `app_key`   varchar(64) COLLATE utf8mb4_unicode_ci  NOT NULL,
  `user_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action`    varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content`   varchar(1024) COLLATE utf8mb4_unicode_ci     DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;

-- ----------------------------
-- Table structure for package_info
-- ----------------------------
DROP TABLE IF EXISTS `package_info`;
CREATE TABLE `package_info`
(
  `identify_id`          int(11)      NOT NULL AUTO_INCREMENT,
  `status`               tinyint(1)        DEFAULT NULL,
  `created`              timestamp    NULL DEFAULT CURRENT_TIMESTAMP,
  `modified`             timestamp    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `identify_name`        varchar(255) NOT NULL,
  `appkey`               varchar(50)  NOT NULL,
  `android_package_name` varchar(255)      DEFAULT NULL,
  `ios_package_name`     varchar(255)      DEFAULT NULL,
  PRIMARY KEY (`identify_id`)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;