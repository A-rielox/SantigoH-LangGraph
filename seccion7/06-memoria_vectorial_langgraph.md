# 📢

En Python, cuando utilizas una ruta relativa como ./chromadb, esta se resuelve
respecto al Directorio de Trabajo Actual (CWD - Current Working Directory), que es
desde donde ejecutas el comando en la terminal, y no respecto a la ubicación del
archivo .py.

Análisis de tu caso:
Si estás parado en:
~/dev/learning/SantiagoH/LangGraph

Y ejecutas:
python seccion7/06-memoria_vectorial_langgraph.py

La carpeta se creará en:
~/dev/learning/SantiagoH/LangGraph/chromadb



✦ Para que la base de datos se cree siempre en la misma carpeta donde reside el
script, utiliza cualquiera de estas dos opciones:

Opción 1: Usando os.path (Clásica)

import os
# Obtiene la carpeta donde está el script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMDB_PATH = os.path.join(BASE_DIR, "chromadb")

Opción 2: U...

Explicación rápida:
* __file__: Es una variable especial de Python que contiene la ruta al archivo
    actual.
* abspath/parent: Aseguran que la ruta sea absoluta desde la raíz de tu disco,
    evitando que dependa de desde qué carpeta abras la terminal.



# 🍑 💨

✦ El problema del "ruido" ocurre porque tienes dos herramientas intentando hacer lo
mismo de formas diferentes:

1. La confusión de identidades:
    * LangChain (vectorstore): Lo configuraste para usar OpenAI. Es como un
        "traductor" que ya sabe qué idioma hablar.
    * Chroma Nativo (client y collection): Es la base de datos "en bruto". Esta no
        sabe nada de tu configuración de OpenAI.

2. Por qué descarga el modelo:
    Cuando el código ejecuta collection.add(...) o collection.query(...), le estás
pidiendo a la base de datos nativa que procese texto. Como ella no sabe que quieres
usar OpenAI, dice: "Bueno, para entender este texto necesito un modelo de IA, voy a
bajarme el que trae por defecto (all-MiniLM-L6-v2)". Ahí es cuando ves toda la barra
de progreso y el texto naranja en la terminal.

3. La solución técnica:
    Debes usar el objeto vectorstore (el de LangChain) para todo. En lugar de usar
collection.add, usarías vectorstore.add_texts. 

    Al hacer esto, LangChain se encarga de:
    * Enviar el texto a OpenAI para convertirlo en vector (usando la API que ya
        pagas).
    * Guardar ese vector en Chroma.

    Como LangChain ya tiene el vector listo, Chroma no necesita descargar ningún
modelo local porque ya recibe el trabajo hecho.




✦ Aquí tienes el desglose de los cambios necesarios. El
problema es que estás mezclando la librería "madre" (Chroma
nativo) con el "conector" (LangChain).

1. La Configuración de la DB 
Debes eliminar el cliente nativo para que Chroma no intente tomar decisiones por su cuenta.

# --- CÓDIGO ACTUAL (MALE) ---
vectorstore = Chroma(
    collection_name="memoria_chat",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory=CHROMDB_PATH
)
# ESTO ES LO QUE ESTÁ MAL: Creas un cliente que no sabe nada de OpenAI
client = chromadb.PersistentClient(path=CHROMDB_PATH)
collection = client.get_collection("memoria_chat")


# --- CÓDIGO CORREGIDO (BIEN) ---
vectorstore = Chroma(
    collection_name="memoria_chat",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    persist_directory=CHROMDB_PATH
)

 # Simplemente eliminamos 'client' y 'collection'. 
 # Usaremos 'vectorstore' para todo.

2. Guardar Información
Cambiamos el método nativo por el de LangChain, que ya sabe que debe enviar el texto a OpenAI antes de guardarlo.

# --- CÓDIGO ACTUAL (MALE) ---
def guardar_memoria(texto):
    try:
        # MAL: 'collection.add' recibe texto plano y Chroma intenta bajar un modelo local para vectorizarlo.
        collection.add(
            documents=[texto],
            ids=[str(uuid.uuid4())]
        )
         print(f"[+] Guardado en memoria: {texto}")
    except Exception as e:
        print(f"Error: {e}")

 # --- CÓDIGO CORREGIDO (BIEN) ---
 def guardar_memoria(texto):
    try:
        # BIEN: 'vectorstore.add_texts' usa 'OpenAIEmbeddings' (que configuramos arriba) para convertir el texto en vector ANTES de mandarlo a la base de datos.
        vectorstore.add_texts(
            texts=[texto],
            ids=[str(uuid.uuid4())]
        )
        print(f"[+] Guardado en memoria: {texto}")
    except Exception as e:
        print(f"Error: {e}")

3. Buscar Información
Al igual que al guardar, la búsqueda debe pasar por el modelo de OpenAI para que la "pregunta" esté en el mismo formato que los "datos guardados".

# --- CÓDIGO ACTUAL (MALE) ---
def buscar_memoria(consulta, k=3):
    try:
        # MAL: 'collection.query' intenta vectorizar tu consulta con el modelo local de Chroma.
        results = collection.query(
            query_texts=[consulta],
            n_results=k
        )
        return results['documents'][0] if results['documents'] else []
    except:
        return []

# --- CÓDIGO CORREGIDO (BIEN) ---
def buscar_memoria(consulta, k=3):
    try:
        # BIEN: LangChain vectoriza la consulta con OpenAI y luego busca los vectores más parecidos en Chroma.
        results = vectorstore.similarity_search(consulta, k=k)
        
        # similarity_search devuelve una lista de objetos 'Document'
        return [doc.page_content for doc in results]
    except Exception as e:
        print(f"Error buscando: {e}")
        return []

4. Mostrar todas las memorias (Función auxiliar)
Incluso para listar todo, es mejor usar el objeto que ya
tenemos vinculado.

# --- CÓDIGO ACTUAL (MALE) ---
def mostrar_memorias():
    # MAL: Depende de 'collection' (el cliente nativo) 
    all_memories = collection.get() 
    # ... resto del código
# --- CÓDIGO CORREGIDO (BIEN) ---
def mostrar_memorias():
    # BIEN: Usamos el método .get() que también tiene el wrapper de LangChain
    all_memories = vectorstore.get()
    # ... el resto de la lógica de impresión se mantiene igual

Resumen del "Por qué": Al usar vectorstore de LangChain, el flujo es: 

Texto -> OpenAI (Cloud) -> Vector -> Chroma (Local). 
Al usar collection de Chroma nativo, el flujo es: 
Texto -> Chroma (Local) -> Modelo Local (Download) -> Vector.

Esa segunda ruta es la que te causa el ruido y las descargas.