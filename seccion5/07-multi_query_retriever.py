# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_classic.retrievers.multi_query import MultiQueryRetriever

# ⭐️⭐️⭐️ MultiQueryRetriever ->  reformula la pregunta de varias formas distintas

vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory="/home/arielox/dev/learning/SantiagoH/LangGraph/seccion5/chroma_db"
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

base_retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
retriever = MultiQueryRetriever.from_llm(retriever=base_retriever, llm=llm)

consulta = "¿Dónde se encuentra el local del contrato en el que participa María Jiménez Campos?"
resultados = retriever.invoke(consulta)

print("Top documentos mas similares a la consulta:\n")
for i, doc in enumerate(resultados, start=1):
    print("==================================================")
    print("==================================================")
    print("======================  ||  ======================")
    print(f"Contenido: {doc.page_content}")
    print("\n\n\n")
    print(f"Metadatos: {doc.metadata}")

# python seccion5/07-multi_query_retriever.py


#
# ⭐️⭐️⭐️                    MultiQueryRetriever 
#
# El `MultiQueryRetriever` resuelve uno de los problemas más comunes y frustrantes de la búsqueda vectorial tradicional: **la sensibilidad a las palabras exactas que usa el usuario.**

# Cuando usas un *retriever* normal (como tu `base_retriever`), el sistema convierte tu pregunta en un vector y busca los vectores de documentos que estén más cerca. Sin embargo, si el usuario formula la pregunta con palabras ligeramente distintas a las del documento original, es posible que el sistema no encuentre la respuesta, aunque la información esté ahí.

# Aquí es donde entra la "magia" del `MultiQueryRetriever`. Su funcionamiento se divide en **3 pasos clave:**

# ### 1. Generación de variantes (Uso del LLM)

# En lugar de buscar directamente tu consulta original, el `MultiQueryRetriever` le envía tu pregunta al LLM que le asignaste (en tu caso, DeepSeek o GPT) y le pide que **genere múltiples versiones diferentes de la misma pregunta**, abordándola desde distintos ángulos.

# Tomando tu ejemplo original:

# > *¿Dónde se encuentra el local del contrato en el que participa María Jiménez Campos?*

# El LLM internamente generaría variantes como:

# * *Variante 1:* "¿Cuál es la dirección de la propiedad mencionada en el acuerdo de María Jiménez Campos?"
# * *Variante 2:* "Ubicación del inmueble arrendado o vendido a María Jiménez Campos según el documento."
# * *Variante 3:* "¿En qué lugar físico está situado el local comercial del contrato de María Jiménez?"

# ### 2. Búsqueda múltiple

# El sistema toma tu consulta original **más** todas las variantes generadas por el LLM y realiza una búsqueda vectorial independiente en tu base de datos (Chroma) para cada una de ellas. Como las preguntas usan sinónimos y enfoques distintos, es capaz de "pescar" documentos que la pregunta original por sí sola habría ignorado.

# ### 3. Unión y deduplicación

# Finalmente, reúne todos los documentos encontrados por todas las consultas, elimina los que estén repetidos (para no pasarte el mismo fragmento de texto dos veces) y te devuelve la lista final consolidada.

# ---

# **En resumen:** Lo que hace es automatizar el proceso mental de *"si no lo encuentro buscando así, déjame intentar buscarlo con estas otras palabras"*. Aumenta significativamente tus probabilidades de encontrar la información correcta (mejora el *recall*), a cambio de consumir un poco más de tokens y tiempo, ya que hace una llamada extra al LLM antes de buscar en la base de datos.