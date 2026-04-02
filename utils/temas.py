"""
utils/temas.py
Controla el modo claro y oscuro de la aplicación.
Aplica los colores a todos los widgets en tiempo real.
"""

# Diccionario con los 2 temas disponibles
TEMAS = {
    "Claro": {
        "bg":       "#F0F2F8",
        "frame_bg": "#FFFFFF",
        "fg":       "#2D3748",
        "entry_bg": "#FFFFFF",
        "entry_fg": "#2D3748",
    },
    "Oscuro": {
        "bg":       "#1A1A2E",
        "frame_bg": "#16213E",
        "fg":       "#E0E0E0",
        "entry_bg": "#0F3460",
        "entry_fg": "#E0E0E0",
    },
}

# Almacena el tema actualmente activo
tema_activo = {"nombre": "Claro"}


def get_tema() -> dict:
    """Retorna el diccionario de colores del tema activo."""
    return TEMAS[tema_activo["nombre"]]


def aplicar_tema(ventana, nombre: str):
    """
    Cambia el tema de la aplicación en tiempo real.
    Recorre todos los widgets y actualiza sus colores.
    """
    tema_activo["nombre"] = nombre
    t = TEMAS[nombre]
    ventana.config(bg=t["bg"])

    def _recorrer(widget):
        try:
            cls = widget.winfo_class()
            if cls in ("Frame", "Labelframe"):
                widget.config(bg=t["frame_bg"])
            elif cls == "Label":
                widget.config(bg=t["bg"], fg=t["fg"])
            elif cls == "Entry":
                widget.config(
                    bg=t["entry_bg"],
                    fg=t["entry_fg"],
                    insertbackground=t["fg"]
                )
            elif cls == "Text":
                widget.config(
                    bg=t["entry_bg"],
                    fg=t["entry_fg"],
                    insertbackground=t["fg"]
                )
        except Exception:
            pass
        for hijo in widget.winfo_children():
            _recorrer(hijo)

    _recorrer(ventana)
