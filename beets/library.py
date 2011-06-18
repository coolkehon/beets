# This file is part of beets.
# Copyright 2011, coolkehon
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# {{{ imports
import sqlite3
import os
import re
import shutil
import sys
from string import Template
import logging
from beets.mediafile import MediaFile
from beets import plugins
from beets import util
from beets.util import bytestring_path, syspath, normpath
# }}} end imports

# {{{ Logger.
log = logging.getLogger('beets')
if not log.handlers:
    log.addHandler(logging.StreamHandler())

# }}} end logger

# {{{ Exceptions.

class InvalidFieldError(Exception):
    pass
# }}} end Exceptions

# {{{ Item base class
class Item(object):
    """Base class for items (Artist, Release, Track, etc)"""
    def __init__(self, lib):
        """Create Item with library"""
        self.__dict__['lib'] = lib
        self.__dict__['records'] = { }
        self.__dict__['dirty'] = { }
        self.__dict__['columns'] = { } # database columns

    def __setattr__(self, key, value):
        """Store attributes in record fields and make them dirty"""
        if self.__dict__.has_key(key):
            self.__dict__[key] = value
        else:
            self.records[key] = value
            self.dirty[key] = True

    def __getattr__(self, key):
        """Return attributes if they are in __dict__ else return them from records[key]"""
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        elif self.records.has_key(key):
            return self.records[key]
        else: # return None to save trouble when values don't exists yet
            return None

    def load(self, item_id):
        """Load the item data from the database (default: No Op)
        If item_id is not in the database then clear all records
        """
        pass

    def save(self, item_id=None):
        """Save item data to database (default: No Op)
        If item_id < 0 then item should be inserted into the database
        If item_id == None and self.records[id] == None then the item should be inserted into the database
        If item_id != self.records[id] then update all values
        If item_id == self.records[id] or item_id == None and self.records[id] != None then update the record
        identified by self.records[id]
        """
        pass

# }}} end Item base class

# {{{ Artist(Item)
class Artist(Item):
    """Class representing an artist in the database"""

    def load(self, artist_id=None):
        """Load the artist data (records) from the database"""
        if self.lib != None and artist_id != None:
            self.records = self.lib.artist(artist_id).records
            self.dirty = { }
        else:
            self.records = { }
            self.dirty = { }

    def _insert(self):
        """Insert the artist info into the database
        Called by save
        """
        cur = self.lib.conn.cursor()
        cur.execute('PRAGMA table_info(%s)' % 'artists')
        columns = [ row[1] for row in cur ]

        sql = 'INSERT INTO artists'
        cols = [ ]
        vals = [ ]

        for key, value in self.records.iteritems():
            if key in columns:
                cols.append(key)
                vals.append(value)
        
        if len(cols) > 0:
            self.lib.conn.execute(' '.join([ sql, '(' + ', '.join(cols) + ')', 'VALUES', '(' + ', '.join([ '?' for i in vals]) + ')' ]), vals)

    def _update(self, artist_id=None):
        """Update the artist info in the database
        Called by save
        """
        cur = self.lib.conn.cursor()
        cur.execute('PRAGMA table_info(%s)' % 'artists')
        columns = [ row[1] for row in cur ]

        id = artist_id if artist_id != None else self.id

        sql = 'UPDATE artists SET'
        clauses = [ ]
        params = [ ]
        for key, value in self.records.iteritems():
            if self.dirty.has_key(key) and self.dirty[key] and key in columns:
                clauses.append(key + '=?')
                params.append(value)

        where = 'WHERE id=?'
        params.append(id)

        if len(clauses) > 0:
            self.lib.conn.execute(' '.join([sql, ', '.join(clauses), where]), params )

    def save(self, artist_id=None, commit=True):
        """Save artist data to database
        @commit whether to commit changes to disk
        """
        if self.lib == None or True not in self.dirty.values():
            return

        if (artist_id != None and artist_id < 0) or (artist_id == None and self.id == None):
            self._insert()
        elif (artist_id != self.id) or (item_id == self.id or item_id == None and self.id != None):
            self._update(artist_id)

        if commit == True:
            self.lib.conn.commit()

# }}} end Artist(Item)

