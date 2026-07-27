select
    id as item_id,
    title,
    type as media_type,
    series_name,
    nullif(year, '')::integer as year,
    genres,
    nullif(runtime_minutes, '')::numeric as runtime_minutes,
    nullif(file_size_bytes, '')::bigint as file_size_bytes,
    container as file_format
from raw_jellyfin_items
