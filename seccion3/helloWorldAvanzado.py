# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)

# =================================================================



from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="deepseek-chat", temperature=0.7) 




tpl = PromptTemplate(input_variables=["nombre"],
                    template="Saluda a {nombre} como si fueras su subdito.")

# le proporciono la plantilla al LLM
chain = tpl | llm

msg = chain.invoke({"nombre": "Arielox"})
print(msg.content)


# en terminal
# python seccion3/hello_world.py
