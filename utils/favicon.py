"""
utils/favicon.py
Define el ícono personalizado de la aplicación.
Dibuja una balanza de justicia usando Pillow.
"""


def aplicar_favicon(ventana):
    """
    Crea y aplica el ícono (favicon) de la ventana.
    Dibuja una balanza de justicia en colores navy y dorado.
    """
    try:
        from PIL import Image, ImageDraw, ImageTk

        # Canvas 64x64 con fondo navy
        img  = Image.new("RGBA", (64, 64), (30, 39, 97, 255))
        draw = ImageDraw.Draw(img)
        gold = (201, 168, 76, 255)

        # Mástil central de la balanza
        draw.rectangle([29, 8, 35, 52], fill=gold)

        # Travesaño horizontal superior
        draw.ellipse([16, 8, 48, 20], fill=gold)

        # Platillo izquierdo
        draw.ellipse([10, 22, 30, 34], fill=gold)

        # Platillo derecho
        draw.ellipse([34, 22, 54, 34], fill=gold)

        # Base de la balanza
        draw.rectangle([18, 50, 46, 54], fill=gold)

        # Aplicar como ícono de la ventana
        ico = ImageTk.PhotoImage(img)
        ventana.iconphoto(True, ico)
        ventana._favicon = ico  # Mantener referencia para evitar garbage collection

    except ImportError:
        pass  # Si Pillow no está instalado, continúa sin favicon
    except Exception:
        pass  # Si falla por cualquier razón, la app sigue funcionando


def cargar_imagen(label_widget, max_w: int = 150, max_h: int = 150):
    """
    Abre un diálogo para seleccionar una imagen JPG, PNG o GIF.
    Valida formato y tamaño máximo (5 MB).
    Redimensiona con Pillow y muestra en el label indicado.
    Retorna los bytes de la imagen para guardar en la base de datos.
    """
    import io
    import os
    from tkinter import filedialog, messagebox

    try:
        from PIL import Image, ImageTk

        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imagenes", "*.jpg *.jpeg *.png *.gif"),
                ("Todos los archivos", "*.*")
            ]
        )
        if not ruta:
            return None

        # Validar formato del archivo
        ext = os.path.splitext(ruta)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".gif"):
            messagebox.showerror(
                "Formato no valido",
                "Solo se aceptan imagenes JPG, PNG y GIF."
            )
            return None

        # Validar tamaño máximo (5 MB)
        tam_mb = os.path.getsize(ruta) / (1024 * 1024)
        if tam_mb > 5:
            messagebox.showerror(
                "Imagen muy grande",
                f"La imagen pesa {tam_mb:.1f} MB. El maximo es 5 MB."
            )
            return None

        # Abrir, convertir a RGB y redimensionar
        img = Image.open(ruta)
        if img.format == "GIF":
            img = img.convert("RGBA").convert("RGB")
        else:
            img = img.convert("RGB")
        img.thumbnail((max_w, max_h), Image.LANCZOS)

        # Mostrar en el label de la interfaz
        foto = ImageTk.PhotoImage(img)
        label_widget.config(image=foto, text="")
        label_widget.image = foto  # Mantener referencia

        # Convertir a bytes PNG para guardar en SQLite
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    except ImportError:
        messagebox.showerror(
            "Libreria faltante",
            "Instala Pillow:\npip install Pillow"
        )
        return None
    except Exception as e:
        messagebox.showerror("Error al cargar imagen", str(e))
        return None


def mostrar_imagen(label_widget, datos_bytes, max_w: int = 150, max_h: int = 150):
    """
    Carga una imagen desde bytes (guardada en la BD) y la muestra en el label.
    Si no hay datos, muestra el texto 'Sin foto'.
    """
    import io

    try:
        from PIL import Image, ImageTk

        if not datos_bytes:
            label_widget.config(image="", text="Sin foto")
            return

        img  = Image.open(io.BytesIO(datos_bytes))
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        label_widget.config(image=foto, text="")
        label_widget.image = foto  # Mantener referencia

    except Exception:
        label_widget.config(image="", text="Sin foto")
