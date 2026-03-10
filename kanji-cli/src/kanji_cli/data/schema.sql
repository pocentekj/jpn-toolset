CREATE TABLE IF NOT EXISTS kanjis (
    kanji TEXT PRIMARY KEY CHECK (length(kanji) >= 1),
    meaning TEXT,
    on_readings TEXT,
    on_readings_norm TEXT,
    kun_readings TEXT,
    name_readings TEXT,
    components TEXT,
    freq INTEGER NOT NULL CHECK (freq > 0)
);

CREATE INDEX IF NOT EXISTS idx_kanjis_freq ON kanjis(freq);
CREATE INDEX IF NOT EXISTS idx_kanjis_on_readings_norm ON kanjis(on_readings_norm);
