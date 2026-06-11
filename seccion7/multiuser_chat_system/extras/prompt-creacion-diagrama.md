gemini "Eres un Arquitecto de Software Senior y Experto en LangGraph y D3.js. Tu objetivo es hacer ingeniería inversa de un archivo Jupyter Notebook de LangGraph y generar una aplicación web interactiva (un único archivo 'index.html' autocontenido). Lee cuidadosamente el archivo adjunto '[NOMBRE_DEL_ARCHIVO.ipynb]'.

Debes aplicar ESTRICTAMENTE la metodología Spec-Driven Development (SDD) siguiendo los 5 pilares a continuación. Tu única salida debe ser el código fuente del archivo 'index.html', sin explicaciones adicionales.

### PILAR 1: INGENIERÍA INVERSA Y EXTRACCIÓN DE DATOS (Estilo Detalle Técnico)
Analiza el código Python del notebook y extrae la lógica de LangGraph (StateGraph, nodes, edges, conditional_edges, schemas, TypedDict, tools). 
Debes construir un diccionario en JavaScript llamado 'nodeData' donde cada llave sea el ID corto de un nodo, y su valor contenga 'title' y 'content'. El 'content' NO DEBE SER un resumen genérico, debe tener un nivel de detalle extremo, incluyendo:
- 'Qué pasa en el código': Explicación de la función Python que se ejecuta.
- 'Estado (State)': Cómo muta el estado global (ej. qué variables se actualizan en el TypedDict).
- 'Lógica Clave/Interrupciones': Si usa 'interrupt()', 'Command()', o invoca herramientas ('tool.invoke'), documéntalo con código literal.
- Formato: Usa etiquetas HTML como <b>, <code> y <pre> para formatear el texto. Los bloques de código deben ser legibles.

### PILAR 2: GENERACIÓN DEL CÓDIGO MERMAID
Genera una variable constante en JS llamada 'mermaidSource' con el diagrama 'graph TD' que represente fielmente el flujo del notebook. Usa etiquetas de texto descriptivas en las flechas (edges) que indiquen qué condición o actualización de estado (Update) ocurre para tomar ese camino.

### PILAR 3: ARQUITECTURA DEL DOM Y ESTILOS (Alto Contraste Obligatorio)
1. Estructura HTML:
   <div id=\"app-container\">
       <div id=\"header\">[Controles]</div>
       <div id=\"graph-container\"></div>
       <div id=\"tooltip\"></div>
   </div>
2. CSS de Accesibilidad:
   - Tooltip: fondo '#111111', texto '#ffffff', z-index muy alto, 'white-space: pre-wrap' para respetar saltos de línea. Etiquetas <code> en cyan ('#00ffff') y <b> en amarillo ('#ffcc00').
   - MermaidConfig: Configura 'theme: 'base''. En 'themeVariables' fuerza colores de máximo contraste: primaryColor: '#ffffff', primaryTextColor: '#000000', lineColor: '#000000', nodeBorder: '#000000'.

### PILAR 4: MOTOR DE RENDERIZADO Y PREVENCIÓN DE BUGS (D3.js)
El renderizado del SVG debe ser a prueba de fallos. Aplica estas reglas matemáticas:
1. Condición de Carrera (Pantallazo Negro): NUNCA uses 'getBBox()'. Lee las dimensiones matemáticas inyectadas por Mermaid usando:
   'const viewBox = svgElement.viewBox.baseVal; const width = viewBox.width || 800; const height = viewBox.height || 600;'.
2. Pausa Asíncrona: Envuelve la inicialización de D3 y eventos en un 'setTimeout(() => { initZoom(svgElement); attachInteractivity(); }, 50);'.
3. ID Dinámico y Limpieza: Usa 'const renderId = \"mermaid-svg-\" + Date.now();' para evitar bugs de caché de Mermaid. Al re-renderizar, usa SOLO 'container.innerHTML = \"\";' (para no destruir el tooltip que está afuera).
4. Retención de Estado del Zoom: Declara una variable global 'let currentTransform = null;'. Antes de re-renderizar por cambio de texto, guarda el estado: 'currentTransform = d3.zoomTransform(oldSvg)'. Al inicializar D3 ('initZoom'), si 'currentTransform' existe, aplícalo directamente en lugar de recalcular el centrado original.

### PILAR 5: SISTEMA DE INTERACTIVIDAD Y UX
1. Botones de Control: Incluye botones para 'Aumentar Texto' (suma 2px a currentFontSize y llama a renderGraph), 'Disminuir Texto' (resta 2px, mínimo 8px) y 'Reset Zoom'. El 'Reset Zoom' DEBE establecer 'currentTransform = null;' antes de ejecutar la transición de centrado.
2. Detección de Nodos Infalible: En 'attachInteractivity()', usa Event Delegation sobre 'container'. Extrae el ID real del nodo limpiando el prefijo dinámico de Mermaid mediante Regex ('flowchart-(.*?)-[0-9]+') o usando 'includes()' contra las llaves de 'nodeData'.
3. Tooltip Cuadrante-Consciente: Calcula el 'getBoundingClientRect()' del tooltip y de la ventana. Ajusta 'top' y 'left' para asegurar que el tooltip JAMÁS se salga de la pantalla (ni por la derecha, ni por abajo).
4. Puente de Hover: Usa un 'setTimeout' de unos 300ms en el 'mouseout' del nodo, que se cancele ('clearTimeout') si el ratón entra al elemento '#tooltip', permitiendo al usuario hacer scroll dentro del texto explicativo largo.

Entrega el código HTML completo y listo para producción." > index.html