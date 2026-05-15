CREATE DATABASE IF NOT EXISTS ChronoHealthDB
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ChronoHealthDB;

CREATE TABLE IF NOT EXISTS paciente_anonimo (
    id_paciente          INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    codigo_hash          CHAR(64)         NOT NULL,
    anio_nacimiento      YEAR             NOT NULL,
    sexo_biologico       ENUM('M', 'F', 'Indeterminado') NOT NULL DEFAULT 'Indeterminado',
    grupo_sanguineo      ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-','Desconocido') NOT NULL DEFAULT 'Desconocido',
    region_sanitaria     VARCHAR(100)     NOT NULL,
    factores_riesgo      TEXT             NULL,
    fecha_registro       DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultima_actualizacion DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo               TINYINT(1)       NOT NULL DEFAULT 1,
    PRIMARY KEY (id_paciente),
    UNIQUE KEY uq_codigo_hash (codigo_hash),
    INDEX idx_sexo_anio (sexo_biologico, anio_nacimiento),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS datos_personales (
    id_paciente          INT UNSIGNED     NOT NULL,
    codigo_hash          CHAR(64)         NOT NULL,
    nombre               VARCHAR(100)     NOT NULL,
    primer_apellido      VARCHAR(100)     NOT NULL,
    segundo_apellido     VARCHAR(100)     NULL,
    documento_identidad  VARCHAR(20)      NOT NULL,
    fecha_nacimiento     DATE             NOT NULL,
    num_seguridad_social VARCHAR(30)      NOT NULL,
    telefono_contacto    VARCHAR(20)      NULL,
    email_contacto       VARCHAR(150)     NULL,
    direccion_completa   VARCHAR(255)     NULL,
    municipio            VARCHAR(100)     NULL,
    provincia            VARCHAR(100)     NULL,
    consentimiento_rgpd  TINYINT(1)       NOT NULL DEFAULT 0,
    fecha_alta           DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion   DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_paciente),
    UNIQUE KEY uq_codigo_hash (codigo_hash),
    UNIQUE KEY uq_documento_identidad (documento_identidad),
    UNIQUE KEY uq_num_seguridad_social (num_seguridad_social),
    CONSTRAINT fk_dp_paciente_anonimo FOREIGN KEY (id_paciente) REFERENCES paciente_anonimo (id_paciente) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS evento_clinico (
    id_evento            BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    id_paciente          INT UNSIGNED     NOT NULL,
    fecha_evento         DATE             NOT NULL,
    fecha_hora_registro  DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tipo_evento          ENUM('Consulta_Primaria', 'Consulta_Especialista', 'Urgencias', 'Hospitalizacion', 'Cirugia', 'Prueba_Diagnostica', 'Baja_Medica', 'Alta_Medica', 'Vacunacion', 'Teleconsulta', 'Otro') NOT NULL,
    codigo_cie10         VARCHAR(8)       NOT NULL,
    descripcion_cie10    VARCHAR(255)     NOT NULL,
    descripcion_clinica  TEXT             NULL,
    especialidad         VARCHAR(100)     NULL,
    centro_sanitario     VARCHAR(200)     NULL,
    duracion_dias        SMALLINT UNSIGNED NULL,
    resolucion           ENUM('Alta_Definitiva', 'Alta_Voluntaria', 'Derivacion_Especialista', 'Seguimiento_Continuado', 'Exitus', 'Pendiente_Resultado') NULL,
    notas_adicionales    TEXT             NULL,
    PRIMARY KEY (id_evento),
    INDEX idx_paciente_fecha (id_paciente, fecha_evento),
    INDEX idx_fecha_evento (fecha_evento),
    INDEX idx_codigo_cie10 (codigo_cie10),
    INDEX idx_tipo_evento (tipo_evento),
    CONSTRAINT fk_ec_paciente_anonimo FOREIGN KEY (id_paciente) REFERENCES paciente_anonimo (id_paciente) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS historico_bajas_medicas (
    id_baja                BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    codigo_hash_paciente   CHAR(64)         NOT NULL,
    fecha_inicio_baja      DATE             NOT NULL,
    fecha_fin_baja         DATE             NULL,
    dias_totales_baja      SMALLINT UNSIGNED NULL,
    codigo_cie10_causa     VARCHAR(8)       NOT NULL,
    descripcion_causa      VARCHAR(500)     NOT NULL,
    tipo_contingencia      ENUM('Enfermedad_Comun', 'Accidente_no_Laboral', 'Enfermedad_Profesional', 'Accidente_Laboral', 'Maternidad_Paternidad', 'Riesgo_Embarazo') NOT NULL,
    centro_emisor          VARCHAR(200)     NULL,
    numero_parte_baja      VARCHAR(50)      NULL,
    fecha_registro_archivo DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_baja)
) ENGINE=ARCHIVE DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS triaje_urgencias_actual (
    id_triaje                    INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    codigo_hash_paciente         CHAR(64)         NOT NULL,
    fecha_hora_llegada           DATETIME         NOT NULL,
    nivel_triaje_manchester      TINYINT UNSIGNED NOT NULL,
    motivo_consulta              VARCHAR(500)     NOT NULL,
    tension_arterial_sistolica   SMALLINT UNSIGNED NULL,
    tension_arterial_diastolica  SMALLINT UNSIGNED NULL,
    frecuencia_cardiaca          SMALLINT UNSIGNED NULL,
    saturacion_oxigeno           DECIMAL(4,1)     NULL,
    temperatura_corporal         DECIMAL(4,1)     NULL,
    estado_actual                ENUM('En_Espera', 'En_Atencion', 'Pendiente_Prueba', 'Derivado_Planta', 'Alta_Urgencias') NOT NULL DEFAULT 'En_Espera',
    sala_box_asignado            VARCHAR(50)      NULL,
    tiempo_espera_estimado_min   SMALLINT UNSIGNED NULL,
    fecha_hora_inicio_atencion   DATETIME         NULL,
    observaciones_triaje         VARCHAR(500)     NULL,
    PRIMARY KEY (id_triaje),
    INDEX idx_nivel_triaje (nivel_triaje_manchester) USING HASH,
    INDEX idx_estado (estado_actual) USING HASH,
    INDEX idx_hora_llegada (fecha_hora_llegada) USING BTREE
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;