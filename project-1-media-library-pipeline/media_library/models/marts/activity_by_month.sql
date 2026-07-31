with combined as (
    select event_date, event_type, 'tv' as media_type from {{ ref('stg_sonarr_history') }}
    union all
    select event_date, event_type, 'movie' as media_type from {{ ref('stg_radarr_history') }}
)

select
    date_trunc('month', event_date) as activity_month,
    media_type,
    event_type,
    count(*) as event_count
from combined
group by 1, 2, 3
order by 1 desc, 2, 3
