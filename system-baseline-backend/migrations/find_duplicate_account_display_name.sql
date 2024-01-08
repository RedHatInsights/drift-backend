select
  account, display_name, count(*)
from
  system_baselines
group by
  account, display_name
having
  count(*) > 1;
