#  📢📢
Ese bloque de código es el corazón de la estrategia de recuperación (retrieval)
del sistema. Su objetivo es aplicar una técnica llamada Búsqueda Híbrida o
Ensemble Retrieval para no depender de un solo método de búsqueda y así obtener
mejores resultados.

Aquí te explico qué hace cada parte y por qué es una buena idea:

1. ¿Qué hace exactamente?
El EnsembleRetriever toma los resultados de dos algoritmos diferentes y los
combina en una única lista final de documentos, dándoles una importancia distinta
a cada uno.

* retrievers=[mmr_multi_retriever, similarity_retriever]: Está mezclando dos
    fuentes:
    * mmr_multi_retriever: Es el "inteligente". Primero usa un LLM para generar
        varias versiones de tu pregunta (MultiQuery) y luego usa el algoritmo MMR
        para asegurarse de que los fragmentos encontrados sean relevantes pero no
        repetidos (busca diversidad).
    * similarity_retriever: Es el "clásico". Simplemente busca los fragmentos
        que más se parecen semánticamente a la pregunta original, sin preocuparse
        por si la información es redundante.

* weights=[0.7, 0.3]: Aquí defines la jerarquía. Le estás diciendo al sistema:
    "Confío un 70% en la diversidad y múltiples consultas de MMR, y un 30% en la
    búsqueda por similitud tradicional". Los resultados del primero tendrán más
    peso al decidir qué mostrarte.

* similarity_threshold: (Usado en algunas implementaciones o wrappers) Filtra
    aquellos documentos que, a pesar de ser los mejores encontrados, no alcanzan
    un nivel mínimo de "parecido" con la pregunta para evitar meter ruido o
    información irrelevante.

---

2. La idea detrás (El "Por qué")
¿Por qué no usar solo uno? Porque cada método tiene "puntos ciegos":

1. El problema de la Similitud pura: A veces te devuelve 3 fragmentos que dicen
    exactamente lo mismo (ej: la misma cláusula de fianza que aparece en tres
    contratos distintos). Esto desperdicia espacio y confunde al LLM.

2. El problema del MultiQuery/MMR: A veces, al intentar ser tan "diverso" y
    buscar diferentes formas de preguntar, puede alejarse un poco de la respuesta
    más obvia y literal que una búsqueda simple encontraría en un segundo.

La Solución Híbrida:
Al combinarlos, obtienes lo mejor de los dos mundos:
* De MMR/MultiQuery obtienes inteligencia, diferentes ángulos de la pregunta y
    variedad de información.

* De Similarity obtienes un "seguro de vida": te aseguras de que, si hay un
    fragmento que coincide casi palabra por palabra con la pregunta, no se quede
    fuera por intentar ser demasiado diverso.

En resumen:
Es como si para resolver una duda legal consultaras a un abogado experto que
analiza el caso desde varios ángulos (MMR + MultiQuery) y también revisaras un
índice de palabras clave (Similarity). El código combina ambas opiniones, pero le
hace más caso al abogado (70%) que al índice (30%).






# ################################################################################################
# 🍑🍑

