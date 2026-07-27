select
    coalesce(genre, 'Unknown') as genre,
    count(*) as track_count
from {{ ref('stg_navidrome_tracks') }}
group by genre
order by track_count desc
