import sqlite3

SCHEMA = '''
PRAGMA foreign_keys = ON;

CREATE TABLE library (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    comment TEXT,
    favorite INTEGER NOT NULL DEFAULT 0,
    options TEXT,
    source_path TEXT UNIQUE
);

CREATE TABLE material (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    comment TEXT,
    favorite INTEGER NOT NULL DEFAULT 0,
    options TEXT,
    source_path TEXT NOT NULL UNIQUE,
    thumbnail BLOB
);

CREATE TABLE material_thumbnail (
    material_id INTEGER NOT NULL,
    engine_id TEXT NOT NULL,
    image BLOB NOT NULL,

    FOREIGN KEY (material_id) REFERENCES material(id) ON DELETE CASCADE
);

CREATE TABLE material_library (
    material_id INTEGER NOT NULL,
    library_id INTEGER NOT NULL,

    PRIMARY KEY (material_id, library_id),

    FOREIGN KEY (material_id) REFERENCES material(id) ON DELETE CASCADE,
    FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
);

CREATE TABLE map_type_tag (
    map_type INTEGER NOT NULL CHECK (map_type >= 0),
    tag TEXT NOT NULL,

    PRIMARY KEY (map_type, tag)
);

CREATE TABLE texture (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    role INTEGER,
    comment TEXT,
    favorite INTEGER NOT NULL DEFAULT 0,
    options TEXT,
    source_path TEXT NOT NULL UNIQUE,
    thumbnail BLOB
);

CREATE TABLE texture_library (
    texture_id INTEGER NOT NULL,
    library_id INTEGER NOT NULL,

    PRIMARY KEY (texture_id, library_id),

    FOREIGN KEY (texture_id) REFERENCES texture(id) ON DELETE CASCADE,
    FOREIGN KEY (library_id) REFERENCES library(id) ON DELETE CASCADE
);

CREATE TABLE texture_material (
    texture_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    role INTEGER,

    PRIMARY KEY (texture_id, material_id),

    FOREIGN KEY (texture_id) REFERENCES texture(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES material(id) ON DELETE CASCADE
);
'''

POPULATE_TAGS = 'INSERT INTO map_type_tag VALUES (?, ?)'


def createDatabase(file_path):
    from ..texture.map_type import DEFAULT_MAP_TYPE_TAGS

    connection = sqlite3.connect(file_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    connection.executescript(SCHEMA)

    for map_type, tags in DEFAULT_MAP_TYPE_TAGS.items():
        connection.executemany(POPULATE_TAGS, [(map_type, tag) for tag in tags])

    connection.commit()
    connection.close()
