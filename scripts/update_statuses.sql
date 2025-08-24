CREATE PROCEDURE update_statuses()
LANGUAGE plpgsql
AS $$
BEGIN

--убираем старые попытки редактирования
delete
from moderate_log
where updated_at < current_timestamp - interval '1 hour';

-- Разблокировка Delay
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

--перенос подтвержденных анкет
MERGE INTO specialists s
USING (
    SELECT *
    FROM moderate_data
    WHERE status = 'APPROVED'
    and applied_category = true
) md
ON s.id = md.id
WHEN MATCHED THEN
UPDATE SET
    status = 'ACTIVE',             -- анкета доступна
    moderate_result = md.status,
    message_to_user = md.message_to_user,
    name = md.name,
    phone = md.phone,
    telegram = md.telegram,
    email = md.email,
    services = md.services,
    about = md.about,
    photo_telegram = md.photo_telegram,
    photo_local = md.photo_local,
    l_services = md.l_services,
    l_work_types = md.l_work_types,
    updated_at = CURRENT_TIMESTAMP;

-- перенос отклоненных и заблокированных анкет, по которым были изменения
MERGE INTO specialists s
USING (
    SELECT *
    FROM moderate_data
    WHERE status in ('REJECTED', 'DELAY')
) md
ON s.id = md.id
WHEN MATCHED THEN
UPDATE SET
    --status = 'ACTIVE',
    moderate_result = md.status,
    message_to_user = md.message_to_user,
    updated_at = CURRENT_TIMESTAMP;

-- перенос заблокированных анкет
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


-- перенос услуг (линков)
create temporary table tmp_moved on commit drop as
    select ms.specialist_id, ms.service_id
    from moderatedata_services ms
    join services s on s.id = ms.service_id
    join categories c on c.id = s.category_id
    where c.is_new = false
      and s.is_new = false;

insert into specialist_services (specialist_id, service_id)
select specialist_id, service_id
from tmp_moved;

delete from moderatedata_services ms
using tmp_moved t
where ms.specialist_id = t.specialist_id
  and ms.service_id = t.service_id;


-- удаленеие обработанных статусов
delete from moderate_data
where status ('REJECTED', 'BANNED', 'PERMANENTLY_BANNED', 'DELAY');

delete from moderate_data
where status  = 'APPROVED'
and applied_category = true;


END;
$$;
