-- ============================================================
--  init.sql — Base de datos: Justicia & Asociados
--  LawFirm Management System
--  Incluye: tablas, vistas, triggers y datos de ejemplo
-- ============================================================

-- TABLA: Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente     INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo         TEXT NOT NULL UNIQUE,
    tipo           TEXT CHECK(tipo IN ('Persona Natural','Empresa')),
    nombre         TEXT NOT NULL,
    documento      TEXT NOT NULL UNIQUE,
    direccion      TEXT,
    telefono       TEXT,
    correo         TEXT,
    fecha_contacto TEXT,
    referido_por   TEXT,
    clasificacion  TEXT,
    foto           BLOB,
    fecha_registro TEXT DEFAULT (date('now'))
);

-- TABLA: Abogados
CREATE TABLE IF NOT EXISTS abogados (
    id_abogado      INTEGER PRIMARY KEY AUTOINCREMENT,
    num_colegiatura TEXT NOT NULL UNIQUE,
    nombres         TEXT NOT NULL,
    apellidos       TEXT NOT NULL,
    especialidad    TEXT,
    anios_exp       INTEGER,
    formacion       TEXT,
    idiomas         TEXT,
    tarifa_hora     REAL,
    disponibilidad  TEXT DEFAULT 'Disponible',
    foto            BLOB,
    fecha_registro  TEXT DEFAULT (date('now'))
);

-- TABLA: Casos Legales
CREATE TABLE IF NOT EXISTS casos (
    id_caso              INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_caso          TEXT NOT NULL UNIQUE,
    titulo               TEXT NOT NULL,
    tipo_caso            TEXT,
    rama_derecho         TEXT,
    fecha_apertura       TEXT,
    id_cliente           INTEGER REFERENCES clientes(id_cliente),
    contraparte          TEXT,
    juzgado              TEXT,
    num_expediente       TEXT,
    id_abogado_principal INTEGER REFERENCES abogados(id_abogado),
    estado               TEXT DEFAULT 'Abierto',
    fecha_conclusion     TEXT,
    fecha_registro       TEXT DEFAULT (date('now'))
);

-- TABLA: Audiencias y Citas
CREATE TABLE IF NOT EXISTS audiencias (
    id_audiencia       INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo             TEXT NOT NULL UNIQUE,
    tipo               TEXT,
    id_caso            INTEGER REFERENCES casos(id_caso),
    fecha_hora         TEXT,
    duracion_estimada  TEXT,
    lugar              TEXT,
    participantes_int  TEXT,
    participantes_ext  TEXT,
    proposito          TEXT,
    resultado_esperado TEXT,
    resultado_real     TEXT,
    fecha_registro     TEXT DEFAULT (date('now'))
);

-- TABLA: Log de eliminaciones (trigger automático)
CREATE TABLE IF NOT EXISTS log_eliminados (
    id_log   INTEGER PRIMARY KEY AUTOINCREMENT,
    tabla    TEXT,
    registro TEXT,
    fecha_op TEXT DEFAULT (datetime('now'))
);

-- ── STORED PROCEDURES simulados como VISTAS ─────────────────

-- Vista: Casos con datos de cliente y abogado relacionados
CREATE VIEW IF NOT EXISTS v_casos AS
    SELECT
        c.id_caso, c.numero_caso, c.titulo, c.tipo_caso,
        c.rama_derecho, c.fecha_apertura,
        cl.nombre   AS cliente,
        c.contraparte,
        a.nombres || ' ' || a.apellidos AS abogado_principal,
        c.estado, c.fecha_conclusion
    FROM casos c
    LEFT JOIN clientes cl ON c.id_cliente       = cl.id_cliente
    LEFT JOIN abogados a  ON c.id_abogado_principal = a.id_abogado;

-- Vista: Audiencias con número de caso relacionado
CREATE VIEW IF NOT EXISTS v_audiencias AS
    SELECT
        au.id_audiencia, au.codigo, au.tipo,
        ca.numero_caso, ca.titulo AS caso_titulo,
        au.fecha_hora, au.duracion_estimada, au.lugar,
        au.resultado_esperado, au.resultado_real
    FROM audiencias au
    LEFT JOIN casos ca ON au.id_caso = ca.id_caso;

-- ── TRIGGERS ─────────────────────────────────────────────────

-- Registra automáticamente cada caso eliminado
CREATE TRIGGER IF NOT EXISTS trg_delete_caso
AFTER DELETE ON casos
BEGIN
    INSERT INTO log_eliminados(tabla, registro)
    VALUES('casos', OLD.numero_caso || ' - ' || OLD.titulo);
END;

-- Registra automáticamente cada cliente eliminado
CREATE TRIGGER IF NOT EXISTS trg_delete_cliente
AFTER DELETE ON clientes
BEGIN
    INSERT INTO log_eliminados(tabla, registro)
    VALUES('clientes', OLD.codigo || ' - ' || OLD.nombre);
END;

-- ── DATOS DE EJEMPLO ─────────────────────────────────────────

INSERT OR IGNORE INTO clientes
    (codigo, tipo, nombre, documento, direccion, telefono, correo, fecha_contacto, referido_por, clasificacion)
VALUES
    ('CLI-001','Empresa','Constructora Andina S.A.S','900123456-7',
     'Calle 45 #12-30, Medellin','604-3214567',
     'contacto@constructoraandina.com','2025-01-15','Dr. Ramirez','Cliente VIP'),
    ('CLI-002','Persona Natural','Juan Pablo Herrera','1023456789',
     'Carrera 70 #32-15, Bogota','300-4567890',
     'jpherrera@gmail.com','2025-02-10','Referencia web','Estandar');

INSERT OR IGNORE INTO abogados
    (num_colegiatura, nombres, apellidos, especialidad, anios_exp, formacion, idiomas, tarifa_hora, disponibilidad)
VALUES
    ('COL-20456','Carlos Andres','Morales Quintero','Mercantil',12,
     'Magister Derecho Comercial - U. Antioquia','Espanol, Ingles',250000,'Disponible'),
    ('COL-18321','Maria Fernanda','Lopez Rios','Laboral',8,
     'Especialista Derecho Laboral - U. Nacional','Espanol, Frances',180000,'Disponible');

INSERT OR IGNORE INTO casos
    (numero_caso, titulo, tipo_caso, rama_derecho, fecha_apertura,
     id_cliente, contraparte, juzgado, num_expediente,
     id_abogado_principal, estado, fecha_conclusion)
VALUES
    ('CASO-2025-001','Disputa contractual por incumplimiento de obra',
     'Incumplimiento contractual','Civil','2025-02-20',
     1,'Inmobiliaria del Norte Ltda',
     'Juzgado 3 Civil Circuito Medellin','EXP-2025-0892',
     1,'En proceso','2025-11-30');

INSERT OR IGNORE INTO audiencias
    (codigo, tipo, id_caso, fecha_hora, duracion_estimada,
     lugar, participantes_int, participantes_ext, proposito, resultado_esperado)
VALUES
    ('AUD-001','Audiencia Preliminar',1,'2025-04-10 09:00','2 horas',
     'Juzgado 3 Civil, Sala 204',
     'Carlos Morales, Laura Gomez',
     'Rep. Inmobiliaria, Juez Hernandez',
     'Presentacion de pruebas documentales',
     'Admision de pruebas y fijacion de fecha para audiencia oral');
