create table if not exists `%slide_ad` (
    id bigint auto_increment primary key,
    img_path varchar(4096) not null,
    url varchar(4096) default null,
    special boolean default false not null,
    status boolean default true not null
)engine=innodb  default charset=utf8mb4;