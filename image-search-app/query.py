import chromadb

DB_PATH=r"image_caption_vdb"


class ChromaDB():
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_PATH)
    
    def initialize_collection(self):
        collection = self.client.get_collection(name="embed_caption_collection",
                                                embedding_function=None,
                                                data_loader=None)
        return collection
    
    def query_collection(self, query, n_results):
        collection = self.initialize_collection()
        results = collection.query(query_texts=[query], n_results=n_results,include=["distances", "metadatas"])
        return results