select
    history_id,
    movie_id,
    event_type,
    date as event_date,
    source_title,
    quality,
    nullif(size_bytes, '')::bigint as size_bytes
from raw_radarr_history
