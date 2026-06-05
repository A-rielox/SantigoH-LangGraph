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

# ✦ La principal diferencia no es el resultado (ambos te
#   devuelven documentos similares), sino la arquitectura y
#   la flexibilidad dentro del ecosistema de LangChain.

#   Aquí te detallo las diferencias clave:

#   1. Interfaz Estándar (Runnable)
#   En el archivo 06-retrievers_langchain.py, al usar
#   vectorstore.as_retriever(), conviertes el almacén de
#   vectores en un objeto tipo Retriever.
#    * Retriever: Implementa la interfaz Runnable de
#      LangChain. Esto significa que tiene métodos
#      estandarizados como .invoke(), .batch() y .stream().
#    * VectorStore: El método .similarity_search() es
#      específico de los almacenes de vectores y no sigue la
#      misma interfaz genérica.

#   2. Desacoplamiento (Modularidad)
#    * En el archivo 05: Estás amarrado a un VectorStore. Si
#      mañana quieres cambiar tu base de datos por una
#      búsqueda en Google o una base de datos SQL, tendrías
#      que cambiar gran parte de tu código.
#    * En el archivo 06: Tu código espera un "Retriever". No
#      le importa si la información viene de Chroma, de un
#      PDF, de una API o de Wikipedia. Mientras el objeto
#      tenga el método .invoke(), el resto de tu cadena
#      (RAG) seguirá funcionando sin cambios.