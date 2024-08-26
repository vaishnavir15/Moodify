# Moodify
---
### Overview

This repository contains an app called Moodify. **Moodify** is an app that curates a custom, specialized playlist for you based on your liked songs on Spotify and a user-inputted prompt. The playlist will be added directly to your Spotify account.

### How it was accomplished

This application integrates Spotify's API with a custom music recommendation system using a Retrieval-Augmented Generation (RAG) framework. It leverages FastAPI, ChromaDB, LangChain, and ColBERT to provide personalized song recommendations.

1. **Spotify API Integration**: The app uses the Spotify API to authenticate users, fetch their liked songs, and create playlists. The Spotipy library manages OAuth authentication and communicates with various Spotify endpoints to retrieve user data, song information, and audio features.

2. **Retrieval-Augmented Generation (RAG) Framework**: The app follows a RAG architecture to enhance the music recommendation process. It combines retrieval techniques with generation models to create a seamless recommendation flow. This involves retrieving relevant song data based on user input and generating personalized playlists that match the user's mood or preferences.

3. **LangChain for Orchestration**: LangChain orchestrates the retrieval and generation components, enabling smooth communication between different models and databases. It helps manage the workflow of embedding generation, data retrieval, and playlist creation, ensuring a cohesive RAG application.

4. **ChromaDB for Vector Storage**: ChromaDB acts as a vector database to store song metadata and audio features. It maintains separate collections for each user's text (lyrics and metadata) and audio data, allowing efficient querying and retrieval of song embeddings.

5. **Generating Embeddings with LLM and ColBERT**: The application uses ColBERT, a powerful embedding model, to generate dense vector representations of song lyrics and metadata. This approach allows the system to capture nuanced textual relationships and semantic similarities between songs. The BGEM3FlagModel (specifically the 'BAAI/bge-m3' model) is used for generating embeddings, representing textual and audio data in a high-dimensional space, which are then stored in ChromaDB for similarity searches.

6. **K-Nearest Neighbors (KNN) Search**: When a user searches for a mood or theme, the app performs a KNN search within ChromaDB to find the most similar songs based on the generated embeddings. This approach utilizes both text and audio collections to provide comprehensive results that reflect the user's desired mood or theme.

7. **Playlist Creation**: Based on the search results, the app generates a playlist by fetching song recommendations and adding tracks to the user's Spotify account. It ensures diversity by combining results from both the search and Spotify's recommendation endpoints.

By integrating a RAG approach with LangChain, ColBERT, and a large language model, this application provides a highly personalized music experience. It leverages advanced machine learning techniques to analyze and interpret user data, delivering tailored song recommendations based on mood or preference.

### Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/Panizghi/Moodify.git
   ```
2. Make a Python virtual environment and go into it
3. Install dependencies:
    ```bash
   pip install -r requirements.txt
   ```
4. Run the backend:
    ```bash
    uvicorn backend:app --host 127.0.0.1 --port 8235 --reload
    ```
5. Run the Moodiy RAG app in another command prompt:
    ```bash
   streamlit run app.py
   ```
---
Credit:

|Name|Email|
|----|-----|
|Vaishnavi Ratnasabapathy|vratnasa@uwaterloo.ca|
|Paniz Ojaghi|paniz.ojaghi@uwaterloo.ca|

MIT License

Copyright (c) 2024, Vaishnavi Ratnasabapathy, Paniz Ojaghi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
