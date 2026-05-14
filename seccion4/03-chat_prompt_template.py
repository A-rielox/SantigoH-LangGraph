# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================
from langchain_core.prompts import ChatPromptTemplate

#    ChatPromptTemplate.   Prompt template for chat models.
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un traductor del español al inglés muy preciso."),
    ("human", "{texto}")
])

# me los devuelve formateados como "SystemMessage" o "HumanMessage"
mensajes = chat_prompt.format_messages(texto="Hola mundo, ¿cómo estás?")

for m in mensajes:
    print(f"{type(m)}: {m.content}")
# <class 'langchain_core.messages.system.SystemMessage'>: Eres un traductor del español al inglés muy preciso.
# <class 'langchain_core.messages.human.HumanMessage'>: Hola mundo, ¿cómo estás?



#         .format_messages
# Create a chat prompt template from a variety of message formats.

# Examples
# Instantiation from a list of message templates:

#     template = ChatPromptTemplate.from_messages(
#         [
#             ("human", "Hello, how are you?"),
#             ("ai", "I'm doing well, thanks!"),
#             ("human", "That's good to hear."),
#         ]