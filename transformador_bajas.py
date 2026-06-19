import xml.etree.ElementTree as ET
from xml.dom import minidom

def estructurar_bajas(archivo_entrada, archivo_salida):
    try:
        tree = ET.parse(archivo_entrada)
        root_mysql = tree.getroot()
    except FileNotFoundError:
        print("Error: Archivo de entrada no encontrado.")
        return

    root_nuevo = ET.Element("Registro_Nacional_Bajas")
    pacientes_dict = {}

    for row in root_mysql.findall('row'):
        hash_id = row.find("field[@name='codigo_hash_paciente']").text
        fecha_inicio = row.find("field[@name='fecha_inicio_baja']").text
        dias = row.find("field[@name='dias_totales_baja']").text
        cie10 = row.find("field[@name='codigo_cie10_causa']").text
        descripcion = row.find("field[@name='descripcion_causa']").text
        tipo = row.find("field[@name='tipo_contingencia']").text

        if hash_id not in pacientes_dict:
            paciente_node = ET.SubElement(root_nuevo, "Expediente_Laboral", id_paciente=hash_id)
            pacientes_dict[hash_id] = paciente_node

        baja_node = ET.SubElement(pacientes_dict[hash_id], "Incapacidad_Temporal", tipo=tipo)
        ET.SubElement(baja_node, "Fecha_Inicio").text = fecha_inicio
        ET.SubElement(baja_node, "Duracion_Dias").text = dias
        ET.SubElement(baja_node, "Motivo_CIE10").text = cie10
        ET.SubElement(baja_node, "Descripcion_Motivo").text = descripcion
        ET.SubElement(baja_node, "Tipo_Contingencia").text = tipo

    xml_string = ET.tostring(root_nuevo, 'utf-8')
    xml_final = minidom.parseString(xml_string).toprettyxml(indent="    ")

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(xml_final)

    print(f"Archivo XML jerárquico generado: {archivo_salida}")

if __name__ == '__main__':
    estructurar_bajas('export_historico.xml', 'bajas_semanticas.xml')