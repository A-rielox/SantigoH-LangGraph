import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.retrievers import EnsembleRetriever, MultiQueryRetriever
import streamlit as st

from config import *
from prompts import *

# inicializa el sistema RAG, @st. .... para que streamlit "cachee" esta parte p'q cuando se ejecute la app no tenga q volver a definir, de esto NADA varia entre ejecuciones
@st.cache_resource
def initialize_rag_system():
    # Vector Store
    vectorestore = Chroma(
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL),\
        persist_directory=CHROMA_DB_PATH
    )

    # Modelos
    llm_queries = ChatOpenAI(model=QUERY_MODEL, temperature=0)
    llm_generation = ChatOpenAI(model=GENERATION_MODEL, temperature=0)

    # Retriever MMR (Maximal Margin Relevance), aquí va la estrategia de cómo va a comparar los embeddings de la/las preguntas con los embeddings de lo q encuentra
    base_retriever = vectorestore.as_retriever(
        search_type=SEARCH_TYPE,
        search_kwargs={
            "k": SEARCH_K,
            "lambda_mult": MMR_DIVERSITY_LAMBDA,
            "fetch_k": MMR_FETCH_K
        }
    )

    # Retriever adicional con similarity para comparar
    similarity_retriever = vectorestore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": SEARCH_K}
    )

    # Prompt personalizado para MultiQueryRetriever ( ... generar múltiples versiones de la consulta del usuario... )
    multi_query_prompt = PromptTemplate.from_template(MULTI_QUERY_PROMPT)

    # MultiQueryRetriever con prompt personalizado, este es el que saca las coincidencias
    mmr_multi_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm_queries,
        prompt=multi_query_prompt
    )

    # Ensemble Retriever que combinar MMR y similarity 
    # 📢📢
    if ENABLE_HYBRID_SEARCH:
        ensemble_retriever = EnsembleRetriever(
            retrievers=[mmr_multi_retriever, similarity_retriever],
            weights=[0.7, 0.3], # mayor peso a MMR
            similarity_threshold=SIMILARITY_THRESHOLD # <-- p'q NO muestre resultado con similitud menor a esto
        )
        final_retriever = ensemble_retriever
    else:
        final_retriever = mmr_multi_retriever

    # prompt final
    prompt = PromptTemplate.from_template(RAG_TEMPLATE)

    # 🍑🍑 Funcion para formatear y preprocesar los documentos recuperados
    def format_docs(docs):
        formatted = []

        # ⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️
        # Entonces aquí lo que estoy haciendo en la cabecera es decirle mira, para este fragmento es el número tal.  Además pertenece a este documento y además dentro de este documento pertenece a esta página concreta y esto le va a ayudar después al LM a proporcionarnos mejores resultados. Y luego, por último, como estamos procesando los fragmentos, también tendremos que concatenar la información del fragmento, el propio contenido del fragmento que se encontrará.

        for i, doc in enumerate(docs, 1):
            header = f"[Fragmento {i}]"
            
            if doc.metadata:
                if 'source' in doc.metadata:
                    # source = doc.metadata['source'].split("\\")[-1] if '\\' in doc.metadata['source'] else doc.metadata['source']
                    # Nota: Esto funciona asumiendo que la DB se creó en Linux (rutas con '/')
                    source = os.path.basename(doc.metadata['source']) # ( es el nombre del archivo )
                    header += f" - Fuente: {source}"
                if 'page' in doc.metadata:
                    header += f" - Pagina: {doc.metadata['page']}"
        
            content = doc.page_content.strip()
            formatted.append(f"{header}\n{content}")
        
        return "\n\n".join(formatted)

    rag_chain = (
        {
            "context": final_retriever | format_docs,  # <-- pasa lo de final_retriever a la entrada de format_docs
            "question": RunnablePassthrough()   # <-- la question se le va a pasar al momento de invocar la cadena
        }       # <--   estas son las variables dinámicas que se le pasan al prompt
        | prompt
        | llm_generation
        | StrOutputParser()
    )

    return rag_chain, mmr_multi_retriever


def query_rag(question):
    try:
        rag_chain, retriever = initialize_rag_system()

        # Obtener respuesta
        response = rag_chain.invoke(question)

        # Obtener documentos para mostrarlos, muestra los documentos de los que saca la informacion
        docs = retriever.invoke(question)

        # Formatear los documentos para mostrar
        docs_info = []
        for i, doc in enumerate(docs[:SEARCH_K], 1):
            doc_info = {   # <-- es p'c/ fragmento
                "fragmento": i,
                "contenido": doc.page_content[:1000] + "..." if len(doc.page_content) > 1000 else doc.page_content,   # <__ va a mostrar solo los primeros 1000 caracteres del fragmento
                # "fuente": doc.metadata.get('source', 'No especificada').split("\\")[-1],
                # Nota: Esto funciona asumiendo que la DB se creó en Linux (rutas con '/')
                "fuente": os.path.basename(doc.metadata.get('source', 'No especificada')),
                "pagina": doc.metadata.get('page', 'No especificada')
            }
            docs_info.append(doc_info) # <-- docs_info va a tener toda esta informacion de los fragmentos concatenada 
        
        return response, docs_info
    
    except Exception as e:
        error_msg = f"Error al procesar la cosulta: {str(e)}"
        return error_msg, []

def get_retriever_info():
    """Obtiene información sobre la configuración del retriever"""

    return {
        "tipo": f"{SEARCH_TYPE.upper()} + MultiQuery" + (" + Hybrid" if ENABLE_HYBRID_SEARCH else ""),
        "documentos": SEARCH_K,
        "diversidad": MMR_DIVERSITY_LAMBDA,
        "candidatos": MMR_FETCH_K,
        "umbral": SIMILARITY_THRESHOLD if ENABLE_HYBRID_SEARCH else "N/A"
    }
