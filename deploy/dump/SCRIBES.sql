/* Structure for scribes database */
DROP DATABASE IF EXISTS `scribes`;

CREATE DATABASE IF NOT EXISTS `scribes` /*!40100 DEFAULT CHARACTER SET utf8 */;


USE `scribes`;



CREATE TABLE traditions
(
    id INT NOT NULL AUTO_INCREMENT,
    tradition_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    archived BIT DEFAULT 0,
    note TEXT,
    is_public BINARY DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE (tradition_name)
);


CREATE TABLE permissions
(
    id INT NOT NULL AUTO_INCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tradition_id INT NOT NULL,
    user VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (tradition_id) REFERENCES traditions(id) ON DELETE CASCADE
);


CREATE TABLE manuscripts
(
    id INT NOT NULL AUTO_INCREMENT,
    manuscript_name VARCHAR(255) NOT NULL,
    tradition_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    note TEXT,
    archived BINARY DEFAULT 0,
    PRIMARY KEY (id),
    FOREIGN KEY (tradition_id) REFERENCES traditions(id) ON DELETE CASCADE,
    UNIQUE (manuscript_name)
);


CREATE TABLE folios
(
    id INT NOT NULL AUTO_INCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    manuscript_id INT NOT NULL,
    folio_name VARCHAR(255) NOT NULL,
    position_in_manuscript INT NOT NULL,
    image_url TEXT DEFAULT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (manuscript_id) REFERENCES manuscripts(id) ON DELETE CASCADE,
    UNIQUE (folio_name)
);


CREATE TABLE columns
(
    id INT NOT NULL AUTO_INCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    folio_id INT NOT NULL,
    position_in_folio INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (folio_id) REFERENCES folios(id) ON DELETE CASCADE,
    UNIQUE (folio_id, position_in_folio)
);


CREATE TABLE column_lines
(
    id INT NOT NULL AUTO_INCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    position_in_column INT NOT NULL,
    column_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (column_id) REFERENCES columns(id) ON DELETE CASCADE,
    UNIQUE (column_id, position_in_column)
);


CREATE TABLE chapters
(
    id INT NOT NULL AUTO_INCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    chapter_number INT NOT NULL,
    tradition_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (tradition_id) REFERENCES traditions(id) ON DELETE CASCADE,
    UNIQUE (tradition_id, chapter_number)
);


CREATE TABLE verses
(
    id INT NOT NULL AUTO_INCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    verse_number INT NOT NULL,
    chapter_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
    UNIQUE (chapter_id, verse_number)
);



CREATE TABLE readings
(
    id INT NOT NULL AUTO_INCREMENT,
    reading TEXT NOT NULL,
    is_xml BINARY NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    line_id INT NOT NULL,
    verse_id INT,
    position_in_line INT NOT NULL,
    position_in_verse INT,
    PRIMARY KEY (id),
    FOREIGN KEY (line_id) REFERENCES column_lines(id) ON DELETE CASCADE,
    FOREIGN KEY (verse_id) REFERENCES verses(id),
    UNIQUE (line_id, position_in_line)
);


CREATE TABLE reading_notes
(
    id INT NOT NULL AUTO_INCREMENT,
    note TEXT NOT NULL,
    reading_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (reading_id) REFERENCES readings(id) ON DELETE CASCADE
);



CREATE TABLE translation_notes
(
    id INT NOT NULL AUTO_INCREMENT,
    note TEXT NOT NULL,
    reading_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (reading_id) REFERENCES readings(id) ON DELETE CASCADE
);


CREATE TABLE verse_notes
(
    id INT NOT NULL AUTO_INCREMENT,
    note TEXT NOT NULL,
    verse_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (verse_id) REFERENCES verses(id) ON DELETE CASCADE
);


CREATE TABLE line_notes
(
    id INT NOT NULL AUTO_INCREMENT,
    note TEXT NOT NULL,
    line_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (line_id) REFERENCES column_lines(id) ON DELETE CASCADE
);


CREATE TABLE morphological_analysis
(
    id INT NOT NULL AUTO_INCREMENT,
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
    PRIMARY KEY (id),
    FOREIGN KEY (reading_id) REFERENCES readings(id)
);




CREATE TRIGGER `permissions_traditions_BEFORE_INSERT` AFTER INSERT ON `traditions` FOR EACH ROW
    INSERT INTO permissions (tradition_id, user) VALUES (NEW.id, NEW.created_by);