# {{{ Release(Item)
class Release(Item):
    """Class representing a release (album) in the database"""
    def load(self, release_id=None):
        """Load the release data (records) from the database"""
        if self.lib != None and release_id != None:
            self.records = self.lib.release(release_id).records
            self.dirty = { }
        else:
            self.records = { }
            self.dirty = { }

    def _insert(self):
        """Insert the release info into the database
        Called by save
        """
        cur = self.lib.conn.cursor()
        cur.execute('PRAGMA table_info(%s)' % 'releases')
        columns = [ row[1] for row in cur ]

        sql = 'INSERT INTO releases'
        cols = [ ]
        vals = [ ]

        for key, value in self.records.iteritems():
            if key in columns:
                cols.append(key)
                vals.append(value)
        
        if len(cols) > 0:
            self.lib.conn.execute(' '.join([ sql, '(' + ', '.join(cols) + ')', 'VALUES', '(' + ', '.join([ '?' for i in vals]) + ')' ]), vals)

    def _update(self, release_id=None):
        """Update the release info in the database
        Called by save
        """
        cur = self.lib.conn.cursor()
        cur.execute('PRAGMA table_info(%s)' % 'releases')
        columns = [ row[1] for row in cur ]

        id = release_id if release_id != None else self.id

        sql = 'UPDATE releases SET'
        clauses = [ ]
        params = [ ]
        for key, value in self.records.iteritems():
            if self.dirty.has_key(key) and self.dirty[key] and key in columns:
                clauses.append(key + '=?')
                params.append(value)

        where = 'WHERE id=?'
        params.append(id)

        if len(clauses) > 0:
            self.lib.conn.execute(' '.join([sql, ', '.join(clauses), where]), params )

    def save(self, release_id=None, commit=True):
        """Save release data to database
        @commit whether to commit changes to disk
        """
        if self.lib == None or True not in self.dirty.values():
            return

        if (release_id != None and release_id < 0) or (release_id == None and self.id == None):
            self._insert()
        elif (release_id != self.id) or (item_id == self.id or item_id == None and self.id != None):
            self._update(release_id)

        if commit == True:
            self.lib.conn.commit()

# }}} end Release(Item)

# {{{ File(Item)
class File(Item):
    pass

# }}} end File(Item)

# {{{ Track(Item)
class Track(Item):
    """Class representing a release (album) in the database"""
    # TODO add artists and releases function   
    def load(self, track_id=None):
        """Load the track data (records) from the database"""
        if self.lib != None and track_id != None:
            self.records = self.lib.track(track_id).records
            self.dirty = { }
        else:
            self.records = { }
            self.dirty = { }

    def _insert(self):
        """Insert the track info into the database
        Called by save
        """
        cur = self.lib.conn.cursor()
        cur.execute('PRAGMA table_info(%s)' % 'tracks')
        columns = [ row[1] for row in cur ]

        sql = 'INSERT INTO tracks'
        cols = [ ]
        vals = [ ]

        for key, value in self.records.iteritems():
            if key in columns:
                cols.append(key)
                vals.append(value)
        
        if len(cols) > 0:
            self.lib.conn.execute(' '.join([ sql, '(' + ', '.join(cols) + ')', 'VALUES', '(' + ', '.join([ '?' for i in vals]) + ')' ]), vals)

    def _update(self, track_id=None):
        """Update the track info in the database
        Called by save
        """
        cur = self.lib.conn.cursor()
        cur.execute('PRAGMA table_info(%s)' % 'tracks')
        columns = [ row[1] for row in cur ]

        id = track_id if track_id != None else self.id

        sql = 'UPDATE tracks SET'
        clauses = [ ]
        params = [ ]
        for key, value in self.records.iteritems():
            if self.dirty.has_key(key) and self.dirty[key] and key in columns:
                clauses.append(key + '=?')
                params.append(value)

        where = 'WHERE id=?'
        params.append(id)

        if len(clauses) > 0:
            self.lib.conn.execute(' '.join([sql, ', '.join(clauses), where]), params )

    def save(self, track_id=None, commit=True):
        """Save track data to database
        @commit whether to commit changes to disk
        """
        if self.lib == None or True not in self.dirty.values():
            return

        if (track_id != None and track_id < 0) or (track_id == None and self.id == None):
            self._insert()
        elif (track_id != self.id) or (item_id == self.id or item_id == None and self.id != None):
            self._update(track_id)

        if commit == True:
            self.lib.conn.commit()

# }}} end Track(Item)

