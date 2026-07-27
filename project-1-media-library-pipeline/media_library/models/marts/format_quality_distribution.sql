select
    file_format,
    count(*) as track_count,
    round(avg(bitrate)) as avg_bitrate,
    min(bitrate) as min_bitrate,
    max(bitrate) as max_bitrate
from {{ ref('stg_navidrome_tracks') }}
where file_format is not null
group by file_format
order by track_count desc
