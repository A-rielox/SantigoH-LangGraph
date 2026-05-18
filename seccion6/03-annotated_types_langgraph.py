from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, List, Annotated
import os
# from tkinter import Tk, filedialog
import openai
from operator import add

from dotenv import load_dotenv
load_dotenv(override=True)



# Configuración
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# Definición del Estado
class State(TypedDict):
    notes: str
    participants: List[str]
    topics: List[str]
    action_items: List[str]
    minutes: str
    summary: str
    logs: Annotated[list[str], add]

# ============= NODOS DEL WORKFLOW =============

def extract_participants(state: State) -> State:
    """Extrae los participantes de la reunión."""

    prompt = f"""
    De las siguientes notas de reunión, extrae SOLO los nombres de los participantes.
    
    Notas: {state['notes']}
    
    Responde ÚNICAMENTE con una lista de nombres separados por comas, sin explicaciones adicionales.
    Ejemplo: Juan García, María López, Carlos Ruiz
    """
    
    response = llm.invoke(prompt)
    participants = [p.strip() for p in response.content.split(',') if p.strip()]
    
    print(f"✓ Participantes extraídos: {len(participants)} personas")
    
    return {
        'participants': participants,
        'logs': ["Paso 1 completado"]
    }

def identify_topics(state: State) -> State:
    """Identifica los temas principales discutidos."""

    prompt = f"""
    Identifica los 3-5 temas principales discutidos en esta reunión.
    
    Notas: {state['notes']}
    
    Responde SOLO con los temas separados por punto y coma (;).
    Ejemplo: Arquitectura del sistema; Plazos de entrega; Asignación de tareas
    """
    
    response = llm.invoke(prompt)
    topics = [t.strip() for t in response.content.split(';') if t.strip()]
    
    print(f"✓ Temas identificados: {len(topics)} temas")
    
    return {
        'topics': topics,
        'logs': ["Paso 2 completado"]
    }

def extract_actions(state: State) -> State:
    """Extrae las acciones acordadas y sus responsables."""

    prompt = f"""
    Extrae las acciones específicas acordadas en la reunión, incluyendo el responsable si se menciona.
    
    Notas: {state['notes']}
    
    Formato de respuesta: Una acción por línea, separadas por |
    Ejemplo: María se encargará del backend | Carlos preparará el plan de testing | Próxima reunión el lunes
    
    Si no hay acciones claras, responde con: "No se identificaron acciones específicas"
    """
    
    response = llm.invoke(prompt)
    
    if "No se identificaron" in response.content:
        action_items = []
    else:
        action_items = [a.strip() for a in response.content.split('|') if a.strip()]
    
    print(f"✓ Acciones extraídas: {len(action_items)} items")
    
    return {
        'action_items': action_items,
        'logs': ["Paso 3 completado"]
    }

def generate_minutes(state: State) -> State:
    """Genera una minuta formal de la reunión."""

    participants_str = ", ".join(state['participants'])
    topics_str = "\n• ".join(state['topics'])
    actions_str = "\n• ".join(state['action_items']) if state['action_items'] else "No se definieron acciones específicas"
    
    prompt = f"""
    Genera una minuta formal y profesional basándote en la siguiente información:
    
    PARTICIPANTES: {participants_str}
    
    TEMAS DISCUTIDOS:
    • {topics_str}
    
    ACCIONES ACORDADAS:
    • {actions_str}
    
    NOTAS ORIGINALES: {state['notes']}
    
    Genera una minuta profesional de máximo 150 palabras que incluya:
    1. Encabezado con tipo de reunión
    2. Lista de asistentes
    3. Puntos principales discutidos
    4. Acuerdos y próximos pasos
    
    Usa un tono formal y estructura clara.
    """
    
    response = llm.invoke(prompt)
    
    print(f"✓ Minuta generada: {len(response.content.split())} palabras")
    
    return {
        'minutes': response.content
    }

def create_summary(state: State) -> State:
    """Crea un resumen ejecutivo ultra-breve."""

    prompt = f"""
    Crea un resumen ejecutivo de MÁXIMO 2 líneas (30 palabras) que capture la esencia de esta reunión.
    
    Participantes: {', '.join(state['participants'][:3])}{'...' if len(state['participants']) > 3 else ''}
    Tema principal: {state['topics'][0] if state['topics'] else 'General'}
    Acciones clave: {len(state['action_items'])} acciones definidas
    
    El resumen debe ser conciso y directo al punto.
    """
    
    response = llm.invoke(prompt)
    
    print(f"✓ Resumen creado")
    
    return {
        'summary': response.content
    }

# ============= CONSTRUCCIÓN DEL GRAFO =============

def create_workflow():
    """Crea y configura el workflow de LangGraph."""
    workflow = StateGraph(State)
    
    # Agregar todos los nodos
    workflow.add_node("extract_participants", extract_participants)
    workflow.add_node("identify_topics", identify_topics)
    workflow.add_node("extract_actions", extract_actions)
    workflow.add_node("generate_minutes", generate_minutes)
    workflow.add_node("create_summary", create_summary)
    
    # Configurar flujo secuencial
    workflow.add_edge(START, "extract_participants")
    workflow.add_edge("extract_participants", "identify_topics")
    workflow.add_edge("identify_topics", "extract_actions")
    workflow.add_edge("extract_actions", "generate_minutes")
    workflow.add_edge("generate_minutes", "create_summary")
    workflow.add_edge("create_summary", END)
    
    return workflow.compile()

# ============= FUNCIONES DE PROCESAMIENTO =============

