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

# En Python, el método __init__ es el equivalente al constructor de otros lenguajes (como Java o C++).
class DocumentProcessor:
    """Procesador de documentos para el sistema RAG."""
    
    def __init__(self, docs_path: str = "docs", chroma_path: str = "./chroma_db"): # 🍑🍑
        self.docs_path = Path(docs_path)
        self.chroma_path = Path(chroma_path)
        self.embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,#indica q unidad ocupa el chunk_size, en este caso "caracteres"
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""] # separadores q puede ocupar para hacer las divisiones
        )
    
    # retorna los documents, donde a c/document le metió más metadatos
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
        
        # Enriquecer metadatos ( este es un documento entero, NO está chunkeado )
        # no es obligatorio pero es lo mejor ( siempre eriquecer los documentos con metadatos extra )
        for doc in documents:
            filename = Path(doc.metadata["source"]).stem

            doc.metadata.update({
                "filename": filename,
                "doc_type": self._get_doc_type(filename),
                "doc_id": self._generate_doc_id(doc.page_content) # p' saber a qué documento pertenece el fragmento concreto, este es el id para este documento completo, luego se hace el "chunking" donde los chunks ocupan este id p' saber a q doc pertenece c/chunk.
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
            # a parte de estos metadatos creados, se c/chunk tiene los metadatos del padre ( del document de donde se sacó, explicación en 🍀 )
        
        print(f"✅ Creados {len(chunks)} chunks")
        return chunks
    
    # 👀 el parámetro "documents" son los chunks
    # aquí se crea la DB            # 🔔🔔
    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """Crea el vectorstore con ChromaDB. Almacena c/chunk por separado"""

        print("🔄 Creando vectorstore con ChromaDB...")
        
        # Limpiar directorio anterior si existe
        if self.chroma_path.exists():
            # Borra la carpeta completa y todo su contenido
            import shutil
            shutil.rmtree(self.chroma_path)
        
        # Crear vectorstore
        vectorstore = Chroma.from_documents(
            documents=documents,    # "documents" son los chunks"
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

# 1. Navega al directorio del proyecto:

# 1     cd
#     /home/arielox/dev/learning/SantiagoH/LangGraph/seccion6/helpdesk_sy
#     stem

# 2. Activa el entorno virtual:

# 1     source ../../venv/bin/activate

# 3. Ejecuta el script:
# 1     python setup_rag.py


