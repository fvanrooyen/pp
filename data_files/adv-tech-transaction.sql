START TRANSACTION;

SET @pids = (SELECT group_concat(pid)
FROM polls
WHERE DATEDIFF(curdate(), DATE(end_date)) > 25);

DELETE FROM polls
WHERE find_in_set(pid, @pids) > 0;

DELETE FROM poll_options
WHERE find_in_set(pid_id, @pids) > 0;

DELETE FROM poll_responses
WHERE find_in_set(pid_id, @pids) > 0;

COMMIT;