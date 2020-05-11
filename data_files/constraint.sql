CREATE TABLE `poll_responses` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `oid_id` integer NOT NULL, `pid_id` integer NOT NULL, `uid_id` integer NOT NULL);
ALTER TABLE `polls` ADD CONSTRAINT `polls_cid_id_134d6045_fk_categories_cid` FOREIGN KEY (`cid_id`) REFERENCES `categories` (`cid`);
ALTER TABLE `polls` ADD CONSTRAINT `polls_uid_id_a62c2223_fk_users_uid` FOREIGN KEY (`uid_id`) REFERENCES `users` (`uid`);
ALTER TABLE `poll_options` ADD CONSTRAINT `poll_options_pid_id_4ccd1ae3_fk_polls_pid` FOREIGN KEY (`pid_id`) REFERENCES `polls` (`pid`);
ALTER TABLE `poll_responses` ADD CONSTRAINT `poll_responses_uid_id_pid_id_1b439e94_uniq` UNIQUE (`uid_id`, `pid_id`);
ALTER TABLE `poll_responses` ADD CONSTRAINT `poll_responses_oid_id_31a1a5a1_fk_poll_options_oid` FOREIGN KEY (`oid_id`) REFERENCES `poll_options` (`oid`);
ALTER TABLE `poll_responses` ADD CONSTRAINT `poll_responses_pid_id_0df9a990_fk_polls_pid` FOREIGN KEY (`pid_id`) REFERENCES `polls` (`pid`);
ALTER TABLE `poll_responses` ADD CONSTRAINT `poll_responses_uid_id_f507f7ea_fk_users_uid` FOREIGN KEY (`uid_id`) REFERENCES `users` (`uid`);
