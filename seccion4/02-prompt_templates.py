# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================
from langchain_core.prompts import PromptTemplate

template = "Eres un experto en marketing. Sugiere un eslogan creativo para un producto {producto}"

# los  PromptTemplate  permiten pasar separando el contenido fijo ( el template ) del variable
prompt = PromptTemplate(
    template = template,
    input_variables=["producto"]
)

prompt_lleno = prompt.format(producto="café orgánico")
print(prompt_lleno)
# python seccion4/02-prompt_templates.py                             [14:43:08]
# Eres un experto en marketing. Sugiere un eslogan creativo para un producto café orgánico
