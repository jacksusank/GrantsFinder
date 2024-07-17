from app import app, db
from models import Opportunity

with app.app_context():
    # Create a new opportunity instance
    opportunity = Opportunity(opportunity_id=123456, long_text='Sample text', embedding_vector=[0.1, 0.2, 0.3])

    # Add the opportunity to the session
    db.session.add(opportunity)

    # Commit the session
    db.session.commit()

    # Query the database to verify
    opportunities = Opportunity.query.all()
    print(opportunities)