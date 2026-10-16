from app import app
from database import initialize_database


if __name__ == "__main__":
    initialize_database(app)
    print(f"Database initialized at {app.config['DATABASE_PATH']}")
