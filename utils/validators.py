"""
utils/validators.py
Valida los datos que ingresa el usuario:
correo, números, longitud de texto y caracteres especiales.
"""
import re
import tkinter as tk
from tkinter import messagebox


def validar_email(valor: str) -> bool:
    """Valida que el correo tenga formato correcto usando expresión regular."""
    patron = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return bool(re.match(patron, valor))


def validar_numerico(valor: str) -> bool:
    """Valida que el valor sea un número entero o decimal."""
    try:
        float(valor)
        return True
    except (ValueError, TypeError):
        return False


def validar_longitud(valor: str, minimo: int = 2, maximo: int = 200) -> bool:
    """Valida longitud mínima y máxima de un campo de texto."""
    return minimo <= len(valor.strip()) <= maximo


def validar_telefono(valor: str) -> bool:
    """Valida que el teléfono contenga solo dígitos, guiones y paréntesis."""
    return bool(re.match(r'^[\d\-\+\s\(\)]{7,20}$', valor))


def bloquear_no_numericos(evento, widget):
    """
    Callback para Entry: elimina en tiempo real
    cualquier carácter que no sea dígito o punto decimal.
    Úsalo con: entry.bind('<KeyRelease>', lambda e: bloquear_no_numericos(e, entry))
    """
    valor  = widget.get()
    limpio = re.sub(r'[^\d.]', '', valor)
    if valor != limpio:
        pos = widget.index(tk.INSERT)
        widget.delete(0, tk.END)
        widget.insert(0, limpio)
        widget.icursor(min(pos, len(limpio)))


# ── Validación de formularios completos ───────────────────────

def validar_cliente(datos: dict) -> list:
    """Valida todos los campos del formulario de Clientes. Retorna lista de errores."""
    errores = []
    if not validar_longitud(datos.get("codigo", ""), 3, 20):
        errores.append("• Codigo: minimo 3 y maximo 20 caracteres")
    if not validar_longitud(datos.get("nombre", ""), 3, 150):
        errores.append("• Nombre / Razon Social: minimo 3 caracteres")
    if not validar_longitud(datos.get("documento", ""), 5, 30):
        errores.append("• Documento / RUC: minimo 5 caracteres")
    if datos.get("correo") and not validar_email(datos["correo"]):
        errores.append("• Correo electronico: formato invalido  (ej: nombre@dominio.com)")
    if datos.get("telefono") and not validar_telefono(datos["telefono"]):
        errores.append("• Telefono: solo digitos, guiones y parentesis (7-20 caracteres)")
    return errores


def validar_abogado(datos: dict) -> list:
    errores = []
    if not validar_longitud(datos.get("num_colegiatura", ""), 3, 20):
        errores.append("• N Colegiatura: minimo 3 caracteres")
    if not validar_longitud(datos.get("nombres", ""), 2, 80):
        errores.append("• Nombres: minimo 2 caracteres")
    if not validar_longitud(datos.get("apellidos", ""), 2, 80):
        errores.append("• Apellidos: minimo 2 caracteres")
    if datos.get("anios_exp") and not validar_numerico(datos["anios_exp"]):
        errores.append("• Anos de experiencia: debe ser un numero")
    if datos.get("tarifa_hora") and not validar_numerico(datos["tarifa_hora"]):
        errores.append("• Tarifa por hora: debe ser un numero")
    return errores


def validar_caso(datos: dict) -> list:
    errores = []
    if not validar_longitud(datos.get("numero_caso", ""), 3, 30):
        errores.append("• Numero de caso: minimo 3 caracteres")
    if not validar_longitud(datos.get("titulo", ""), 5, 200):
        errores.append("• Titulo: minimo 5 caracteres")
    return errores


def validar_audiencia(datos: dict) -> list:
    errores = []
    if not validar_longitud(datos.get("codigo", ""), 3, 20):
        errores.append("• Codigo: minimo 3 caracteres")
    if not validar_longitud(datos.get("lugar", ""), 3, 200):
        errores.append("• Lugar: minimo 3 caracteres")
    return errores


def mostrar_errores(errores: list) -> bool:
    """Muestra un messagebox con los errores encontrados. Retorna True si hay errores."""
    if errores:
        messagebox.showerror("Errores de validacion", "\n".join(errores))
        return True
    return False
