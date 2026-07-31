with combined as (
    select event_date, size_bytes, 'tv' as media_type from {{ ref('stg_sonarr_history') }}
    where event_type = 'downloadFolderImported'
    union all
    select event_date, size_bytes, 'movie' as media_type from {{ ref('stg_radarr_history') }}
    where event_type = 'downloadFolderImported'
)

select
    date_trunc('month', event_date) as activity_month,
    media_type,
    sum(size_bytes) as total_bytes_added,
    count(*) as files_imported
from combined
group by 1, 2
order by 1 desc, 2
