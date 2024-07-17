from app import app, db
from models import Opportunity
from utils import delete_opportunity

with app.app_context():
    opportunities = Opportunity.query.all()
    for opportunity in opportunities:
        delete_opportunity(opportunity.opportunity_id)

    db.session.commit()

with app.app_context():
    opportunities = Opportunity.query.all()

print(len(opportunities))

if len(opportunities) == 0:
    print("Database cleared successfully.")
