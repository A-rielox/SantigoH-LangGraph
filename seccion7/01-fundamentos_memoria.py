from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv(override=True)

################################################################

llm = ChatOpenAI(model="deepseek-chat", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Eres un asistente útil."),
    MessagesPlaceholder(variable_name='history'),
    ("human", "{input}")
])

chain = prompt | llm
history = []

print("Chat en terminal (escribe 'salir' para terminar)\n")

while True:
    try:
        user_input = input("Tú: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nHasta luego!")
        break

    if not user_input:
        continue
    if user_input.lower() in {"salir", "exit", "quit"}:
        print("Hasta luego!")
        break

    respuesta = chain.invoke({ "history":history, "input": user_input })
    print("Asistente:", respuesta.content)
    print("history: ", history)

    # Actualizar el historial
    history.extend([
        HumanMessage( content=user_input ),
        AIMessage( content=respuesta.content )
    ])

# python seccion7/01-fundamentos_memoria.py