# {{{ BaseLibrary
class BaseLibrary(object):
    """Abstract BaseLibrary class for music libraries"""
    def __init__(self):
        raise NotImplemented

    def add(self, item):
        """Add a Item (track, release, artist, etc) to the database"""
        raise NotImplemented

    # Basic functions
    def releases(self, query=None):
        """Should return a list of releases in database matching query.
        If query is None then return all releases
        """
        raise NotImplemented

    def release(self, release_id):
        """Should return one release identified by release_id"""
        raise NotImplemented

    def artists(self, query=None):
        """Similar to releases() but for artist"""
        raise NotImplemented

    def artist(self, artist_id):
        """Should return one artist identified by artist_id"""
        raise NotImplemented

    def tracks(self, query=None):
        """Similar to releases() but for tracks"""
        raise NotImplemented

    def track(self, track_id):
        """Should return on track identifed by track_id"""
        raise NotImplemented
        
# }}} end BaseLibrary

# {{{ Library(BaseLibrary)
class Library(BaseLibrary):
    """A Music Library using an SQLite database as the metadata store."""
    # {{{ __init__(self, path, directory, path_format, art_filename)
    def __init__(self, path='library.blb',
                       directory='~/Music',
                       path_formats=None,
                       art_filename='cover'):
        self.path = bytestring_path(path)
        self.directory = bytestring_path(directory)
        if path_formats is None:
            path_formats = {'default': '$artist/$album/$track $title'}
        elif isinstance(path_formats, basestring):
            path_formats = {'default': path_formats}
        self.path_formats = path_formats
        self.art_filename = bytestring_path(art_filename)

        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row

        # make sure that the database tables are created
        self._check_sql()

    # }}} end __init__(self, path, directory, path_format, art_filename)

    # {{{ _check_sql(self)
    def _check_sql(self):
        """Check that the tables are created in the database and if not then create them"""
        # TODO: update library init sql below
        sql = '''
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
    FOREIGN KEY (artist) REFERENCES artists(id)
);

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
    length INTEGER, -- track time in seconds
    FOREIGN KEY (artist) REFERENCES artist(id),
    FOREIGN KEY (release) REFERENCES releases(id)
);
'''

        self.conn.executescript(sql)
        self.conn.commit()
        # }}} end _check_sql(self) 

    # {{{ get_clause(self, field)
    def get_clause(self, field):
        """Transform a field into an sql WHERE clause using python regex
        Returns dictionary with sql and params defined
        dict['sql'] is the SQL statement
        dict['params'] is a list of the parameters for ? in the sql statement
        """
        clause = { 'sql' : '', 'params' : [ ] }

        # like matches
        m = re.match(r'^(.*?):(.*?)$', field)
        if m != None:
            if re.match(r'^(album|release)$', m.group(1), re.I):
                return { 'sql' : 'releases.name LIKE ?', 'params' : [ '%' + m.group(2) + '%' ] }

            elif re.match(r'^artist$', m.group(1), re.I):
                return { 'sql' : 'artists.name LIKE ?', 'params' : [ '%' + m.group(2) + '%' ] }

            elif re.match(r'^(title|track)$', m.group(1), re.I):
                return { 'sql' : 'tracks.name LIKE ?', 'params' : [ '%' + m.group(2) + '%' ] }

            elif re.match(r'^path$', m.group(1), re.I):
                return { 'sql' : 'releases.dirpath LIKE ? OR tracks.filepath LIKE ?', 'params' : [ '%' + m.group(2) + '%', '%' + m.group(2) + '%' ] }

        # exact matches
        m = re.match(r'^(.*?)=(.*?)$', field)
        if m != None:
            if re.match(r'^(album|release)$', m.group(1), re.I):
                return { 'sql' : 'releases.name = ?', 'params' : [ '%' + m.group(2) + '%' ] }

            elif re.match(r'^artist$', m.group(1), re.I):
                return { 'sql' : 'artists.name = ?', 'params' : [ '%' + m.group(2) + '%' ] }

            elif re.match(r'^(title|track)$', m.group(1), re.I):
                return { 'sql' : 'tracks.name = ?', 'params' : [ '%' + m.group(2) + '%' ] }

            elif re.match(r'^path$', m.group(1), re.I):
                return { 'sql' : 'releases.dirpath = ? OR tracks.filepath = ?', 'params' : [ '%' + m.group(2) + '%', '%' + m.group(2) + '%' ] }


        
        # TODO add more regex filters
        # TODO add +tag filters
        # TODO add singleton:(1|true) like boolean value filters
        return { 'sql' : 'artists.name LIKE ? OR releases.name LIKE ? OR tracks.name LIKE ?', 'params' : [ '%' + field + '%' for i in range(3) ] }

    # }}} end get_clause(self, field)

    def add(self, item):
        """Add a Item (track, release, artist, etc) to the database"""
        if item != None and isinstance(item, Item):
            # save without passing item_id, item should insert into the database if
            # it does not have an item_id and save is not passed one
            item.save(-1)

    def artist(self, artist_id):
        if artist_id == None:
            return None
        else:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM artists WHERE id = ? LIMIT 1', [ artist_id ])
            row = cur.fetchone()
            if row != None:
                artist = Artist(self)
                for key in row.keys():
                    artist.records[key] = row[key]
                return artist
            else:
                return None


    def artists(self, fields=None):
        """Return a list of Artist objects from the database base on fields
        If no fields then return all artist in database
        """
        sql = 'SELECT artists.* FROM artists LEFT JOIN releases ON artists.id = releases.artist LEFT JOIN tracks ON artists.id = tracks.artist'
        clauses = [ ]
        params = [ ]

        if isinstance(fields, list) and len(fields) > 0:
            for field in fields:
                clause = self.get_clause(field)

                if len(clause['sql']) < 1: # skip zero length sql
                    continue

                clauses.append(clause['sql'])
                params.extend(clause['params'])

        cur = self.conn.cursor()
        if len(clauses) > 0:
            cur.execute(' '.join([ sql, 'WHERE', 'AND '.join(clauses) ]), params)
        else:
            cur.execute(sql)

        artists = [ ]
        for row in cur:
            art = Artist(self)
            for key in row.keys():
                art.records[key] = row[key]
            artists.append(art)

        return artists

    def release(self, release_id):
        if release_id == None:
            return None
        else:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM releases WHERE id = ? LIMIT 1', [ release_id ])
            row = cur.fetchone()
            if row != None:
                release = Release(self)
                for key in row.keys():
                    release.records[key] = row[key]
                return release
            else:
                return None

    def releases(self, fields=None):
        """Return a list of release objects from the database base on fields
        If no fields then return all releases in database
        """
        # TODO: add support for various artist release search
        # need to join release track artists
        sql = 'SELECT releases.* FROM releases LEFT JOIN artists ON releases.artist = artists.id LEFT JOIN tracks ON releases.id = tracks.release'
        clauses = [ ]
        params = [ ]

        if isinstance(fields, list) and len(fields) > 0:
            for field in fields:
                clause = self.get_clause(field)

                if len(clause['sql']) < 1: # skip zero length sql
                    continue

                clauses.append(clause['sql'])
                params.extend(clause['params'])

        cur = self.conn.cursor()
        if len(clauses) > 0:
            cur.execute(' '.join([ sql, 'WHERE', ' AND '.join(clauses) ]), params)
        else:
            cur.execute(sql)

        releases = [ ]
        for row in cur:
            rel = Release(self)
            for key in row.keys():
                rel.records[key] = row[key]
            releases.append(rel)

        return releases


    def track(self, track_id):
        if track_id == None:
            return None
        else:
            cur = self.conn.cursor()
            cur.execute('SELECT * FROM tracks WHERE id = ? LIMIT 1', [ track_id ])
            row = cur.fetchone()
            if row != None:
                track = Track(self)
                for key in row.keys():
                    track.records[key] = row[key]
                return track
            else:
                return None

    def tracks(self, fields=None):
        """Return a list of track objects from the database base on fields
        If no fields then return all tracks in database
        """
        # TODO: add support for featured artist track search
        # need to join track track artists
        sql = 'SELECT tracks.* FROM tracks LEFT JOIN artists ON tracks.artist = artists.id LEFT JOIN releases ON tracks.release = releases.id'
        clauses = [ ]
        params = [ ]

        if isinstance(fields, list) and len(fields) > 0:
            for field in fields:
                clause = self.get_clause(field)

                if len(clause['sql']) < 1: # skip zero length sql
                    continue

                clauses.append(clause['sql'])
                params.extend(clause['params'])

        cur = self.conn.cursor()
        if len(clauses) > 0:
            cur.execute(' '.join([ sql, 'WHERE', 'AND '.join(clauses) ]), params)
        else:
            cur.execute(sql)

        tracks = [ ]
        for row in cur:
            trk = Track(self)
            for key in row.keys():
                trk.records[key] = row[key]
            tracks.append(trk)

        return tracks

# }}} end Library(BaseLibrary)

