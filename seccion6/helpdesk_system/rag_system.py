from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import MultiQueryRetriever
from pathlib import Path
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict, Any

from config import *


class VectorRAGSystem:
    """Sistema RAG avanzado con ChromaDB y MultiQueryRetriever."""
    
    def __init__(self, chroma_path: str = "chroma_db"):
        self.chroma_path = Path(chroma_path)
        self.embeddings = OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.vectorstore = None
        self.retriever = None
        
        # Configurar logging para MultiQueryRetriever
        logging.basicConfig()
        logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
        
        self._load_vectorstore()
    
    def _load_vectorstore(self):
        """Carga el vectorstore de ChromaDB."""

        try:
            # si no existe la dbv
            if not self.chroma_path.exists():
                print(f"⚠️ Vectorstore no encontrado en {self.chroma_path}")
                return
            
            # si existe la leo
            self.vectorstore = Chroma(
                persist_directory=str(self.chroma_path),
                embedding_function=self.embeddings,
                collection_name="helpdesk_knowledge"
            )
            
            # Crear MultiQueryRetriever
            self.retriever = MultiQueryRetriever.from_llm(
                # 1. ¿DÓNDE va a buscar los documentos finales?
                retriever=self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 4}  # Extrae los 4 fragmentosmás similares
                ),
                # 2. ¿QUIÉN va a generar las versiones alternativas de la pregunta?
                llm=self.llm,
                # 3. ¿CÓMO se le instruye a la IA para que haga esas versiones?
                prompt=self._get_multi_query_prompt()
            )
            # 1. MultiQueryRetriever.from_llm(...): Le estamos diciendo a LangChain: "Créame un buscador avanzado utilizando un modelo de lenguaje (LLM)".
            # 2. retriever=self.vectorstore.as_retriever(...): Aquí conectamos el buscador avanzado con tu base de datos ( vectorstore Chroma). Le decimos que cuando busque, use el método de "similitud" y que por cada variante de la pregunta que genere, intente traer los 4 documentos más relevantes ("k": 4).
            # 3. llm=self.llm: Le pasamos la Inteligencia Artificial que configuraste antes en el __init__ (probablemente gpt-4o-mini). Esta es la "mente" que va a inventar las nuevas preguntas.
            # 4. prompt=self._get_multi_query_prompt(): Le pasamos las instrucciones exactas de cómo queremos que redacte las nuevas preguntas. Si ves tu función _get_multi_query_prompt, notarás que le pides explícitamente: "Genera 3 versiones diferentes de la consulta original considerando: Sinónimos técnicos...".

            
            print("✅ VectorRAGSystem inicializado correctamente")
        
        except Exception as e:
            print(f"❌ Error cargando vectorstore: {str(e)}")
            self.vectorstore = None
            self.retriever = None
    
    def _get_multi_query_prompt(self):
        """Prompt personalizado para MultiQueryRetriever."""
        
        return ChatPromptTemplate.from_template(
            """Eres un asistente de helpdesk experto. Tu tarea es generar múltiples versiones de la consulta del usuario para recuperar documentos relevantes de una base de conocimiento de soporte técnico.

            Genera 3 versiones diferentes de la consulta original, considerando:
            - Sinónimos técnicos
            - Diferentes formas de expresar el mismo problema
            - Variaciones en terminología de helpdesk

            Consulta original: {question}

            Versiones alternativas:"""
        )
    
    def buscar(self, consulta: str) -> Dict[str, Any]:
        """Busca respuestas usando MultiQueryRetriever."""

        if not self.retriever:
            return {
                "respuesta": "Sistema RAG no disponible. Verifique la configuración.",
                "confianza": 0.0,
                "fuentes": []
            }
        
        try:
            # Buscar "documentos" relevantes con MultiQueryRetriever
            documentos = self.retriever.invoke(consulta)
            
            if not documentos:
                return {
                    "respuesta": "No encontré información relevante en la base de conocimiento.",
                    "confianza": 0.1,
                    "fuentes": []
                }
            
            # Extraer información de los documentos
            contexto_partes = []
            fuentes = []
            
            for i, doc in enumerate(documentos[:3]):  # Usar top 3 documentos
                contenido = doc.page_content.strip()
                
                if contenido:
                    contexto_partes.append(f"Documento {i+1}: {contenido}")
                    
                    # Extraer fuentes
                    filename = doc.metadata.get('filename', f'doc_{i+1}')
                    if filename not in fuentes:
                        fuentes.append(filename)
            
            if not contexto_partes:
                return {
                    "respuesta": "Documentos encontrados pero sin contenido útil.",
                    "confianza": 0.2,
                    "fuentes": fuentes
                }
            
            # Generar respuesta usando el contexto encontrado
            contexto = "\n\n".join(contexto_partes)
            respuesta = self._generar_respuesta(consulta, contexto)
            
            # Calcular confianza basada en la relevancia
            confianza = self._calcular_confianza(consulta, documentos)
            
            return {
                "respuesta": respuesta,
                "confianza": confianza,
                "fuentes": fuentes
            }
            
        except Exception as e:
            print(f"❌ Error en búsqueda RAG: {str(e)}")
            return {
                "respuesta": f"Error interno en la búsqueda: {str(e)}",
                "confianza": 0.0,
                "fuentes": []
            }
    
    def busqueda_xd() -> None:
        """ahora explicame, con este mismo detalle, tal vez un poco    
        más de detalle, la función "def buscar(self, ... "          
        ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

        Explicación de la función buscar: 
        Analizar y explicar en detalle la función `buscar` dentro
        de `rag_system.py`, desglosando su lógica paso a paso.


        ✦ ¡Excelente! Vamos a desmenuzar la función buscar(self,
        consulta: str) -> Dict[str, Any] bloque por bloque.

        Esta función es el "corazón" de tu sistema. Es la puerta de
        entrada: recibe la pregunta del usuario (consulta), busca la
        información, le pide a la IA que redacte una respuesta y
        evalúa qué tan buena es esa respuesta.

        1. La firma de la función y la validación inicial

        1 def buscar(self, consulta: str) -> Dict[str, Any]:
        2     ""Busca respuestas usando MultiQueryRetriever.""
        3
        4     if not self.retriever:
        5         return {
        6             "respuesta": "Sistema RAG no disponible.
            Verifique la configuración.",
        7             "confianza": 0.0,
        8             "fuentes": []
        9         }
        * -> Dict[str, Any]: Esto es una "sugerencia de tipos" (Type
            Hinting). Le dice a otros programadores (y a tu editor de
            código) que esta función devolverá un Diccionario donde
            las llaves son textos (str) y los valores pueden ser
            cualquier cosa (Any, como números, listas o textos).
        * Validación de seguridad (if not self.retriever:): Antes de
            hacer nada, el sistema verifica si el "motor de búsqueda"
            (el MultiQueryRetriever que vimos antes) realmente se
            cargó correctamente cuando se creó el objeto. Si por
            alguna razón la base de datos no estaba, el retriever será
            None, y en lugar de que el programa "explote" (lance un
            error), devuelve un mensaje controlado diciendo que no
            está disponible.

        ---

        2. La Búsqueda (El bloque Try)

            1     try:
            2         # Buscar documentos relevantes con
            MultiQueryRetriever
            3         documentos = self.retriever.invoke(consulta)
            4         
            5         if not documentos:
            6             return {
            7                 "respuesta": "No encontré información
            relevante en la base de conocimiento.",
            8                 "confianza": 0.1,
            9                 "fuentes": []
        10             }
        * try:: Aquí empieza un bloque de manejo de errores. Si algo
            falla catastroficamente al comunicarse con la IA o la base
            de datos, el programa no se cerrará, sino que brincará a
            la sección except que está al final.
        * self.retriever.invoke(consulta): ¡Aquí ocurre la magia de
            la búsqueda! Esta sola línea hace todo lo que explicamos
            en el paso anterior: contacta a la IA, crea las 3
            preguntas alternativas, busca en ChromaDB y te devuelve
            una lista de los fragmentos de texto más relevantes que
            encontró.
        * if not documentos:: Si la lista de documentos regresa
            vacía (la base de datos no tenía absolutamente nada
            relacionado), el sistema responde cordialmente que no
            encontró nada, con una confianza muy baja (0.1).

        ---

        3. Procesando los resultados encontrados

            1         # Extraer información de los documentos
            2         contexto_partes = []
            3         fuentes = []
            4         
            5         for i, doc in enumerate(documentos[:3]):  # Usar
            top 3 documentos
            6             contenido = doc.page_content.strip()
            7             if contenido:
            8                 contexto_partes.append(f"Documento {i+1}:
            {contenido}")
            9                 
        10                 # Extraer fuentes
        11                 filename = doc.metadata.get('filename',
            f'doc_{i+1}')
        12                 if filename not in fuentes:
        13                     fuentes.append(filename)
        Si el sistema sí encontró documentos, ahora tiene que
        "limpiarlos" y organizarlos.
        * El for recorre la lista, pero fíjate en documentos[:3]:
            ¡solo está tomando los 3 mejores resultados! Aunque el
            retriever haya traído más, aquí se recorta para no enviar
            demasiada información a la IA (para ahorrar tokens y no
            confundirla).
        * doc.page_content.strip(): Extrae el texto del documento y
            le quita espacios en blanco innecesarios al inicio y al
            final.
        * contexto_partes.append(...): Va armando una lista de
            textos. Cada texto se etiqueta ordenadamente, por ejemplo:
            "Documento 1: Para reiniciar el router...".
        * Extracción de fuentes: Los documentos en ChromaDB pueden
            guardar "metadatos" (información extra, como el nombre del
            archivo del que salieron). doc.metadata.get('filename'...)
            intenta sacar el nombre del archivo. Si no lo tiene,
            inventa uno (doc_1, doc_2). Luego lo guarda en la lista
            fuentes asegurándose de no repetir nombres (if filename
            not in fuentes).

        ---

        4. ¿Qué pasa si los documentos estaban en blanco?

        1         if not contexto_partes:
        2             return {
        3                 "respuesta": "Documentos encontrados pero
            sin contenido útil.",
        4                 "confianza": 0.2,
        5                 "fuentes": fuentes
        6             }
        Esto es una validación de seguridad extra. A veces la base de
        datos devuelve un documento, pero resulta que el texto estaba
        vacío o solo eran espacios en blanco. Si la lista
        contexto_partes quedó vacía, se detiene aquí.

        ---

        5. Generando la Respuesta Final (La Síntesis)

        1         # Generar respuesta usando el contexto encontrado
        2         contexto = "\n\n".join(contexto_partes)
        3         respuesta = self._generar_respuesta(consulta,
            contexto)
        * "\n\n".join(contexto_partes): Toma la lista de textos que
            armamos antes (Documento 1, Documento 2...) y los pega
            todos juntos en un solo bloque de texto gigante, separados
            por dos saltos de línea (como párrafos). Este bloque
            gigante es el Contexto.
        * self._generar_respuesta(...): Aquí le pasamos el problema
            del usuario (consulta) y la información que encontramos
            (contexto) a otra función que tienes abajo. Esa función
            tomará ambos textos y se los enviará a gpt-4o-mini con
            instrucciones como: "Eres un asistente, usando ESTA
            información, responde ESTA pregunta".

        ---

        6. Calculando la Confianza y Retornando

        1         # Calcular confianza basada en la relevancia
        2         confianza = self._calcular_confianza(consulta,
            documentos)
        3         
        4         return {
        5             "respuesta": respuesta,
        6             "confianza": confianza,
        7             "fuentes": fuentes
        8         }
        * Antes de terminar, llama a otra función
            _calcular_confianza que analiza matemáticamente qué tantas
            palabras de la pregunta original se encontraron en los
            documentos rescatados.
        * Finalmente, devuelve el diccionario con las tres piezas de
            información listas para mostrarse al usuario o a una
            interfaz gráfica (como Streamlit).

        ---

        7. El Manejo de Errores (El bloque Except)

        1     except Exception as e:
        2         print(f"❌ Error en búsqueda RAG: {str(e)}")
        3         return {
        4             "respuesta": f"Error interno en la búsqueda:
            {str(e)}",
        5             "confianza": 0.0,
        6             "fuentes": []
        7         }
        Si en cualquier parte del bloque try (por ejemplo, si se cae
        el internet y no te puedes conectar a OpenAI), ocurre un
        error (Exception), el código salta inmediatamente aquí.
        Imprime el error en la consola y le devuelve al usuario un
        mensaje elegante de que hubo un error interno, evitando que
        la aplicación se congele.

        En resumen:
        La función buscar es la orquestadora: verifica si puede
        trabajar -> busca -> limpia lo que encontró -> le pide a la
        IA que lo resuma -> califica qué tan bueno es el resultado ->
        se lo entrega al usuario."""


    def _generar_respuesta(self, consulta: str, contexto: str) -> str:
        """Genera una respuesta basada en el contexto encontrado."""

        prompt = ChatPromptTemplate.from_template(
            """Eres un asistente de helpdesk experto. Responde a la consulta del usuario basándote únicamente en el contexto proporcionado de la base de conocimiento.

            Instrucciones:
            - Proporciona una respuesta clara, directa y útil
            - Si el contexto no contiene información suficiente, dilo claramente
            - Mantén un tono profesional pero amigable
            - No inventes información que no esté en el contexto

            Contexto de la base de conocimiento:
            {contexto}

            Consulta del usuario: {consulta}

            Respuesta:"""
        )
        
        try:
            response = self.llm.invoke(prompt.format(consulta=consulta, contexto=contexto))
            return response.content.strip()
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"
    
    def _calcular_confianza(self, consulta: str, documentos: List) -> float:
        """Calcula la confianza basada en la relevancia de los documentos."""

        if not documentos:
            return 0.0
        
        # Factores para calcular confianza
        num_docs = len(documentos)
        palabras_consulta = set(consulta.lower().split())
        
        puntuacion_relevancia = 0
        total_contenido = 0
        
        for doc in documentos[:3]:  # Evaluar top 3
            contenido = doc.page_content.lower()
            total_contenido += len(contenido.split())
            
            # Contar coincidencias de palabras clave
            coincidencias = sum(1 for palabra in palabras_consulta 
                                if palabra in contenido and len(palabra) > 2)
            
            puntuacion_relevancia += coincidencias
        
        # Normalizar puntuación
        if palabras_consulta and total_contenido > 0:
            confianza_base = min(puntuacion_relevancia / len(palabras_consulta), 1.0)
            
            # Bonus por tener múltiples documentos relevantes
            bonus_documentos = min(num_docs / 4.0, 0.2)
            
            # Bonus por longitud adecuada del contenido
            bonus_contenido = min(total_contenido / 1000.0, 0.1)
            
            confianza_final = min(confianza_base + bonus_documentos + bonus_contenido, 1.0)
            
            return round(confianza_final, 2)
        
        return 0.3  # Confianza mínima si se encontraron documentos

