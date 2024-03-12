CREATE TABLE traditions (
    id SERIAL PRIMARY KEY,
    tradition_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    archived BOOLEAN DEFAULT FALSE,
    note TEXT,
    is_public BOOLEAN DEFAULT FALSE
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tradition_id INT NOT NULL,
    "user" VARCHAR(255) NOT NULL,
    FOREIGN KEY (tradition_id) REFERENCES traditions(id) ON DELETE CASCADE
);

CREATE TABLE manuscripts (
    id SERIAL PRIMARY KEY,
    manuscript_name VARCHAR(255) NOT NULL UNIQUE,
    tradition_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    note TEXT,
    archived BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (tradition_id) REFERENCES traditions(id) ON DELETE CASCADE
);

CREATE TABLE folios (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    manuscript_id INT NOT NULL,
    folio_name VARCHAR(255) NOT NULL UNIQUE,
    position_in_manuscript INT NOT NULL,
    image_url TEXT,
    FOREIGN KEY (manuscript_id) REFERENCES manuscripts(id) ON DELETE CASCADE
);

CREATE TABLE columns (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    folio_id INT NOT NULL,
    position_in_folio INT NOT NULL,
    FOREIGN KEY (folio_id) REFERENCES folios(id) ON DELETE CASCADE,
    UNIQUE (folio_id, position_in_folio)
);

CREATE TABLE column_lines (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    position_in_column INT NOT NULL,
    column_id INT NOT NULL,
    FOREIGN KEY (column_id) REFERENCES columns(id) ON DELETE CASCADE,
    UNIQUE (column_id, position_in_column)
);

CREATE TABLE chapters (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    chapter_number INT NOT NULL,
    tradition_id INT NOT NULL,
    FOREIGN KEY (tradition_id) REFERENCES traditions(id) ON DELETE CASCADE,
    UNIQUE (tradition_id, chapter_number)
);

CREATE TABLE verses (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    verse_number INT NOT NULL,
    chapter_id INT NOT NULL,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
    UNIQUE (chapter_id, verse_number)
);

CREATE TABLE readings (
    id SERIAL PRIMARY KEY,
    reading TEXT NOT NULL,
    is_xml BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    line_id INT NOT NULL,
    verse_id INT,
    position_in_line INT NOT NULL,
    position_in_verse INT,
    FOREIGN KEY (line_id) REFERENCES column_lines(id) ON DELETE CASCADE,
    FOREIGN KEY (verse_id) REFERENCES verses(id),
    UNIQUE (line_id, position_in_line)
);

CREATE TABLE reading_notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL,
    reading_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    FOREIGN KEY (reading_id) REFERENCES readings(id) ON DELETE CASCADE
);

CREATE TABLE translation_notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL,
    reading_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    FOREIGN KEY (reading_id) REFERENCES readings(id) ON DELETE CASCADE
);

CREATE TABLE verse_notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL,
    verse_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    FOREIGN KEY (verse_id) REFERENCES verses(id) ON DELETE CASCADE
);

CREATE TABLE line_notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL,
    line_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    FOREIGN KEY (line_id) REFERENCES column_lines(id) ON DELETE CASCADE
);

CREATE TABLE morphological_analysis (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    reading_id INT NOT NULL,
    POS VARCHAR(255) NOT NULL,
    lemma VARCHAR(255) NOT NULL,
    gender VARCHAR(255),
    morpho_number VARCHAR(255),
    morpho_case VARCHAR(255),
    mood VARCHAR(255),
    voice VARCHAR(255),
    tense VARCHAR(255),
    FOREIGN KEY (reading_id) REFERENCES readings(id)
);

CREATE OR REPLACE FUNCTION permissions_traditions_before_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO permissions (tradition_id, "user") VALUES (NEW.id, NEW.created_by);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER permissions_traditions_before_insert_trigger
AFTER INSERT ON traditions
FOR EACH ROW
EXECUTE FUNCTION permissions_traditions_before_insert();
