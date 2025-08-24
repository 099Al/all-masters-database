CREATE OR REPLACE PROCEDURE move_links()
LANGUAGE plpgsql
AS $$
BEGIN

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


END;
$$;


