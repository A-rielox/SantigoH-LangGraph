# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# pip install chromadb

loader = PyPDFDirectoryLoader("/home/arielox/dev/learning/SantiagoH/LangGraph/seccion5/contratos")
documentos = loader.load()   # este ya tiene todos los documentos

print(f"Se cargaron {len(documentos)} documentos desde el directorio.")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=5000,
    chunk_overlap=1000
)

docs_split = text_splitter.split_documents(documentos) # me hace el split de los doucuments

print(f"Se crearon {len(docs_split)} chunks de texto.")

vectorstore = Chroma.from_documents(
    docs_split,
    embedding=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory="/home/arielox/dev/learning/SantiagoH/LangGraph/seccion5/chroma_db"
)

consulta = "¿Dónde se encuentra el local del contrato en el que participa María Jiménez Campos"

# k=2 p'q me devuelva los 2 resultados más similares que encuentre
resultados = vectorstore.similarity_search(consulta, k=3)

print("Top 3 documentos mas similares a la consulta:\n")

for i, doc in enumerate(resultados, start=1):
    print("==================================================")
    print("==================================================")
    print("======================  ||  ======================")
    print(f"Contenido: {doc.page_content}")
    print("\n\n\n")
    print(f"Metadatos: {doc.metadata}")

# python seccion5/05-vector_stores.py