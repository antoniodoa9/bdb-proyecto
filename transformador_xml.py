import xml.etree.ElementTree as ET
from xml.dom import minidom

def dar_sentido_al_xml(archivo_entrada, archivo_salida):
    print(f"Leyendo el XML plano exportado de MySQL...")
    
    try:
        tree = ET.parse(archivo_entrada)
        root_mysql = tree.getroot()
    except FileNotFoundError:
        print(f"Error: No se encuentra el archivo '{archivo_entrada}'. Asegúrate de exportarlo primero desde Workbench.")
        return

    # Creamos la nueva raíz con significado biomédico
    root_nuevo = ET.Element("Historiales_Clinicos_Estructurales")
    pacientes_registrados = {}

    # Agrupamos las filas planas en una estructura de árbol
    for row in root_mysql.findall('row'):
        # Extracción de campos basados en el atributo 'name' del XML de MySQL
        hash_id = row.find("field[@name='codigo_hash']").text
        anio = row.find("field[@name='anio_nacimiento']").text
        sexo = row.find("field[@name='sexo_biologico']").text
        grupo = row.find("field[@name='grupo_sanguineo']").text
        region = row.find("field[@name='region_sanitaria']").text
        
        fecha = row.find("field[@name='fecha_evento']").text
        tipo = row.find("field[@name='tipo_evento']").text
        cie10 = row.find("field[@name='codigo_cie10']").text
        desc = row.find("field[@name='descripcion_cie10']").text

        # Si el paciente no se ha agrupado aún, creamos su nodo principal y su demografía
        if hash_id not in pacientes_registrados:
            paciente_node = ET.SubElement(root_nuevo, "Paciente", id=hash_id)
            
            demografia = ET.SubElement(paciente_node, "Datos_Demograficos")
            ET.SubElement(demografia, "Anio_Nacimiento").text = anio
            ET.SubElement(demografia, "Sexo_Biologico").text = sexo
            ET.SubElement(demografia, "Grupo_Sanguineo").text = grupo
            ET.SubElement(demografia, "Region_Sanitaria").text = region
            
            # Contenedor exclusivo para sus eventos longitudinales
            eventos_container = ET.SubElement(paciente_node, "Fichero_Eventos")
            pacientes_registrados[hash_id] = eventos_container

        # Insertamos el evento dentro de su correspondiente paciente
        evento_node = ET.SubElement(pacientes_registrados[hash_id], "Evento_Medico", tipo=tipo)
        ET.SubElement(evento_node, "Fecha_Registro").text = fecha
        ET.SubElement(evento_node, "Diagnostico_CIE10", codigo=cie10).text = desc

    # Formateamos el documento para que incluya tabulaciones y sangrías legibles
    xml_string = ET.tostring(root_nuevo, 'utf-8')
    xml_final = minidom.parseString(xml_string).toprettyxml(indent="    ")

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(xml_final)
        
    print(f"¡Hecho! El archivo '{archivo_salida}' ya tiene sentido jerárquico y significado clínico.")

if __name__ == '__main__':
    dar_sentido_al_xml('export_maximo.xml', 'historiales_semanticos_maximo.xml')