import gradio as gr
from database_manager import DatabaseManager
from sql_agent import SQLAgent
from bi_agent import BIAgent
import os
from dotenv import load_dotenv

def procesar_consulta(pregunta):
    """Procesa la consulta en lenguaje natural y devuelve los resultados y el script del gráfico."""
    load_dotenv()
    db_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"), 
        "database": os.getenv("DB_NAME") 
    }
    
    try:
        db = DatabaseManager(**db_config)
        db.connect()
        schema = db.obtener_esquema_bd()
        agent = SQLAgent()
        agent.inicializar(schema)
        
        query = agent.generar_consulta(pregunta)
        columns, results = db.ejecutar_consulta(query)
        resultados_texto = mostrar_resultados(columns, results)
        
        bi_agent = BIAgent()
        script = bi_agent.generar_script_grafico(columns, results)
        ejecutar_script(script)
        
        return resultados_texto, script
    except Exception as e:
        return f"Error al procesar la consulta: {e}", None
    finally:
        if 'db' in locals():
            db.close()

def mostrar_resultados(columns, results):
    """Devuelve los resultados de la consulta en formato de texto."""
    resultado = "\nResultados:\n" + "-" * 80 + "\n"
    headers = " | ".join(f"{col:<15}" for col in columns)
    resultado += headers + "\n" + "-" * 80 + "\n"
    
    for row in results:
        formatted_row = [str(val)[:15] for val in row]
        row_str = " | ".join(f"{val:<15}" for val in formatted_row)
        resultado += row_str + "\n"
    
    resultado += "=" * 80
    return resultado

def ejecutar_script(script):
    """Ejecuta el script del gráfico."""
    # Aquí asumimos que el script es compatible con matplotlib
    try:
        namespace = {}
        exec(script, namespace)
        print("Script ejecutado con éxito.")
    except Exception as e:
        print(f"Error al ejecutar el script: {e}")
    
    return namespace['fig']


# Configuración de la interfaz de Gradio
iface = gr.Interface(
    fn=procesar_consulta,
    inputs="text",
    outputs=["text", "text"],
    live=False,
    title="Consulta SQL con Gradio",
    description="Introduce una consulta en lenguaje natural para obtener resultados SQL y generar gráficos."
)

iface.launch()