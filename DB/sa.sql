CREATE TABLE infra_server(
    id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT 'id 主键',
    server_hostname VARCHAR(20) NOT NULL DEFAULT '' COMMENT '机器名',
    server_ip INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '服务器IP',
    server_username VARCHAR(20) NOT NULL DEFAULT '' COMMENT '登录名',
    server_password VARCHAR(100) NOT NULL DEFAULT '' COMMENT '登录密码',
    server_env TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '1 PRODUCTION, 2 TEST',
    server_os TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '1 UBUNTU, 2 WINDOWS, 3 ALi-cloud',
    server_version VARCHAR(20) NOT NULL DEFAULT '' COMMENT '服务器版本',
    server_cpu TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '服务器CPU',
    server_mem INT NOT NULL DEFAULT 0 COMMENT '服务器MEM, 默认单位M',
    server_disk INT NOT NULL DEFAULT 0 COMMENT '服务器DISK, 默认单位G',
    server_type TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '1 物理机, 2 虚拟机',
    server_loc VARCHAR(100) NOT NULL DEFAULT '' COMMENT '服务器机房与机架号',
    is_delete TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 启用，1 删除'
);

CREATE TABLE infra_instance(
    id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT 'id 主键',
    server_ip INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '服务器IP',
    instance_name VARCHAR(20) NOT NULL DEFAULT '' COMMENT '实例名',
    instance_type TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '1 MySQL, 2 SQLSERVER',
    instance_username VARCHAR(20) NOT NULL DEFAULT '' COMMENT '实例登录名',
    instance_password VARCHAR(100) NOT NULL DEFAULT '' COMMENT '实例登录密码',
    instance_port INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '实例端口',
    is_delete TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 启用，1 删除'
);

CREATE TABLE infra_instance_backup(
    id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT 'id 主键',
    instance_id INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '实例ID',
    backup_interval TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '间隔多少分钟备份一次',
    backup_time TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '备份时间',
    backup_type TINYINT UNSIGNED NOT NULL DEFAULT 2 COMMENT '备份类型 1 完全备份 2 增量备份',
    is_delete TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 启用，1 删除'
);

CREATE TABLE user (
  user_id INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'auto_increment id',
  username VARCHAR(20) NOT NULL DEFAULT '' COMMENT 'username',
  password VARCHAR(100) NOT NULL DEFAULT '' COMMENT 'password',
  salt CHAR(4) NOT NULL COMMENT 'salt',
  nickname VARCHAR(20) NOT NULL DEFAULT '' COMMENT 'nick name',
  is_delete TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '0 False 1 True',
  PRIMARY KEY (user_id)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COMMENT='用户表';