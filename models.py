from app import db
from sqlalchemy.dialects.postgresql import ARRAY


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, unique=True, nullable=False)
    long_text = db.Column(db.Text, nullable=False)
    embedding_vector = db.Column(db.JSON, nullable=True) # Store as JSON

    def __repr__(self):
        return f'Opportunity: {self.opportunity_id}'

    def set_embedding_vector(self, embedding_vector):
        self.embedding_vector = embedding_vector

    def get_embedding_vector(self):
        return self.embedding_vector
    
    # String version of the Opportunity object that includes the id, opportunity_id, and the long_text
    def __str__(self):
        return f'Opportunity: {self.id}, {self.opportunity_id}, {self.long_text}'


class OptimizedOpportunity(db.Model):
    __bind_key__ = 'optimized'
    __tablename__ = 'optimized_opportunity'
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, unique=True, nullable=False)
    long_text = db.Column(db.Text, nullable=False)  
    embedding_vector = db.Column(db.JSON, nullable=True) # Store as JSON

    def __repr__(self):
        return f'OptimizedOpportunity: {self.opportunity_id}'

    def set_embedding_vector(self, embedding_vector):
        self.embedding_vector = embedding_vector

    def get_embedding_vector(self):
        return self.embedding_vector
    
    # String version of the OptimizedOpportunity object that includes the id, opportunity_id, and the long_text
    def __str__(self):
        return f'OptimizedOpportunity: {self.id}, {self.opportunity_id}, {self.long_text}'