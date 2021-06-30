import sqlite3

SCHEMA = '''
PRAGMA foreign_keys = ON;

CREATE TABLE library (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    comment TEXT,
    favorite INTEGER NOT NULL DEFAULT 0,
    options TEXT,
    path TEXT
);

CREATE TABLE material (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    comment TEXT,
    favorite INTEGER NOT NULL DEFAULT 0,
    options TEXT,
    path TEXT
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

CREATE TABLE map_types_labels (
    map_type TEXT NOT NULL,
    label TEXT NOT NULL UNIQUE,

    PRIMARY KEY (map_type, label)
);

CREATE TABLE texture (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    role TEXT,
    comment TEXT,
    favorite INTEGER NOT NULL DEFAULT 0,
    options TEXT,
    path TEXT NOT NULL UNIQUE,
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
    role TEXT,

    PRIMARY KEY (texture_id, material_id),

    FOREIGN KEY (texture_id) REFERENCES texture(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES material(id) ON DELETE CASCADE
);
'''

POPULATE_LABELS = 'INSERT INTO map_types_labels VALUES (?, ?)'


def createDatabase(file_path):
    from hammer_tools.material_library.map_type import DEFAULT_MAP_TYPES_LABELS

    connection = sqlite3.connect(file_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    connection.executescript(SCHEMA)
    for map_type, labels in DEFAULT_MAP_TYPES_LABELS.items():
        connection.executemany(POPULATE_LABELS, [(map_type, label) for label in labels])

    connection.commit()
    connection.close()
