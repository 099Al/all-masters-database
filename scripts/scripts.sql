CREATE PROCEDURE update_statuses()
LANGUAGE plpgsql
AS $$
BEGIN
    delete
from moderate_log
where updated_at < current_timestamp - interval '1 hour';


update specialists
set moderate_result = NULL
where id in (
select id
from(
select id
from specialists s
where moderate_result = 'DELAY'
) s1 left join moderate_log ml  on s1.id = ml.user_id
group by id
having count(updated_at) < 10
);

MERGE INTO specialists s
USING (
    SELECT *
    FROM moderate_data
    WHERE status = 'APPROVED'
) md
ON s.id = md.id
WHEN MATCHED THEN
UPDATE SET
    status = 'ACTIVE',
    moderate_result = md.status,
    message_to_user = md.message_to_user,
    name = md.name,
    phone = md.phone,
    telegram = md.telegram,
    email = md.email,
    specialty = md.specialty,
    about = md.about,
    photo_telegram = md.photo_telegram,
    photo_local = md.photo_local,
    updated_at = CURRENT_TIMESTAMP;

MERGE INTO specialists s
USING (
    SELECT *
    FROM moderate_data
    WHERE status in ('REJECTED', 'DELAY')
) md
ON s.id = md.id
WHEN MATCHED THEN
UPDATE SET
    status = 'ACTIVE',
    moderate_result = md.status,
    message_to_user = md.message_to_user,
    updated_at = CURRENT_TIMESTAMP;


MERGE INTO specialists s
USING (
    SELECT *
    FROM moderate_data
    WHERE status in ('BANNED', 'PERMANENTLY_BANNED')
) md
ON s.id = md.id
WHEN MATCHED THEN
UPDATE SET
    status = 'BANNED',
    moderate_result = md.status,
    message_to_user = md.message_to_user,
    updated_at = CURRENT_TIMESTAMP;


delete from moderate_data
where status in ('APPROVED', 'REJECTED', 'BANNED', 'PERMANENTLY_BANNED', 'DELAY');



END;
$$;
