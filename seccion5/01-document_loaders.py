from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
# PyPDFLoader con pip install pypdf

# importa datos externos en un formato unificado
loader = PyPDFLoader("./seccion5/RFC.pdf") # 📢
# loader = WebBaseLoader("https://techmind.ac/")

pages = loader.load()

for i, page in enumerate(pages):
    print(f"================================================================")
    print(f"========================== Página {i + 1} ============================")
    print(f"Contenido: {page.page_content}")
    print(f"Metadatos: {page.metadata}")

# 📢
# "./RFC.pdf". En Python, el prefijo ./ significa "el directorio de trabajo actual de la terminal".
# python seccion5/01-document_loaders.py