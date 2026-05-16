# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# ya tengo la info en la DB desde la clase anterior
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory="/home/arielox/dev/learning/SantiagoH/LangGraph/seccion5/chroma_db"
)

# {"k": 2} p'q me devuelva 2 documentos
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})

consulta = "¿Dónde se encuentra el local del contrato en el que participa María Jiménez Campos?"

# aquí obtengo los 2 resultados con mayor coincidencia para la consulta
resultados = retriever.invoke(consulta)

print("Top 2 documentos mas similares a la consulta:\n")
for i, doc in enumerate(resultados, start=1):
    print("==================================================")
    print("==================================================")
    print("======================  ||  ======================")
    print(f"Contenido: {doc.page_content}")
    print("\n\n\n")
    print(f"Metadatos: {doc.metadata}")

# python seccion5/06-retrievers_langchain.py