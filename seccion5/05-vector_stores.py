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

# loader.load() va a separar c/ página, la carpeta tiene 5 documentos, c/u tiene 3 páginas, xeso da 15 "documentos"
print(f"Se cargaron {len(documentos)} documentos desde el directorio.")

# ( cada documento tiene entre 2 mil y mil caracteres solamente )
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=5000,
    chunk_overlap=500
)

docs_split = text_splitter.split_documents(documentos) # me hace el split de los doucuments

print("\n\n\n")
print(f"Se crearon {len(docs_split)} chunks de texto.")

vectorstore = Chroma.from_documents(
    docs_split,
    embedding=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory="/home/arielox/dev/learning/SantiagoH/LangGraph/seccion5/chroma_db"
)

consulta = "¿Dónde se encuentra el local del contrato en el que participa María Jiménez Campos"

# k=2 p'q me devuelva los 2 resultados más similares que encuentre
resultados = vectorstore.similarity_search(consulta, k=3)

#   Dato importante: En este archivo 05-vector_stores.py no hay un modelo de chat (como GPT-4) generando una respuesta textual. Solo estás haciendo Recuperación (Retrieval). Es decir, estás buscando los fragmentos de los PDFs donde vive la respuesta, pero todavía no hay una IA "escribiendo" una respuesta final amigable; eso se hace en pasos posteriores (como verás en la sección de RAG).

print("\n\n\n")
print("Top 3 documentos mas similares a la consulta:\n")

for i, doc in enumerate(resultados, start=1):
    print("==================================================")
    print("==================================================")
    print("======================  ||  ======================")
    print(f"Contenido: {doc.page_content}")
    print("\n\n\n")
    print(f"Metadatos: {doc.metadata}")

# python seccion5/05-vector_stores.py

#  > "... cada document en documents      
#    tiene menos de 3000..."                                
# ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
# ✦ Exactamente, eso confirma lo que explicaba:

#   Como cada document (cada página) tiene menos de 3000 caracteres y tu
#   chunk_size es de 5000, el splitter no corta nada. 

#   Para el RecursiveCharacterTextSplitter, si el texto que le pasas es más
#   pequeño que el chunk_size, simplemente lo deja tal cual. En tu caso:

#    1. Resultado: Tendrás exactamente el mismo número de chunks que de
#       páginas originales (15 chunks).
#    2. Overlap: El chunk_overlap=500 no se aplica, porque el overlap solo
#       ocurre cuando un documento es lo suficientemente grande como para
#       ser dividido en dos o más partes. 
#    3. Contenido: Cada chunk será la página completa.