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


    def _crear_prompt(self, data, tipo_grafico):
        """
        Crea un prompt para el modelo de lenguaje
        """
        template = """
Rol del sistema: Eres un experimentado asistente de generación de código en Python. Tu objetivo es generar un script de Python que, dada la siguiente información, cree un gráfico utilizando la librería matplotlib.

Instrucciones para la generación del script:

1- Debes recibir un diccionario con datos como parámetro de entrada. Este diccionario contendrá los valores que se utilizarán para crear el grafico.

2- El script debe utilizar la librería matplotlib para crear un gráfico.

3- Basándote en el diccionario proporcionado, elige automáticamente el tipo de gráfico de matplotlib que mejor represente los datos (por ejemplo: línea, barras, pastel, dispersión, etc.).

4- Incluir el diccionario con datos en el script generado como un dataframe pandas, para utilizarlo en el scrip del grafico.

5- Asegúrate de incluir comentarios en el script para explicar cada paso del proceso.

6- El script solo debe crear el grafico. el script debe guardar el grafico en un archivo con nombre: grafico.png. El script debe ejecutar las instrucciones desde el script principal, sin funciones.

7- Genera solo el script, sin comentarios al final del script generado.

Entrada :

{data}

"""
        return template.format(data=data, tipo_grafico=tipo_grafico)
