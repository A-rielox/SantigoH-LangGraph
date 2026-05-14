from langchain_community.document_loaders import GoogleDriveLoader

# pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

credentials_path = "/home/arielox/dev/learning/SantiagoH/LangGraph/seccion5/credentials.json"
token_path = "/home/arielox/dev/learning/SantiagoH/LangGraph/seccion5/token.json"

loader = GoogleDriveLoader(
    folder_id="1ZTZGZs0ljso_Qz-VZLT3jN6Xdym58Z4X",
    credentials_path=credentials_path,
    token_path=token_path,
    recursive=True
)

documents = loader.load()

print(f"Metadatos: {documents[0].metadata}")
print(f"Contenido: {documents[0].page_content}")