La función format_docs(docs) es una pieza fundamental en el engranaje de este sistema RAG
  (Retrieval-Augmented Generation). Su función principal es actuar como un traductor o
  formateador que convierte los datos crudos que devuelve la base de datos vectorial en un
  formato que el modelo de lenguaje (LLM) pueda entender perfectamente.

  Aquí tienes una explicación detallada dividida en varios puntos clave:

  1. ¿Dónde se ubica y qué recibe?
  Esta función se encuentra dentro de initialize_rag_system() en el archivo rag_system.py.
  Recibe como parámetro docs, que es una lista de objetos tipo Document de LangChain. Cada
  objeto Document contiene:
   * page_content: El texto literal del fragmento del contrato.
   * metadata: Un diccionario con información extra (nombre del archivo, número de página,
     etc.).

  2. Análisis paso a paso de su lógica
  La función recorre cada fragmento recuperado y lo "empaqueta" de forma legible:

   1. Identificación del Fragmento: Asigna un número ([Fragmento 1], [Fragmento 2], etc.)
      usando enumerate(docs, 1). Esto ayuda al LLM a distinguir dónde termina un contrato y
      empieza otro.
   2. Limpieza de la Fuente: 

   source = doc.metadata['source'].split("\\")[-1] if '\\' in doc.metadata['source']
     else doc.metadata['source']

        Si la ruta del archivo es algo como C:\proyectos\datos\contrato_arrendamiento.pdf, la
        función se queda solo con contrato_arrendamiento.pdf. Esto ahorra tokens y evita confundir
        al LLM con rutas de carpetas locales.
   3. Inclusión de Metadatos: Si el documento tiene información de página, la añade al
      encabezado: header += f" - Pagina: {doc.metadata['page']}".
   4. Limpieza de Texto: Usa .strip() en el contenido para eliminar espacios en blanco
      innecesarios al inicio o final de cada fragmento.
   5. Unión Final: Al final, toma todos los fragmentos procesados y los une con dos saltos
      de línea ("\n\n".join(formatted)), creando un solo bloque de texto coherente.

  3. ¿Por qué es necesaria? ( La Finalidad )
  Sin esta función, estarías enviando al LLM una lista de objetos de Python, lo cual
  causaría un error. Pero más allá de evitar errores, su finalidad estratégica es:

   * Dar Contexto Estructurado: El prompt en prompts.py tiene una sección llamada FRAGMENTOS
     DE CONTRATOS: {context}. format_docs es quien rellena ese {context}.
   * Facilitar la Citación: Al incluir la fuente y la página en el texto, le permites al LLM
     responder cosas como: "Según el Fragmento 1 del contrato 'Vivienda_1.pdf' en la página
     2, la fianza es de...". Esto le da validez legal a la respuesta.
   * Separación de Conceptos: Al poner encabezados claros, el LLM no mezcla el final de una
     cláusula de un contrato con el principio de otra cláusula de un contrato diferente.

  4. Su papel en la "Cadena" (Chain)
  La función se integra en la rag_chain de esta manera:

   "context": final_retriever | format_docs
  Esto es una operación de "tubería" (pipe):
   1. El final_retriever busca los fragmentos más relevantes en la base de datos.
   2. Inmediatamente después, esos fragmentos pasan por format_docs.
   3. El resultado (un string largo y bonito) se inyecta en el prompt final.

  Ejemplo de salida de la función:
  Si el sistema recupera dos fragmentos, format_docs devolverá algo así:

  > [Fragmento 1] - Fuente: contrato_vivienda.pdf - Pagina: 3
  > La renta mensual se fija en la cantidad de 800 euros, pagaderos en los primeros 5
  días...
  >
  > [Fragmento 2] - Fuente: contrato_local.pdf - Pagina: 1
  > El arrendatario se obliga a no realizar obras sin consentimiento expreso por escrito...

  En resumen: Es el "maquillador" de datos que asegura que el LLM reciba la información
  legal organizada, identificada por fuente y lista para ser analizada.




ok y que pasa con el "solapamiento" de los chunks, porque el principio y final de los    
   chunks en que se guarda tiene un "solapamiento" por como se definió la extraccion:       
   "text_splitter = RecursiveCharacterTextSplitter(                                         
       chunk_size=5000,                                                                     
       chunk_overlap=1000                                                                   
   )" me refiero al overlap   

El overlap (solapamiento) es una técnica crucial en el procesamiento de documentos para
  RAG, y en el caso de documentos legales como contratos, su importancia es aún mayor.

  Aquí tienes la explicación detallada de por qué existe y qué sucede exactamente con esos
  1000 caracteres de solapamiento que mencionas:

  1. ¿Qué es físicamente el Overlap?
  Imagina que tienes un contrato de 15,000 caracteres. Al usar chunk_size=5000 y
  chunk_overlap=1000, el "cortador" (Text Splitter) no corta de forma limpia como una
  guillotina. Lo hace así:

   * Chunk 1: Caracteres del 0 al 5000.
   * Chunk 2: Empieza en el 4000 (retrocede 1000) y llega hasta el 9000.
   * Chunk 3: Empieza en el 8000 y llega hasta el 13000.

  Es decir, el final de un fragmento es idéntico al principio del siguiente.

  2. ¿Cuál es la finalidad técnica? (El "Por qué")

  A. Evitar la "Pérdida de Contexto"
  La búsqueda semántica (embeddings) funciona mejor cuando una idea está completa. Si una
  cláusula importante sobre "Causas de Rescisión" empieza en el carácter 4950 y termina en
  el 5100, sin overlap la cláusula quedaría partida:
   * El final del Chunk 1 diría: "El contrato se rescinde si..."
   * El principio del Chunk 2 diría: "...el inquilino no paga la fianza."

  Individualmente, ninguno de los dos chunks tiene la información completa. El LLM tendría
  dificultades para entender quién rescinde qué. Con el overlap de 1000, ambos chunks
  contendrán la cláusula completa.

  B. Mantener la Continuidad Semántica
  Cuando generamos el "embedding" (el vector numérico) de un chunk, ese vector representa el
  significado de ese texto. Si cortas una oración por la mitad, el significado se corrompe.
  El overlap asegura que las frases que están en los bordes mantengan su contexto gramatical
  y de significado.

  3. ¿Cómo afecta esto al sistema RAG que analizamos?

  En tu código de rag_system.py, esto tiene un impacto directo:

   1. En la Recuperación (Retriever):
      Si el usuario pregunta por algo que justo estaba en el "borde" de un corte, el sistema
  encontrará el documento con mayor facilidad porque la información está presente (y
  completa) en dos sitios diferentes.

   2. En el Formateo (format_docs):
      Aquí es donde ocurre algo curioso. Si el final_retriever recupera el Chunk 1 y el
  Chunk 2 porque ambos son muy similares a la pregunta, la función format_docs los pegará
  uno tras otro. 
       * Resultado: El LLM verá un texto donde un párrafo parece repetirse (el final de uno
         es igual al principio del otro).
       * ¿Es esto un problema? No. Los LLM modernos (como GPT-4o que usas en el proyecto)
         son excelentes ignorando esa redundancia y usándola para confirmar que la
         información es consistente. Es preferible que el modelo lea información repetida a
         que lea información incompleta.

  4. ¿Por qué elegiste esos valores (5000 / 1000)?

   * Chunk Size (5000): Es un tamaño bastante grande (unas 800-1000 palabras). Es ideal para
     contratos porque las cláusulas legales suelen ser largas y complejas. Quieres que el
     LLM vea la cláusula entera de una vez.
   * Overlap (1000): Un 20% de solapamiento (1000 de 5000) es el estándar de oro en la
     industria. Es lo suficientemente grande para asegurar que incluso los párrafos más
     largos de un contrato no se queden sin contexto en los bordes.

  En resumen:
  El overlap es el "pegamento" que evita que el conocimiento se fragmente. En un asistente
  legal, asegura que las condiciones, excepciones y nombres de las partes no se pierdan por
  un corte arbitrario de caracteres, permitiendo que el LLM siempre tenga la "foto completa"
  de cada regla del contrato.





▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
 > me refiero a si esta funcion que te menciono hace algo para "arreglar" esto, o para      
   "ajustar" la respuesta teniendo esto en mente                                            
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
✦ La respuesta corta es: No, la función format_docs no hace nada para "arreglar" o eliminar
  el solapamiento (overlap) de forma programática.

  Si analizamos el código de la función que tienes en rag_system.py:

   1 def format_docs(docs):
   2     formatted = []
   3     for i, doc in enumerate(docs, 1):
   4         # ... lógica de encabezados y metadatos ...
   5         content = doc.page_content.strip()
   6         formatted.append(f"{header}\n{content}")
   7     return "\n\n".join(formatted)

  Verás que es un bucle simple. Si el Retriever le entrega dos fragmentos que se solapan
  (donde el final de uno es igual al principio del otro), la función los pegará tal cual,
  con sus respectivos encabezados.

  Entonces, ¿quién se encarga de que ese solapamiento no arruine la respuesta? El sistema
  confía en dos "filtros" que ocurren antes y después de esta función:

  1. El Filtro Previo: El Algoritmo MMR (La solución real)
  En tu archivo config.py y rag_system.py, tienes configurado:
  SEARCH_TYPE = "mmr" y MMR_DIVERSITY_LAMBDA = 0.7.

  Este es el verdadero "mecanismo de ajuste". El algoritmo MMR (Maximal Margin Relevance)
  está diseñado precisamente para evitar la redundancia. 
   * Si el sistema ya seleccionó un fragmento, el MMR penaliza a otros fragmentos que sean
     muy similares (como los que tienen mucho solapamiento).
   * En lugar de traerte el Fragmento A y el Fragmento B (que es casi igual al A por el
     overlap), el MMR preferirá traer el Fragmento A y el Fragmento C (que habla de otro
     tema).

  2. El Filtro Posterior: La Inteligencia del LLM (GPT-4o)
  Cuando la función format_docs termina su trabajo, le entrega al modelo (GPT-4o) un texto
  que podría verse así:
  > [Fragmento 1]: "...el pago se hará los días 5. La fianza será de..."
  >
  > [Fragmento 2]: "La fianza será de dos mensualidades..."

  El LLM es lo suficientemente inteligente para entender que "La fianza será de" se repite.
  Al generar la respuesta final, el modelo sintetiza la información y no te dirá las cosas
  dos veces. Para el modelo, el solapamiento es como leer un libro donde la última palabra
  de una página es la primera de la siguiente: no le confunde, le ayuda a confirmar que los
  fragmentos están conectados.

  Una observación sobre los comentarios del código:
  Curiosamente, en el archivo rag_system.py hay un comentario que dice:
  # se eliminan duplicados, se ponen metadatos

  Sin embargo, el código de la función no elimina duplicados. Es un comentario de intención
  que no se llegó a implementar en el código Python (no hay un if content not in formatted
  ni nada parecido). El código simplemente confía en el MMR y en el LLM.

  ¿Qué pasaría si quisieras "arreglarlo" en la función?
  Si quisieras que format_docs fuera más inteligente, tendrías que añadir lógica para
  comparar el final de un string con el principio del siguiente y "coserlos" eliminando la
  parte repetida. Pero en RAG esto no se suele hacer porque:
   1. Es costoso computacionalmente.
   2. Al LLM le gusta tener un poco de contexto repetido para estar seguro de la
      continuidad.

  En conclusión: La función no ajusta el overlap; simplemente lo presenta de forma ordenada
  para que el LLM, ayudado por la diversidad del retriever MMR, genere una respuesta
  coherente.