
from langchain_community.embeddings import HuggingFaceBgeEmbeddings 


class Embedding():
    def __init__(self):
        self.model = "BAAI/bge-m3"
        self.embedding_fucntion = HuggingFaceBgeEmbeddings(model_name=self.model)

    def get_embedding_function(self):
        return self.embedding_fucntion
    
    def store_embedding(self, document, collection_name): 
        pass # check later 

