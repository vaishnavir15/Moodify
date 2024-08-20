import os

def create_project_structure():
    # Define the directory structure
    structure = [
        "app/routes",
        "app/services",
        "app/models",
        "app/utils",
        "tests"
    ]

    # Define the files to be created
    files = {
        "app/__init__.py": "",
        "app/main.py": "",
        "app/routes/__init__.py": "",
        "app/routes/auth.py": "",
        "app/routes/lyrics.py": "",
        "app/routes/embeddings.py": "",
        "app/routes/playlists.py": "",
        "app/services/__init__.py": "",
        "app/services/spotify_service.py": "",
        "app/services/chroma_service.py": "",
        "app/services/genius_service.py": "",
        "app/models/__init__.py": "",
        "app/models/user.py": "",
        "app/models/document.py": "",
        "app/utils/__init__.py": "",
        "app/utils/logging.py": "",
        "app/utils/helpers.py": "",
        "app/config.py": "",
        "tests/__init__.py": "",
        "tests/test_auth.py": "",
        "tests/test_lyrics.py": "",
        "tests/test_embeddings.py": "",
        "tests/test_playlists.py": "",
        ".env": "",
        "requirements.txt": "",
        "README.md": "",
        "run.py": ""
    }

    # Create the directories
    for directory in structure:
        os.makedirs(directory, exist_ok=True)

    # Create the files
    for file_path, content in files.items():
        with open(file_path, "w") as f:
            f.write(content)

    structure, files



def convert_strings_to_lists(metadata):
    """
    Convert JSON strings in the metadata back to lists after retrieving them from ChromaDB.
    """
    new_metadata = {}
    for key, value in metadata.items():
        try:
            # Try to convert the string back to a list
            new_metadata[key] = json.loads(value) if isinstance(value, str) else value
        except json.JSONDecodeError:
            # If it's not a valid JSON string, keep the value as is
            new_metadata[key] = value
    return new_metadata


def convert_lists_to_strings(metadata):
    """
    Convert lists in the metadata to JSON strings before storing them in ChromaDB.
    Convert None values to empty strings.
    """
    new_metadata = {}
    for key, value in metadata.items():
        if value is None:
            new_metadata[key] = ""  # Convert None to empty string
        elif isinstance(value, list):
            new_metadata[key] = json.dumps(value)
        elif isinstance(value, dict):
            new_metadata[key] = convert_lists_to_strings(value)  # Recursively handle nested dictionaries
        else:
            new_metadata[key] = value
    return new_metadata
