from database_manager import DatabaseManager
from sql_agent import SQLAgent
from bi_agent import BIAgent
import os
from dotenv import load_dotenv

def mostrar_resultados(columns, results):
    """Muestra los resultados de la consulta en formato tabular"""
    print("\nResultados:")
    print("-" * 80)
    headers = " | ".join(f"{col:<15}" for col in columns)
    print(headers)
    print("-" * 80)
    
    for row in results:
        formatted_row = [str(val)[:15] for val in row]
        row_str = " | ".join(f"{val:<15}" for val in formatted_row)
        print(row_str)
    
    print("=" * 80)

def main():
    # Cargar las variables del archivo .env
    load_dotenv()
    # Configuración de la base de datos
    db_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"), 
        "database": os.getenv("DB_NAME") 
    }

    try:
        # Inicializar el gestor de base de datos
        db = DatabaseManager(**db_config)
        db.connect()
        #db.crear_esquema_tienda()
        
        # Obtener el esquema y crear el agente
        schema = db.obtener_esquema_bd()
        agent = SQLAgent()
        agent.inicializar(schema)
        
        # Inicializar el agente BI
        bi_agent = BIAgent()
        
        print("\n¡Asistente listo! Escribe 'salir' para terminar.")
        print("=" * 50)

        # Bucle principal
        while True:
            pregunta = input("\nTu consulta: ")
            
            if pregunta.lower() in ['salir', 'exit', 'quit']:
                print("\n¡Hasta luego!")
                break
            
            try:
                # Generar y ejecutar la consulta
                print("\nGenerando consulta SQL...")
                query = agent.generar_consulta(pregunta)
                print(f"\nConsulta SQL generada:\n{query}\n")
                
                print("Ejecutando consulta...")
                columns, results = db.ejecutar_consulta(query)
                
                mostrar_resultados(columns, results)
                
                # Generar script de gráfico
                print("\nGenerando script de gráfico...")
                script = bi_agent.generar_script_grafico(columns, results)
                if script:
                    print("\nScript de gráfico generado:\n")
                    print(script)
                    bi_agent.ejecutar_script(script.replace("```", ""))
            except Exception as e:
                print(f"Error al procesar la consulta: {e}")
                
    except Exception as e:
        print(f"Error en la aplicación: {e}")
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()