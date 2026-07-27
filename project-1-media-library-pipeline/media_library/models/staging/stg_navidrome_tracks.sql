select
    id as track_id,
    title,
    artist,
    album,
    genre,
    nullif(year, '')::integer as year,
    nullif(duration, '')::integer as duration_seconds,
    suffix as file_format,
    nullif(bitrate, '')::integer as bitrate,
    nullif(track, '')::integer as track_number,
    album_id,
    artist_id
from raw_navidrome_tracks
