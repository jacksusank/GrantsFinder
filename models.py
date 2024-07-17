from app import db

class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, unique=True, nullable=False)
    long_text = db.Column(db.Text, nullable=False)
    embedding_vector = db.Column(db.JSON, nullable=True)  # Store as JSON

    def __repr__(self):
        return f'Opportunity: {self.opportunity_id}'

    def set_embedding_vector(self, embedding_vector):
        self.embedding_vector = embedding_vector

    def get_embedding_vector(self):
        return self.embedding_vector