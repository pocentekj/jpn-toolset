CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    headword TEXT,
    reading TEXT,
    gloss TEXT
);

CREATE INDEX idx_headword ON words(headword);
CREATE INDEX idx_reading ON words(reading);
