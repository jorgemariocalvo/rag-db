import psycopg2

class DatabaseManager:
    def __init__(self, host, port, user, password, database):
        self.connection_params = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }
        self.conn = None

    def connect(self):
        """Establece la conexión con la base de datos"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.set_client_encoding('UTF8')
            print("Conexión establecida exitosamente")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise

    def crear_esquema_tienda(self):
        """Crea el esquema de la tienda con datos de ejemplo"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SET client_encoding TO 'UTF8';")
                
                # Borrar tablas si existen
                cur.execute("""
                    DROP TABLE IF EXISTS ventas;
                    DROP TABLE IF EXISTS productos;
                    DROP TABLE IF EXISTS categorias;
                    DROP TABLE IF EXISTS clientes;
                """)
                
                # Crear tablas con COLLATE específico
                cur.execute("""
                CREATE TABLE categorias (
                    id_categoria SERIAL PRIMARY KEY,
                    nombre VARCHAR(50) COLLATE "C",
                    descripcion TEXT COLLATE "C"
                );

                CREATE TABLE productos (
                    id_producto SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) COLLATE "C",
                    precio DECIMAL(10,2),
                    stock INTEGER,
                    id_categoria INTEGER REFERENCES categorias(id_categoria)
                );

                CREATE TABLE clientes (
                    id_cliente SERIAL PRIMARY KEY,
                    nombre VARCHAR(50) COLLATE "C",
                    email VARCHAR(100) COLLATE "C",
                    fecha_registro DATE
                );

                CREATE TABLE ventas (
                    id_venta SERIAL PRIMARY KEY,
                    id_cliente INTEGER REFERENCES clientes(id_cliente),
                    id_producto INTEGER REFERENCES productos(id_producto),
                    cantidad INTEGER,
                    fecha_venta DATE,
                    total DECIMAL(10,2)
                );
                """)
                
                # Insertar datos de ejemplo usando codificación ASCII
                cur.execute("""
                INSERT INTO categorias (nombre, descripcion) VALUES
                    ('Electronicos', 'Productos electronicos y gadgets'),
                    ('Ropa', 'Vestimenta y accesorios'),
                    ('Libros', 'Libros fisicos y digitales');

                INSERT INTO productos (nombre, precio, stock, id_categoria) VALUES
                    ('Smartphone XYZ', 599.99, 50, 1),
                    ('Laptop ABC', 999.99, 30, 1),
                    ('Camiseta Cool', 29.99, 100, 2),
                    ('Jeans Classic', 49.99, 75, 2),
                    ('Python Mastery', 39.99, 60, 3);

                INSERT INTO clientes (nombre, email, fecha_registro) VALUES
                    ('Ana Garcia', 'ana@email.com', '2023-01-15'),
                    ('Carlos Lopez', 'carlos@email.com', '2023-02-20'),
                    ('Maria Rodriguez', 'maria@email.com', '2023-03-10');

                INSERT INTO ventas (id_cliente, id_producto, cantidad, fecha_venta, total) VALUES
                    (1, 1, 1, '2024-01-15', 599.99),
                    (2, 3, 2, '2024-01-16', 59.98),
                    (3, 5, 1, '2024-01-17', 39.99);
                """)
                
            self.conn.commit()
            print("Esquema de tienda creado exitosamente")
        except Exception as e:
            print(f"Error creando el esquema: {e}")
            self.conn.rollback()
            raise

    def obtener_esquema_bd(self):
        """Obtiene la estructura del esquema de la base de datos"""
        try:
            schema = {}
            with self.conn.cursor() as cur:
                # Obtener todas las tablas
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_type = 'BASE TABLE';
                """)
                tables = cur.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    cur.execute("""
                        SELECT 
                            column_name,
                            data_type,
                            CASE WHEN is_nullable = 'YES' THEN 'NULL' ELSE 'NOT NULL' END as nullable
                        FROM information_schema.columns
                        WHERE table_name = %s
                        ORDER BY ordinal_position;
                    """, (table_name,))
                    columns = cur.fetchall()
                    
                    cur.execute("""
                        SELECT
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name
                        FROM information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY'
                            AND tc.table_name = %s;
                    """, (table_name,))
                    foreign_keys = cur.fetchall()
                    
                    schema[table_name] = {
                        'columns': columns,
                        'foreign_keys': foreign_keys
                    }
            
            return schema
        except Exception as e:
            print(f"Error al obtener el esquema: {e}")
            raise

    def ejecutar_consulta(self, query):
        """Ejecuta una consulta SQL y devuelve los resultados"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                
                if cur.description is None:
                    return ["Affected rows"], [cur.rowcount]
                
                columns = [desc[0] for desc in cur.description]
                results = cur.fetchall()
                
                if not results:
                    return columns, [["No se encontraron resultados"]]
                
                return columns, results
                
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return ["Error"], [[str(e)]]

    def close(self):
        """Cierra la conexión con la base de datos"""
        if self.conn:
            self.conn.close()
            print("Conexión cerrada")