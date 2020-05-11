CREATE EVENT IF NOT EXISTS cleanup_event
ON SCHEDULE AT CURRENT_TIMESTAMP + INTERVAL 1 HOUR
DO
START TRANSACTION;
SET @pids = (SELECT group_concat(pid)
FROM polls
WHERE DATEDIFF(curdate(), DATE(end_date)) > 25);

DELETE FROM poll_responses
WHERE find_in_set(pid_id, @pids) > 0;

UPDATE polls
SET active = 0
WHERE find_in_set(pid, @pids) > 0;

COMMIT;