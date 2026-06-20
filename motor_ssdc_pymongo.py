import pymongo
from datetime import datetime

def generar_informe_alertas_geriatricas():
    print("\n" + "="*70)
    print(" INICIANDO MOTOR DE INFERENCIA CLÍNICA (CDSS) - MONGODB")
    print(" Buscando pacientes geriátricos con criterios de ingreso...")
    print("="*70 + "\n")

    try:
        # 1. Conexión a MongoDB 
        client = pymongo.MongoClient('mongodb+srv://antoniodoa9:root@cluster0.wcpugac.mongodb.net/')
        db = client['PROYECTO']
        coleccion_pacientes = db['pacientes_externos']

        pipeline = [
           
            {'$match': {'anio_nacimiento': {'$lte': 1956}}},

            {'$lookup': {
                'from': 'guias_clinicas',
                'localField': 'diagnostico_principal',
                'foreignField': 'codigo_cie10',
                'as': 'guia_aplicada'
            }},
            
            {'$unwind': '$guia_aplicada'},
            
            {'$match': {
                'guia_aplicada.protocolo_tratamiento.criterios_ingreso': {'$exists': True}
            }},
            
            {'$project': {
                '_id': 0,
                'id_paciente': 1,
                'edad_estimada': {'$subtract': [2026, '$anio_nacimiento']},
                'diagnostico': '$descripcion_patologia',
                'especialidad': '$guia_aplicada.especialidad_referencia',
                'criterios_ingreso': '$guia_aplicada.protocolo_tratamiento.criterios_ingreso'
            }},
            
            {'$sort': {'edad_estimada': -1}},
            
        ]

        # 3. Ejecutar el pipeline en el motor NoSQL
        resultados = list(coleccion_pacientes.aggregate(pipeline))

        # 4. Formatear y mostrar el informe 
        if not resultados:
            print(" No se han detectado alertas activas en el sistema.")
            return

        print(f" [!] Se han generado {len(resultados)} alertas:\n")
        
        for idx, alerta in enumerate(resultados, 1):
            print(f" ⚠️  ALERTA #{idx:02d} | Especialidad: {alerta['especialidad']}")
            print(f"    Paciente hash : {alerta['id_paciente'][:15]}...")
            print(f"    Edad estimada : {alerta['edad_estimada']} años")
            print(f"    Diagnóstico   : {alerta['diagnostico']}")
            print(f"    CRITERIOS DE INGRESO A VIGILAR:")
            for criterio in alerta['criterios_ingreso']:
                print(f"      - {criterio}")
            print("-" * 70)

    except Exception as e:
        print(f" [ERROR] Fallo en la conexión o ejecución: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    generar_informe_alertas_geriatricas()