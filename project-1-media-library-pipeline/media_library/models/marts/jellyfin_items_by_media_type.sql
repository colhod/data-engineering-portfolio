select
    media_type,
    count(*) as item_count,
    round(avg(runtime_minutes)) as avg_runtime_minutes,
    sum(file_size_bytes) as total_file_size_bytes
from {{ ref('stg_jellyfin_items') }}
group by media_type
order by item_count desc
