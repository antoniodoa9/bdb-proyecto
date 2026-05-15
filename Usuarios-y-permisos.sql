USE PROYECTO;

CREATE USER IF NOT EXISTS 'doctor'@'%' IDENTIFIED BY 'Medicina_2026*';

GRANT SELECT, INSERT, UPDATE ON PROYECTO.paciente_anonimo TO 'doctor'@'%';
GRANT SELECT, INSERT, UPDATE ON PROYECTO.datos_personales TO 'doctor'@'%';
GRANT SELECT, INSERT, UPDATE ON PROYECTO.evento_clinico TO 'doctor'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON PROYECTO.triaje_urgencias_actual TO 'doctor'@'%';
GRANT SELECT, INSERT ON PROYECTO.historico_bajas_medicas TO 'doctor'@'%';

CREATE USER IF NOT EXISTS 'investigador'@'%' IDENTIFIED BY 'Bioinfo_2026*';

GRANT SELECT ON PROYECTO.paciente_anonimo TO 'investigador'@'%';
GRANT SELECT ON PROYECTO.evento_clinico TO 'investigador'@'%';
GRANT SELECT ON PROYECTO.historico_bajas_medicas TO 'investigador'@'%';

FLUSH PRIVILEGES;