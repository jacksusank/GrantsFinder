# init_db.py

from app import app, db

# Create an application context
with app.app_context():
    # Create all database tables
    db.create_all()
    
    # Create all tables for the new database bind
    engine = db.engines['optimized']
    with engine.connect() as connection:
        db.metadata.create_all(connection)

    print("Databases initialized successfully.")