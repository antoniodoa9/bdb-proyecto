import pymysql.cursors
import random
from datetime import datetime, timedelta

# Conexión a la base de datos (misma que tu script original)
DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="root",
    db="PROYECTO",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

def rellenar_sala_espera(num_pacientes_urgencias=200):
    print(f"\nAbriendo las puertas de Urgencias... (Llenando tabla MEMORY)")
    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            # 1. Obtenemos códigos hash de pacientes reales que sean mayores (<= 1980)
            # para garantizar que tu consulta XML funcione a la perfección.
            cur.execute("""
                SELECT codigo_hash 
                FROM paciente_anonimo 
                WHERE anio_nacimiento <= 1980 
                ORDER BY RAND() 
                LIMIT %s
            """, (num_pacientes_urgencias,))
            
            pacientes = cur.fetchall()
            
            if not pacientes:
                print("No se encontraron pacientes mayores de 45 años en la base de datos.")
                return

            print(f"Se van a ingresar {len(pacientes)} pacientes en triaje...\n")

            # 2. Los metemos en la tabla de triaje uno a uno
            for i, p in enumerate(pacientes):
                codigo_hash = p['codigo_hash']
                
                # Forzamos niveles de triaje altos (1, 2, o 3) para la consulta XML
                nivel = random.choice([1, 2, 2, 3, 3]) 
                
                llegada = datetime.now() - timedelta(minutes=random.randint(5, 120))
                motivo = random.choice([
                    "Disnea aguda y dolor torácico.",
                    "Síncope en domicilio. Palpitaciones previas.",
                    "Exacerbación EPOC. Trabajo respiratorio aumentado.",
                    "Fiebre alta, tos productiva y desaturación.",
                    "Déficit neurológico focal de inicio súbito."
                ])
                
                # Constantes vitales alteradas (acordes a la gravedad)
                tas = random.randint(140, 190)
                tad = random.randint(90, 110)
                fc = random.randint(100, 140)
                sat = round(random.uniform(85.0, 93.0), 1)
                temp = round(random.uniform(37.5, 39.5), 1)
                
                espera_estimada = random.randint(0, 30)

                cur.execute(
                    """INSERT INTO triaje_urgencias_actual
                       (codigo_hash_paciente, fecha_hora_llegada, nivel_triaje_manchester,
                        motivo_consulta, tension_arterial_sistolica, tension_arterial_diastolica,
                        frecuencia_cardiaca, saturacion_oxigeno, temperatura_corporal,
                        estado_actual, sala_box_asignado, tiempo_espera_estimado_min,
                        observaciones_triaje) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        codigo_hash, llegada, nivel, motivo,
                        tas, tad, fc, sat, temp,
                        "En_Espera", f"Box-{random.randint(1,10):02d}", espera_estimada,
                        "Ingreso directo mediante script de repoblación MEMORY."
                    ),
                )

        conn.commit()
        print("¡Sala de espera llena! Tabla MEMORY repoblada con éxito.")

    except Exception as exc:
        print(f"[ERROR] {exc}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    rellenar_sala_espera(200)