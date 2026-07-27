select
    'Navidrome (Music)' as source,
    count(*) as item_count,
    round(avg(duration_seconds) / 60, 1) as avg_duration_minutes
from {{ ref('stg_navidrome_tracks') }}

union all

select
    'Jellyfin (Video)' as source,
    count(*) as item_count,
    round(avg(runtime_minutes), 1) as avg_duration_minutes
from {{ ref('stg_jellyfin_items') }}
