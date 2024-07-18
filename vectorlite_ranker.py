from app import app, db
from models import Opportunity
import numpy as np
from vectorlite import VectorLite, Document

# Initialize vectorlite with your desired configuration
vector_db = VectorLite()

def load_vectors():
    with app.app_context():
        opportunities = Opportunity.query.all()
        documents = []
        for opportunity in opportunities:
            if opportunity.get_embedding_vector():
                documents.append(Document(
                    page_content=opportunity.long_text,
                    metadata={'id': opportunity.id}
                ))
        vector_db.create(documents)

# load_vectors()

def ranker(query_text):
    """
    This function performs a semantic search on the embeddings in the database and returns the 25 most similar opportunities.
    
    Args:
        query_text (str): The query text to compare against the embeddings in the database.
        
    Returns:
        list: A list of the 25 most similar opportunities.
    """
    # Perform semantic search
    results = vector_db.semantic_search(query_text, k=25)

    # Fetch the opportunities from the results
    top_opportunities = []
    for doc in results:
        opportunity = Opportunity.query.get(doc.metadata['id'])
        top_opportunities.append((opportunity, doc.metadata))

    return top_opportunities

if __name__ == "__main__":
    # Example usage
    query_text = "Example query text"  # Replace with your actual query text
    top_opportunities = ranker(query_text)
    for opportunity, metadata in top_opportunities:
        print(f"Opportunity ID: {opportunity.opportunity_id}, Similarity Score: {metadata}\n\n")