# /home/arielox/dev/learning/SantiagoH/LangGraph/seccion6/helpdesk_system/rag_system.py

#############################################################################3
#
# ¡Claro! Estos son conceptos fundamentales de la Programación Orientada a Objetos (POO) en Python. Vamos a desglosarlos usando tu archivo rag_system.py como ejemplo:

#   1. ¿Qué es __init__?
#   Es el constructor de la clase. Es un método especial que Python ejecuta automáticamente en el momento en que creas un objeto de esa clase.

#   Imagina que la clase VectorRAGSystem es un plano arquitectónico. El __init__ es el proceso de construcción donde decides qué materiales usar para esa casa en específico.

#     En tu código:

#     1 def __init__(self, chroma_path: str = "chroma_db"):
#     2     self.chroma_path = Path(chroma_path)
#     3     self.embeddings =
#       OpenAIEmbeddings(model=EMBEDDINGS_MODEL)
#     4     # ... inicializa más cosas ...
#   Cuando tú haces sistema = VectorRAGSystem(), Python corre todo lo que está dentro de ese __init__ para dejar el sistema listo para usarse (configura las rutas, carga los modelos de IA, etc.).

#   ---

#   2. ¿Qué es ese famoso self?
#   El self representa a la instancia específica del objeto que estás usando. Es como decir "mi propio/a" o "este".

