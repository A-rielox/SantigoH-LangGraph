Actúa como un Arquitecto de Software Senior y experto absoluto en LangGraph. Te he adjuntado un archivo `.ipynb` que contiene la definición de un grafo de ejecución. Tu objetivo es realizar una ingeniería inversa exhaustiva de este código y generar una documentación técnica estructurada y un diagrama Mermaid.

ANTES de escribir una sola línea de la respuesta final, DEBES realizar un análisis mental estructurado siguiendo estos pasos. No omitas ningún detalle.

### FASE 1: ANÁLISIS PROFUNDO DEL CÓDIGO (No lo imprimas, hazlo mentalmente)

1. Identifica el `State` (ej. TypedDict, MessagesState) y lista todas sus variables.
2. Mapea todos los nodos (`add_node`) y sus funciones asociadas.
3. Mapea todos los bordes (edges) y bordes condicionales (`add_conditional_edges`).
4. Rastrea las mutaciones: Por cada función de nodo, identifica exactamente qué variables del estado se actualizan y cómo (ej. `return {"messages": [nuevo_mensaje]}`).
5. Identifica interrupciones y control de flujo: Busca específicamente el uso de `interrupt()`, `Command(goto=..., update=...)` y llamadas a herramientas (`tool.invoke`).

### FASE 2: ENTREGABLES (Esto es lo que debes imprimir en tu respuesta)

Genera tu respuesta estrictamente en los siguientes dos bloques:

**BLOQUE 1: DICCIONARIO DE NODOS (Nivel de Detalle Extremo)**
Crea un desglose de cada nodo del grafo. Para cada nodo (incluyendo nodos condicionales y sub-grafos), provee:

- **Título del Nodo:** [ID del nodo] (Nombre descriptivo)
- **Qué pasa en el código:** Explica la lógica de la función Python literal. Si invoca a un LLM, menciona con qué herramientas. Si hay un `interrupt()`, menciona exactamente qué datos se envían en el request.
- **Evolución del Estado (State):** Detalla cómo muta el estado global tras pasar por este nodo. Qué llaves se sobreescriben y qué se añade a las listas (como `messages`).
- **Destino / Retorno:** Indica hacia dónde va el flujo (el edge de salida) o si retorna un `Command` para alterar el flujo dinámicamente.
  _Nota: Usa formato Markdown (negritas para variables, bloques de código para fragmentos literales)._

**BLOQUE 2: CÓDIGO MERMAID**
Genera un diagrama `graph TD` de Mermaid que represente este flujo a la perfección.
Reglas estrictas para el Mermaid:

1. Usa nodos visualmente distintos para inicios/fines `(())`, sub-grafos, decisiones lógicas `{}`, y pausas humanas/interrupciones.
2. LAS FLECHAS (Edges) DEBEN TENER TEXTO. Cada flecha debe explicar la condición para tomar ese camino (ej. `| "Si decision == 'respond' <br> Update: messages" |`).
3. Asegúrate de que los IDs del Mermaid coincidan con los conceptos explicados en el Bloque 1.

### FASE 3: AUDITORÍA FINAL

Antes de terminar tu generación, verifica:

- ¿Se me escapó algún nodo condicional oculto en el código?
- ¿Están documentadas las mutaciones del `State` de cada paso?
- ¿El código Mermaid compila lógicamente (sin nodos huérfanos ni sintaxis inválida)?
  Si todo es correcto, entrega la respuesta.
