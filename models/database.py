"""
models/database.py
Maneja la conexión con la base de datos y todas las consultas (CRUD).
Actúa como capa de datos del sistema — stored procedures en Python.
"""
import sqlite3
import os

# Ruta a la base de datos (relativa a este archivo)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lawfirm.db")
SQL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "init.sql")


# ── Conexión ──────────────────────────────────────────────────

def get_connection():
    """Abre y retorna una conexión a SQLite con row_factory activado."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_base_de_datos():
    """
    Crea la base de datos leyendo init.sql si no existe.
    Se ejecuta una sola vez al iniciar la aplicación.
    """
    if not os.path.exists(DB_PATH):
        with open(SQL_PATH, "r", encoding="utf-8") as f:
            script = f.read()
        with get_connection() as conn:
            conn.executescript(script)


# ════════════════════════════════════════════════════════════════
#  STORED PROCEDURES — CLIENTES
# ════════════════════════════════════════════════════════════════

def sp_insertar_cliente(data: dict):
    sql = """
        INSERT INTO clientes
            (codigo, tipo, nombre, documento, direccion, telefono,
             correo, fecha_contacto, referido_por, clasificacion, foto)
        VALUES
            (:codigo, :tipo, :nombre, :documento, :direccion, :telefono,
             :correo, :fecha_contacto, :referido_por, :clasificacion, :foto)
    """
    with get_connection() as conn:
        conn.execute(sql, data)


def sp_actualizar_cliente(data: dict):
    sql = """
        UPDATE clientes SET
            tipo=:tipo, nombre=:nombre, documento=:documento,
            direccion=:direccion, telefono=:telefono, correo=:correo,
            fecha_contacto=:fecha_contacto, referido_por=:referido_por,
            clasificacion=:clasificacion, foto=:foto
        WHERE codigo=:codigo
    """
    with get_connection() as conn:
        conn.execute(sql, data)


def sp_eliminar_cliente(codigo: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM clientes WHERE codigo=?", (codigo,))


def sp_obtener_clientes(filtro: dict = None):
    sql = "SELECT * FROM clientes WHERE 1=1"
    params = []
    if filtro:
        if filtro.get("tipo"):
            sql += " AND tipo=?";            params.append(filtro["tipo"])
        if filtro.get("fecha_desde"):
            sql += " AND fecha_contacto>=?"; params.append(filtro["fecha_desde"])
        if filtro.get("fecha_hasta"):
            sql += " AND fecha_contacto<=?"; params.append(filtro["fecha_hasta"])
        if filtro.get("clasificacion"):
            sql += " AND clasificacion=?";   params.append(filtro["clasificacion"])
    sql += " ORDER BY nombre"
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def sp_obtener_cliente(codigo: str):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM clientes WHERE codigo=?", (codigo,)
        ).fetchone()


def get_clientes_combo():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id_cliente, nombre FROM clientes ORDER BY nombre"
        ).fetchall()
    return {r["nombre"]: r["id_cliente"] for r in rows}


# ════════════════════════════════════════════════════════════════
#  STORED PROCEDURES — ABOGADOS
# ════════════════════════════════════════════════════════════════

def sp_insertar_abogado(data: dict):
    sql = """
        INSERT INTO abogados
            (num_colegiatura, nombres, apellidos, especialidad, anios_exp,
             formacion, idiomas, tarifa_hora, disponibilidad, foto)
        VALUES
            (:num_colegiatura, :nombres, :apellidos, :especialidad, :anios_exp,
             :formacion, :idiomas, :tarifa_hora, :disponibilidad, :foto)
    """
    with get_connection() as conn:
        conn.execute(sql, data)


def sp_actualizar_abogado(data: dict):
    sql = """
        UPDATE abogados SET
            nombres=:nombres, apellidos=:apellidos, especialidad=:especialidad,
            anios_exp=:anios_exp, formacion=:formacion, idiomas=:idiomas,
            tarifa_hora=:tarifa_hora, disponibilidad=:disponibilidad, foto=:foto
        WHERE num_colegiatura=:num_colegiatura
    """
    with get_connection() as conn:
        conn.execute(sql, data)


def sp_eliminar_abogado(num: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM abogados WHERE num_colegiatura=?", (num,))


def sp_obtener_abogados(filtro: dict = None):
    sql = "SELECT * FROM abogados WHERE 1=1"
    params = []
    if filtro:
        if filtro.get("especialidad"):
            sql += " AND especialidad=?";   params.append(filtro["especialidad"])
        if filtro.get("disponibilidad"):
            sql += " AND disponibilidad=?"; params.append(filtro["disponibilidad"])
    sql += " ORDER BY apellidos"
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def sp_obtener_abogado(num: str):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM abogados WHERE num_colegiatura=?", (num,)
        ).fetchone()


def get_abogados_combo():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id_abogado, nombres||' '||apellidos AS n FROM abogados ORDER BY apellidos"
        ).fetchall()
    return {r["n"]: r["id_abogado"] for r in rows}


# ════════════════════════════════════════════════════════════════
#  STORED PROCEDURES — CASOS LEGALES
# ════════════════════════════════════════════════════════════════

def sp_insertar_caso(data: dict):
    sql = """
        INSERT INTO casos
            (numero_caso, titulo, tipo_caso, rama_derecho, fecha_apertura,
             id_cliente, contraparte, juzgado, num_expediente,
             id_abogado_principal, estado, fecha_conclusion)
        VALUES
            (:numero_caso, :titulo, :tipo_caso, :rama_derecho, :fecha_apertura,
             :id_cliente, :contraparte, :juzgado, :num_expediente,
             :id_abogado_principal, :estado, :fecha_conclusion)
    """
    with get_connection() as conn:
        conn.execute(sql, data)


def sp_actualizar_caso(data: dict):
    sql = """
        UPDATE casos SET
            titulo=:titulo, tipo_caso=:tipo_caso, rama_derecho=:rama_derecho,
            fecha_apertura=:fecha_apertura, id_cliente=:id_cliente,
            contraparte=:contraparte, juzgado=:juzgado,
            num_expediente=:num_expediente,
            id_abogado_principal=:id_abogado_principal,
            estado=:estado, fecha_conclusion=:fecha_conclusion
        WHERE numero_caso=:numero_caso
    """
    with get_connection() as conn:
        conn.execute(sql, data)


def sp_eliminar_caso(numero: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM casos WHERE numero_caso=?", (numero,))


def sp_obtener_casos(filtro: dict = None):
    sql = "SELECT * FROM v_casos WHERE 1=1"
    params = []
    if filtro:
        if filtro.get("estado"):
            sql += " AND estado=?";         params.append(filtro["estado"])
        if filtro.get("rama_derecho"):
            sql += " AND rama_derecho=?";   params.append(filtro["rama_derecho"])
        if filtro.get("fecha_desde"):
            sql += " AND fecha_apertura>=?";params.append(filtro["fecha_desde"])
        if filtro.get("fecha_hasta"):
            sql += " AND fecha_apertura<=?";params.append(filtro["fecha_hasta"])
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def sp_obtener_caso(numero: str):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM casos WHERE numero_caso=?", (numero,)
        ).fetchone()


def get_casos_combo():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id_caso, numero_caso FROM casos ORDER BY numero_caso"
        ).fetchall()
    return {r["numero_caso"]: r["id_caso"] for r in rows}


# ════════════════════════════════════════════════════════════════
#  STORED PROCEDURES — AUDIENCIAS Y CITAS
# ════════════════════════════════════════════════════════════════

def sp_insertar_audiencia(data: dict):
    sql = """
        INSERT INTO audiencias
            (codigo, tipo, id_caso, fecha_hora, duracion_estimada,
             lugar, participantes_int, participantes_ext,
             proposito, resultado_esperado, resultado_real)
        VALUES
            (:codigo, :tipo, :id_caso, :fecha_hora, :duracion_estimada,
             :lugar, :participantes_int, :participantes_ext,
             :proposito, :resultado_esperado, :resultado_real)
    """
    with get_connection() as conn:
        conn.execute(sql, data)


def sp_actualizar_audiencia(data: dict):
    sql = """
        UPDATE audiencias SET
            tipo=:tipo, id_caso=:id_caso, fecha_hora=:fecha_hora,
            duracion_estimada=:duracion_estimada, lugar=:lugar,
            participantes_int=:participantes_int,
            participantes_ext=:participantes_ext,
            proposito=:proposito,
            resultado_esperado=:resultado_esperado,
            resultado_real=:resultado_real
        WHERE codigo=:codigo
    """
    with get_connection() as conn:
        conn.execute(sql, data)


def sp_eliminar_audiencia(codigo: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM audiencias WHERE codigo=?", (codigo,))


def sp_obtener_audiencias(filtro: dict = None):
    sql = "SELECT * FROM v_audiencias WHERE 1=1"
    params = []
    if filtro:
        if filtro.get("tipo"):
            sql += " AND tipo=?";       params.append(filtro["tipo"])
        if filtro.get("fecha_desde"):
            sql += " AND fecha_hora>=?";params.append(filtro["fecha_desde"])
        if filtro.get("fecha_hasta"):
            sql += " AND fecha_hora<=?";params.append(filtro["fecha_hasta"])
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def sp_obtener_audiencia(codigo: str):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM audiencias WHERE codigo=?", (codigo,)
        ).fetchone()
