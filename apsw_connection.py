import vectorlite_py
import apsw
import numpy as np

# Connect to your existing SQLite database
conn = apsw.Connection('ragrants.db')
conn.enable_load_extension(True)
conn.load_extension(vectorlite_py.vectorlite_path())

cursor = conn.cursor()
# Check if vectorlite is loaded
print(cursor.execute('select vectorlite_info()').fetchall())

# Create a virtual table for the vectors
DIM = 768 
NUM_ELEMENTS = 4615  # Replace with the number of vectors you have
cursor.execute(f'create virtual table opportunity_vectors using vectorlite(embedding float32[{DIM}], hnsw(max_elements={NUM_ELEMENTS}))')

# Insert existing data into the new virtual table
existing_data = cursor.execute('SELECT id, embedding_vector FROM opportunities').fetchall()
cursor.executemany('INSERT INTO opportunity_vectors(rowid, embedding) VALUES (?, ?)', [(row[0], row[1]) for row in existing_data])

# Query the virtual table
result = cursor.execute('select vector_to_json(embedding) from opportunity_vectors where rowid = 1234').fetchone()
print(f'vector at rowid 1234: {result[0]}')

# Find 10 approximate nearest neighbors of the vector at rowid 0
first_vector = cursor.execute('SELECT embedding FROM opportunity_vectors WHERE rowid = 0').fetchone()[0]
result = cursor.execute('select rowid, distance from opportunity_vectors where knn_search(embedding, knn_param(?, 10))', [first_vector]).fetchall()
print(f'10 nearest neighbors of row 0 is {result}')

conn.close()
