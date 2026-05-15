import pymysql.cursors
import time

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root', 
                             db='PROYECTO',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def medir_consulta_temporal():
    sql = """
        SELECT COUNT(*) as total_eventos 
        FROM evento_clinico_myisam
        WHERE fecha_evento BETWEEN '2023-01-01' AND '2023-01-31';
    """

    sql2 = """
        SELECT pa.id_paciente,
            pa.sexo_biologico,
            pa.anio_nacimiento,
            pa.region_sanitaria,
            ec.fecha_evento,
            ec.tipo_evento,
            ec.codigo_cie10,
            ec.descripcion_cie10,
            ec.especialidad,
            ec.resolucion
        FROM paciente_anonimo pa
        INNER JOIN evento_clinico ec ON ec.id_paciente = pa.id_paciente
        WHERE pa.id_paciente = 1
        ORDER BY ec.fecha_evento ASC;
        """
    
    sql3 = """
        SELECT id_triaje, codigo_hash_paciente, fecha_hora_llegada,
            motivo_consulta, sala_box_asignado, tiempo_espera_estimado_min
        FROM triaje_urgencias_actual
        WHERE nivel_triaje_manchester = 1 AND estado_actual = "En_Espera";;
        """
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            iteraciones = 50
            tiempo_total = 0
            
            print(f"Ejecutando consulta temporal {iteraciones} veces...")
            
            for _ in range(iteraciones):
                inicio = time.perf_counter() 
                cursor.execute(sql)
                fin = time.perf_counter()
                tiempo_total += (fin - inicio)
            
            tiempo_medio_ms = (tiempo_total / iteraciones) * 1000
            
            cursor.execute(sql)
            resultado = cursor.fetchone()
            
            #print(f"Eventos encontrados: {resultado['total_eventos']}")

            print(f"Tiempo MEDIO de ejecución: {tiempo_medio_ms:.4f} milisegundos")

    except connection.Error as err:
        print(f"Error: {err}")

if __name__ == '__main__':
    try:
        medir_consulta_temporal()
    finally:
        connection.close()