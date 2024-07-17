from app import app, db
from sqlalchemy import text

with app.app_context():
    # Execute the VACUUM command to reduce the file size
    with db.engine.connect() as connection:
        connection.execute(text('VACUUM'))
    print("Database vacuumed successfully.")