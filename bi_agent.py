from langchain_community.llms import Ollama
from langchain_core.callbacks import CallbackManager
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
import pandas as pd
import re
from decimal import Decimal

class BIAgent:
    def __init__(self):
        self.llm = Ollama(
            model="codellama",
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
            temperature=0.1
        )

    def generar_script_grafico(self, columns, results, tipo_grafico='bar'):
        """
        Genera un script de Python que crea un gráfico usando Plotly
        """
        try:
            # Convertir resultados a un DataFrame de pandas
            df = pd.DataFrame(results, columns=columns)
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, Decimal)).any():
                    df[col] = df[col].astype(float)

            data_dict = df.to_dict(orient="records")

            # Crear el prompt
            prompt = self._crear_prompt(data_dict, tipo_grafico)
            print(prompt)
            # Generar el script de gráfico usando el modelo de lenguaje
            script = self.llm.invoke(prompt)
            return script
        except Exception as e:
            print(f"Error al generar el script de gráfico: {e}")
            return None

    def ejecutar_script(self, script):
        """
        Ejecuta un script de Python proporcionado como una cadena de texto
        """
        try:
            # Ejecutar el script de Python
            exec(script)
            print(f"Script ejecutado")
        except Exception as e:
            print(f"Error al ejecutar el script: {e}")

    def _crear_prompt(self, data, tipo_grafico):
        """
        Crea un prompt para el modelo de lenguaje
        """
        template = """
Eres un experto en visualización de datos con scripts python.
Generar un script de Python utilizando la libreria Plotly que genere un grafico de tipo '{tipo_grafico}'. usa los siguientes datos: 

{data}

El gráfico debe mostrar los datos y sus valores de manera clara y efectiva. 
Asegúrate de incluir títulos y etiquetas adecuadas.
Solo retorna el script python. 
Eliminar las explicaciones.
"""
        return template.format(data=data, tipo_grafico=tipo_grafico)
