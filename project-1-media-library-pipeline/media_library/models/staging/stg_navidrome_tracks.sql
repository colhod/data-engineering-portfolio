select
    id as track_id,
    title,
    artist,
    album,
    case
        when nullif(trim(genre), '') is null then 'Unknown'
        when lower(trim(genre)) = 'hip hop' then 'Hip-Hop'
        else trim(genre)
    end as genre,
    nullif(year, '')::integer as year,
    nullif(duration, '')::integer as duration_seconds,
    suffix as file_format,
    nullif(bitrate, '')::integer as bitrate,
    nullif(track, '')::integer as track_number,
    album_id,
    artist_id
from raw_navidrome_tracks
