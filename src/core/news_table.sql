create table if not exists `%snews` (
    id bigint auto_increment primary key,
    news_type varchar(64) not null,
    title varchar(64) default null,
    detail varchar(1024) default null,
    url text default null,
    img_path text default null,
    special boolean default false,
    status boolean not null
)engine=innodb  default charset=utf8mb4;