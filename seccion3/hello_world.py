# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)

# =================================================================

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="deepseek-chat", temperature=0.7) 

pregunta = "¿en qué año llegó el hombre a la luna ?"
print("\n \n Pregunta: ", pregunta)

respuesta = llm.invoke(pregunta)
print("\n \n Respuesta: ", respuesta.content)


# en terminal
# python seccion3/hello_world.py








from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="openai:deepseek-chat", temperature=0.5) 
tpl = PromptTemplate(input_variables=["nombre"],
                    template="Saluda a {nombre} como si fueras un asistente cortés.") 

chain = tpl | llm 
msg = chain.invoke({"nombre": "Carlos"}) # dict, no kwargs sueltos print(msg.content)
print(msg.content)


