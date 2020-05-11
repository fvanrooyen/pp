-- 1. User audit table
CREATE TABLE users_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    uid INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    change_date DATETIME DEFAULT NULL,
    action VARCHAR(50) DEFAULT NULL
);

-- 2. A triger to update user audit table when table user is updated 

drop trigger before_users_update IF EXISTS;

CREATE TRIGGER before_users_update 
    BEFORE UPDATE ON users
    FOR EACH ROW 
 INSERT INTO users_audit
 SET action = 'update',
     uid = OLD.uid,
     username = OLD.username,
     change_date = NOW();


--  3. Verification step
--  a. Update one row of data in table "users":
--     update users set username = "rcordeaurr" where uid = 1000

--  b. Check table "users_audit":
--    audit_id, uid,    username,   change_date,          action
--    1         1000    rcordeaurr  2020-05-11 03:03:52   update