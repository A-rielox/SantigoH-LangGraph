import os

# Configuración de modelos
EMBEDDING_MODEL = "text-embedding-3-large"
QUERY_MODEL = "gpt-4o-mini"
GENERATION_MODEL = "gpt-4o"

# Configuración del vector store
# CHROMA_DB_PATH = "/home/arielox/dev/learning/SantiagoH/LangGraph/seccion5/chroma_db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
CHROMA_DB_PATH = os.path.join(PARENT_DIR, "chroma_db")

# Configuración del retriever
SEARCH_TYPE = "mmr"
MMR_DIVERSITY_LAMBDA = 0.7
MMR_FETCH_K = 20
SEARCH_K = 2

# Configuracion alternativa para retriever hibrido
ENABLE_HYBRID_SEARCH = True
SIMILARITY_THRESHOLD = 0.70


# El parámetro `MMR_DIVERSITY_LAMBDA` (que en el código se asigna a `lambda_mult`) es el valor que controla el **equilibrio entre la relevancia y la diversidad** de los fragmentos de texto recuperados por tu sistema RAG.

# Para entenderlo, primero hay que ver cómo funciona la estrategia **MMR (Maximal Margin Relevance)** que definiste en tu configuración.

# ### ## ¿Cómo funciona tu Retriever MMR?

# Dado que tienes configurado `fetch_k = 20` y `k = 2`, el algoritmo hace lo siguiente:

# 1. **Recuperación Inicial:** Primero, busca en tu base de datos Chroma y extrae los **20** (`fetch_k`) documentos que son más similares semánticamente a la pregunta del usuario.
# 2. **Selección del Mejor:** De esos 20, toma el documento número 1 (el más relevante) y lo añade directamente a la lista final.
# 3. **Penalización por Redundancia (Aquí entra Lambda):** Para elegir el **2º** documento (ya que tu `k=2`), el algoritmo evalúa los 19 restantes, pero ahora no solo busca que respondan a la pregunta, sino que **penaliza** a aquellos que sean muy similares al documento que ya seleccionó en el paso 2.

# ### ## La Matemática detrás del Lambda

# El algoritmo califica a los documentos candidatos usando la siguiente ecuación:

# $$MMR\_Score = \lambda \cdot \text{Similitud}(Q, D_i) - (1 - \lambda) \cdot \max(\text{Similitud}(D_i, D_{seleccionados}))$$

# Donde `lambda` es exactamente tu parámetro `MMR_DIVERSITY_LAMBDA` establecido en **0.7**.

# * **Si Lambda = 1.0:** El algoritmo ignora por completo la diversidad. Se convierte en una búsqueda por similitud normal (te traería los 2 documentos más parecidos a la pregunta, aunque digan exactamente lo mismo).
# * **Si Lambda = 0.0:** El algoritmo ignora la pregunta y solo busca maximizar la diferencia entre los documentos. Te traería información muy variada, pero probablemente inútil.
# * **Tu configuración (Lambda = 0.7):** Le estás diciendo al sistema: *"Dale un **70% de importancia** a que el documento responda directamente a la pregunta, y un **30% de importancia** a que el documento aporte información nueva y diferente al primer documento recuperado"*.

# ### ## El Impacto Práctico

# En contextos de ingeniería de datos financieros, si estás analizando reportes trimestrales o prospectos de FIBRAs y SOFIPOs, a menudo te encontrarás con párrafos legales o resúmenes de dividendos que son copiados y pegados textualmente a lo largo del PDF.

# Si un usuario pregunta *"¿Cuáles son los riesgos asociados a esta SOFIPO?"* y usas un retriever tradicional de similitud pura (`search_type="similarity"`), tu RAG podría extraer 2 o 3 fragmentos casi idénticos que mencionan el mismo riesgo legal, perdiendo la oportunidad de mostrar otros riesgos.

# Al usar **MMR con un lambda de 0.7**, tu RAG asegurará el fragmento con el riesgo principal, pero empujará hacia abajo los fragmentos repetidos en favor de otro fragmento que discuta un riesgo diferente (por ejemplo, riesgo de liquidez), dándole un contexto mucho más rico al LLM de generación.

# Aquí tienes un simulador interactivo para que veas en tiempo real cómo modificar este parámetro altera matemáticamente la selección final del RAG: