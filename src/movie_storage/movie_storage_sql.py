from pathlib import Path
from sqlalchemy import create_engine, text


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "movies.db"
DB_URL = f"sqlite:///{DB_PATH}"

# Create the engine
engine = create_engine(DB_URL, echo=False)

def _init_db():
    """
    Create tables if they do not exist and enable foreign keys.
    """
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON;"))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """))

        connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS movies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        year INTEGER NOT NULL,
                        rating REAL NOT NULL,
                        poster_url TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        UNIQUE(user_id, title)
                    )
                """))
        connection.commit()

_init_db()


# -------------- Users --------------
def list_users():
    """
    Return a list of all users as [(id, name), ...]
    """
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, name FROM users ORDER BY name"))
        return result.fetchall()

def get_or_create_user(name: str) -> int:
    """
    Get a user ID by name, create user if it does not exist.
    """
    name = name.strip()
    if not name:
        raise ValueError("User name must not be empty.")

    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON;"))

        row = connection.execute(
            text("SELECT id FROM users WHERE name = :name"),
            {"name": name},
        ).fetchone()

        if row:
            return int(row[0])

        connection.execute(
            text("INSERT INTO users (name) VALUES (:name)"),
            {"name": name},
        )
        connection.commit()

        row = connection.execute(
            text("SELECT id FROM users WHERE name = :name"),
            {"name": name},
        ).fetchone()

        return int(row[0])


# -------------- Movies (per user) --------------
def list_movies(user_id: int):
    """
    Retrieve all movies from the database for a specific user.
    """
    with engine.connect() as connection:

        result = connection.execute(
            text("""
                SELECT title, year, rating, poster_url
                FROM movies
                WHERE user_id = :user_id
                ORDER BY title
                """),
                {"user_id": user_id},
        )

        rows = result.fetchall()

    return {
        row[0]: {"year": row[1], "rating": row[2], "poster_url": row[3]}
        for row in rows
    }

def add_movie(user_id: int, title: str, year: int, rating: float, poster_url: str | None = None):
    """Add a new movie to the database for a specific user."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                INSERT INTO movies (user_id, title, year, rating, poster_url)
                VALUES (:user_id,:title, :year, :rating, :poster_url)
                """),
        {
                    "user_id": user_id,
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster_url": poster_url,
                }
            )
            connection.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

def delete_movie(user_id: int, title: str) -> bool:
    """
    Delete a movie from the database for a specific user.
    """
    with engine.connect() as connection:

        result = connection.execute(
            text("DELETE FROM movies WHERE user_id = :user_id AND title = :title"),
            {"user_id": user_id, "title": title},
        )
        connection.commit()
        return result.rowcount > 0

def update_movie(user_id: int, title: str, rating: float) -> bool:
    """
    Update a movie's rating in the database for a specific user.
    """
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                UPDATE movies 
                SET rating = :rating 
                WHERE user_id = :user_id AND title = :title
            """),
{"user_id": user_id, "title": title, "rating": rating},
        )
        connection.commit()
        return result.rowcount > 0
