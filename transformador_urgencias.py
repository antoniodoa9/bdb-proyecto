import xml.etree.ElementTree as ET
from xml.dom import minidom

def estructurar_urgencias_criticas(archivo_entrada, archivo_salida):
    print("Procesando datos de pacientes críticos en urgencias...")
    try:
        tree = ET.parse(archivo_entrada)
        root_mysql = tree.getroot()
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo '{archivo_entrada}'.")
        return
    except ET.ParseError:
        print(f"Error: El archivo '{archivo_entrada}' no es un XML válido.")
        return

    root_nuevo = ET.Element("Alerta_Urgencias_Geriatricas")

    for row in root_mysql.findall('ROW'):
        # Función auxiliar para extraer texto de forma segura
        def buscar_campo(nombre_campo):
            nodo = row.find(f"{nombre_campo}")
            return nodo.text if nodo is not None else "Desconocido"

        # Extraer variables de forma segura
        hash_id = buscar_campo('codigo_hash')
        anio = buscar_campo('anio_nacimiento')
        sexo = buscar_campo('sexo_biologico')
        llegada = buscar_campo('fecha_hora_llegada')
        nivel = buscar_campo('nivel_triaje_manchester')
        motivo = buscar_campo('motivo_consulta')
        sat_o2 = buscar_campo('saturacion_oxigeno')
        estado = buscar_campo('estado_actual')

        # Crear el nodo del paciente
        paciente_node = ET.SubElement(root_nuevo, "Paciente_Critico", identificador=hash_id)
        
        # Datos demográficos
        ET.SubElement(paciente_node, "Anio_Nacimiento").text = anio
        ET.SubElement(paciente_node, "Sexo").text = sexo
        
        # Datos del episodio de urgencia actual
        episodio_node = ET.SubElement(paciente_node, "Estado_Clinico_Actual", nivel_prioridad=nivel)
        ET.SubElement(episodio_node, "Hora_Ingreso").text = llegada
        ET.SubElement(episodio_node, "Motivo_Principal").text = motivo
        ET.SubElement(episodio_node, "Saturacion_O2", unidad="%").text = sat_o2 if sat_o2 != 'NULL' else "Desconocida"
        ET.SubElement(episodio_node, "Fase_Asistencia").text = estado

    # --- MOVIDO FUERA DEL BUCLE FOR ---
    # Formateo y escritura del XML final
    xml_string = ET.tostring(root_nuevo, 'utf-8')
    xml_final = minidom.parseString(xml_string).toprettyxml(indent=" ")

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(xml_final)
        
    print(f"Generación completada: {archivo_salida}")

if __name__ == '__main__':
    estructurar_urgencias_criticas('urgencias_criticas_crudas.xml', 'urgencias_criticas_semanticas.xml')
