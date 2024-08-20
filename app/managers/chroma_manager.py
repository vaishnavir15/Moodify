from app.managers.spotify_manager import SpotifyManager
from langchain_core.documents import Document
from langchain_chroma import Chroma

from models.embedding import embedding_function

class ChromaManager():
    def __init__(self):
        self.spotify_manager = SpotifyManager()
        self.username = self.spotify_manager.username

    def get_text_collection(self):
    # Create a unique collection name for textual data based on user ID
        collection_name = f"{self.username}_text_collection"
        
        # Initialize Chroma vector store for text data with the embedding function
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory="./chroma_langchain_db"
        )
        
        return vector_store
    
    def get_audio_collection(self):
        # Create a unique collection name for audio data based on user ID
        collection_name = f"{self.username}_audio_collection"
        
        # Initialize Chroma vector store for audio data with the embedding function
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory="./chroma_langchain_db"
        )
        
        return vector_store
    
    def filter_non_metadata(self ,metadata):
       if isinstance(metadata, dict):
            return {key: value for key, value in metadata.items() if value is not None}


    def create_text_document(self, text, metadata):
        # test need 
        # Filter out non-metadata fields
        metadata = self.filter_non_metadata(metadata)
        
        # Create a document object with the text and metadata
        document = Document(
            text=text,
            metadata=metadata
        )
        
        return document
    
    def create_audio_document(self, audio_path, metadata):
        # Filter out non-metadata fields
        metadata = self.filter_non_metadata(metadata)
        
        # Create a document object with the audio path and metadata
        document = Document(
            audio_path=audio_path,
            metadata=metadata
        )
        
        return document
    

    
