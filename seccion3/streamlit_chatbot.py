# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

# 🔔🔔 SystemMessage es para los mensajes del desarrollador del sistema

# Configuración inicial
st.set_page_config(page_title="Chatbot Básico", page_icon="🤖")
st.title("🤖 Chatbot Básico con LangChain")
st.markdown("Este es un *chatbot de ejemplo* construido con LangChain + Streamlit. ¡Escribe tu mensaje abajo para comenzar!")

with st.sidebar:
    st.header("Configuración")
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.5, 0.1)
    model_name = st.selectbox("Modelo", ["deepseek-chat", "gemini-2.5-flash"])

    # Recrear el modelo con nuevos parámetros
    chat_model = ChatOpenAI(model=model_name, temperature=temperature)

# Inicializar el historial de mensajes en session_state
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Crear el template de prompt con comportamiento específico
prompt_template = PromptTemplate(
    input_variables=["mensaje", "historial"],
    template="""Eres un asistente útil y amigable llamado ChatBot Pro. 

Historial de conversación:
{historial}

Responde de manera clara y concisa a la siguiente pregunta: {mensaje}"""
)

# Crear cadena usando LCEL (LangChain Expression Language)
# le estoy proporcionando el template al modelo
cadena = prompt_template | chat_model

# Renderizar historial existente
for msg in st.session_state.mensajes:
    if isinstance(msg, SystemMessage):
        continue  # no mostrar mensajes del sistema al usuario
        
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    
    # p'q pinte los mensajes dependiendo de si el mensaje es de rol "assistant" o "user"
    with st.chat_message(role):
        st.markdown(msg.content)

if st.button("🗑️ Nueva conversación"):
    st.session_state.mensajes = []
    st.rerun()

# Input de usuario
# st bloquea la ejecución del programa hasta que el user introdusca el texto
pregunta = st.chat_input("Escribe tu mensaje:")

if pregunta:
    # Mostrar y almacenar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(pregunta)
    
    # Generar y mostrar respuesta del asistente
    try:
        with st.chat_message("assistant"):
            # response_placeholder es lo q contiene la respuesta q va generando el llm
            response_placeholder = st.empty()
            full_response = ""

            # Streaming de la respuesta
            for chunk in cadena.stream({"mensaje": pregunta, "historial": st.session_state.mensajes}):
                full_response += chunk.content
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
        
        # almacenando los mensajes en el state
        st.session_state.mensajes.append(HumanMessage(content=pregunta))
        st.session_state.mensajes.append(AIMessage(content=full_response))
        
    except Exception as e:
        st.error(f"Error al generar respuesta: {str(e)}")
        st.info("Verifica que tu API Key de OpenAI esté configurada correctamente.")
