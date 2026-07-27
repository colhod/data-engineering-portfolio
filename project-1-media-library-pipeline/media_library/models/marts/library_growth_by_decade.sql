select
    (floor(year / 10) * 10)::text || 's' as decade,
    count(*) as track_count
from {{ ref('stg_navidrome_tracks') }}
where year is not null
group by floor(year / 10) * 10
order by floor(year / 10) * 10
