import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path("touchgrass.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS flock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            common_name TEXT NOT NULL UNIQUE,
            scientific_name TEXT NOT NULL,
            description TEXT,
            xp INTEGER NOT NULL DEFAULT 0,
            times_identified INTEGER NOT NULL DEFAULT 0,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            image_url TEXT
        )
    """)

    columns = connection.execute(
        "PRAGMA table_info(flock)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "image_url" not in column_names:
        connection.execute(
            "ALTER TABLE flock ADD COLUMN image_url TEXT"
        )

    if "description" not in column_names:
        connection.execute(
            "ALTER TABLE flock ADD COLUMN description TEXT"
        )

    connection.execute("""
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_xp INTEGER NOT NULL DEFAULT 0
        )
    """)

    connection.execute("""
        INSERT OR IGNORE INTO player (id, total_xp)
        VALUES (1, 0)
    """)

    connection.commit()
    connection.close()


def get_level(total_xp):
    if total_xp >= 400:
        return "MAX"

    return total_xp // 100


def add_discovery(
    common_name,
    scientific_name,
    image_url=None,
    description=None,
):
    connection = get_connection()

    now = datetime.now(timezone.utc).isoformat()

    existing = connection.execute(
        """
        SELECT *
        FROM flock
        WHERE common_name = ?
        """,
        (common_name,),
    ).fetchone()

    if existing:
        xp_earned = 25

        connection.execute(
            """
            UPDATE flock
            SET
                xp = xp + ?,
                times_identified = times_identified + 1,
                last_seen_at = ?,
                image_url = COALESCE(image_url, ?),
                description = COALESCE(description, ?)
            WHERE common_name = ?
            """,
            (
                xp_earned,
                now,
                image_url,
                description,
                common_name,
            ),
        )

        new_discovery = False

    else:
        xp_earned = 100

        connection.execute(
            """
            INSERT INTO flock (
                common_name,
                scientific_name,
                description,
                xp,
                times_identified,
                first_seen_at,
                last_seen_at,
                image_url
            )
            VALUES (?, ?, ?, ?, 1, ?, ?, ?)
            """,
            (
                common_name,
                scientific_name,
                description,
                xp_earned,
                now,
                now,
                image_url,
            ),
        )

        new_discovery = True

    connection.execute(
        """
        UPDATE player
        SET total_xp = total_xp + ?
        WHERE id = 1
        """,
        (xp_earned,),
    )

    player = connection.execute(
        """
        SELECT total_xp
        FROM player
        WHERE id = 1
        """
    ).fetchone()

    bird = connection.execute(
        """
        SELECT *
        FROM flock
        WHERE common_name = ?
        """,
        (common_name,),
    ).fetchone()

    connection.commit()
    connection.close()

    total_xp = player["total_xp"]

    return {
        "added": True,
        "new_discovery": new_discovery,
        "xp_earned": xp_earned,
        "total_xp": total_xp,
        "level": get_level(total_xp),
        "bird_xp": bird["xp"],
        "times_identified": bird["times_identified"],
    }


def update_bird_image(common_name, image_url):
    connection = get_connection()

    connection.execute(
        """
        UPDATE flock
        SET image_url = ?
        WHERE common_name = ?
        """,
        (
            image_url,
            common_name,
        ),
    )

    connection.commit()
    connection.close()


def update_bird_description(common_name, description):
    connection = get_connection()

    connection.execute(
        """
        UPDATE flock
        SET description = ?
        WHERE common_name = ?
        """,
        (
            description,
            common_name,
        ),
    )

    connection.commit()
    connection.close()


def get_flock():
    connection = get_connection()

    player = connection.execute(
        """
        SELECT total_xp
        FROM player
        WHERE id = 1
        """
    ).fetchone()

    birds = connection.execute(
        """
        SELECT
            id,
            common_name,
            scientific_name,
            description,
            xp,
            times_identified,
            first_seen_at,
            last_seen_at,
            image_url
        FROM flock
        ORDER BY first_seen_at ASC
        """
    ).fetchall()

    connection.close()

    total_xp = player["total_xp"]

    return {
        "total_birds": len(birds),
        "total_xp": total_xp,
        "level": get_level(total_xp),
        "birds": [dict(bird) for bird in birds],
    }
