# ⭐️⭐️

✦ ¡Ah, excelente pregunta! Es muy normal confundirse con eso porque los nombres son iguales, pero se refieren a objetos distintos. Vamos a desenredarlo.

    1. ¿A quién está llamando self.text_splitter.split_documents(documents)?

        No se está llamando a sí misma (no hay ciclo infinito) ni a la función padre de la clase RAGSetup que creaste.

        Está llamando a un método que le pertenece a un objeto de la librería LangChain. 

        Si revisamos el método __init__ (línea 19), vemos esto:

        self.text_splitter = RecursiveCharacterTextSplitter(...) Aquí estás guardando dentro de la variable self.text_splitter un objeto de la clase RecursiveCharacterTextSplitter (que viene de LangChain). 

        Entonces, cuando haces:
        chunks = self.text_splitter.split_documents(documents) Le estás diciendo a ese objeto específico de LangChain (RecursiveCharacterTextSplitter): "Oye, usa tu propio método interno llamado split_documents para picar esta lista de documentos". Casualmente, tú le pusiste el mismo nombre a tu función en setup_rag.py, pero son dos funciones diferentes en dos clases diferentes.

    2. 🍀 ¿Cómo heredan los metadatos? ¿Es siempre automático?

        Sí, es siempre automático cuando usas los text splitters de LangChain.

        Cuando RecursiveCharacterTextSplitter (o casi cualquier otro splitter de LangChain) recibe un objeto Document que tiene texto y metadatos (como el doc_id o el filename), el proceso interno de LangChain funciona así:

        1. Lee el texto completo del documento.
        2. Lo pica en pedacitos según el tamaño configurado.
        3. Crea un nuevo objeto Document para cada pedacito.
        4. Copia exactamente el mismo diccionario de metadatos del documento original y se lo pega a cada uno de esos nuevos fragmentos.

        No tienes que programarlo ni especificarlo; está diseñado por defecto en la librería de LangChain para que nunca pierdas el rastro de dónde vino un fragmento de texto. 

    Por eso tu función toma esos pedacitos (que ya traen el doc_id y filename copiados) y luego, tú decides agregarle además el chunk_id y el chunk_size.


# self

> revisa el archivo @setup_rag.py y explicame que son todos esos "self" que 
   veo por todos lados                                                       
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀


✦ ¡Hola! Es una excelente pregunta. En Python, la palabra reservada self es fundamental cuando trabajamos con Programación Orientada a Objetos (POO), que es exactamente lo que se está haciendo en el archivo setup_rag.py con la clase DocumentProcessor.

Aquí te explico de forma sencilla qué es y para qué sirve todo ese montón de self:

1. Representa "este objeto en sí mismo"
    Cuando creas una "Clase" en Python (como class DocumentProcessor:), estás creando un plano o molde. Cuando luego usas ese molde para crear algo real como en la línea processor = DocumentProcessor(...), estás creando un objeto o instancia.

    self es la manera que tiene ese objeto de referirse a sí mismo desde adentro. Es el equivalente a cuando tú dices "yo", "mis brazos", "mi memoria".

2. Guardar cosas que el objeto debe recordar (Atributos)
    En la función __init__ vemos cosas como:

    1 self.docs_path = Path(docs_path)
    2 self.chroma_path = Path(chroma_path)
    3 self.embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
    4 self.text_splitter = RecursiveCharacterTextSplitter(...)

    Al ponerle self. delante, le estás diciendo a Python: "Guarda estas variables dentro de mí, para que yo pueda usarlas más tarde en mis otras funciones". 

    Si no usaras self., esas variables se destruirían apenas termine la función __init__ y el resto de la clase no sabría que existen.

3. Poder usar las cosas que guardó en otras funciones Más abajo en el código, el objeto necesita usar   esas cosas que guardó. Por ejemplo, en load_documents:

    print(f"📚 Cargando documentos desde {self.docs_path}")
    Al decir self.docs_path, el objeto está diciendo: "Oye, dame esa ruta de documentos que yo guardé cuando me crearon". 

    Otro ejemplo está en split_documents:

    chunks = self.text_splitter.split_documents(documents)
    Aquí está usando el cortador de textos (self.text_splitter) que configuró al inicio.

4. Llamar a sus propias funciones (Métodos internos)
    El self también se usa cuando el objeto necesita usar sus propias herramientas o funciones. 

    Por ejemplo, dentro de load_documents, necesita procesar el tipo de documento y llama a su propia función _get_doc_type así:
    
    "doc_type": self._get_doc_type(filename)

    Y en setup_rag_system, la clase se auto-dirige todo el flujo llamando a sus propias funciones en cadena:

    1 documents = self.load_documents()
    2 chunks = self.split_documents(documents)
    3 vectorstore = self.create_vectorstore(chunks)

¿Por qué siempre es el primer parámetro de las funciones?
Si te fijas, todas las funciones dentro de la clase empiezan recibiendo self:

1 def load_documents(self):
2 def _get_doc_type(self, filename: str) -> str:
3 def split_documents(self, documents: List[Document]) -> List[Document]:

Esto es una regla de Python. Cuando tú llamas a processor.load_documents(), Python por detrás secretamente hace esto:
DocumentProcessor.load_documents(processor).

Python automáticamente pasa el objeto mismo como el primer argumento de la función para que la función sepa sobre qué objeto tiene que trabajar. A ese primer argumento, por convención universal en Python, siempre se le llama self.

En resumen: self es la palabra mágica que permite que un objeto en Python tenga "memoria" (guardar variables como self.algo) y "autoconciencia" poder llamar a sus propias funciones como self.hacer_algo().


