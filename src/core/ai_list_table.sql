create table if not exists `%ai_list` (
    id bigint auto_increment primary key,
    name varchar(64) default null,
    twitter varchar(128) not null,
    img text default null,
    icon text default null,
    bg text default null,
    url text default null,
    first_word varchar(256) default null,
    details varchar(2048) default null,
    password varchar(64) not null
)engine=innodb  default charset=utf8mb4;