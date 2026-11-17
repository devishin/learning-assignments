-- Sports club database — schema
PRAGMA foreign_keys = ON;

CREATE TABLE members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    birth_date TEXT NOT NULL,
    phone TEXT NOT NULL,
    joined_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TRIGGER members_age_check_insert
BEFORE INSERT ON members
FOR EACH ROW
WHEN (julianday('now') - julianday(NEW.birth_date)) / 365.25 < 14
BEGIN
    SELECT RAISE(ABORT, 'member age must be at least 14 years');
END;

CREATE TRIGGER members_age_check_update
BEFORE UPDATE OF birth_date ON members
FOR EACH ROW
WHEN (julianday('now') - julianday(NEW.birth_date)) / 365.25 < 14
BEGIN
    SELECT RAISE(ABORT, 'member age must be at least 14 years');
END;

CREATE TABLE trainers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    specialization TEXT NOT NULL,
    hired_at TEXT NOT NULL
);

CREATE TABLE membership_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    duration_days INTEGER NOT NULL,
    price REAL NOT NULL,
    CHECK (duration_days > 0),
    CHECK (price > 0)
);

CREATE TABLE memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    membership_type_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY (membership_type_id) REFERENCES membership_types(id),
    CHECK (julianday(end_date) > julianday(start_date))
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainer_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    room TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    FOREIGN KEY (trainer_id) REFERENCES trainers(id),
    CHECK (capacity > 0),
    CHECK (julianday(ends_at) > julianday(starts_at))
);

CREATE TABLE class_enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    enrolled_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    UNIQUE (member_id, class_id)
);

CREATE TABLE visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    class_id INTEGER,
    visited_at TEXT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    membership_id INTEGER,
    amount REAL NOT NULL,
    paid_at TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY (membership_id) REFERENCES memberships(id) ON DELETE SET NULL,
    CHECK (amount > 0)
);

CREATE INDEX idx_memberships_member_id ON memberships(member_id);
CREATE INDEX idx_class_enrollments_class_id ON class_enrollments(class_id);
CREATE INDEX idx_visits_member_id ON visits(member_id);
CREATE INDEX idx_visits_visited_at ON visits(visited_at);
CREATE INDEX idx_classes_trainer_id ON classes(trainer_id);
CREATE INDEX idx_classes_starts_at ON classes(starts_at);