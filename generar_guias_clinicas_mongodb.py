import json

guias_clinicas = [
    # ── RESPIRATORIO ──
    {
        "codigo_cie10": "J18.9",
        "enfermedad": "Neumonía no especificada",
        "especialidad_referencia": "Neumología",
        "protocolo_tratamiento": {
            "primera_linea": ["Amoxicilina-Clavulánico", "Azitromicina"],
            "criterios_ingreso": ["Saturación O2 < 92%", "Frecuencia respiratoria > 30 rpm"]
        },
        "fuente_externa": "Sociedad Española de Neumología (SEPAR) 2026"
    },
    {
        "codigo_cie10": "J45.9",
        "enfermedad": "Asma no especificada",
        "especialidad_referencia": "Alergología",
        "protocolo_tratamiento": {
            "primera_linea": ["Corticoides inhalados", "Salbutamol a demanda"],
            "criterios_ingreso": ["Crisis severa que no responde a broncodilatadores", "Uso de musculatura accesoria"]
        },
        "fuente_externa": "Global Initiative for Asthma (GINA) 2025"
    },

    # ── CARDIOVASCULAR ──
    {
        "codigo_cie10": "I10",
        "enfermedad": "Hipertensión esencial (primaria)",
        "especialidad_referencia": "Cardiología",
        "protocolo_tratamiento": {
            "primera_linea": ["IECA (Enalapril)", "ARA-II (Losartán)"],
            "modificaciones_estilo_vida": ["Dieta DASH", "Reducción de sodio < 2g/día"]
        },
        "fuente_externa": "Guía Europea de Cardiología (ESC) 2024"
    },
    {
        "codigo_cie10": "I20.9",
        "enfermedad": "Angina de pecho no especificada",
        "especialidad_referencia": "Cardiología",
        "protocolo_tratamiento": {
            "primera_linea": ["AAS 100mg", "Nitroglicerina sublingual", "Estatinas alta intensidad"],
            "criterios_ingreso": ["Dolor en reposo", "Cambios en el ECG", "Troponinas elevadas"]
        },
        "fuente_externa": "American Heart Association (AHA) 2025"
    },

    # ── ENDOCRINO ──
    {
        "codigo_cie10": "E11.9",
        "enfermedad": "Diabetes mellitus tipo 2 sin complicaciones",
        "especialidad_referencia": "Endocrinología",
        "protocolo_tratamiento": {
            "primera_linea": ["Metformina"],
            "segunda_linea": ["iSGLT2 (Empagliflozina)", "arGLP-1 (Semaglutida)"],
            "objetivos_control": ["HbA1c < 7.0%"]
        },
        "fuente_externa": "American Diabetes Association (ADA) 2026"
    },
    {
        "codigo_cie10": "E78.0",
        "enfermedad": "Hipercolesterolemia pura",
        "especialidad_referencia": "Medicina General",
        "protocolo_tratamiento": {
            "primera_linea": ["Atorvastatina", "Rosuvastatina"],
            "objetivos_control": ["LDL < 70 mg/dL en pacientes de muy alto riesgo"]
        },
        "fuente_externa": "Sociedad Española de Arteriosclerosis (SEA) 2024"
    },

    # ── SALUD MENTAL ──
    {
        "codigo_cie10": "F41.1",
        "enfermedad": "Trastorno de ansiedad generalizada",
        "especialidad_referencia": "Psiquiatría",
        "protocolo_tratamiento": {
            "primera_linea": ["ISRS (Escitalopram)", "Terapia Cognitivo-Conductual (TCC)"],
            "modificaciones_estilo_vida": ["Higiene del sueño", "Evitar excitantes y alcohol"]
        },
        "fuente_externa": "Guía Clínica del Sistema Nacional de Salud 2023"
    },

    # ── NEUROLÓGICO ──
    {
        "codigo_cie10": "G43.9",
        "enfermedad": "Migraña no especificada",
        "especialidad_referencia": "Neurología",
        "protocolo_tratamiento": {
            "primera_linea": ["Triptanes (Sumatriptán) al inicio del dolor", "AINEs"],
            "tratamiento_preventivo": ["Topiramato", "Amitriptilina si hay insomnio asociado"]
        },
        "fuente_externa": "Sociedad Española de Neurología (SEN) 2025"
    },

    # ── DIGESTIVO ──
    {
        "codigo_cie10": "K29.7",
        "enfermedad": "Gastritis no especificada",
        "especialidad_referencia": "Digestología",
        "protocolo_tratamiento": {
            "primera_linea": ["IBP (Omeprazol) durante 4 semanas", "Dieta blanda"],
            "criterios_prueba": ["Test de aliento para H. pylori si no hay mejoría"]
        },
        "fuente_externa": "Asociación Española de Gastroenterología (AEG) 2024"
    },
    {
        "codigo_cie10": "K57.3",
        "enfermedad": "Enfermedad diverticular del intestino grueso",
        "especialidad_referencia": "Cirugía General",
        "protocolo_tratamiento": {
            "primera_linea": ["Amoxicilina-Clavulánico o Ciprofloxacino + Metronidazol", "Dieta líquida"],
            "criterios_ingreso": ["Fiebre alta", "Defensa abdominal", "Intolerancia oral"]
        },
        "fuente_externa": "Guía de Práctica Clínica WSES 2025"
    },

    # ── TRAUMATOLOGÍA ──
    {
        "codigo_cie10": "S93.4",
        "enfermedad": "Esguince y distensión de ligamentos del tobillo",
        "especialidad_referencia": "Traumatología",
        "protocolo_tratamiento": {
            "primera_linea": ["Protocolo RICE", "AINEs sistémicos y tópicos"],
            "inmovilizacion": ["Vendaje funcional por 2 semanas", "Muletas con descarga parcial"]
        },
        "fuente_externa": "Sociedad Española de Cirugía Ortopédica (SECOT) 2023"
    },
    {
        "codigo_cie10": "M54.5",
        "enfermedad": "Lumbago no especificado",
        "especialidad_referencia": "Rehabilitación",
        "protocolo_tratamiento": {
            "primera_linea": ["Ibuprofeno + Ciclobenzaprina", "Calor local"],
            "recomendaciones": ["Evitar reposo en cama prolongado", "Higiene postural"]
        },
        "fuente_externa": "Organización Mundial de la Salud (OMS) 2024"
    }
]

with open('guias_externas_completas.json', 'w', encoding='utf-8') as f:
    json.dump(guias_clinicas, f, indent=4, ensure_ascii=False)

print("Archivo guias_externas_completas.json generado con éxito con 12 guías clínicas clave.")