import pymysql.cursors
from faker import Faker
import hashlib
import random
from datetime import datetime, timedelta

# Configuramos Faker para datos de España
fake = Faker('es_ES')

# CONEXIÓN A LA BASE DE DATOS
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='PROYECTO',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def generar_datos_longitudinales(num_pacientes):
    print(f"Iniciando la generación de {num_pacientes} historiales con combinatoria clínica real...")
    
    # =====================================================================
    # DICCIONARIOS DE CONSTRUCCIÓN CLÍNICA (Para evitar textos sin sentido)
    # =====================================================================
    
    # 1. Factores de Riesgo
    riesgos_base = ['Ninguno', 'Fumador activo (1 paquete/día)', 'Exfumador (desde hace 5 años)', 'Hipertensión arterial', 'Diabetes Mellitus Tipo 2', 'Obesidad Grado I', 'Sedentarismo grave', 'Dislipemia']
    riesgos_modificador = ['sin tratamiento actual.', 'controlado con medicación.', 'con mal control terapéutico.', 'de diagnóstico reciente.', 'en seguimiento por su médico de cabecera.', '']

    # 2. Eventos Clínicos: Descripciones y Exploraciones
    descripciones_cie10 = ['Infección respiratoria aguda', 'Cefalea tensional', 'Gastroenteritis', 'Lumbalgia mecánica', 'Crisis hipertensiva', 'Arritmia no especificada', 'Cuadro de ansiedad', 'Anemia ferropénica', 'Dermatitis atópica', 'Infección urinaria', 'Faringoamigdalitis', 'Esguince de tobillo', 'Migraña', 'Crisis asmática']
    
    estado_general = ["Paciente consciente y orientado.", "Refiere malestar general de varios días de evolución.", "Acude por dolor agudo de inicio súbito.", "Estado general conservado.", "Refiere astenia y anorexia en las últimas semanas."]
    exploracion_fisica = ["Auscultación cardiopulmonar rítmica y sin soplos.", "Abdomen blando, depresible y doloroso a la palpación.", "No se palpan adenopatías.", "Se observa eritema e inflamación local.", "Exploración neurológica básica sin hallazgos patológicos.", "Movilidad articular reducida por dolor."]
    
    alergias_y_notas = ["Sin alergias medicamentosas conocidas.", "Alergia a Penicilina.", "Alergia a AINEs.", "Intolerancia a la lactosa.", "Se pauta tratamiento analgésico y reposo.", "Se solicita analítica completa.", "Pendiente de ecografía de control.", "Se aconseja beber abundante líquido.", "Derivado a fisioterapia."]

    # 3. Bajas Médicas
    causas_baja = ['Recuperación postoperatoria', 'Cuadro de ansiedad y estrés', 'Gripe estacional severa', 'Fractura ósea leve', 'Gastroenteritis aguda', 'Esguince cervical', 'Lumbociatalgia', 'Intervención oftalmológica']
    contexto_baja = ['que impide el desarrollo de su actividad laboral habitual.', 'tras accidente in itinere.', 'con pronóstico favorable a corto plazo.', 'que requiere reposo absoluto.', 'pendiente de valoración por el tribunal médico.']

    # 4. Triaje Urgencias
    motivos_urgencia = ['Dolor torácico irradiado', 'Dificultad respiratoria progresiva', 'Síncope con recuperación espontánea', 'Dolor abdominal agudo', 'Cefalea intensa con fotofobia', 'Traumatismo craneoencefálico leve', 'Reacción alérgica cutánea', 'Crisis de ansiedad']
    observaciones_triaje = ["Llega por su propio pie.", "Trasladado en ambulancia básica.", "Acompañado por un familiar.", "Constantes estables en el momento del triaje.", "Se deriva a box de críticos por precaución.", "Paciente muy quejumbroso."]

    try:
        with connection.cursor() as cursor:
            for i in range(num_pacientes):
                
                # --- DATOS BASE DEL PACIENTE ---
                documento = fake.unique.nif()
                codigo_hash = hashlib.sha256(documento.encode()).hexdigest()
                fecha_nac = fake.date_of_birth(minimum_age=1, maximum_age=95)
                sexo = random.choice(['M', 'F']) 
                grupo_sangre = random.choice(['A+','A-','B+','B-','AB+','AB-','O+','O-'])
                provincia = fake.state()
                
                # Factor de riesgo combinado (Ej: "Diabetes Mellitus Tipo 2 controlado con medicación.")
                factores = f"{random.choice(riesgos_base)} {random.choice(riesgos_modificador)}".strip()

                # --- PACIENTE ANÓNIMO ---
                sql_anonimo = """
                    INSERT INTO paciente_anonimo 
                    (codigo_hash, anio_nacimiento, sexo_biologico, grupo_sanguineo, region_sanitaria, factores_riesgo, activo) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_anonimo, (codigo_hash, fecha_nac.year, sexo, grupo_sangre, provincia, factores, 1))
                id_paciente = cursor.lastrowid 

                # --- DATOS PERSONALES ---
                direccion_unica = f"{fake.street_name()}, {random.randint(1, 150)}, Puerta {random.randint(1, 10)}"
                sql_personal = """
                    INSERT INTO datos_personales 
                    (id_paciente, codigo_hash, nombre, primer_apellido, segundo_apellido, documento_identidad, 
                     fecha_nacimiento, num_seguridad_social, telefono_contacto, email_contacto, direccion_completa, 
                     municipio, provincia, consentimiento_rgpd) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_personal, (
                    id_paciente, codigo_hash, fake.first_name(), fake.last_name(), fake.last_name(), 
                    documento, fecha_nac, str(fake.unique.random_number(digits=12)), 
                    fake.phone_number(), fake.unique.free_email(), direccion_unica, 
                    fake.city(), provincia, random.choice([0, 1, 1, 1])
                ))

                # --- EVENTOS CLÍNICOS ---
                num_eventos = random.randint(2, 6)
                for _ in range(num_eventos):
                    fecha_evento = fake.date_between(start_date='-5y', end_date='today')
                    tipo_evento = random.choice(['Consulta_Primaria', 'Consulta_Especialista', 'Urgencias', 'Prueba_Diagnostica', 'Vacunacion'])
                    codigo_cie10 = f"{random.choice(['J', 'I', 'E', 'M', 'S', 'Z'])}{random.randint(10, 99)}" 
                    resolucion = random.choice(['Alta_Definitiva', 'Derivacion_Especialista', 'Seguimiento_Continuado', 'Pendiente_Resultado'])
                    
                    # Combinatoria para descripciones con total sentido médico
                    desc_cie10 = random.choice(descripciones_cie10)
                    desc_clinica = f"{random.choice(estado_general)} {random.choice(exploracion_fisica)}"
                    notas = f"{random.choice(alergias_y_notas)} {random.choice(alergias_y_notas)}" # Junta dos notas
                    centro = f"Centro de Salud {fake.city()}" if tipo_evento == 'Consulta_Primaria' else f"Hospital {fake.last_name()}"

                    sql_evento = """
                        INSERT INTO evento_clinico 
                        (id_paciente, fecha_evento, tipo_evento, codigo_cie10, descripcion_cie10, 
                         descripcion_clinica, especialidad, centro_sanitario, duracion_dias, resolucion, notas_adicionales) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_evento, (
                        id_paciente, fecha_evento, tipo_evento, codigo_cie10, desc_cie10, 
                        desc_clinica, fake.job(), centro, random.randint(1, 15), resolucion, notas
                    ))

                # --- HISTÓRICO DE BAJAS (15%) ---
                if random.random() < 0.15:
                    fecha_inicio_baja = fake.date_between(start_date='-3y', end_date='-1m')
                    dias_baja = random.randint(5, 45)
                    fecha_fin_baja = fecha_inicio_baja + timedelta(days=dias_baja)
                    
                    causa_combinada = f"{random.choice(causas_baja)} {random.choice(contexto_baja)}"
                    
                    sql_baja = """
                        INSERT INTO historico_bajas_medicas 
                        (codigo_hash_paciente, fecha_inicio_baja, fecha_fin_baja, dias_totales_baja, 
                         codigo_cie10_causa, descripcion_causa, tipo_contingencia, centro_emisor, numero_parte_baja) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_baja, (
                        codigo_hash, fecha_inicio_baja, fecha_fin_baja, dias_baja,
                        f"Z{random.randint(10,99)}", causa_combinada,
                        random.choice(['Enfermedad_Comun', 'Accidente_no_Laboral', 'Accidente_Laboral']),
                        f"Mutua {fake.company()}", f"PB-{fake.unique.random_number(digits=8)}"
                    ))

                # --- TRIAJE URGENCIAS (2%) ---
                if random.random() < 0.02:
                    motivo_combinado = f"{random.choice(motivos_urgencia)} de inicio reciente."
                    obs_triaje = random.choice(observaciones_triaje)

                    sql_triaje = """
                        INSERT INTO triaje_urgencias_actual 
                        (codigo_hash_paciente, fecha_hora_llegada, nivel_triaje_manchester, motivo_consulta, 
                         tension_arterial_sistolica, tension_arterial_diastolica, frecuencia_cardiaca, 
                         saturacion_oxigeno, temperatura_corporal, estado_actual, sala_box_asignado, tiempo_espera_estimado_min, observaciones_triaje) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_triaje, (
                        codigo_hash, datetime.now(), random.randint(1, 5), motivo_combinado,
                        random.randint(110, 160), random.randint(60, 100), random.randint(60, 120),
                        round(random.uniform(92.0, 99.9), 1), round(random.uniform(36.0, 39.5), 1),
                        'En_Espera', f"Box-{random.randint(1,20)}", random.randint(15, 120), obs_triaje
                    ))

                if (i + 1) % 100 == 0:
                    print(f"Progreso: {i + 1} pacientes generados...")

            connection.commit()
            print("¡Éxito! Base de datos poblada. Los textos son ahora 100% lógicos y realistas.")

    except connection.Error as err:
        print(f"Error en MySQL: {err}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == '__main__':
    generar_datos_longitudinales(1000)