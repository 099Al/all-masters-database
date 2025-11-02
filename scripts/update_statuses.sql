CREATE OR REPLACE PROCEDURE update_statuses()
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
    whatsapp = md.whatsapp,
    instagram = md.instagram,
    email = md.email,
    services = md.services,
    about = md.about,
    photo_telegram = md.photo_telegram,
    photo_name = md.photo_name,
    photo_location = replace(md.photo_location, '/new_', '/'), -- /new/ -> /md.photo_location,
    l_services = md.l_services,
    l_work_types = md.l_work_types,
    updated_at = CURRENT_TIMESTAMP;


delete from specialist_photos s
where specialist_id in (
    SELECT distinct mdp.specialist_id
    FROM moderate_data m
    JOIN moderate_specialist_photos mdp on mdp.specialist_id = m.id
    WHERE status = 'APPROVED'
    and applied_category = true
);


INSERT into specialist_photos(specialist_id, photo_telegram_id, photo_name, photo_location, photo_type, created_at)
 SELECT mdp.specialist_id, mdp.photo_telegram_id, mdp.photo_name, replace(mdp.photo_location, '/new_', '/'), mdp.photo_type, current_timestamp
    FROM moderate_data m
    JOIN moderate_specialist_photos mdp on mdp.specialist_id = m.id
    WHERE status = 'APPROVED'
    and applied_category = true;



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


--перенос фото



-- удаленеие обработанных статусов
delete from moderate_specialist_photos
where specialist_id in (
    select id
    from moderate_data s
    where status = 'APPROVED'
    and applied_category = true
);

delete from moderate_log
where user_id in (
    select id
    from moderate_data s
    where status = 'APPROVED'
    and applied_category = true
);

delete from moderate_data
where status in ('REJECTED', 'BANNED', 'PERMANENTLY_BANNED', 'DELAY');

delete from moderate_data
where status  = 'APPROVED'
and applied_category = true;



END;
$$;
