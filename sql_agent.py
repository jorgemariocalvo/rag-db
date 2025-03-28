from langchain_community.llms import Ollama
from langchain_core.callbacks import CallbackManager
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

class SQLAgent:
    def __init__(self):
        self.llm = None
        self.prompt = None

    def inicializar(self, schema):
        """Inicializa el agente con el esquema de la base de datos"""
        try:
            # Configurar el modelo
            self.llm = Ollama(
                model="llama3",
                callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
                temperature=0.1
            )
            
            # Crear el prompt
            self.prompt = self._crear_prompt_sql(schema)
            print("Agente SQL inicializado correctamente")
        except Exception as e:
            print(f"Error al inicializar el agente: {e}")
            raise

    def _crear_prompt_sql(self, schema):
        """Crea el prompt especializado para consultas SQL"""
        schema_info = []
        for table, details in schema.items():
            columns = [f"{col[0]} ({col[1]})" for col in details['columns']]
            foreign_keys = [f"{fk[0]} -> {fk[1]}.{fk[2]}" for fk in details['foreign_keys']]
            
            schema_info.append(f"""
Tabla: {table}
Columnas: {', '.join(columns)}
Relaciones: {', '.join(foreign_keys) if foreign_keys else 'Ninguna'}
            """)
        
        template = """Eres un experto en SQL que convierte consultas en lenguaje natural a consultas SQL.
Utiliza el siguiente esquema de base de datos:

{0}

Convertir la siguiente consulta en lenguaje natural a una consulta SQL válida.
Solo devuelve la consulta SQL, sin explicaciones adicionales.

Consulta: {{input}}

SQL:"""

        template = template.format('\n'.join(schema_info))
        return PromptTemplate(
            input_variables=["input"],
            template=template
        )

    def generar_consulta(self, pregunta):
        """Genera una consulta SQL a partir de una pregunta en lenguaje natural"""
        try:
            if not self.llm or not self.prompt:
                raise Exception("El agente no ha sido inicializado")
            
            return self.llm.invoke(self.prompt.format(input=pregunta))
        except Exception as e:
            print(f"Error al generar la consulta: {e}")
            raise
