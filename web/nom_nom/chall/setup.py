import os, secrets, sqlite3
from werkzeug.security import generate_password_hash


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    used_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_reset_tokens_user_created
ON reset_tokens(user_id, created_at);
"""


def initialize_database(db_path: str = "./db/lite.db", victim_email: str | None = None) -> None:
    with sqlite3.connect(db_path) as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript(SCHEMA_SQL)

        target_email = (victim_email or os.getenv("VICTIM_EMAIL", "blackhole@dragonsec.si")).strip().lower()
        if target_email:
            victim_user = db.execute(
                "SELECT id FROM users WHERE email = ?",
                (target_email,),
            ).fetchone()

            if victim_user is None:
                seeded_password = secrets.token_urlsafe(18)
                db.execute(
                    "INSERT INTO users(email, password_hash) VALUES (?, ?)",
                    (target_email, generate_password_hash(seeded_password)),
                )

        db.commit()


if __name__ == "__main__":
    initialize_database()
