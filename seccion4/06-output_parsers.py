# from pydantic import BaseModel

# # es p' el procesamiento de los datos de salida del llm

# class Usuario(BaseModel):
#     id: int
#     nombre: str
#     activo: bool = True

# data = {"id": "123", "nombre": "Ana"}

# # pydantic valida y "completa" el resto, checar que el str de id lo pasó a int
# usuario = Usuario(**data)

# print(usuario.model_dump_json())
# # {"id":123,"nombre":"Ana","activo":true}


# Load environment variables and set up auto-reload
from dotenv import load_dotenv
load_dotenv(override=True)
# ==================================================
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

# la descripción es p' q el llm sepa lo q tiene q devolver
class AnalisisTexto(BaseModel):
    resumen: str = Field(description="Resumen breve del texto.")
    sentimiento: str = Field(description="Sentimiento del texto (Positivo, neutro o negativo)")

llm = ChatOpenAI(model="deepseek-chat", temperature=0.6)

# structured_llm = llm.with_structured_output(AnalisisTexto)
structured_llm = llm.with_structured_output(AnalisisTexto, method="function_calling") # 👀👀👀✨ p' poder usar deepseek

texto_prueba = "Me encantó la nueva película de acción, tiene muchos efectos especiales y emoción."

resultado = structured_llm.invoke(f"Analiza el siguiente texto: {texto_prueba}")

print(resultado.model_dump_json())
# {
#   "resumen":"El texto expresa una opinión positiva sobre una nueva película de acción, destacando sus efectos especiales y la emoción que transmite.",
#   "sentimiento":"Positivo"
# }