def transcribe_media_direct(file_path: str) -> str:
    """Transcribe usando directamente la API de OpenAI Whisper."""
    try:
        print("🎙️ Transcribiendo con OpenAI Whisper API directa...")
        
        client = openai.OpenAI()  # Usa OPENAI_API_KEY del entorno
        
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="es",  # Español
                prompt="Esta es una reunión de trabajo en español con múltiples participantes.",
                response_format="text"
            )
        
        print(f"✓ Transcripción completada: {len(transcript)} caracteres")
        return transcript
        
    except Exception as e:
        print(f"❌ Error en transcripción: {e}")
        return f"Error: {str(e)}"

def process_meeting_notes(notes: str, app):
    """Procesa una nota de reunión individual."""
    initial_state = {
        'notes': notes,
        'participants': [],
        'topics': [],
        'action_items': [],
        'minutes': '',
        'summary': '',
        'logs': []
    }
    
    print("\n" + "="*60)
    print("🔄 Procesando nota de reunión...")
    print("="*60)
    
    result = app.invoke(initial_state)
    return result

def display_results(result: State, meeting_num: int):
    """Muestra los resultados de forma estructurada."""
    print(f"\n📋 RESULTADOS - REUNIÓN #{meeting_num}")
    print("-"*60)
    
    print(f"\n👥 Participantes ({len(result['participants'])}):")
    for p in result['participants']:
        print(f"   • {p}")
    
    print(f"\n📍 Temas tratados ({len(result['topics'])}):")
    for t in result['topics']:
        print(f"   • {t}")
    
    print(f"\n✅ Acciones acordadas ({len(result['action_items'])}):")
    if result['action_items']:
        for a in result['action_items']:
            print(f"   • {a}")
    else:
        print("   • No se definieron acciones específicas")
    
    print(f"\n📄 MINUTA FORMAL:")
    print("-"*40)
    print(result['minutes'])
    print("-"*40)
    
    print(f"\n💡 RESUMEN EJECUTIVO:")
    print(f"   {result['summary']}")
    
    print("\n" + "="*60)

    print(result['logs'])

# ============= DEMOSTRACIÓN =============

if __name__ == "__main__":
    app = create_workflow()

    # --- CAMBIO PARA LINUX/CONSOLA ---
    # Se comenta la interfaz gráfica para evitar errores de $DISPLAY en entornos sin GUI.
    # En su lugar, se hardcodea la ruta del archivo a procesar.
    # Pequeña interfaz gráfica: selector de archivo
    # Tk().withdraw()
    # file_path = filedialog.askopenfilename(
    #     title="Selecciona un vídeo o transcripción",
    #     filetypes=[
    #         ("Vídeo/Audio", "*.mp4 *.mov *.m4a *.mp3 *.wav *.mkv *.webm"),
    #         ("Texto", "*.txt *.md")
    #     ]
    # )

    # Reemplazo manual para ejecución directa:
    #   🧭
    file_path = os.path.join(os.path.dirname(__file__), "Simulacion_reunion.mp4")
    print(f"📂 Procesando archivo configurado: {file_path}")

    if not file_path:
        print("No se seleccionó archivo.")
        raise SystemExit(0)

    ext = os.path.splitext(file_path)[1].lower() #   🪇
    media_exts = {".mp4", ".mov", ".m4a", ".mp3", ".wav", ".mkv", ".webm"}

    if ext in media_exts:
        notes = transcribe_media_direct(file_path) 
    else: # si no es de los de arriba => ya está en texto
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            notes = f.read()

    result = process_meeting_notes(notes, app)
    display_results(result, 1)


# python 03-annotated_types_langgraph.py

# ##############################################
#   🧭
#
# Esta expresión es una forma muy común y profesional de construir rutas de archivos en
#   Python para que funcionen en cualquier computadora (Windows, Mac o Linux).

#   Aquí tienes el desglose paso a paso:

#   1. __file__
#   Es una variable especial de Python que contiene la ruta del archivo que se está
#   ejecutando en este momento (en tu caso, la ruta de
#   02-procesador_reuniones_langgraph.py).

#   2. os.path.dirname(...)
#   Esta función toma una ruta y devuelve el nombre del directorio (carpeta) donde se
#   encuentra.
#    * Ejemplo: Si __file__ es /home/usuario/proyecto/script.py,
#      os.path.dirname(__file__) devolverá /home/usuario/proyecto/.

#   3. "Simulacion_reunion.mp4"
#   Es simplemente el nombre del archivo de video que quieres abrir. Al estar en la misma
#   carpeta que tu script, necesitamos unirlo a la ruta obtenida en el paso anterior.

#   4. os.path.join(carpeta, archivo)
#   Es la función encargada de unir o concatenar ambas partes para formar la ruta
#   completa.
#    * Lo más importante: Se encarga de poner las barras inclinadas correctas
#      automáticamente.
#        * En Linux/Mac pondrá una /.
#        * En Windows pondrá una \.


# ##############################################
#   🪇
#
# Esta línea se utiliza para extraer la extensión del archivo de forma segura y uniforme.
#   Vamos a romperla en partes:

#   1. os.path.splitext(file_path)
#   Esta función divide la ruta del archivo en dos partes: el nombre base y la extensión.
#   Devuelve una tupla con dos elementos.
#    * Ejemplo: Si file_path es "reunion.mp4", el resultado es ('reunion', '.mp4').

#   2. [1]
#   Como la función anterior devuelve una lista de dos cosas, usamos [1] para quedarnos con el
#   segundo elemento, que es justamente la extensión (incluyendo el punto).
#    * Siguiendo el ejemplo: de ('reunion', '.mp4') nos quedamos con '.mp4'.

#   3. .lower()
#   Convierte la extensión a minúsculas.
#    * ¿Por qué? Porque para una computadora, .MP4, .Mp4 y .mp4 son diferentes. Al pasarlo
#      todo a minúsculas, te aseguras de que el programa funcione aunque el archivo tenga la
#      extensión en mayúsculas.