#    * ¿Para qué sirve? Sirve para que el objeto pueda "recordar" cosas y compartir información entre sus propios métodos.

#   Ejemplo con "mi propio/a":
#   Si tienes self.chroma_path, le estás diciendo a Python:
#   "Guarda esta ruta en MI PROPIA variable llamada chroma_path".

#   Luego, en otro método como buscar, puedes usar self.retriever. Sin el self, Python no sabría dónde buscar esa variable porque pensaría que es una variable local que ya desapareció al terminar el __init__.

#   Analogía de la vida real:
#   Si yo te digo "Lávate tus manos", el "tus" es como el self. 
#    * Sin el self (tus), yo diría "Lavar manos", y no sabrías qué manos lavar.
#    * Con el self, cada persona (objeto) sabe que debe lavar sus propias manos.

#   En resumen en tu código:
#    * self.llm = ...: "Guarda este modelo de lenguaje en mi memoria interna".
#    * self._load_vectorstore(): "Yo mismo voy a ejecutar mi función de cargar la base de datos".
#    * def buscar(self, consulta): "Esta es una acción que yo (el sistema RAG) sé hacer".

#   ¿Te queda más claro con esta explicación o quieres que profundicemos en alguna parte?
# ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
#   > y que diferencia tiene con guardarlo en una variable normal a la que se pueda referir ?                                 
# ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
# ✦ La diferencia principal es el alcance (scope) y la persistencia de la información. 

