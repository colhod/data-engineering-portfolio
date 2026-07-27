select
    trim(genre) as genre,
    count(*) as item_count
from (
    select
        item_id,
        unnest(string_to_array(genres, ',')) as genre
    from {{ ref('stg_jellyfin_items') }}
    where genres is not null
) as exploded_genres
group by trim(genre)
order by item_count desc
