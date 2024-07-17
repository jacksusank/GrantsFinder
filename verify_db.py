from app import app, db
from models import Opportunity
from utils import delete_opportunity

with app.app_context():
    # Delete the last 200 opportunities in my database
    opportunities = Opportunity.query.all()
    for opportunity in opportunities[-200:]:
        opportunity_id = opportunity.opportunity_id
        delete_opportunity(opportunity_id)
    db.session.commit()






