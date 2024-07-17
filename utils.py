from sklearn.metrics.pairwise import cosine_similarity
from app import db
from models import Opportunity


def calculate_cosine_similarity(vector1, vector2):
    similarity = cosine_similarity([vector1], [vector2])[0][0]
    return similarity

def get_embedding_vectors():
    opportunities = Opportunity.query.all()
    embeddings = [(opportunity.opportunity_id, opportunity.get_embedding_vector()) for opportunity in opportunities]
    return embeddings

def add_opportunity(opportunity_id, long_text, embedding_vector):
    opportunity = Opportunity(opportunity_id=opportunity_id, long_text=long_text)
    opportunity.set_embedding_vector(embedding_vector)

    db.session.add(opportunity)
    db.session.commit()

def delete_opportunity(opportunity_id):
    opportunity = Opportunity.query.filter_by(opportunity_id=opportunity_id).first()
    db.session.delete(opportunity)
    db.session.commit()