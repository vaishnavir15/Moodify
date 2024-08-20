import streamlit as st
import requests
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

st.set_page_config(page_title="LangChain: Chat with search", page_icon="🦜")
st.title("🦜 LangChain: Chat with search")

# Custom class to interact with FastAPI endpoints
class FastAPILLM:
    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url

    def call_api(self, endpoint, params=None, data=None):
        try:
            url = f"{self.endpoint_url}/{endpoint}"
            if data:
                response = requests.post(url, json=data)
            else:
                response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API call failed: {str(e)}")
            return {"error": str(e)}

    def get_lyrics(self, artist, title):
        return self.call_api("lyrics", params={"artist": artist, "title": title})

    def store_embeddings(self, limit):
        return self.call_api("store_embeddings", params={"limit": limit})

    def create_playlist(self, query, k):
        return self.call_api("create_playlist", params={"query": query, "k": k})

    def get_recommendations(self, query, k):
        return self.call_api("get_recommendations", params={"query": query, "k": k})

# FastAPI URL input
fastapi_url = st.sidebar.text_input("FastAPI URL", value="http://localhost:8235")

if not fastapi_url:
    st.error("Please provide a valid FastAPI URL.")
    st.stop()

llm = FastAPILLM(fastapi_url)

# Initialize chat history and memory
msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
    msgs.clear()
    msgs.add_ai_message("How can I help you?")
    st.session_state.steps = {}

avatars = {"human": "user", "ai": "assistant"}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):
        st.write(msg.content)

if prompt := st.chat_input(placeholder="Enter your query here..."):
    st.chat_message("user").write(prompt)
    st.session_state.steps = {}

    # Example: Get user input for lyrics
    artist = st.text_input("Artist name:", value="Adele")
    title = st.text_input("Song title:", value="Hello")
    
    if st.button("Get Lyrics"):
        response = llm.get_lyrics(artist=artist, title=title)
        if "error" not in response:
            st.chat_message("assistant").write(response.get("lyrics", "No lyrics found."))
        else:
            st.chat_message("assistant").write(f"Error: {response['error']}")

    # Example: Store embeddings with user-defined limit
    limit = st.number_input("Number of liked songs to fetch:", min_value=1, max_value=100, value=50)
    
    if st.button("Store Embeddings"):
        embeddings_response = llm.store_embeddings(limit=limit)
        if "error" not in embeddings_response:
            st.write(f"Stored embeddings response: {embeddings_response}")
        else:
            st.write(f"Error: {embeddings_response['error']}")

    # Example: Create a playlist with user-defined query and number of results
    playlist_query = st.text_input("Playlist query:", value="Happy songs")
    k = st.number_input("Number of songs to fetch:", min_value=1, max_value=50, value=5)
    
    if st.button("Create Playlist"):
        playlist_response = llm.create_playlist(query=playlist_query, k=k)
        if "error" not in playlist_response:
            st.write(f"Playlist creation response: {playlist_response}")
        else:
            st.write(f"Error: {playlist_response['error']}")

    # Example: Get song recommendations with user-defined query and number of results
    rec_query = st.text_input("Recommendation query:", value="Chill music")
    k_rec = st.number_input("Number of recommendations:", min_value=1, max_value=50, value=5)
    
    if st.button("Get Recommendations"):
        recommendations_response = llm.get_recommendations(query=rec_query, k=k_rec)
        if "error" not in recommendations_response:
            st.write(f"Recommendations: {recommendations_response}")
        else:
            st.write(f"Error: {recommendations_response['error']}")
