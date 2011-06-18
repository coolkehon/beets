CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    artpath TEXT -- artist picture
);

CREATE TABLE IF NOT EXISTS releases (
    id INTEGER PRIMARY KEY,
    artpath TEXT,
    artist INTEGER, -- albumartist / releaseartist
    name TEXT,
    type TEXT, -- release type
    date DATE, -- release date
    tracktotal INTEGER, -- total number of tracks
    disctotal INTEGER, -- total number of disc
    composition BOOLEAN, -- true if album is a composition
    genre TEXT, -- track genre (generic)
    dirpath TEXT -- where release should be on filesystem
--    FOREIGN KEY (artist) REFERENCES artists(id) -- TODO remove foreign key constraints
);
-- Various Artist can be gotten by looking through tracks.artist in release 
-- and track_artist

CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY,
    artist INTEGER,
    album INTEGER,
    release INTEGER,
    filepath TEXT, -- file path
    title TEXT,
    composer TEXT, -- composer
    lyrics TEXT, -- lyrics
    comments TEXT,
    bitrate INTEGER, -- track bitrate
    format TEXT, -- file format
    length INTEGER -- track time in seconds
--    FOREIGN KEY (artist) REFERENCES artist(id),
--    FOREIGN KEY (release) REFERENCES releases(id)
);

-- Join track artist for featured and Various Artist tracks
CREATE TABLE IF NOT EXISTS track_artist (
    id INTEGER PRIMARY KEY,
    track_id INTEGER,
    artist_id INTEGER
);

-- tags, user generated or imported from last.fm
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    origin TEXT -- tag origin, last.fm, user, etc
);

CREATE TABLE IF NOT EXISTS track_tags (
    id INTEGER PRIMARY KEY,
    tag INTEGER, -- tag id
    track INTEGER -- track id
--    FOREIGN KEY (tag) REFERENCES tags(id),
--    FOREIGN KEY (track) REFERENCES tracks(id)
);

CREATE TABLE IF NOT EXISTS artist_tags (
    id INTEGER PRIMARY KEY,
    tag INTEGER,
    artist INTEGER
--    FOREIGN KEY (tag) REFERENCES tags(id),
--    FOREIGN KEY (artist) REFERENCES artists(id)
);

CREATE TABLE IF NOT EXISTS release_tags (
    id INTEGER PRIMARY KEY,
    tag INTEGER,
    release INTEGER,
--    FOREIGN KEY (tag) REFERENCES tags(id),
--    FOREIGN KEY (release) REFERENCES releases(id)
);

-- use defined attributes
-- lyrics, comments, etc
CREATE TABLE IF NOT EXISTS attributes (
    id INTEGER PRIMARY KEY,
    name TEXT,
    value TEXT
);

-- file attachments
CREATE TABLE IF NOT EXISTS attachment (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    filepath TEXT
);

-- TODO track_attachments etc

-- Views
CREATE VIEW view_tracks AS
   SELECT -- track title, album, artist, file
        tracks.title, releases.name, artists.name
   FROM
        tracks, releases, artists
   LEFT JOIN
        tracks.artist = artists.id
   LEFT JOIN 
        tracks.release = releases.id
;
