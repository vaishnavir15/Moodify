import unittest
from unittest.mock import patch, MagicMock
from app.managers.spotify_manager import SpotifyManager
from langchain_core.documents import Document
from langchain_chroma import Chroma
from models.embedding import embedding_function
from app.managers.chroma_manager import ChromaManager
class TestChromaService(unittest.TestCase):

    @patch('app.services.chroma_service.SpotifyManager')
    @patch('app.services.chroma_service.Chroma')
    @patch('app.services.chroma_service.embedding_function')
    def setUp(self, mock_embedding_function, mock_chroma, mock_spotify_manager):
        # Mock SpotifyManager instance and its attributes
        self.mock_spotify_manager = mock_spotify_manager.return_value
        self.mock_spotify_manager.username = "test_user"

        # Initialize ChromaService with mocked dependencies
        self.service = ChromaManager()

    def test_get_text_collection(self):
        # Test get_text_collection method
        vector_store = self.service.get_text_collection()
        self.assertEqual(vector_store.collection_name, "test_user_text_collection")
        self.assertEqual(vector_store.persist_directory, "./chroma_langchain_db")

    def test_get_audio_collection(self):
        # Test get_audio_collection method
        vector_store = self.service.get_audio_collection()
        self.assertEqual(vector_store.collection_name, "test_user_audio_collection")
        self.assertEqual(vector_store.persist_directory, "./chroma_langchain_db")

    def test_filter_non_metadata(self):
        # Test filter_non_metadata method
        metadata = {"title": "Song", "artist": None, "album": "Album"}
        filtered_metadata = self.service.filter_non_metadata(metadata)
        self.assertEqual(filtered_metadata, {"title": "Song", "album": "Album"})

    @patch('langchain_core.documents.Document')
    def test_create_text_document(self, mock_document):
        # Test create_text_document method
        text = "Sample text"
        metadata = {"title": "Document", "author": None}
        document = self.service.create_text_document(text, metadata)
        mock_document.assert_called_once_with(text=text, metadata={"title": "Document"})
        self.assertEqual(document, mock_document.return_value)

    @patch('langchain_core.documents.Document')
    def test_create_audio_document(self, mock_document):
        # Test create_audio_document method
        audio_path = "/path/to/audio.mp3"
        metadata = {"title": "Audio", "artist": None}
        document = self.service.create_audio_document(audio_path, metadata)
        mock_document.assert_called_once_with(audio_path=audio_path, metadata={"title": "Audio"})
        self.assertEqual(document, mock_document.return_value)


if __name__ == '__main__':
    unittest.main()
