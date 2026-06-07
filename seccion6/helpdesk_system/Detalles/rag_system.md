# MultiQueryRetriever

✦ El MultiQueryRetriever es una herramienta avanzada de LangChain diseñada para vencer las limitaciones de las búsquedas simples por palabras clave o similitud.

Imagina que un usuario pregunta: "No puedo entrar a mi cuenta". Pero en tu manual técnico, la solución está escrita como: "Procedimiento de recuperación de credenciales". Una búsqueda normal podría fallar porque las palabras son muy distintas.

Aquí es donde entra el MultiQueryRetriever. Su funcionamiento se divide en tres pasos automáticos:

1. ¿Cómo funciona en tu código?
Cuando el usuario envía una consulta, el MultiQueryRetriever hace lo siguiente:

1. Genera variaciones: Envía la pregunta original al LLM (en tu caso gpt-4o-mini) usando el prompt que definiste en _get_multi_query_prompt. El LLM inventa 3 formas diferentes de decir lo mismo.
    * Original: "No puedo entrar a mi cuenta"
    * Var 1: "Problemas de inicio de sesión"
    * Var 2: "Error al validar contraseña"
    * Var 3: "Acceso denegado al portal"

2. Busca en paralelo: Realiza 4 búsquedas en tu base de datos (la original + las 3 nuevas).

3. Combina y Limpia: Reúne todos los documentos encontrados y elimina los duplicados, entregándote un conjunto de información mucho más rico y preciso.

2. Desglose de los parámetros en _load_vectorstore:
En la línea donde lo inicializas, le pasas tres cosas clave:

self.retriever = MultiQueryRetriever.from_llm(
    # 1. El "Buscador": Le dices que use tu base de datos ChromaDB
        retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
    
    # 2. El "Cerebro": Quién va a pensar las preguntas alternativas (GPT-4o-mini) llm=self.llm,
    
    # 3. El "Manual de estilo": El prompt que le dice cómo debe reescribir    
          prompt=self._get_multi_query_prompt()
    )

3. ¿Por qué es mejor que un buscador normal?
    * Supera la ambigüedad: Si el usuario es poco claro o usa jerga, la IA "traduce" esa duda a términos más técnicos que probablemente estén en tus documentos.
    * Mayor cobertura: Al buscar de 4 formas distintas, es mucho más probable que encuentre el fragmento exacto que resuelve el problema.
    * Robustez: Hace que tu sistema de Helpdesk parezca más inteligente" porque entiende la intención detrás de la pregunta, no solo las letras exactas.

En resumen: Es un optimizador de preguntas que usa la inteligencia de GPT para asegurarse de que la búsqueda en la base de datos no falle por una mala elección de palabras del usuario.


# 🍑

1. MultiQueryRetriever.from_llm(...): Le estamos diciendo a LangChain: "Créame un buscador avanzado utilizando un modelo de lenguaje (LLM)".

2. retriever=self.vectorstore.as_retriever(...): Aquí conectamos el buscador avanzado con tu base de datos ( vectorstore Chroma). Le decimos que cuando busque, use el método de "similitud" y que por cada variante de la pregunta que genere, intente traer los 4 documentos más relevantes ("k": 4).

3. llm=self.llm: Le pasamos la Inteligencia Artificial que configuraste antes en el __init__ (probablemente gpt-4o-mini). Esta es la "mente" que va a inventar las nuevas preguntas.

4. prompt=self._get_multi_query_prompt(): Le pasamos las instrucciones exactas de cómo queremos que redacte las nuevas preguntas. Si ves tu función _get_multi_query_prompt, notarás que le pides explícitamente: "Genera 3 versiones diferentes de la consulta original considerando: Sinónimos técnicos...".

# 🎃
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
"
ahora explicame, con este mismo detalle, tal vez un poco más de detalle, la  función "def buscar(self, ... "          
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

Esta función es el "corazón" de tu sistema. Es la puerta de entrada: recibe la pregunta del usuario (consulta), busca la información, le pide a la IA que redacte una respuesta y evalúa qué tan buena es esa respuesta.

1. ...

---

2. La Búsqueda (El bloque Try)

    try:
        # Buscar documentos relevantes con MultiQueryRetriever
        documentos = self.retriever.invoke(consulta)
        
        if not documentos:
            return {
                "respuesta": "No encontré información relevante en la base de conocimiento.",
                "confianza": 0.1,
                "fuentes": []
             }
    * self.retriever.invoke(consulta): ¡Aquí ocurre la magia de la búsqueda! Esta sola línea hace todo lo que explicamos en el paso anterior: contacta a la IA, crea las 3 preguntas alternativas, busca en ChromaDB y te devuelve una lista de los fragmentos de texto más relevantes que encontró.
    
    * if not documentos:: Si la lista de documentos regresa vacía (la base de datos no tenía absolutamente nada relacionado), el sistema responde cordialmente que no encontró nada, con una confianza muy baja (0.1).

---

3. Procesando los resultados encontrados

    # Extraer información de los documentos
    contexto_partes = []
    fuentes = []
    
    for i, doc in enumerate(documentos[:3]):  # Usar top 3 documentos
        contenido = doc.page_content.strip()
        if contenido:
            contexto_partes.append(f"Documento {i+1}:
                {contenido}")
                
                # Extraer fuentes
                filename = doc.metadata.get('filename', f'doc_{i+1}')
                if filename not in fuentes:
                    fuentes.append(filename)

    Si el sistema sí encontró documentos, ahora tiene que "limpiarlos" y organizarlos.
    * El for recorre la lista, pero fíjate en documentos[:3]:
        ¡solo está tomando los 3 mejores resultados! Aunque el retriever haya traído más, aquí se recorta para no enviar demasiada información a la IA (para ahorrar tokens y no confundirla).
    
    * doc.page_content.strip(): Extrae el texto del documento y le quita espacios en blanco innecesarios al inicio y al final.

    * contexto_partes.append(...): Va armando una lista de textos. Cada texto se etiqueta ordenadamente, por ejemplo:
        "Documento 1: Para reiniciar el router...".

    * 👌 Extracción de fuentes: Los documentos en ChromaDB pueden guardar "metadatos" (información extra, como el nombre del archivo del que salieron). doc.metadata.get('filename'...) intenta sacar el nombre del archivo. Si no lo tiene, inventa uno (doc_1, doc_2). Luego lo guarda en la lista fuentes asegurándose de no repetir nombres (if filename not in fuentes).

---

4. ...

---

5. Generando la Respuesta Final (La Síntesis)

    # Generar respuesta usando el contexto encontrado
    contexto = "\n\n".join(contexto_partes)
    respuesta = self._generar_respuesta( consulta, contexto )

    * "\n\n".join(contexto_partes): Toma la lista de textos que armamos antes (Documento 1, Documento 2...) y los pega todos juntos en un solo bloque de texto gigante, separados por dos saltos de línea (como párrafos). Este bloque gigante es el Contexto.

    * self._generar_respuesta(...): Aquí le pasamos el problema del usuario (consulta) y la información que encontramos (contexto) a otra función que tienes abajo. Esa función tomará ambos textos y se los enviará a gpt-4o-mini con instrucciones como: "Eres un asistente, usando ESTA información, responde ESTA pregunta".

---

6. ...

---

7. El Manejo de Errores ...

En resumen:
La función buscar es la orquestadora: verifica si puede trabajar -> busca -> limpia lo que encontró -> le pide a la IA que lo resuma -> califica qué tan bueno es el resultado -> se lo entrega al usuario.

