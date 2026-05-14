# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)

# =================================================================

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7) 

pregunta = "¿en qué año llegó Colón a América ?"
print("\n \n Pregunta: ", pregunta)

respuesta = llm.invoke(pregunta)
print("\n \n Respuesta: ", respuesta.content)


# en terminal
# python seccion3/hello_world_Gemini.py






