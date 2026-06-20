import tkinter as tk
from tkinter import ttk, messagebox
import pymongo

class AppHospitalCDSS:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de soporte a la decisión clínica")
        self.root.geometry("1050x750")
        self.root.configure(bg="#f4f6f9")
        
        # Conexión a MongoDB
        try:
            self.client = pymongo.MongoClient('mongodb+srv://antoniodoa9:lacasito.O@cluster0.wcpugac.mongodb.net/')
            self.db = self.client['PROYECTO']
            self.coleccion = self.db['pacientes_externos']
        except Exception as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a MongoDB: {e}")
            self.root.destroy()

        self.crear_interfaz()

    def crear_interfaz(self):
        # Título Principal
        lbl_titulo = tk.Label(self.root, text="Panel de control", 
                              font=("Helvetica", 16, "bold"), bg="#f4f6f9", fg="#2c3e50")
        lbl_titulo.pack(pady=10)

        # MÓDULO 1: BÚSQUEDA  INDIVIDUAL
        frame_buscador = tk.LabelFrame(self.root, text=" 🔍 Búsqueda de pacientes", 
                                       bg="#f4f6f9", font=("Helvetica", 11, "bold"), fg="#2c3e50")
        frame_buscador.pack(pady=10, padx=20, fill="x")

        tk.Label(frame_buscador, text="Introduzca ID / Hash del paciente:", bg="#f4f6f9", font=("Helvetica", 10)).grid(row=0, column=0, padx=10, pady=15)
        
        self.entry_id = tk.Entry(frame_buscador, width=45, font=("Consolas", 10))
        self.entry_id.grid(row=0, column=1, padx=10, pady=15)
        
        btn_buscar = tk.Button(frame_buscador, text="Consultar historial y protocolo", 
                               bg="#8e44ad", fg="white", font=("Helvetica", 10, "bold"), 
                               command=self.buscar_paciente)
        btn_buscar.grid(row=0, column=2, padx=15, pady=15)


        # MÓDULO 2: ANÁLISIS EPIDEMIOLÓGICO
        frame_botones = tk.LabelFrame(self.root, text=" 📊 Análisis global", 
                                      bg="#f4f6f9", font=("Helvetica", 11, "bold"), fg="#2c3e50")
        frame_botones.pack(pady=10, padx=20, fill="x")

        btn_cdss = tk.Button(frame_botones, text="1. Resumen tratamientos", font=("Helvetica", 10, "bold"), bg="#2ecc71", fg="white", command=self.ejecutar_cdss, width=28)
        btn_cdss.grid(row=0, column=0, padx=10, pady=10)

        btn_alertas = tk.Button(frame_botones, text="2. Alertas geriátricas", font=("Helvetica", 10, "bold"), bg="#e74c3c", fg="white", command=self.ejecutar_alertas_geriatricas, width=28)
        btn_alertas.grid(row=0, column=1, padx=10, pady=10)

        btn_carga = tk.Button(frame_botones, text="3. Carga por departamento", font=("Helvetica", 10, "bold"), bg="#f39c12", fg="white", command=self.ejecutar_carga_asistencial, width=28)
        btn_carga.grid(row=0, column=2, padx=10, pady=10)

        btn_epidemiologia = tk.Button(frame_botones, text="4. Distribución por edades", font=("Helvetica", 10, "bold"), bg="#3498db", fg="white", command=self.ejecutar_epidemiologia, width=28)
        btn_epidemiologia.grid(row=0, column=3, padx=10, pady=10)


        # PANTALLA DE INFORMES
        self.texto_informe = tk.Text(self.root, font=("Consolas", 10), wrap=tk.WORD, 
                                     bg="#2c3e50", fg="#ecf0f1", padx=15, pady=15)
        self.texto_informe.pack(expand=True, fill=tk.BOTH, padx=20, pady=15)
        self.texto_informe.insert(tk.END, ">>> Módulos inicializados. Conexión segura a MongoDB (50.000 registros) establecida.\n>>> Introduzca un Hash de paciente para búsqueda individual, o pulse un botón...")
        self.texto_informe.config(state=tk.DISABLED)

    def mostrar_resultado(self, texto):
        self.texto_informe.config(state=tk.NORMAL)
        self.texto_informe.delete(1.0, tk.END)
        self.texto_informe.insert(tk.END, texto)
        self.texto_informe.config(state=tk.DISABLED)

    # BUSCADOR INDIVIDUAL
    def buscar_paciente(self):
        id_buscado = self.entry_id.get().strip()
        if not id_buscado:
            self.mostrar_resultado("[!] Error: Debes introducir un ID de paciente válido.")
            return
            
        # Pipeline
        pipeline = [
            {'$match': {'id_paciente': id_buscado}},
            {'$lookup': {'from': 'guias_clinicas', 'localField': 'diagnostico_principal', 'foreignField': 'codigo_cie10', 'as': 'guia'}},
            # preserveNullAndEmptyArrays=True permite mostrar al paciente aunque no tenga guía clínica asignada
            {'$unwind': {'path': '$guia', 'preserveNullAndEmptyArrays': True}} 
        ]
        
        resultados = list(self.coleccion.aggregate(pipeline))
        
        if not resultados:
            self.mostrar_resultado(f"[x] Base de Datos: No se ha encontrado ningún paciente con el ID: {id_buscado}")
            return
            
        r = resultados[0] # Al ser búsqueda por ID único, cogemos el primer documento
        edad_estimada = 2026 - int(r.get('anio_nacimiento', 2026))
        
        salida = f"=== EXPEDIENTE DEL PACIENTE: {id_buscado} ===\n\n"
        salida += f"👤 Edad: {edad_estimada} años | Sexo: {r.get('sexo_biologico', 'N/A')}\n"
        salida += f"🏥 Centro sanitario: {r.get('centro_sanitario', 'N/A')} | Ingreso: {r.get('fecha_ingreso', 'N/A')}\n"
        salida += f"🩺 Diagnóstico: {r.get('descripcion_patologia', 'N/A')} ({r.get('diagnostico_principal', '')})\n\n"
        
        if 'guia' in r and r['guia']:
            guia = r['guia']
            salida += "📋 PROTOCOLO ASIGNADO:\n"
            salida += f"   - Especialidad: {guia.get('especialidad_referencia', 'N/A')}\n"
            salida += f"   - Fuente:  {guia.get('fuente_externa', 'N/A')}\n"
            
            tratamiento = guia.get('protocolo_tratamiento', {})
            salida += f"   - 💊 Medicación 1ª línea: {', '.join(tratamiento.get('primera_linea', []))}\n"
            
            if 'criterios_ingreso' in tratamiento:
                salida += f"   - ⚠️ CRITERIOS INGRESO: {', '.join(tratamiento['criterios_ingreso'])}\n"
        else:
            salida += "📋 PROTOCOLO: Manejo rutinario. No hay guías clínicas digitalizadas para esta patología.\n"
            
        self.mostrar_resultado(salida)


    def ejecutar_cdss(self):
        pipeline = [
            {'$lookup': {'from': 'guias_clinicas', 'localField': 'diagnostico_principal', 'foreignField': 'codigo_cie10', 'as': 'guia_aplicada'}},
            {'$match': {'guia_aplicada': {'$ne': []}}},
            {'$unwind': {'path': '$guia_aplicada'}},
            {'$project': {'_id': 0, 'id_paciente': 1, 'diagnostico': '$descripcion_patologia', 'fuente_protocolo': '$guia_aplicada.fuente_externa', 'medicacion_primera_linea': '$guia_aplicada.protocolo_tratamiento.primera_linea'}},
            {'$limit': 10}
        ]
        resultados = list(self.coleccion.aggregate(pipeline))
        salida = "SISTEMA DE SOPORTE A LA DECISIÓN CLÍNICA (ÚLTIMOS 10)\n\n"
        for r in resultados:
            salida += f"👤 Paciente: {r.get('id_paciente', 'N/A')[:15]}...\n"
            salida += f"   Diagnóstico: {r.get('diagnostico', 'N/A')}\n"
            salida += f"   Protocolo aplicado: {r.get('fuente_protocolo', 'N/A')}\n"
            salida += f"   💊 Tratamiento 1ª línea: {', '.join(r.get('medicacion_primera_linea', []))}\n"
            salida += "-"*60 + "\n"
        self.mostrar_resultado(salida)

    def ejecutar_alertas_geriatricas(self):
        pipeline = [
            {'$match': {'anio_nacimiento': {'$lte': 1956}}},
            {'$lookup': {'from': 'guias_clinicas', 'localField': 'diagnostico_principal', 'foreignField': 'codigo_cie10', 'as': 'guia_aplicada'}},
            {'$unwind': {'path': '$guia_aplicada'}},
            {'$match': {'guia_aplicada.protocolo_tratamiento.criterios_ingreso': {'$exists': True}}},
            {'$project': {'_id': 0, 'id_paciente': 1, 'edad_estimada': {'$subtract': [2026, '$anio_nacimiento']}, 'diagnostico': '$descripcion_patologia', 'criterios_para_ingreso': '$guia_aplicada.protocolo_tratamiento.criterios_ingreso'}},
            {'$sort': {'edad_estimada': -1}},
            {'$limit': 5}
        ]
        resultados = list(self.coleccion.aggregate(pipeline))
        salida = "ALERTAS DE INGRESO GERIÁTRICO\n\n"
        for r in resultados:
            salida += f"⚠️ Paciente {r.get('id_paciente', 'N/A')[:10]}... | Edad: {r.get('edad_estimada', 'N/A')} años\n"
            salida += f"   Patología: {r.get('diagnostico', 'N/A')}\n"
            salida += f"   Criterios de ingreso: {', '.join(r.get('criterios_para_ingreso', []))}\n"
            salida += "-"*60 + "\n"
        self.mostrar_resultado(salida)

    def ejecutar_carga_asistencial(self):
        pipeline = [
            {'$lookup': {'from': 'guias_clinicas', 'localField': 'diagnostico_principal', 'foreignField': 'codigo_cie10', 'as': 'guia_aplicada'}},
            {'$unwind': {'path': '$guia_aplicada'}},
            {'$group': {'_id': {'especialidad': '$guia_aplicada.especialidad_referencia', 'patologia': '$guia_aplicada.enfermedad'}, 'total_pacientes': {'$sum': 1}, 'edad_media': {'$avg': {'$subtract': [2026, '$anio_nacimiento']}}}},
            {'$sort': {'total_pacientes': -1}},
            {'$project': {'_id': 0, 'departamento': '$_id.especialidad', 'patologia': '$_id.patologia', 'carga_pacientes': '$total_pacientes', 'edad_media': {'$round': ['$edad_media', 1]}}}
        ]
        resultados = list(self.coleccion.aggregate(pipeline))
        salida = "3. CARGA  POR DEPARTAMENTO \n\n"
        for r in resultados:
            salida += f"🏥 Departamento: {r.get('departamento', 'N/A')} | Patología: {r.get('patologia', 'N/A')}\n"
            salida += f"   Pacientes atendidos: {r.get('carga_pacientes', 0)}\n"
            salida += f"   Edad media: {r.get('edad_media', 'N/A')} años\n"
            salida += "-"*60 + "\n"
        self.mostrar_resultado(salida)

    def ejecutar_epidemiologia(self):
        pipeline = [
            {'$lookup': {'from': 'guias_clinicas', 'localField': 'diagnostico_principal', 'foreignField': 'codigo_cie10', 'as': 'guia'}},
            {'$unwind': {'path': '$guia'}},
            {'$addFields': {'edad': {'$subtract': [2026, '$anio_nacimiento']}}},
            {'$bucket': {
                'groupBy': '$edad', 
                'boundaries': [0, 18, 45, 65, 120], 
                'default': 'Edad desconocida', 
                'output': {'total_pacientes_riesgo': {'$sum': 1}, 'patologias_frecuentes': {'$addToSet': '$guia.enfermedad'}}
            }},
            {'$project': {
                '_id': 0, 
                'cohorte': {
                    '$switch': {
                        'branches': [
                            {'case': {'$eq': ['$_id', 0]}, 'then': 'Pediatría (0-17 años)'},
                            {'case': {'$eq': ['$_id', 18]}, 'then': 'Adulto joven (18-44 años)'},
                            {'case': {'$eq': ['$_id', 45]}, 'then': 'Adulto maduro (45-64 años)'},
                            {'case': {'$eq': ['$_id', 65]}, 'then': 'Geriatría (65+ años)'}
                        ], 
                        'default': 'Cohorte desconocida'
                    }
                }, 
                'total_pacientes': '$total_pacientes_riesgo', 
                'patologias_registradas': '$patologias_frecuentes'
            }}
        ]
        resultados = list(self.coleccion.aggregate(pipeline))
        salida = "4. DISTRIBUCIÓN POR EDAD\n\n"
        for r in resultados:
            salida += f"📊 Cohorte: {r.get('cohorte', 'N/A')} | Pacientes: {r.get('total_pacientes', 0)}\n"
            salida += f"   Patologías registradas: {', '.join(r.get('patologias_registradas', []))}\n"
            salida += "-"*60 + "\n"
        self.mostrar_resultado(salida)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppHospitalCDSS(root)
    root.mainloop()