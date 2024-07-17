from utils import add_opportunity
from sentence_transformers import SentenceTransformer
from XMLScanner import documents
from app import app, db # Import Flask app and db

# Ensure app context is active
with app.app_context():
    # Extract page contents and opportunity IDs
    page_contents_list = [doc["page_content"] for doc in documents]
    opportunity_ids_list = [doc["opportunity_id"] for doc in documents]

    # Initialize the model
    print("Initializing the model...")
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    print("Model initialized successfully!")

    # Encode the page contents to get embeddings
    if page_contents_list:
        embeddings_list = model.encode(page_contents_list, show_progress_bar=True)
        print("Embeddings generated successfully!")
    else:
        print("No page contents found. Exiting...")
        exit()


    # Convert embeddings to list format
    formatted_embeddings_list = [embedding.tolist() for embedding in embeddings_list]

    # Add each opportunity to the database
    for i in range(len(documents)):
        # print(f"Adding opportunity {i+1} to the database...")
        opportunity_id = opportunity_ids_list[i]
        page_content = page_contents_list[i]
        embedding_vector = formatted_embeddings_list[i]
        add_opportunity(opportunity_id, page_content, embedding_vector)

    print("All opportunities added to the database successfully!")