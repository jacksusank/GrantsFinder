# init_db.py

from app import app, db

# Create an application context
with app.app_context():
    # Create all database tables
    db.create_all()

print("Database tables created successfully.")