#   Aquí tienes la comparación directa:

#   1. Variables "normales" (locales)
#   Viven solo mientras la función se está ejecutando. En cuanto la función termina (return), la variable desaparece de la memoria.

#     1 def _load_vectorstore(self):
#     2     ruta_temporal = "esta/es/una/ruta" # Variable normal
#     3     print(ruta_temporal)
#     4     # Al terminar esta función, 'ruta_temporal' SE BORRA.
#   Si intentas usar ruta_temporal en la función buscar(), Python te dará un error: NameError: name 'ruta_temporal' is not defined.

#   2. Variables con self (Atributos de instancia) Viven mientras el objeto exista. Son como la "memoria a largo plazo" de tu sistema.

#     1 def __init__(self):
#     2     self.mi_modelo = "GPT-4" # Variable con self
#     3
#     4 def buscar(self):
#     5     print(self.mi_modelo) # ¡Todavía existe!
#   Como usaste self, el objeto "recuerda" su modelo aunque hayan pasado horas desde que lo creaste.

#   ---

#   ¿Por qué no usar variables Globales? (La "otra" variable normal)
#   Podrías pensar: "Bueno, pongo la variable fuera de la clase y ya es global". El problema es que perderías la capacidad de tener múltiples sistemas independientes.

#   Imagina este escenario:
#    * Quieres un sistema_soporte_tecnico (con sus propios documentos).
#    * Quieres un sistema_ventas (con otros documentos diferentes).

#   Si usas variables globales, uno sobrescribiría al otro. Con self, cada uno tiene su propio espacio:
#    * sistema_soporte.vectorstore es uno.
#    * sistema_ventas.vectorstore es otro totalmente distinto.

#   En resumen:
#    * Variable normal: "Dato rápido" para un cálculo inmediato.
#    * Variable con self: "Memoria del objeto" para que todos sus métodos puedan trabajar con la misma información.
