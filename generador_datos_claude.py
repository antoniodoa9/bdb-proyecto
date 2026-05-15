"""
generador_datos.py
==================
Poblador de ChronoHealthDB con datos clínicos 100 % coherentes.

Instala dependencias si hace falta:
    pip install pymysql faker

Uso:
    python generador_datos.py
"""

import hashlib
import random
from datetime import datetime, timedelta

import pymysql.cursors
from faker import Faker

fake = Faker("es_ES")
#Faker.seed(0)
#random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
#  CONEXIÓN  (ajusta usuario/contraseña si es necesario)
# ─────────────────────────────────────────────────────────────────────────────
DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="root",
    db="PROYECTO",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

# ─────────────────────────────────────────────────────────────────────────────
#  CATÁLOGO DE ESCENARIOS CLÍNICOS
#
#  Cada escenario agrupa todos los campos relacionados para que el INSERT
#  en evento_clinico, historico_bajas_medicas y triaje_urgencias_actual
#  sea internamente consistente (código CIE-10 ↔ descripción ↔ especialidad
#  ↔ tipo de evento ↔ constantes vitales ↔ duración de baja…).
# ─────────────────────────────────────────────────────────────────────────────

ESCENARIOS = [

    # ── RESPIRATORIO ──────────────────────────────────────────────────────────
    {
        "cie10": "J06.9",
        "descripcion": "Infección aguda de las vías respiratorias superiores",
        "especialidades": ["Medicina General", "Pediatría"],
        "tipos_evento": ["Consulta_Primaria"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado"],
        "duracion": (3, 8),
        "edad_rango": (1, 85),
        "plantillas_clinica": [
            "Paciente que consulta por cuadro catarral de {dias} días de evolución con "
            "rinorrea serosa, odinofagia y tos seca. Afebril. Faringe hiperémica sin "
            "exudados. Auscultación pulmonar con buena entrada de aire bilateral.",
            "Refiere congestión nasal y malestar general desde hace {dias} días. "
            "Temperatura {temp}°C. Sin signos de complicación. Oídos sin hallazgos.",
        ],
        "plantillas_notas": [
            "Tratamiento sintomático: ibuprofeno y solución salina nasal. "
            "Hidratación adecuada y reposo relativo. Revisión si fiebre o empeoramiento en 72 h.",
            "Se indica paracetamol según necesidad. Evitar ambientes secos. "
            "Consultar si aparece disnea o fiebre alta.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    {
        "cie10": "J18.9",
        "descripcion": "Neumonía no especificada",
        "especialidades": ["Neumología", "Medicina Interna", "Urgencias"],
        "tipos_evento": ["Urgencias", "Hospitalizacion", "Consulta_Especialista"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado", "Derivacion_Especialista"],
        "duracion": (7, 21),
        "edad_rango": (20, 95),
        "plantillas_clinica": [
            "Fiebre de hasta {temp}°C de {dias} días de evolución, tos productiva con "
            "expectoración purulenta y disnea de esfuerzo. SatO2 {sat}% basal. "
            "Crepitantes en base {lado}. Rx de tórax: condensación {lado}.",
            "Cuadro febril con tos y expectoración amarillenta. Analítica con leucocitosis "
            "{leucos} x10³/µL con desviación izquierda. PCR elevada. Se instaura "
            "antibioterapia empírica. Rx compatible con infiltrado {lado}.",
        ],
        "plantillas_notas": [
            "Antibioterapia con amoxicilina-clavulánico + azitromicina. Antipirético. "
            "Control radiológico y analítico en 7 días. Baja médica pautada.",
            "Ingreso para antibioterapia IV y monitorización. Oxigenoterapia si SatO2 < 92%. "
            "Alta al mejorar saturación y tolerar vía oral.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (10, 25),
        "es_urgencia": True,
        "nivel_triaje": (2, 3),
        "constantes": {"tas": (100, 140), "tad": (60, 85), "fc": (90, 115), "sat": (86, 94), "temp": (38.2, 40.0)},
    },

    {
        "cie10": "J45.9",
        "descripcion": "Asma no especificada",
        "especialidades": ["Neumología", "Alergología", "Medicina General"],
        "tipos_evento": ["Urgencias", "Consulta_Primaria", "Consulta_Especialista"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado", "Derivacion_Especialista"],
        "duracion": (1, 5),
        "edad_rango": (5, 70),
        "plantillas_clinica": [
            "Paciente asmático conocido con crisis de disnea y sibilancias de inicio "
            "en las últimas {horas} h. SatO2 {sat}%. Auscultación con sibilancias "
            "espiratorias difusas bilaterales. Sin uso de musculatura accesoria.",
            "Crisis asmática de intensidad {intensidad}. Refiere haber usado el inhalador "
            "de rescate sin mejoría completa. FR {fr} rpm. Buena entrada de aire bilateral "
            "con roncus y sibilancias dispersas.",
        ],
        "plantillas_notas": [
            "Salbutamol nebulizado con mejoría progresiva. Se refuerza técnica inhalatoria "
            "y plan de acción escrito. Control en consulta en 48-72 h.",
            "Se ajusta pauta de corticoide inhalado. Derivación a Neumología para "
            "espirometría y valoración de tratamiento de mantenimiento.",
        ],
        "baja_contingencia": None,
        "es_urgencia": True,
        "nivel_triaje": (2, 3),
        "constantes": {"tas": (105, 140), "tad": (60, 90), "fc": (90, 120), "sat": (88, 95), "temp": (36.4, 37.6)},
    },

    {
        "cie10": "J44.1",
        "descripcion": "Enfermedad pulmonar obstructiva crónica con exacerbación aguda",
        "especialidades": ["Neumología", "Medicina Interna"],
        "tipos_evento": ["Urgencias", "Hospitalizacion", "Consulta_Especialista"],
        "resoluciones": ["Alta_Definitiva", "Derivacion_Especialista", "Seguimiento_Continuado"],
        "duracion": (7, 14),
        "edad_rango": (50, 95),
        "plantillas_clinica": [
            "Paciente con EPOC estadio {gold} que acude por empeoramiento de disnea habitual, "
            "aumento de expectoración y cambio de coloración a purulenta en los últimos {dias} días. "
            "SatO2 {sat}% basal. Auscultación con hipofonesis generalizada y sibilancias espiratorias.",
            "Exacerbación de EPOC con disnea de reposo y taquipnea (FR {fr} rpm). "
            "Gasometría: pO2 {po2} mmHg, pCO2 {pco2} mmHg. Se inicia O2 controlado y broncodilatadores.",
        ],
        "plantillas_notas": [
            "Broncodilatadores de larga acción, corticoide sistémico y antibiótico. "
            "Oxigenoterapia domiciliaria si SatO2 basal < 88%. Derivado a Neumología.",
            "Alta con ajuste de inhaladores. Plan escrito de agudización. Revisión en 4 semanas.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (10, 30),
        "es_urgencia": True,
        "nivel_triaje": (2, 3),
        "constantes": {"tas": (110, 150), "tad": (65, 90), "fc": (85, 115), "sat": (82, 92), "temp": (37.0, 39.0)},
    },

    # ── CARDIOVASCULAR ────────────────────────────────────────────────────────
    {
        "cie10": "I10",
        "descripcion": "Hipertensión esencial (primaria)",
        "especialidades": ["Medicina General", "Cardiología", "Medicina Interna"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista", "Urgencias"],
        "resoluciones": ["Seguimiento_Continuado", "Alta_Definitiva", "Derivacion_Especialista"],
        "duracion": (1, 3),
        "edad_rango": (35, 95),
        "plantillas_clinica": [
            "Paciente hipertenso en seguimiento con cifras tensionales de {tas}/{tad} mmHg. "
            "Refiere cumplimiento irregular de la medicación. Asintomático. "
            "Sin datos de repercusión orgánica aguda. FC {fc} lpm, ritmo sinusal.",
            "Acude por cefalea occipital y cifras de TA de {tas}/{tad} mmHg. "
            "Sin signos de encefalopatía hipertensiva. Fondo de ojo sin papiledema. "
            "Analítica sin alteraciones de función renal.",
        ],
        "plantillas_notas": [
            "Se ajusta pauta de antihipertensivo. Dieta hiposódica, actividad física aeróbica "
            "30 min/día y pérdida de peso si sobrepeso. Control en 4 semanas.",
            "Automedición domiciliaria de TA. Objetivo < 130/80 mmHg. Se añade IECA/ARA-II.",
        ],
        "baja_contingencia": None,
        "es_urgencia": True,
        "nivel_triaje": (2, 3),
        "constantes": {"tas": (155, 200), "tad": (90, 120), "fc": (65, 95), "sat": (95, 99), "temp": (36.0, 37.2)},
    },

    {
        "cie10": "I20.9",
        "descripcion": "Angina de pecho no especificada",
        "especialidades": ["Cardiología", "Medicina Interna"],
        "tipos_evento": ["Urgencias", "Hospitalizacion", "Consulta_Especialista"],
        "resoluciones": ["Derivacion_Especialista", "Seguimiento_Continuado", "Alta_Definitiva"],
        "duracion": (1, 5),
        "edad_rango": (45, 95),
        "plantillas_clinica": [
            "Episodio de dolor torácico opresivo irradiado a brazo izquierdo de {mins} minutos "
            "de duración. Cedido espontáneamente antes de la llegada. ECG: sin alteraciones "
            "agudas de la repolarización. Troponina I: {troponina} ng/mL.",
            "Dolor centrotorácico de características isquémicas que cede con nitroglicerina SL. "
            "FRCV: HTA, DL, fumador activo. ECG con cambios inespecíficos en ST. "
            "Se solicita ergometría y ecocardiograma.",
        ],
        "plantillas_notas": [
            "AAS 100 mg + bisoprolol + atorvastatina. Derivación preferente a Cardiología "
            "para estudio de isquemia miocárdica. Evitar esfuerzos.",
            "Se cursa ingreso para monitorización continua, enzimas seriadas y cateterismo "
            "si confirma SCASEST.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (5, 21),
        "es_urgencia": True,
        "nivel_triaje": (1, 2),
        "constantes": {"tas": (130, 180), "tad": (80, 105), "fc": (78, 110), "sat": (93, 98), "temp": (36.0, 37.5)},
    },

    {
        "cie10": "I48.9",
        "descripcion": "Fibrilación auricular no especificada",
        "especialidades": ["Cardiología", "Medicina Interna"],
        "tipos_evento": ["Urgencias", "Consulta_Especialista"],
        "resoluciones": ["Seguimiento_Continuado", "Derivacion_Especialista", "Alta_Definitiva"],
        "duracion": (1, 4),
        "edad_rango": (50, 95),
        "plantillas_clinica": [
            "Paciente que refiere palpitaciones y latido irregular de inicio brusco "
            "hace {horas} horas. Hemodinámicamente estable. ECG: FA con respuesta "
            "ventricular media {fc} lpm. Sin signos de insuficiencia cardíaca.",
            "Episodio de FA paroxística. PA {tas}/{tad} mmHg. Bien tolerada. "
            "Ecocardiograma previo sin valvulopatía significativa. CHA₂DS₂-VASc {score} puntos.",
        ],
        "plantillas_notas": [
            "Control de frecuencia con bisoprolol. Anticoagulación con ACOD. "
            "Derivación a Cardiología para valoración de cardioversión electiva.",
            "Cardioversión farmacológica con flecainida IV con reversión a sinusal. "
            "Alta con anticoagulante oral y betabloqueante. Control en 2 semanas.",
        ],
        "baja_contingencia": None,
        "es_urgencia": True,
        "nivel_triaje": (2, 3),
        "constantes": {"tas": (110, 155), "tad": (65, 95), "fc": (100, 145), "sat": (94, 98), "temp": (36.0, 37.2)},
    },

    {
        "cie10": "I50.9",
        "descripcion": "Insuficiencia cardíaca no especificada",
        "especialidades": ["Cardiología", "Medicina Interna"],
        "tipos_evento": ["Urgencias", "Hospitalizacion", "Consulta_Especialista"],
        "resoluciones": ["Seguimiento_Continuado", "Derivacion_Especialista", "Alta_Definitiva"],
        "duracion": (5, 15),
        "edad_rango": (55, 95),
        "plantillas_clinica": [
            "Paciente con IC conocida que acude por aumento de disnea de esfuerzo y ortopnea. "
            "Edemas maleolares con fóvea ++. Crepitantes bibasales. SatO2 {sat}% con O2 "
            "a {litros} l/min. NT-proBNP {bnp} pg/mL.",
            "Descompensación de IC con fracción de eyección reducida ({fe}%). "
            "Ingurgitación yugular. Rx: redistribución vascular y líneas B de Kerley. "
            "Se inicia diurético IV.",
        ],
        "plantillas_notas": [
            "Furosemida IV + optimización de tratamiento crónico. Restricción hídrica "
            "1.5 l/día. Dieta hiposódica. Control de peso diario.",
            "Alta con ajuste de diuréticos orales y seguimiento estrecho en consulta de IC.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (10, 30),
        "es_urgencia": True,
        "nivel_triaje": (2, 3),
        "constantes": {"tas": (100, 145), "tad": (60, 90), "fc": (85, 120), "sat": (86, 93), "temp": (36.0, 37.5)},
    },

    # ── DIGESTIVO ─────────────────────────────────────────────────────────────
    {
        "cie10": "K29.7",
        "descripcion": "Gastritis no especificada",
        "especialidades": ["Medicina General", "Digestología"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado"],
        "duracion": (5, 21),
        "edad_rango": (18, 85),
        "plantillas_clinica": [
            "Epigastralgia urente de {semanas} semanas de evolución que empeora en ayunas "
            "y mejora con ingesta. Náuseas ocasionales. Abdomen blando, doloroso en "
            "epigastrio a la palpación. Sin signos de peritonismo.",
            "Dolor epigástrico crónico. Refiere toma frecuente de AINEs por artralgias previas. "
            "Test rápido de ureasa positivo para Helicobacter pylori.",
        ],
        "plantillas_notas": [
            "Omeprazol 20 mg/día en ayunas durante 4 semanas. Evitar AINEs, tabaco y alcohol. "
            "Dieta blanda. Revisión si no mejoría.",
            "Triple terapia erradicadora de H. pylori (OCA-7). Control de erradicación "
            "con test de aliento en 4 semanas tras finalizar tratamiento.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    {
        "cie10": "A09",
        "descripcion": "Gastroenteritis y colitis de origen infeccioso no especificado",
        "especialidades": ["Medicina General", "Urgencias"],
        "tipos_evento": ["Consulta_Primaria", "Urgencias"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado"],
        "duracion": (3, 7),
        "edad_rango": (1, 85),
        "plantillas_clinica": [
            "Cuadro de diarrea acuosa ({deposiciones} deposiciones/día sin sangre ni moco), "
            "vómitos y febrícula de {temp}°C de {dias} días de evolución. Abdomen blando "
            "y ligeramente doloroso de forma difusa. Signos de deshidratación leve.",
            "Gastroenteritis aguda con intolerancia oral. Mucosa oral semiseca. "
            "Sin alteraciones hidroelectrolíticas relevantes en analítica. "
            "Coprocultivo en curso.",
        ],
        "plantillas_notas": [
            "Sueroterapia oral/IV según tolerancia. Dieta astringente progresiva. "
            "Antieméticos. Sin indicación de antibioterapia. Revisión si fiebre alta o rectorragia.",
            "Rehidratación oral con soluciones isotónicas. Loperamida si diarrea muy frecuente "
            "sin fiebre. Lavado de manos frecuente.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (3, 7),
        "es_urgencia": False,
    },

    {
        "cie10": "K57.3",
        "descripcion": "Enfermedad diverticular del intestino grueso sin perforación ni absceso",
        "especialidades": ["Digestología", "Cirugía General", "Medicina General"],
        "tipos_evento": ["Urgencias", "Consulta_Especialista", "Consulta_Primaria"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado", "Derivacion_Especialista"],
        "duracion": (5, 14),
        "edad_rango": (45, 95),
        "plantillas_clinica": [
            "Paciente con diverticulosis conocida que acude por dolor en fosa ilíaca "
            "izquierda de {dias} días de evolución, con fiebre de {temp}°C y cambio en el "
            "ritmo intestinal. Abdomen con defensa localizada en FII. PCR {pcr} mg/L.",
            "Diverticulitis aguda no complicada confirmada por TC abdominal con contraste. "
            "Afebril tras inicio de antibioterapia. Tolerancia oral correcta.",
        ],
        "plantillas_notas": [
            "Antibioterapia oral (amoxicilina-clavulánico o ciprofloxacino + metronidazol) "
            "durante 7 días. Dieta líquida progresiva. Control en 6 semanas con colonoscopia.",
            "Ingreso para antibioterapia IV si fiebre alta o signos de complicación. "
            "Cirugía si perforación o absceso no drenables.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (7, 14),
        "es_urgencia": True,
        "nivel_triaje": (3, 4),
        "constantes": {"tas": (110, 145), "tad": (65, 90), "fc": (80, 110), "sat": (95, 99), "temp": (37.5, 39.2)},
    },

    # ── MUSCULOESQUELÉTICO ────────────────────────────────────────────────────
    {
        "cie10": "M54.5",
        "descripcion": "Lumbago no especificado",
        "especialidades": ["Medicina General", "Traumatología", "Rehabilitación"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista"],
        "resoluciones": ["Alta_Definitiva", "Derivacion_Especialista", "Seguimiento_Continuado"],
        "duracion": (7, 30),
        "edad_rango": (18, 90),
        "plantillas_clinica": [
            "Lumbalgia mecánica de {dias} días de evolución sin irradiación a miembros "
            "inferiores. Contractura paravertebral bilateral. Lasègue negativo bilateral. "
            "Sin signos neurológicos de alarma. Empeora con movimiento y mejora con reposo.",
            "Dolor lumbar agudo tras esfuerzo postural. No irradia. Palpación dolorosa en "
            "musculatura paravertebral L4-L5. Movilidad reducida por dolor. "
            "Rx lumbar sin hallazgos agudos.",
        ],
        "plantillas_notas": [
            "Ibuprofeno 600 mg/8h con protección gástrica + ciclobenzaprina nocturna. "
            "Calor local. Reposo relativo 48 h. Ejercicio de higiene postural.",
            "Derivado a Rehabilitación para fisioterapia. Evitar reposo prolongado. "
            "Corrección de posturas forzadas y cargas pesadas en el trabajo.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (7, 21),
        "es_urgencia": False,
    },

    {
        "cie10": "S93.4",
        "descripcion": "Esguince y distensión de ligamentos del tobillo",
        "especialidades": ["Traumatología", "Urgencias", "Medicina General"],
        "tipos_evento": ["Urgencias", "Consulta_Primaria"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado"],
        "duracion": (7, 21),
        "edad_rango": (10, 75),
        "plantillas_clinica": [
            "Mecanismo de inversión forzada de tobillo {lado} durante actividad física. "
            "Dolor, edema e impotencia funcional. Equimosis perilesional. "
            "Rx sin lesión ósea (regla de Ottawa negativa). Grado {grado}.",
            "Esguince de ligamento lateral externo grado {grado}. Maniobra del cajón anterior "
            "{cajón}. Punto de máximo dolor sobre el ligamento peroneoastragalino anterior. "
            "Sin crepitación.",
        ],
        "plantillas_notas": [
            "Protocolo RICE (reposo, hielo 20'/4 h, compresión, elevación). Vendaje funcional "
            "2 semanas. Ibuprofeno tópico. Fisioterapia propioceptiva desde fase subaguda.",
            "Muletas descarga parcial 5 días. Ejercicios de movilidad activa sin dolor "
            "desde el primer día. Alta deportiva en {semanas} semanas según evolución.",
        ],
        "baja_contingencia": "Accidente_no_Laboral",
        "dias_baja": (7, 21),
        "es_urgencia": False,
    },

    {
        "cie10": "M16.9",
        "descripcion": "Coxartrosis no especificada",
        "especialidades": ["Traumatología", "Reumatología"],
        "tipos_evento": ["Consulta_Especialista"],
        "resoluciones": ["Seguimiento_Continuado", "Derivacion_Especialista"],
        "duracion": (1, 2),
        "edad_rango": (55, 95),
        "plantillas_clinica": [
            "Coxalgia de meses de evolución con empeoramiento progresivo. Dolor mecánico "
            "que limita la deambulación. Marcha antiálgica. Rx: pinzamiento articular "
            "y osteofitos marginales en cadera {lado}. Sin afectación contralateral significativa.",
            "Artrosis de cadera avanzada (Kellgren-Lawrence {grado}). Rigidez matutina "
            "inferior a 30 min. Crepitación a la movilización. Dolor nocturno en últimas semanas.",
        ],
        "plantillas_notas": [
            "Paracetamol + AINE tópico. Valoración de infiltración intraarticular "
            "con ácido hialurónico. Derivado a Traumatología para valoración de prótesis.",
            "Pérdida de peso y fisioterapia para mejorar musculatura periarticular. "
            "Valorar prótesis total de cadera si fracaso del tratamiento conservador.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    {
        "cie10": "M79.3",
        "descripcion": "Fibromialgia",
        "especialidades": ["Reumatología", "Medicina General", "Psiquiatría"],
        "tipos_evento": ["Consulta_Especialista", "Consulta_Primaria"],
        "resoluciones": ["Seguimiento_Continuado"],
        "duracion": (1, 3),
        "edad_rango": (25, 70),
        "plantillas_clinica": [
            "Paciente con dolor musculoesquelético crónico y difuso de meses de evolución, "
            "fatiga crónica y alteración del sueño. Criterios ACR 2010 positivos. "
            "EVA dolor {eva}/10. Exploración sin artritis activa. Analítica sin autoanticuerpos.",
            "Síndrome fibromiálgico en seguimiento. Refiere empeoramiento con el estrés y el frío. "
            "Impacto funcional {impacto}. Sin nuevas manifestaciones sistémicas.",
        ],
        "plantillas_notas": [
            "Duloxetina + pregabalina a dosis bajas progresivas. Programa de ejercicio aeróbico "
            "supervisado. Psicoterapia cognitivo-conductual. Higiene del sueño.",
            "Se refuerza la importancia del ejercicio físico adaptado. Revisión en 3 meses.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (14, 45),
        "es_urgencia": False,
    },

    # ── ENDOCRINOLÓGICO ───────────────────────────────────────────────────────
    {
        "cie10": "E11.9",
        "descripcion": "Diabetes mellitus tipo 2 sin complicaciones",
        "especialidades": ["Medicina General", "Endocrinología"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista"],
        "resoluciones": ["Seguimiento_Continuado"],
        "duracion": (1, 2),
        "edad_rango": (35, 95),
        "plantillas_clinica": [
            "Control metabólico de DM2. HbA1c {hba1c}%. Glucemia basal {glucemia} mg/dL. "
            "Cumplimiento terapéutico irregular. Sin hipoglucemias en el último mes. "
            "Examen de pie sin lesiones activas.",
            "Paciente diabético tipo 2 en seguimiento. Objetivos de TA y colesterol en rango. "
            "Microalbuminuria {microalb} mg/g creatinina. Fondo de ojo anual normal.",
        ],
        "plantillas_notas": [
            "Ajuste de metformina. Se añade iSGLT-2 por beneficio cardiorrenal. "
            "Dieta hipocalórica e índice glucémico bajo. Automonitorización glucémica.",
            "Se refuerzan medidas higiénico-dietéticas. HbA1c objetivo < 7%. Analítica en 3 meses.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    {
        "cie10": "E03.9",
        "descripcion": "Hipotiroidismo no especificado",
        "especialidades": ["Medicina General", "Endocrinología"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista"],
        "resoluciones": ["Seguimiento_Continuado", "Alta_Definitiva"],
        "duracion": (1, 2),
        "edad_rango": (25, 85),
        "plantillas_clinica": [
            "Hipotiroidismo en tratamiento sustitutivo. Refiere astenia y sensación de frío. "
            "TSH {tsh} mU/L. T4 libre en rango. Se ajusta dosis de levotiroxina.",
            "Control de función tiroidea. Paciente eutiroidea clínicamente. "
            "Analítica reciente: TSH {tsh} mU/L, T4L 1.1 ng/dL. Sin síntomas actuales.",
        ],
        "plantillas_notas": [
            "Levotiroxina sódica {dosis} µg en ayunas 30 min antes del desayuno. "
            "No tomar con hierro ni calcio. Control analítico en 6 semanas.",
            "Función tiroidea en objetivo. Control analítico anual.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    {
        "cie10": "E78.0",
        "descripcion": "Hipercolesterolemia pura",
        "especialidades": ["Medicina General", "Cardiología"],
        "tipos_evento": ["Consulta_Primaria"],
        "resoluciones": ["Seguimiento_Continuado", "Alta_Definitiva"],
        "duracion": (1, 1),
        "edad_rango": (30, 90),
        "plantillas_clinica": [
            "Dislipemia en seguimiento. Colesterol total {ct} mg/dL, LDL {ldl} mg/dL, "
            "HDL {hdl} mg/dL, TG {tg} mg/dL. Riesgo cardiovascular {riesgo}. "
            "Sin xantomas ni xantelasmas.",
            "Control lipídico con estatina. LDL {ldl} mg/dL. Objetivo LDL < {objetivo} mg/dL "
            "según riesgo cardiovascular {riesgo}. Adherencia referida como buena.",
        ],
        "plantillas_notas": [
            "Se mantiene dosis de atorvastatina {dosis} mg. Dieta mediterránea. "
            "Reducir grasas saturadas y alcohol. Control analítico en 6 meses.",
            "Objetivo LDL alcanzado. Control anual con perfil lipídico.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    # ── SALUD MENTAL ──────────────────────────────────────────────────────────
    {
        "cie10": "F41.1",
        "descripcion": "Trastorno de ansiedad generalizada",
        "especialidades": ["Medicina General", "Psiquiatría", "Psicología Clínica"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista", "Urgencias"],
        "resoluciones": ["Seguimiento_Continuado", "Derivacion_Especialista", "Alta_Definitiva"],
        "duracion": (1, 3),
        "edad_rango": (18, 75),
        "plantillas_clinica": [
            "Paciente con nerviosismo persistente, preocupación excesiva e insomnio de "
            "conciliación de meses de evolución. Palpitaciones y tensión muscular. "
            "Sin ideación autolítica. Escala Hamilton-Ansiedad: {hamilton} puntos.",
            "TAG con síntomas somáticos predominantes. Refiere situación de estrés laboral "
            "como desencadenante. Sin antecedentes psiquiátricos previos. PHQ-4 positivo.",
        ],
        "plantillas_notas": [
            "Se inicia escitalopram 10 mg/día con titulación progresiva. Derivación a "
            "Psicología Clínica para TCC. Se explica el perfil de latencia del ISRS.",
            "Técnicas de relajación y mindfulness. Higiene del sueño. Evitar cafeína "
            "y alcohol. Revisión en 3 semanas.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (14, 60),
        "es_urgencia": True,
        "nivel_triaje": (3, 4),
        "constantes": {"tas": (115, 155), "tad": (70, 95), "fc": (88, 120), "sat": (96, 99), "temp": (36.0, 37.5)},
    },

    {
        "cie10": "F32.9",
        "descripcion": "Episodio depresivo no especificado",
        "especialidades": ["Medicina General", "Psiquiatría", "Psicología Clínica"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista"],
        "resoluciones": ["Seguimiento_Continuado", "Derivacion_Especialista"],
        "duracion": (1, 3),
        "edad_rango": (18, 85),
        "plantillas_clinica": [
            "Estado de ánimo deprimido, anhedonia y anergia de {semanas} semanas de "
            "evolución. Insomnio con despertar precoz. PHQ-9: {phq9} puntos. "
            "Sin ideación autolítica activa. Funcionalidad laboral afectada.",
            "Episodio depresivo de intensidad {intensidad}. Sin síntomas psicóticos. "
            "Antecedentes de episodio previo hace {anios} años, tratado con buena respuesta.",
        ],
        "plantillas_notas": [
            "Sertralina 50 mg/día. Derivado a Psicología para psicoterapia de apoyo. "
            "Control en 4 semanas. Se pacta plan de seguridad.",
            "Se mantiene antidepresivo. Mejoría parcial. Se valora aumento de dosis a 100 mg.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (14, 90),
        "es_urgencia": False,
    },

    # ── NEUROLÓGICO ───────────────────────────────────────────────────────────
    {
        "cie10": "G43.9",
        "descripcion": "Migraña no especificada",
        "especialidades": ["Neurología", "Medicina General"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista", "Urgencias"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado", "Derivacion_Especialista"],
        "duracion": (1, 3),
        "edad_rango": (15, 65),
        "plantillas_clinica": [
            "Crisis de cefalea hemicraneal pulsátil de {horas} h de evolución, con náuseas "
            "y fotofobia. Exploración neurológica sin focalidad. Analgesia previa sin "
            "respuesta satisfactoria. Antecedentes migrañosos desde la adolescencia.",
            "Crisis migrañosa con aura visual (escotoma centelleante de {min} min) "
            "seguida de cefalea intensa. {frecuencia} crisis/mes de media. "
            "MIDAS: {midas} puntos.",
        ],
        "plantillas_notas": [
            "Sumatriptán 50 mg con buena respuesta. Se refuerza pauta de rescate. "
            "Evitar analgesia frecuente (>10 días/mes) para prevenir cefalea por abuso.",
            "Se inicia tratamiento preventivo con topiramato titulando progresivamente. "
            "Diario de cefalea para seguimiento. Control en 3 meses.",
        ],
        "baja_contingencia": None,
        "es_urgencia": True,
        "nivel_triaje": (3, 4),
        "constantes": {"tas": (110, 140), "tad": (65, 88), "fc": (65, 92), "sat": (97, 99), "temp": (36.0, 37.5)},
    },

    {
        "cie10": "G40.9",
        "descripcion": "Epilepsia no especificada",
        "especialidades": ["Neurología"],
        "tipos_evento": ["Urgencias", "Consulta_Especialista"],
        "resoluciones": ["Seguimiento_Continuado", "Derivacion_Especialista"],
        "duracion": (1, 3),
        "edad_rango": (5, 70),
        "plantillas_clinica": [
            "Paciente traído por familiar tras crisis convulsiva generalizada tonicoclónica "
            "de {min} minutos de duración con período poscrítico. Sin fiebre. "
            "Exploración neurológica normal. Sin traumatismos.",
            "Epilepsia conocida con crisis de escape por incumplimiento terapéutico. "
            "Valproato en nivel subterapéutico. Sin crisis en los últimos {meses} meses con buen cumplimiento.",
        ],
        "plantillas_notas": [
            "Analítica urgente, glucemia y niveles de anticomicial. TC craneal sin contraste: "
            "sin lesiones agudas. Alta con ajuste de dosis de valproato.",
            "Se refuerza importancia de cumplimiento terapéutico. Restricción de conducción "
            "según normativa vigente. Control en Neurología en 4 semanas.",
        ],
        "baja_contingencia": "Enfermedad_Comun",
        "dias_baja": (7, 21),
        "es_urgencia": True,
        "nivel_triaje": (2, 3),
        "constantes": {"tas": (110, 145), "tad": (65, 90), "fc": (80, 110), "sat": (95, 99), "temp": (36.0, 37.8)},
    },

    # ── UROLÓGICO ─────────────────────────────────────────────────────────────
    {
        "cie10": "N30.0",
        "descripcion": "Cistitis aguda",
        "especialidades": ["Medicina General", "Urología"],
        "tipos_evento": ["Consulta_Primaria"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado"],
        "duracion": (5, 10),
        "edad_rango": (15, 85),
        "plantillas_clinica": [
            "Disuria, polaquiuria y urgencia miccional de {dias} días. Sin fiebre ni "
            "dolor lumbar. Tira reactiva: nitritos positivos, leucocituria ++. "
            "Sin antecedentes de ITU de repetición.",
            "ITU baja no complicada. {episodios} episodio(s) en el último año. "
            "Sin alergias antimicrobianas conocidas. Urocultivo en curso.",
        ],
        "plantillas_notas": [
            "Fosfomicina trometamol 3 g monodosis. Abundante ingesta hídrica. "
            "Urocultivo de control si persisten síntomas.",
            "Nitrofurantoína 100 mg/12 h durante 5 días. Control si ITU de repetición "
            "para estudio y profilaxis.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    {
        "cie10": "N40",
        "descripcion": "Hiperplasia de la próstata",
        "especialidades": ["Urología", "Medicina General"],
        "tipos_evento": ["Consulta_Especialista", "Consulta_Primaria"],
        "resoluciones": ["Seguimiento_Continuado", "Derivacion_Especialista"],
        "duracion": (1, 2),
        "edad_rango": (50, 95),
        "plantillas_clinica": [
            "STUI obstructivos de meses de evolución: chorro débil, prolongado, "
            "con goteo postmiccional y nicturia x{nicturia}. Volumen prostático {vol} cc "
            "en ecografía. PSA {psa} ng/mL. IPSS {ipss} puntos.",
            "HPB en seguimiento. Flujometría: Qmáx {qmax} mL/s, residuo postmiccional {rpm} mL. "
            "Sin hematuria ni infección sobreañadida.",
        ],
        "plantillas_notas": [
            "Alfuzosina 10 mg/día. Restricción de líquidos vespertinos y cafeína. "
            "Control con flujometría y ecografía en 3 meses.",
            "Se añade dutasterida por volumen prostático > 40 cc. Derivado a Urología "
            "para valoración de resección transuretral.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    # ── DERMATOLÓGICO ─────────────────────────────────────────────────────────
    {
        "cie10": "L20.9",
        "descripcion": "Dermatitis atópica no especificada",
        "especialidades": ["Dermatología", "Alergología", "Medicina General"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista"],
        "resoluciones": ["Seguimiento_Continuado", "Alta_Definitiva"],
        "duracion": (7, 30),
        "edad_rango": (1, 60),
        "plantillas_clinica": [
            "Brote de dermatitis atópica con eritema, vesiculación y prurito intenso en "
            "pliegues antecubitales y poplíteos. Xerosis generalizada. Puntuación SCORAD: {scorad}. "
            "Antecedentes de asma alérgica y rinoconjuntivitis.",
            "Eccema atópico moderado-grave con lesiones liquenificadas y costrosas. "
            "Alteración del sueño por prurito nocturno. IgE total {ige} UI/mL.",
        ],
        "plantillas_notas": [
            "Corticoide tópico de potencia {potencia} en zonas activas 2 semanas. "
            "Emoliente enriquecido varias veces al día. Antihistamínico oral nocturno.",
            "Derivado a Dermatología para valoración de dupilumab (anti-IL-4Rα). "
            "Evitar factores desencadenantes: sudoración, tejidos sintéticos.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    {
        "cie10": "L40.0",
        "descripcion": "Psoriasis vulgar",
        "especialidades": ["Dermatología"],
        "tipos_evento": ["Consulta_Especialista"],
        "resoluciones": ["Seguimiento_Continuado"],
        "duracion": (1, 2),
        "edad_rango": (20, 75),
        "plantillas_clinica": [
            "Psoriasis en placas moderada-grave (PASI {pasi}) con afectación de codos, "
            "rodillas y cuero cabelludo. Sin artropatía psoriásica activa. "
            "Control de efectos adversos del tratamiento biológico: sin datos de infección.",
            "Brote de psoriasis guttata en contexto de infección faríngea previa. "
            "Lesiones en tronco y extremidades. DLQI: {dlqi} puntos.",
        ],
        "plantillas_notas": [
            "Se mantiene tratamiento biológico. Analítica de seguridad: sin alteraciones. "
            "Fotoprotección solar. Emolientes diarios.",
            "Se inicia metotrexato con folato. Control analítico hepático mensual los "
            "primeros 6 meses. Se desaconseja alcohol.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    # ── TRAUMATISMO ───────────────────────────────────────────────────────────
    {
        "cie10": "S52.5",
        "descripcion": "Fractura de la epífisis distal del radio",
        "especialidades": ["Traumatología", "Urgencias"],
        "tipos_evento": ["Urgencias", "Consulta_Especialista"],
        "resoluciones": ["Alta_Definitiva", "Seguimiento_Continuado"],
        "duracion": (28, 56),
        "edad_rango": (10, 90),
        "plantillas_clinica": [
            "Caída con apoyo de mano en extensión (FOOSH). Deformidad en dorso de tenedor, "
            "dolor intenso y tumefacción en muñeca {lado}. Rx: fractura distal de radio "
            "con {desplazamiento}. Pulsos y sensibilidad distales conservados.",
            "Fractura de Colles confirmada radiológicamente. Reducción cerrada bajo anestesia "
            "local. Rx post-reducción: alineación {alineacion}. Se aplica escayola antebraquial.",
        ],
        "plantillas_notas": [
            "Escayola antebraquial 4-6 semanas. Control radiológico a los 7 días. "
            "AINE + metamizol. Movilización de dedos desde el primer día.",
            "Valoración quirúrgica para fijación interna con placa volar. "
            "Fisioterapia intensiva tras retirada de inmovilización.",
        ],
        "baja_contingencia": "Accidente_no_Laboral",
        "dias_baja": (28, 56),
        "es_urgencia": True,
        "nivel_triaje": (3, 4),
        "constantes": {"tas": (115, 145), "tad": (70, 90), "fc": (72, 100), "sat": (97, 99), "temp": (36.0, 37.5)},
    },

    # ── PREVENTIVO / RUTINARIO ────────────────────────────────────────────────
    {
        "cie10": "Z00.0",
        "descripcion": "Examen médico general de adulto sano",
        "especialidades": ["Medicina General", "Medicina Preventiva"],
        "tipos_evento": ["Consulta_Primaria"],
        "resoluciones": ["Alta_Definitiva", "Derivacion_Especialista"],
        "duracion": (1, 1),
        "edad_rango": (18, 95),
        "plantillas_clinica": [
            "Revisión periódica anual. Paciente asintomático. Exploración física por "
            "aparatos sin hallazgos patológicos. PA {tas}/{tad} mmHg. IMC {imc}. "
            "Analítica de rutina solicitada.",
            "Control de salud. Sin quejas activas. Vacunas al día. "
            "Screening de FRCV: PA, glucemia, perfil lipídico y tabaquismo.",
        ],
        "plantillas_notas": [
            "Hábitos saludables reforzados. Actividad física aeróbica ≥ 150 min/semana. "
            "Dieta mediterránea. Cribado de cáncer según edad.",
            "Consejo antitabaco. Sin necesidad de tratamiento farmacológico. Revisión anual.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    {
        "cie10": "Z23",
        "descripcion": "Vacunación profiláctica",
        "especialidades": ["Medicina Preventiva", "Medicina General", "Enfermería"],
        "tipos_evento": ["Vacunacion"],
        "resoluciones": ["Alta_Definitiva"],
        "duracion": (1, 1),
        "edad_rango": (1, 95),
        "plantillas_clinica": [
            "Administración de {vacuna} en región deltoidea {lado} según calendario "
            "vacunal vigente. Lote verificado. Paciente tolera el procedimiento sin incidencias.",
            "Vacunación de adulto. Se administra {vacuna}. Sin antecedentes de reacción "
            "adversa vacunal previa. Observación 15 min postadministración sin incidencias.",
        ],
        "plantillas_notas": [
            "Se registra lote, caducidad y vía de administración. Próxima dosis/refuerzo "
            "en {meses_refuerzo} meses si requiere pauta.",
            "Documentación entregada al paciente. Sin reacciones locales ni sistémicas "
            "inmediatas.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },

    # ── HEMATOLÓGICO ──────────────────────────────────────────────────────────
    {
        "cie10": "D50.9",
        "descripcion": "Anemia ferropénica no especificada",
        "especialidades": ["Medicina General", "Hematología", "Digestología"],
        "tipos_evento": ["Consulta_Primaria", "Consulta_Especialista", "Prueba_Diagnostica"],
        "resoluciones": ["Seguimiento_Continuado", "Derivacion_Especialista"],
        "duracion": (1, 2),
        "edad_rango": (15, 85),
        "plantillas_clinica": [
            "Astenia, palidez y disnea de esfuerzo de semanas de evolución. "
            "Analítica: Hb {hb} g/dL, VCM {vcm} fL, ferritina {ferritina} µg/L. "
            "Se investiga causa del déficit de hierro.",
            "Anemia microcítica hipocrómica en seguimiento. Buena respuesta al hierro "
            "oral. Hb actual {hb} g/dL (previa {hb_prev} g/dL hace 6 semanas).",
        ],
        "plantillas_notas": [
            "Sulfato ferroso 200 mg/día en ayunas. Evitar ingesta con lácteos, té o café. "
            "Gastroscopia y colonoscopia para estudio etiológico.",
            "Se mantiene hierro oral. Analítica de control en 8 semanas. "
            "Si no respuesta, valorar hierro IV.",
        ],
        "baja_contingencia": None,
        "es_urgencia": False,
    },
]

# Listas de referencia para rellenar plantillas
_VACUNAS = [
    "Gripe estacional tetravalente", "COVID-19 bivalente (XBB.1.5)",
    "Neumococo 23-valente (PPSV23)", "Neumococo 13-valente (PCV13)",
    "Tétanos-Difteria (Td)", "Hepatitis B recombinante",
    "Herpes zóster recombinante (RZV)", "Meningococo ACWY",
    "Virus del papiloma humano (VPH)", "Hepatitis A inactivada",
]
_LADOS        = ["derecho", "izquierdo"]
_INTENSIDADES = ["leve", "moderada", "grave"]
_GOLD         = ["I", "II", "III", "IV"]


def _fill(texto: str) -> str:
    """Rellena los marcadores de las plantillas con valores aleatorios coherentes."""
    sustituciones = {
        "{dias}":           str(random.randint(2, 10)),
        "{semanas}":        str(random.randint(2, 8)),
        "{anios}":          str(random.randint(1, 10)),
        "{meses}":          str(random.randint(2, 24)),
        "{meses_refuerzo}": str(random.choice([6, 12, 60])),
        "{horas}":          str(random.randint(1, 12)),
        "{min}":            str(random.randint(10, 30)),
        "{mins}":           str(random.randint(10, 45)),
        "{frecuencia}":     str(random.randint(1, 6)),
        "{sat}":            str(random.randint(87, 95)),
        "{temp}":           str(round(random.uniform(37.5, 39.8), 1)),
        "{fc}":             str(random.randint(80, 140)),
        "{fr}":             str(random.randint(20, 35)),
        "{tas}":            str(random.randint(130, 190)),
        "{tad}":            str(random.randint(80, 110)),
        "{deposiciones}":   str(random.randint(5, 12)),
        "{leucos}":         str(random.randint(12, 25)),
        "{pcr}":            str(random.randint(30, 180)),
        "{hba1c}":          str(round(random.uniform(6.5, 10.0), 1)),
        "{glucemia}":       str(random.randint(130, 310)),
        "{microalb}":       str(random.randint(30, 250)),
        "{tsh}":            str(round(random.uniform(0.1, 10.0), 2)),
        "{dosis}":          str(random.choice([25, 50, 75, 100, 125, 150])),
        "{ct}":             str(random.randint(210, 310)),
        "{ldl}":            str(random.randint(130, 220)),
        "{hdl}":            str(random.randint(35, 55)),
        "{tg}":             str(random.randint(100, 300)),
        "{riesgo}":         random.choice(["bajo", "moderado", "alto", "muy alto"]),
        "{objetivo}":       str(random.choice([55, 70, 100])),
        "{hamilton}":       str(random.randint(15, 35)),
        "{phq9}":           str(random.randint(10, 25)),
        "{intensidad}":     random.choice(_INTENSIDADES),
        "{pasi}":           str(random.randint(5, 30)),
        "{dlqi}":           str(random.randint(5, 25)),
        "{scorad}":         str(random.randint(15, 60)),
        "{ige}":            str(random.randint(150, 1200)),
        "{potencia}":       random.choice(["baja", "media", "alta"]),
        "{nicturia}":       str(random.randint(1, 4)),
        "{vol}":            str(random.randint(35, 100)),
        "{psa}":            str(round(random.uniform(1.5, 12.0), 1)),
        "{ipss}":           str(random.randint(8, 28)),
        "{qmax}":           str(random.randint(5, 14)),
        "{rpm}":            str(random.randint(30, 150)),
        "{hb}":             str(round(random.uniform(7.0, 11.5), 1)),
        "{hb_prev}":        str(round(random.uniform(6.5, 10.0), 1)),
        "{vcm}":            str(random.randint(62, 78)),
        "{ferritina}":      str(random.randint(2, 12)),
        "{troponina}":      str(round(random.uniform(0.01, 0.08), 3)),
        "{score}":          str(random.randint(1, 5)),
        "{fe}":             str(random.randint(25, 45)),
        "{bnp}":            str(random.randint(500, 5000)),
        "{litros}":         str(random.choice([2, 3, 4])),
        "{po2}":            str(random.randint(45, 65)),
        "{pco2}":           str(random.randint(42, 65)),
        "{gold}":           random.choice(_GOLD),
        "{grado}":          random.choice(["I", "II", "III", "IV", "II-III"]),
        "{cajón}":          random.choice(["positivo", "ligeramente positivo"]),
        "{desplazamiento}": random.choice(["desplazamiento dorsal mínimo", "desplazamiento moderado", "conminución dorsal"]),
        "{alineacion}":     random.choice(["aceptable", "anatómica", "satisfactoria"]),
        "{midas}":          str(random.randint(6, 30)),
        "{meses}":          str(random.randint(3, 18)),
        "{episodios}":      str(random.randint(1, 4)),
        "{eva}":            str(random.randint(5, 9)),
        "{impacto}":        random.choice(["leve", "moderado", "grave"]),
        "{imc}":            str(round(random.uniform(18.5, 38.0), 1)),
        "{vacuna}":         random.choice(_VACUNAS),
        "{lado}":           random.choice(_LADOS),
    }
    for k, v in sustituciones.items():
        texto = texto.replace(k, v)
    return texto


def _constantes_normales() -> dict:
    return {
        "tas":  random.randint(110, 130),
        "tad":  random.randint(65, 82),
        "fc":   random.randint(62, 88),
        "sat":  round(random.uniform(96.5, 99.5), 1),
        "temp": round(random.uniform(36.0, 37.1), 1),
    }


def _constantes_escenario(esc: dict) -> dict:
    c = esc.get("constantes")
    if not c:
        return _constantes_normales()
    return {
        "tas":  random.randint(*c["tas"]),
        "tad":  random.randint(*c["tad"]),
        "fc":   random.randint(*c["fc"]),
        "sat":  round(random.uniform(*c["sat"]), 1),
        "temp": round(random.uniform(*c["temp"]), 1),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────
REGIONES_SANITARIAS = [
    "Andalucía", "Aragón", "Asturias", "Baleares", "Canarias",
    "Cantabria", "Castilla-La Mancha", "Castilla y León",
    "Cataluña", "Comunitat Valenciana", "Extremadura", "Galicia",
    "La Rioja", "Madrid", "Murcia", "Navarra", "País Vasco",
]

HOSPITALES = [
    "General Universitario", "Clínico San Carlos", "La Paz",
    "Virgen del Rocío", "Valle de Hebrón", "Son Espases",
    "Marqués de Valdecilla", "Gregorio Marañón", "La Fe",
    "Virgen de la Arrixaca", "Puerta de Hierro", "Ramón y Cajal",
]

ESCENARIOS_URGENCIA = [e for e in ESCENARIOS if e.get("es_urgencia")]


def generar_datos(num_pacientes: int = 1000) -> None:
    print(f"\n{'─'*62}")
    print(f"  ChronoHealthDB — Generador de datos clínicos realistas")
    print(f"  Base de datos objetivo : ChronoHealthDB")
    print(f"  Pacientes a generar    : {num_pacientes}")
    print(f"{'─'*62}\n")

    conn = pymysql.connect(**DB_CONFIG)

    try:
        with conn.cursor() as cur:
            for i in range(num_pacientes):

                # ── 1. DATOS BASE ─────────────────────────────────────────
                documento = fake.unique.nif()
                codigo_hash = hashlib.sha256(documento.encode()).hexdigest()
                edad = random.randint(1, 90)
                fecha_nac = fake.date_of_birth(minimum_age=edad, maximum_age=edad)
                sexo = random.choice(["M", "F"])
                grupo = random.choice(["A+","A-","B+","B-","AB+","AB-","O+","O-"])
                region = random.choice(REGIONES_SANITARIAS)

                # Factores de riesgo escalados con la edad
                pool = ["Sin factores de riesgo conocidos"]
                if edad > 15: pool += ["Fumador activo", "Sedentarismo"]
                if edad > 30: pool += ["Sobrepeso (IMC 27-29)", "Consumo moderado de alcohol"]
                if edad > 40: pool += ["Hipertensión arterial", "Dislipemia", "Exfumador"]
                if edad > 50: pool += ["Diabetes mellitus tipo 2", "Obesidad grado I"]
                if edad > 60: pool += ["Cardiopatía isquémica crónica", "EPOC leve", "Fibrilación auricular"]
                if edad > 70: pool += ["Insuficiencia renal crónica estadio 2", "Polimedicación (>5 fármacos)"]

                n_fact = random.choices([1, 2, 3], weights=[0.55, 0.30, 0.15])[0]
                factores = ", ".join(random.sample(pool, min(n_fact, len(pool))))

                # ── 2. PACIENTE ANÓNIMO ───────────────────────────────────
                cur.execute(
                    """INSERT INTO paciente_anonimo
                       (codigo_hash, anio_nacimiento, sexo_biologico, grupo_sanguineo,
                        region_sanitaria, factores_riesgo, activo)
                       VALUES (%s, %s, %s, %s, %s, %s, 1)""",
                    (codigo_hash, fecha_nac.year, sexo, grupo, region, factores),
                )
                id_pac = cur.lastrowid

                # ── 3. DATOS PERSONALES ───────────────────────────────────
                nombre = fake.first_name_male() if sexo == "M" else fake.first_name_female()
                num_ss = f"{random.randint(10,99)}/{random.randint(10000000,99999999)}/{random.randint(10,99)}"
                cur.execute(
                    """INSERT INTO datos_personales
                       (id_paciente, codigo_hash, nombre, primer_apellido, segundo_apellido,
                        documento_identidad, fecha_nacimiento, num_seguridad_social,
                        telefono_contacto, email_contacto, direccion_completa,
                        municipio, provincia, consentimiento_rgpd)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        id_pac, codigo_hash, nombre,
                        fake.last_name(), fake.last_name(),
                        documento, fecha_nac,
                        num_ss,
                        fake.phone_number(),
                        fake.unique.free_email(),
                        f"{fake.street_name()}, {random.randint(1,200)}, "
                        f"{random.randint(1,8)}º{random.randint(1,4)}",
                        fake.city(), fake.state(),
                        random.choices([0, 1], weights=[0.08, 0.92])[0],
                    ),
                )

                # ── 4. EVENTOS CLÍNICOS (2-7 por paciente) ────────────────
                esc_validos = [e for e in ESCENARIOS
                               if e["edad_rango"][0] <= edad <= e["edad_rango"][1]]
                if not esc_validos:
                    esc_validos = ESCENARIOS

                for _ in range(random.randint(2, 7)):
                    esc = random.choice(esc_validos)
                    fecha_ev = fake.date_between(start_date="-5y", end_date="today")
                    tipo_ev = random.choice(esc["tipos_evento"])
                    especialidad = random.choice(esc["especialidades"])
                    resolucion = random.choice(esc["resoluciones"])

                    dur_min, dur_max = esc["duracion"]
                    if tipo_ev == "Consulta_Primaria":
                        duracion = random.randint(1, min(3, dur_max))
                    elif tipo_ev in ("Hospitalizacion", "Cirugia"):
                        duracion = random.randint(max(3, dur_min), dur_max)
                    else:
                        duracion = random.randint(dur_min, dur_max)

                    if tipo_ev in ("Consulta_Primaria", "Vacunacion"):
                        centro = f"Centro de Salud {fake.city()}"
                    elif tipo_ev == "Urgencias":
                        centro = f"Hospital {random.choice(HOSPITALES)} — Urgencias"
                    elif tipo_ev == "Prueba_Diagnostica":
                        servicio = random.choice(["Radiodiagnóstico", "Laboratorio", "Medicina Nuclear", "Endoscopia"])
                        centro = f"Hospital {random.choice(HOSPITALES)} — {servicio}"
                    else:
                        centro = f"Hospital {random.choice(HOSPITALES)}"

                    desc_clin = _fill(random.choice(esc["plantillas_clinica"]))
                    notas     = _fill(random.choice(esc["plantillas_notas"]))

                    cur.execute(
                        """INSERT INTO evento_clinico
                           (id_paciente, fecha_evento, tipo_evento, codigo_cie10, descripcion_cie10,
                            descripcion_clinica, especialidad, centro_sanitario, duracion_dias,
                            resolucion, notas_adicionales)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (id_pac, fecha_ev, tipo_ev,
                         esc["cie10"], esc["descripcion"],
                         desc_clin, especialidad, centro,
                         duracion, resolucion, notas),
                    )

                # ── 5. BAJA MÉDICA (15 % de los pacientes) ────────────────
                if random.random() < 0.15:
                    esc_baja = [e for e in esc_validos if e.get("baja_contingencia")]
                    if not esc_baja:
                        esc_baja = [e for e in ESCENARIOS if e.get("baja_contingencia")]
                    eb = random.choice(esc_baja)

                    rng = eb.get("dias_baja", eb["duracion"])
                    dias_baja = random.randint(
                        max(5, rng[0]),
                        min(90, rng[1] * 3 if rng[1] < 30 else rng[1]),
                    )
                    f_inicio = fake.date_between(start_date="-3y", end_date="-15d")
                    f_fin    = f_inicio + timedelta(days=dias_baja)

                    desc_baja = _fill(random.choice(eb["plantillas_clinica"]))[:490]

                    centro_emisor = random.choice([
                        f"Centro de Salud {fake.city()} — {random.choice(eb['especialidades'])}",
                        f"Mutua {fake.company()[:25]} — {fake.city()}",
                        f"Hospital {random.choice(HOSPITALES)} — {random.choice(eb['especialidades'])}",
                    ])

                    cur.execute(
                        """INSERT INTO historico_bajas_medicas
                           (codigo_hash_paciente, fecha_inicio_baja, fecha_fin_baja,
                            dias_totales_baja, codigo_cie10_causa, descripcion_causa,
                            tipo_contingencia, centro_emisor, numero_parte_baja)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (
                            codigo_hash, f_inicio, f_fin, dias_baja,
                            eb["cie10"], desc_baja,
                            eb["baja_contingencia"],
                            centro_emisor,
                            f"PB-{random.randint(10_000_000, 99_999_999)}",
                        ),
                    )

                # ── 6. TRIAJE URGENCIAS (2 % de los pacientes) ────────────
                if random.random() < 0.02:
                    eu = random.choice(ESCENARIOS_URGENCIA)
                    nivel = random.randint(*eu.get("nivel_triaje", (3, 4)))
                    ctes  = _constantes_escenario(eu)

                    motivo = _fill(random.choice(eu["plantillas_clinica"]))[:490]
                    obs    = random.choice([
                        "Llega por su propio pie. Acompañado de familiar.",
                        "Traslado en SVB. Constantes estables durante el transporte.",
                        "Refiere inicio brusco de la sintomatología.",
                        "Derivado desde guardia de Atención Primaria.",
                        "Se avisa a médico de guardia por nivel de triaje 1-2.",
                        "Paciente colaborador. Constantes iniciales registradas.",
                    ])


                    t_espera = {1: (0, 0), 2: (0, 15), 3: (15, 60), 4: (30, 120), 5: (60, 240)}
                    espera = random.randint(*t_espera.get(nivel, (15, 90)))
                    llegada = datetime.now() - timedelta(minutes=random.randint(5, 240))

                    estado_paciente = random.choices(
                        ["En_Espera", "En_Atencion", "Pendiente_Prueba"],
                        weights=[0.70, 0.20, 0.10],
                    )[0]

                    if estado_paciente == "En_Espera":
                        inicio_atencion = None
                    else:
                        inicio_atencion = llegada + timedelta(minutes=random.randint(2, 40))

                    cur.execute(
                        """INSERT INTO triaje_urgencias_actual
                           (codigo_hash_paciente, fecha_hora_llegada, nivel_triaje_manchester,
                            motivo_consulta, tension_arterial_sistolica, tension_arterial_diastolica,
                            frecuencia_cardiaca, saturacion_oxigeno, temperatura_corporal,
                            estado_actual, sala_box_asignado, tiempo_espera_estimado_min,
                            observaciones_triaje, fecha_hora_inicio_atencion) 
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (
                            codigo_hash, llegada, nivel, motivo,
                            ctes["tas"], ctes["tad"], ctes["fc"],
                            ctes["sat"], ctes["temp"],
                            estado_paciente,
                            f"Box-{random.randint(1,20):02d}",
                            espera,
                            obs,
                            inicio_atencion  
                        ),
                    )

                # Commit parcial y progreso cada 100 pacientes
                if (i + 1) % 100 == 0:
                    conn.commit()
                    print(f"  ✓  {i + 1:>4} / {num_pacientes} pacientes insertados...")

        conn.commit()
        print(f"\n{'─'*62}")
        print(f"  ¡Completado! {num_pacientes} historiales clínicos generados.")
        print(f"{'─'*62}\n")

    except Exception as exc:
        print(f"\n  [ERROR] {exc}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    generar_datos(40000)
