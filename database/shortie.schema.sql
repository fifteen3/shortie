CREATE TABLE IF NOT EXISTS `url_hashes` (
    `short_hash` char(7) NOT NULL DEFAULT '',
    `long_hash` varchar(256) NOT NULL DEFAULT '',
    `user_id` integer,
    `created` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (`short_hash`)
) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS `urls` (
    `short_hash` char(7),
    `url_type` varchar(7),
    `url` text
);
CREATE TABLE IF NOT EXISTS `users` (
    `email` text,
    `first_name` text,
    `last_name` text,
    PRIMARY kEY (`email`)
);
CREATE TABLE IF NOT EXISTS `visits` (
    `short_hash` char(7),
    `url_type` varchar(7),
    `visited` DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);
