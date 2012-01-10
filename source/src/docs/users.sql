create table users(
    id			integer not null primary key,
    screen_name		varchar(50) not null,
    obj_data		text,
    retweet_factor	float,
    impact_factor	float,
    mc_factor		float
);
