# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================


import hashlib
from typing import List
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config import *

class DocumentProcessor:
    """Procesador de documentos para el sistema RAG."""
    
    def __init__(self, docs_path: str = "docs", chroma_path: str = "./chroma_db"):
        self.docs_path = Path(docs_path)
        self.chroma_path = Path(chroma_path)
        self.embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,#indica q unidad ocupa el chunk_size, en este caso "caracteres"
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""] # separadores q puede ocupar para hacer las divisiones
        )
        
    def load_documents(self) -> List[Document]:
        """Carga documentos markdown del directorio docs."""
        print(f"📚 Cargando documentos desde {self.docs_path}")
        
        # Carga todos los archivos markdown de la carpeta
        loader = DirectoryLoader(
            str(self.docs_path),
            glob="*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        documents = loader.load()
        
        # Enriquecer metadatos
        # no es obligatorio pero es lo mejor, siempre eriquecer los documentos con metadatos extra
        for doc in documents:
            filename = Path(doc.metadata["source"]).stem
            doc.metadata.update({
                "filename": filename,
                "doc_type": self._get_doc_type(filename),
                "doc_id": self._generate_doc_id(doc.page_content)# p' saber a qué documento pertenece el fragmento concreto, este es el id para este documento completo, luego se hace el "chunking" donde los chunks ocupan este id.
            })
        
        print(f"✅ Cargados {len(documents)} documentos")
        return documents
    
    def _get_doc_type(self, filename: str) -> str:
        """Determina el tipo de documento basado en el nombre."""

        if "faq" in filename.lower():
            return "faq"
        elif "manual" in filename.lower():
            return "manual"
        elif "troubleshooting" in filename.lower():
            return "troubleshooting"
        else:
            return "general"
    
    def _generate_doc_id(self, content: str) -> str:
        """Genera un ID único para el documento."""

        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    # Recién aquí divide los documentos 
    # ⭐️⭐️
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Divide documentos en chunks más pequeños."""

        print("✂️  Dividiendo documentos en chunks...")
        
        # llama a "split_documents" pero de la fcn "__init__", explicación en # ⭐️⭐️
        chunks = self.text_splitter.split_documents(documents)
        
        # Agregar metadatos de chunk
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": i,
                "chunk_size": len(chunk.page_content)
            })
        
        print(f"✅ Creados {len(chunks)} chunks")
        return chunks
    
    def xd() -> None:
        """✦ ¡Ah, excelente pregunta! Es muy normal confundirse con eso porque los nombres son iguales, pero se refieren a objetos distintos. Vamos a desenredarlo.

        1. ¿A quién está llamando self.text_splitter.split_documents(documents)?

        No se está llamando a sí misma (no hay ciclo infinito) ni a la función padre de la clase RAGSetup que creaste.

        Está llamando a un método que le pertenece a un objeto de la librería LangChain. 

        Si revisamos el método __init__ (línea 19), vemos esto:

        1 self.text_splitter = RecursiveCharacterTextSplitter(...) Aquí estás guardando dentro de la variable self.text_splitter un objeto de la clase RecursiveCharacterTextSplitter (que viene de LangChain). 

        Entonces, cuando haces:
        1 chunks = self.text_splitter.split_documents(documents) Le estás diciendo a ese objeto específico de LangChain (RecursiveCharacterTextSplitter): "Oye, usa tu propio método interno llamado split_documents para picar esta lista de documentos". Casualmente, tú le pusiste el mismo nombre a tu función en setup_rag.py, pero son dos funciones diferentes en dos clases diferentes.

        2. ¿Cómo heredan los metadatos? ¿Es siempre automático?

        Sí, es siempre automático cuando usas los text splitters de LangChain.

        Cuando RecursiveCharacterTextSplitter (o casi cualquier otro splitter de LangChain) recibe un objeto Document que tiene texto y metadatos (como el doc_id o el filename), el proceso interno de LangChain funciona así:

        1. Lee el texto completo del documento.
        2. Lo pica en pedacitos según el tamaño configurado.
        3. Crea un nuevo objeto Document para cada pedacito.
        4. Copia exactamente el mismo diccionario de metadatos del documento original y se lo pega a cada uno de esos nuevos fragmentos.

        No tienes que programarlo ni especificarlo; está diseñado por defecto en la librería de LangChain para que nunca pierdas el rastro de dónde vino un fragmento de texto. 

        Por eso tu función toma esos pedacitos (que ya traen el doc_id y filename copiados) y luego, tú decides agregarle además el chunk_id y el chunk_size."""
    
    # 👀 el parámetro "documents" son los chunks
    # aquí se crea la DB
    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """Crea el vectorstore con ChromaDB. Almacen c/chunk por separado"""
        print("🔄 Creando vectorstore con ChromaDB...")
        
        # Limpiar directorio anterior si existe
        if self.chroma_path.exists():
            import shutil
            shutil.rmtree(self.chroma_path)
        
        # Crear vectorstore
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(self.chroma_path),
            collection_name="helpdesk_knowledge"
        )
        
        print(f"✅ Vectorstore creado en {self.chroma_path}")
        print(f"📊 Total de vectores: {len(documents)}")
        
        return vectorstore
    
    # en caso de que no quiera crear una nueva y ya tengo una existente
    def load_existing_vectorstore(self) -> Chroma:
        """Carga vectorstore existente."""
        if not self.chroma_path.exists():
            raise FileNotFoundError(f"Vectorstore no encontrado en {self.chroma_path}")
        
        vectorstore = Chroma(
            persist_directory=str(self.chroma_path),
            embedding_function=self.embeddings,
            collection_name="helpdesk_knowledge"
        )
        
        return vectorstore
    
    def setup_rag_system(self, force_rebuild: bool = False):
        """Configura el sistema RAG completo."""
        print("🚀 Configurando sistema RAG...")
        
        # Verificar si ya existe y no forzar rebuild
        if self.chroma_path.exists() and not force_rebuild:
            print("📦 Vectorstore existente encontrado")
            return self.load_existing_vectorstore()
        
        # Cargar y procesar documentos
        documents = self.load_documents()
        if not documents:
            print("⚠️  No se encontraron documentos para procesar")
            return None
        
        # Dividir documentos
        chunks = self.split_documents(documents)
        
        # Crear vectorstore
        vectorstore = self.create_vectorstore(chunks)
        
        print("✅ Sistema RAG configurado exitosamente")
        return vectorstore
    
    def test_search(self, vectorstore: Chroma, query: str = "resetear contraseña"):
        """Prueba la funcionalidad de búsqueda."""
        print(f"\n🔍 Probando búsqueda: '{query}'")
        
        results = vectorstore.similarity_search(query, k=3) # retorna solo 3 docs
        
        for i, doc in enumerate(results, 1):
            print(f"\n📄 Resultado {i}:")
            print(f"Tipo: {doc.metadata.get('doc_type', 'unknown')}")
            print(f"Archivo: {doc.metadata.get('filename', 'unknown')}")
            print(f"Contenido: {doc.page_content[:200]}...")
        
        return results


def main():
    """Función principal para configurar RAG."""
    print("🎧 Configuración RAG - Helpdesk 2.0")
    print("=" * 40)
    
    # Configurar procesador
    processor = DocumentProcessor(docs_path=DOCS_PATH, chroma_path=CHROMADB_PATH)
    
    # Configurar sistema RAG
    vectorstore = processor.setup_rag_system(force_rebuild=True)
    
    if vectorstore:
        # Probar búsquedas
        test_queries = [
            "resetear contraseña",
            "error 500",
            "cancelar suscripción",
            "aplicación lenta"
        ]
        
        for query in test_queries:
            processor.test_search(vectorstore, query)
    
    print("\n✅ Configuración completada")


if __name__ == "__main__":
    main()



# /home/arielox/dev/learning/SantiagoH/LangGraph/seccion6/helpdesk_system/setup_rag.py