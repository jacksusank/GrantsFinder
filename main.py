from app import app, db
from models import Opportunity

with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("Tables created successfully.")


if __name__ == '__main__':
    app.run(debug=True)