create table if not exists `%sclients` (
    id bigint auto_increment primary key,
    client_id varchar(144) not null unique,
    client_type varchar(64) not null,
    ip varchar(256) not null,
    time datetime not null
)engine=innodb  default charset=utf8mb4;