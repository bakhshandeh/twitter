create table tracking(
	tracking_id			integer not null primary key,
	tracking_user_id		text,
	tracking_date			timestamp without time zone,
	tracking_count			int
);

create table tracking_users(
	id 			serial,
	tracking_id		integer references tracking,
	current_id		text,
	user_id			text,
	user_screen_name	text
);

create sequence tracking_seq;
