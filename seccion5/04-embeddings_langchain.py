# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================


from langchain_openai import OpenAIEmbeddings
import numpy as np

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

texto1 = "La capital de Francia es París."
texto2 = "Paris es la ciudad capital de Francia."
texto3 = "París es un nombre común para mascotas."

vec1 = embeddings.embed_query(texto1)
vec2 = embeddings.embed_query(texto2)
vec3 = embeddings.embed_query(texto3)

print(f"Dimensión de los vectores: {len(vec1)}")

# medida de similitud
cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
cos_sim2 = np.dot(vec1, vec3) / (np.linalg.norm(vec1) * np.linalg.norm(vec3))

print(f"Similitud coseno entre vec1 y vec2: {cos_sim:.3f}")
print(f"Similitud coseno entre vec1 y vec3: {cos_sim2:.3f}")
# Dimensión de los vectores: 3072
# Similitud coseno entre vec1 y vec2: 0.836
# Similitud coseno entre vec1 y vec3: 0.491

# seccion5/04-embeddings_langchain.py


####################################################################
##   🔔📢🔔📢🔔📢🔔📢    Gemini me sugiere esto

# La Solución: Procesamiento por lotes (Batching)
# La mejor práctica en LangChain para vectorizar múltiples textos al mismo tiempo es usar embed_documents. Esto empaqueta toda tu lista de textos y hace un solo viaje a la API de OpenAI, reduciendo el tiempo de ejecución drásticamente.

# Aquí tienes la versión optimizada. Si le pones un time por delante al ejecutarlo en tu zsh (time python seccion5/04-embeddings_langchain.py), vas a notar la diferencia de




# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================

from langchain_openai import OpenAIEmbeddings
import numpy as np

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Agrupamos los textos en una lista
textos = [
    "La capital de Francia es París.",
    "Paris es la ciudad capital de Francia.",
    "París es un nombre común para mascotas."
]

# MAGIA AQUÍ: Un solo viaje a la API para traer todos los vectores
vectores = embeddings.embed_documents(textos)

# Desempaquetamos los resultados
vec1, vec2, vec3 = vectores[0], vectores[1], vectores[2]

print(f"Dimensión de los vectores: {len(vec1)}")

# medida de similitud
cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
cos_sim2 = np.dot(vec1, vec3) / (np.linalg.norm(vec1) * np.linalg.norm(vec3))

print(f"Similitud coseno entre vec1 y vec2: {cos_sim:.3f}")
print(f"Similitud coseno entre vec1 y vec3: {cos_sim2:.3f}")