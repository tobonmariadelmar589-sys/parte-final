"""
main.py
Parte principal donde se ve la interfaz y se controla todo el sistema.
Importa y conecta: base de datos, validaciones, exportaciones, temas e imágenes.

Estructura del proyecto:
    main.py              ← Este archivo (interfaz + control)
    models/database.py   ← Conexión a la base de datos y consultas
    utils/validators.py  ← Validaciones de campos
    utils/exportar.py    ← Exportación a Excel y PDF
    utils/temas.py       ← Temas claro y oscuro
    utils/favicon.py     ← Ícono de la aplicación e imágenes
    init.sql             ← Base de datos con tablas y datos de ejemplo
    requirements.txt     ← Librerías necesarias
"""
import sys
import os

# Asegurar que Python encuentre los módulos desde cualquier ubicación
sys.path.insert(0, os.path.dirname(__file__))

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

# ── Importar módulos del proyecto ─────────────────────────────
from models.database import (
    inicializar_base_de_datos,
    sp_insertar_cliente,  sp_actualizar_cliente,  sp_eliminar_cliente,
    sp_obtener_clientes,  sp_obtener_cliente,      get_clientes_combo,
    sp_insertar_abogado,  sp_actualizar_abogado,   sp_eliminar_abogado,
    sp_obtener_abogados,  sp_obtener_abogado,       get_abogados_combo,
    sp_insertar_caso,     sp_actualizar_caso,       sp_eliminar_caso,
    sp_obtener_casos,     sp_obtener_caso,           get_casos_combo,
    sp_insertar_audiencia,sp_actualizar_audiencia,  sp_eliminar_audiencia,
    sp_obtener_audiencias,sp_obtener_audiencia,
)
from utils.validators import (
    validar_cliente, validar_abogado, validar_caso,
    validar_audiencia, mostrar_errores, bloquear_no_numericos,
)
from utils.exportar  import exportar_excel, exportar_pdf
from utils.temas     import aplicar_tema
from utils.favicon   import aplicar_favicon, cargar_imagen, mostrar_imagen

# ── Inicializar base de datos ─────────────────────────────────
inicializar_base_de_datos()

# ════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ════════════════════════════════════════════════════════════════

root = tk.Tk()
root.geometry("1100x720")
root.title("Justicia & Asociados — LawFirm Management")
root.minsize(900, 600)
aplicar_favicon(root)

# ── Menú superior ─────────────────────────────────────────────
menubar   = tk.Menu(root)
m_tema    = tk.Menu(menubar, tearoff=0)
m_tema.add_command(label="Tema Claro",
                   command=lambda: aplicar_tema(root, "Claro"))
m_tema.add_command(label="Tema Oscuro",
                   command=lambda: aplicar_tema(root, "Oscuro"))
menubar.add_cascade(label="Tema", menu=m_tema)
root.config(menu=menubar)

# ── Notebook (pestañas) ───────────────────────────────────────
notebook = ttk.Notebook(root)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)
notebook.add(tab1, text="Clientes")
notebook.add(tab2, text="Abogados")
notebook.add(tab3, text="Casos Legales")
notebook.add(tab4, text="Audiencias y Citas")
notebook.pack(expand=True, fill="both")

# ════════════════════════════════════════════════════════════════
#  HELPERS DE INTERFAZ
# ════════════════════════════════════════════════════════════════

NAVY  = "#1E2761"
GOLD  = "#C9A84C"
WHITE = "#FFFFFF"
LIGHT = "#F0F2F8"
DARK  = "#2D3748"

BTN = {
    "Guardar":    ("#4CAF50", "Guardar"),
    "Actualizar": ("#2196F3", "Actualizar"),
    "Eliminar":   ("#f44336", "Eliminar"),
    "Limpiar":    ("#FF9800", "Limpiar"),
    "Excel":      ("#7B1FA2", "Exportar Excel"),
    "PDF":        ("#D32F2F", "Exportar PDF"),
}


def make_scroll(parent):
    """Crea un canvas con scrollbar vertical. Retorna el frame interior."""
    c     = tk.Canvas(parent, highlightthickness=0)
    sb    = ttk.Scrollbar(parent, orient="vertical", command=c.yview)
    inner = tk.Frame(c)
    inner.bind("<Configure>",
               lambda e: c.configure(scrollregion=c.bbox("all")))
    c.create_window((0, 0), window=inner, anchor="nw")
    c.configure(yscrollcommand=sb.set)
    c.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return inner


def lbl(p, texto, fila, col=0):
    tk.Label(p, text=texto, font=("Calibri", 11),
             fg=NAVY, anchor="w").grid(
        row=fila, column=col, sticky="w", padx=(0, 10), pady=6)


def ent(p, fila, col=1, ancho=28):
    e = tk.Entry(p, width=ancho, font=("Calibri", 11),
                 relief="solid", bd=1, bg=WHITE, fg=DARK)
    e.grid(row=fila, column=col, sticky="w", pady=6)
    return e


def cmb(p, var, vals, fila, col=1):
    cb = ttk.Combobox(p, textvariable=var, values=vals,
                      width=26, state="readonly")
    cb.grid(row=fila, column=col, sticky="w", pady=6)
    return cb


def make_tree(parent, cols, alto=6):
    f  = tk.Frame(parent)
    f.pack(fill="x", padx=40, pady=5)
    tv = ttk.Treeview(f, columns=cols, show="headings", height=alto)
    for c in cols:
        tv.heading(c, text=c)
        tv.column(c, width=130, anchor="center")
    sb = ttk.Scrollbar(f, orient="horizontal", command=tv.xview)
    tv.configure(xscrollcommand=sb.set)
    tv.pack(fill="x")
    sb.pack(fill="x")
    return tv


def make_btns(parent, cmds):
    f = tk.Frame(parent)
    f.pack(pady=10)
    for nombre, fn in cmds.items():
        color, texto = BTN.get(nombre, ("#607D8B", nombre))
        tk.Button(f, text=texto, font=("Calibri", 10, "bold"),
                  bg=color, fg="white", padx=10, pady=4,
                  relief="flat", cursor="hand2",
                  command=fn).pack(side=tk.LEFT, padx=4)


def make_filtro(parent, fn_widgets):
    f = tk.LabelFrame(parent, text=" Filtros de Exportacion ",
                      font=("Calibri", 10, "bold"),
                      fg=NAVY, padx=10, pady=5)
    f.pack(fill="x", padx=40, pady=(5, 0))
    fn_widgets(f)


def foto_panel(parent, lbl_ref, foto_ref):
    """Crea el panel de foto con botones Seleccionar y Quitar."""
    tk.Label(parent, text="Foto", font=("Calibri", 10, "bold"),
             fg=NAVY).pack()
    lbl_ref[0] = tk.Label(parent, text="Sin foto", width=18, height=7,
                           relief="solid", bd=1, bg=LIGHT)
    lbl_ref[0].pack(pady=4)
    tk.Button(parent, text="Seleccionar foto",
              font=("Calibri", 9), bg=NAVY, fg="white",
              command=lambda: foto_ref.__setitem__(
                  0, cargar_imagen(lbl_ref[0])
              )).pack(fill="x", pady=2)
    tk.Button(parent, text="Quitar foto",
              font=("Calibri", 9), bg="#607D8B", fg="white",
              command=lambda: [
                  foto_ref.__setitem__(0, None),
                  lbl_ref[0].config(image="", text="Sin foto")
              ]).pack(fill="x")


# ════════════════════════════════════════════════════════════════
#  MÓDULO 1 — CLIENTES
# ════════════════════════════════════════════════════════════════

foto_cli  = [None]
lbl_fc    = [None]

inner1 = make_scroll(tab1)
tk.Label(inner1, text="GESTION DE CLIENTES",
         font=("Georgia", 15, "bold"), fg=NAVY).pack(pady=(15, 5))

pane1 = tk.Frame(inner1); pane1.pack(fill="x", padx=40, pady=5)
f1    = tk.Frame(pane1);  f1.grid(row=0, column=0, sticky="nw")
fp1   = tk.Frame(pane1);  fp1.grid(row=0, column=1, sticky="n", padx=(30, 0))

lbl(f1, "Codigo Cliente: *",        1); c_cod  = ent(f1, 1)
lbl(f1, "Tipo Cliente: *",          2); c_tipo = tk.StringVar()
cmb(f1, c_tipo, ["Persona Natural", "Empresa"], 2)
lbl(f1, "Nombre / Razon Social: *", 3); c_nom  = ent(f1, 3)
lbl(f1, "Documento / RUC: *",       4); c_doc  = ent(f1, 4)
lbl(f1, "Direccion:",               5); c_dir  = ent(f1, 5)
lbl(f1, "Telefono:",                6); c_tel  = ent(f1, 6)
lbl(f1, "Correo Electronico:",      7); c_cor  = ent(f1, 7)
lbl(f1, "Fecha Primer Contacto:",   8)
c_fec = DateEntry(f1, width=26, date_pattern="yyyy-mm-dd",
                  font=("Calibri", 11))
c_fec.grid(row=8, column=1, sticky="w", pady=6)
lbl(f1, "Referido Por:",            9); c_ref  = ent(f1, 9)
lbl(f1, "Clasificacion Interna:",  10); c_cla  = tk.StringVar()
cmb(f1, c_cla, ["Cliente VIP", "Estandar", "Corporativo", "Pro Bono"], 10)

foto_panel(fp1, lbl_fc, foto_cli)

# Variables de filtro
f1_tipo = tk.StringVar(); f1_cla2 = tk.StringVar()
f1_des  = [None];         f1_has  = [None]


def get_d1():
    return {
        "codigo":         c_cod.get().strip(),
        "tipo":           c_tipo.get(),
        "nombre":         c_nom.get().strip(),
        "documento":      c_doc.get().strip(),
        "direccion":      c_dir.get().strip(),
        "telefono":       c_tel.get().strip(),
        "correo":         c_cor.get().strip(),
        "fecha_contacto": c_fec.get(),
        "referido_por":   c_ref.get().strip(),
        "clasificacion":  c_cla.get(),
        "foto":           foto_cli[0],
    }


def get_filtro1():
    return {
        "tipo":          f1_tipo.get() or None,
        "fecha_desde":   f1_des[0].get() if f1_des[0] else None,
        "fecha_hasta":   f1_has[0].get() if f1_has[0] else None,
        "clasificacion": f1_cla2.get() or None,
    }


def refresh1():
    tree1.delete(*tree1.get_children())
    for r in sp_obtener_clientes(get_filtro1()):
        tree1.insert("", "end", values=(
            r["codigo"], r["tipo"], r["nombre"], r["documento"],
            r["telefono"] or "", r["correo"] or "",
            r["clasificacion"] or ""
        ))


def on_sel1(e):
    s = tree1.selection()
    if not s:
        return
    r = sp_obtener_cliente(str(tree1.item(s[0])["values"][0]))
    if not r:
        return
    for w, k in [(c_cod, "codigo"), (c_nom, "nombre"), (c_doc, "documento"),
                 (c_dir, "direccion"), (c_tel, "telefono"), (c_cor, "correo"),
                 (c_ref, "referido_por")]:
        w.delete(0, tk.END); w.insert(0, r[k] or "")
    c_tipo.set(r["tipo"] or "")
    c_cla.set(r["clasificacion"] or "")
    mostrar_imagen(lbl_fc[0], r["foto"])
    foto_cli[0] = r["foto"]


def save1():
    d = get_d1()
    if mostrar_errores(validar_cliente(d)):
        return
    try:
        sp_insertar_cliente(d)
        messagebox.showinfo("Guardado", "Cliente guardado correctamente.")
        clear1(); refresh1()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def update1():
    if not messagebox.askyesno("Confirmar", "Actualizar este cliente?"):
        return
    d = get_d1()
    if mostrar_errores(validar_cliente(d)):
        return
    try:
        sp_actualizar_cliente(d)
        messagebox.showinfo("Actualizado", "Cliente actualizado correctamente.")
        refresh1()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def delete1():
    cod = c_cod.get().strip()
    if not cod:
        messagebox.showwarning("Aviso", "Selecciona un cliente del listado.")
        return
    if not messagebox.askyesno("Eliminar",
            f"Eliminar el cliente '{cod}'?\nEsta accion no se puede deshacer."):
        return
    try:
        sp_eliminar_cliente(cod)
        messagebox.showinfo("Eliminado", "Cliente eliminado correctamente.")
        clear1(); refresh1()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def clear1():
    for w in [c_cod, c_nom, c_doc, c_dir, c_tel, c_cor, c_ref]:
        w.delete(0, tk.END)
    c_tipo.set(""); c_cla.set("")
    foto_cli[0] = None
    if lbl_fc[0]:
        lbl_fc[0].config(image="", text="Sin foto")


def excel1():
    rows = sp_obtener_clientes(get_filtro1())
    exportar_excel(
        "Clientes",
        ["Codigo", "Tipo", "Nombre", "Documento",
         "Telefono", "Correo", "Clasificacion"],
        [(r["codigo"], r["tipo"], r["nombre"], r["documento"],
          r["telefono"] or "", r["correo"] or "",
          r["clasificacion"] or "") for r in rows],
        f"Tipo:{f1_tipo.get() or 'Todos'}"
    )


def pdf1():
    rows = sp_obtener_clientes(get_filtro1())
    exportar_pdf(
        "Clientes",
        ["Codigo", "Tipo", "Nombre", "Documento",
         "Telefono", "Correo", "Clasificacion"],
        [(r["codigo"], r["tipo"], r["nombre"], r["documento"],
          r["telefono"] or "", r["correo"] or "",
          r["clasificacion"] or "") for r in rows],
        f"Tipo:{f1_tipo.get() or 'Todos'}"
    )


def build_filtros1(f):
    tk.Label(f, text="Tipo:", font=("Calibri", 10)).grid(
        row=0, column=0, padx=5)
    ttk.Combobox(f, textvariable=f1_tipo,
        values=["", "Persona Natural", "Empresa"],
        width=14, state="readonly").grid(row=0, column=1, padx=5)
    tk.Label(f, text="Desde:", font=("Calibri", 10)).grid(
        row=0, column=2, padx=5)
    f1_des[0] = DateEntry(f, width=12, date_pattern="yyyy-mm-dd")
    f1_des[0].grid(row=0, column=3, padx=5)
    tk.Label(f, text="Hasta:", font=("Calibri", 10)).grid(
        row=0, column=4, padx=5)
    f1_has[0] = DateEntry(f, width=12, date_pattern="yyyy-mm-dd")
    f1_has[0].grid(row=0, column=5, padx=5)
    tk.Label(f, text="Clasificacion:", font=("Calibri", 10)).grid(
        row=0, column=6, padx=5)
    ttk.Combobox(f, textvariable=f1_cla2,
        values=["", "Cliente VIP", "Estandar", "Corporativo", "Pro Bono"],
        width=12, state="readonly").grid(row=0, column=7, padx=5)
    tk.Button(f, text="Filtrar", font=("Calibri", 9, "bold"),
              bg=NAVY, fg="white",
              command=refresh1).grid(row=0, column=8, padx=10)


make_filtro(inner1, build_filtros1)
tree1 = make_tree(inner1,
    ("Codigo", "Tipo", "Nombre", "Documento",
     "Telefono", "Correo", "Clasificacion"))
tree1.bind("<<TreeviewSelect>>", on_sel1)
make_btns(inner1, {
    "Guardar": save1, "Actualizar": update1,
    "Eliminar": delete1, "Limpiar": clear1,
    "Excel": excel1, "PDF": pdf1
})
refresh1()


# ════════════════════════════════════════════════════════════════
#  MÓDULO 2 — ABOGADOS
# ════════════════════════════════════════════════════════════════

foto_abo = [None]
lbl_fa   = [None]

inner2 = make_scroll(tab2)
tk.Label(inner2, text="GESTION DE ABOGADOS",
         font=("Georgia", 15, "bold"), fg=NAVY).pack(pady=(15, 5))

pane2 = tk.Frame(inner2); pane2.pack(fill="x", padx=40, pady=5)
f2    = tk.Frame(pane2);  f2.grid(row=0, column=0, sticky="nw")
fp2   = tk.Frame(pane2);  fp2.grid(row=0, column=1, sticky="n", padx=(30, 0))

lbl(f2, "N Colegiatura: *",     1); a_col  = ent(f2, 1)
lbl(f2, "Nombres: *",           2); a_nom  = ent(f2, 2)
lbl(f2, "Apellidos: *",         3); a_ape  = ent(f2, 3)
lbl(f2, "Especialidad:",        4); a_esp  = tk.StringVar()
cmb(f2, a_esp, ["Civil", "Penal", "Laboral", "Tributario", "Mercantil"], 4)
lbl(f2, "Anos de Experiencia:", 5)
a_ani = ent(f2, 5)
a_ani.bind("<KeyRelease>", lambda e: bloquear_no_numericos(e, a_ani))
lbl(f2, "Formacion Academica:", 6); a_for  = ent(f2, 6)
lbl(f2, "Idiomas:",             7); a_idi  = ent(f2, 7)
lbl(f2, "Tarifa por Hora ($):", 8)
a_tar = ent(f2, 8)
a_tar.bind("<KeyRelease>", lambda e: bloquear_no_numericos(e, a_tar))
lbl(f2, "Disponibilidad:",      9); a_dis  = tk.StringVar(value="Disponible")
cmb(f2, a_dis, ["Disponible", "Ocupado", "De vacaciones"], 9)

foto_panel(fp2, lbl_fa, foto_abo)

f2_esp = tk.StringVar(); f2_dis = tk.StringVar()


def get_d2():
    return {
        "num_colegiatura": a_col.get().strip(),
        "nombres":         a_nom.get().strip(),
        "apellidos":       a_ape.get().strip(),
        "especialidad":    a_esp.get(),
        "anios_exp":       a_ani.get().strip() or None,
        "formacion":       a_for.get().strip(),
        "idiomas":         a_idi.get().strip(),
        "tarifa_hora":     a_tar.get().strip() or None,
        "disponibilidad":  a_dis.get(),
        "foto":            foto_abo[0],
    }


def get_filtro2():
    return {
        "especialidad":   f2_esp.get() or None,
        "disponibilidad": f2_dis.get() or None,
    }


def refresh2():
    tree2.delete(*tree2.get_children())
    for r in sp_obtener_abogados(get_filtro2()):
        tarifa = f"${r['tarifa_hora']:,.0f}" if r["tarifa_hora"] else ""
        tree2.insert("", "end", values=(
            r["num_colegiatura"],
            f"{r['nombres']} {r['apellidos']}",
            r["especialidad"],
            r["anios_exp"] or "",
            tarifa,
            r["disponibilidad"]
        ))


def on_sel2(e):
    s = tree2.selection()
    if not s:
        return
    r = sp_obtener_abogado(str(tree2.item(s[0])["values"][0]))
    if not r:
        return
    for w, k in [(a_col, "num_colegiatura"), (a_nom, "nombres"),
                 (a_ape, "apellidos"), (a_ani, "anios_exp"),
                 (a_for, "formacion"), (a_idi, "idiomas"),
                 (a_tar, "tarifa_hora")]:
        w.delete(0, tk.END); w.insert(0, str(r[k] or ""))
    a_esp.set(r["especialidad"] or "")
    a_dis.set(r["disponibilidad"])
    mostrar_imagen(lbl_fa[0], r["foto"])
    foto_abo[0] = r["foto"]


def save2():
    d = get_d2()
    if mostrar_errores(validar_abogado(d)):
        return
    try:
        sp_insertar_abogado(d)
        messagebox.showinfo("Guardado", "Abogado guardado correctamente.")
        clear2(); refresh2()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def update2():
    if not messagebox.askyesno("Confirmar", "Actualizar este abogado?"):
        return
    d = get_d2()
    if mostrar_errores(validar_abogado(d)):
        return
    try:
        sp_actualizar_abogado(d)
        messagebox.showinfo("Actualizado", "Abogado actualizado correctamente.")
        refresh2()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def delete2():
    col = a_col.get().strip()
    if not col:
        messagebox.showwarning("Aviso", "Selecciona un abogado del listado.")
        return
    if not messagebox.askyesno("Eliminar", f"Eliminar el abogado '{col}'?"):
        return
    try:
        sp_eliminar_abogado(col)
        messagebox.showinfo("Eliminado", "Abogado eliminado correctamente.")
        clear2(); refresh2()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def clear2():
    for w in [a_col, a_nom, a_ape, a_ani, a_for, a_idi, a_tar]:
        w.delete(0, tk.END)
    a_esp.set(""); a_dis.set("Disponible")
    foto_abo[0] = None
    if lbl_fa[0]:
        lbl_fa[0].config(image="", text="Sin foto")


def excel2():
    rows = sp_obtener_abogados(get_filtro2())
    exportar_excel(
        "Abogados",
        ["Colegiatura", "Nombres", "Apellidos", "Especialidad",
         "Anos", "Tarifa", "Disponibilidad"],
        [(r["num_colegiatura"], r["nombres"], r["apellidos"],
          r["especialidad"], r["anios_exp"] or "",
          r["tarifa_hora"] or "", r["disponibilidad"]) for r in rows],
        f"Especialidad:{f2_esp.get() or 'Todas'}"
    )


def pdf2():
    rows = sp_obtener_abogados(get_filtro2())
    exportar_pdf(
        "Abogados",
        ["Colegiatura", "Nombre Completo", "Especialidad",
         "Tarifa/Hora", "Disponibilidad"],
        [(r["num_colegiatura"],
          f"{r['nombres']} {r['apellidos']}",
          r["especialidad"], r["tarifa_hora"] or "",
          r["disponibilidad"]) for r in rows],
        f"Especialidad:{f2_esp.get() or 'Todas'}"
    )


def build_filtros2(f):
    tk.Label(f, text="Especialidad:",   font=("Calibri", 10)).grid(
        row=0, column=0, padx=5)
    ttk.Combobox(f, textvariable=f2_esp,
        values=["", "Civil", "Penal", "Laboral", "Tributario", "Mercantil"],
        width=14, state="readonly").grid(row=0, column=1, padx=5)
    tk.Label(f, text="Disponibilidad:", font=("Calibri", 10)).grid(
        row=0, column=2, padx=5)
    ttk.Combobox(f, textvariable=f2_dis,
        values=["", "Disponible", "Ocupado", "De vacaciones"],
        width=14, state="readonly").grid(row=0, column=3, padx=5)
    tk.Button(f, text="Filtrar", font=("Calibri", 9, "bold"),
              bg=NAVY, fg="white",
              command=refresh2).grid(row=0, column=4, padx=10)


make_filtro(inner2, build_filtros2)
tree2 = make_tree(inner2,
    ("Colegiatura", "Nombre Completo", "Especialidad",
     "Anos Exp.", "Tarifa/Hora", "Disponibilidad"))
tree2.bind("<<TreeviewSelect>>", on_sel2)
make_btns(inner2, {
    "Guardar": save2, "Actualizar": update2,
    "Eliminar": delete2, "Limpiar": clear2,
    "Excel": excel2, "PDF": pdf2
})
refresh2()


# ════════════════════════════════════════════════════════════════
#  MÓDULO 3 — CASOS LEGALES
# ════════════════════════════════════════════════════════════════

inner3 = make_scroll(tab3)
tk.Label(inner3, text="GESTION DE CASOS LEGALES",
         font=("Georgia", 15, "bold"), fg=NAVY).pack(pady=(15, 5))

f3 = tk.Frame(inner3); f3.pack(fill="x", padx=60, pady=5)

lbl(f3, "Numero de Caso: *",      1); ca_num = ent(f3, 1)
lbl(f3, "Titulo Descriptivo: *",  2); ca_tit = ent(f3, 2, ancho=40)
lbl(f3, "Tipo de Caso:",          3); ca_tip = ent(f3, 3)
lbl(f3, "Rama del Derecho:",      4); ca_ram = tk.StringVar()
cmb(f3, ca_ram,
    ["Civil", "Penal", "Laboral", "Tributario", "Mercantil", "Administrativo"], 4)
lbl(f3, "Fecha de Apertura:",     5)
ca_fec = DateEntry(f3, width=26, date_pattern="yyyy-mm-dd", font=("Calibri", 11))
ca_fec.grid(row=5, column=1, sticky="w", pady=6)
lbl(f3, "Cliente:",               6); ca_cli_v  = tk.StringVar()
ca_cli_cb = ttk.Combobox(f3, textvariable=ca_cli_v, width=26, state="readonly")
ca_cli_cb.grid(row=6, column=1, sticky="w", pady=6)
lbl(f3, "Contraparte:",           7); ca_con = ent(f3, 7)
lbl(f3, "Juzgado / Entidad:",     8); ca_juz = ent(f3, 8)
lbl(f3, "N Expediente Externo:",  9); ca_exp = ent(f3, 9)
lbl(f3, "Abogado Principal:",    10); ca_abo_v  = tk.StringVar()
ca_abo_cb = ttk.Combobox(f3, textvariable=ca_abo_v, width=26, state="readonly")
ca_abo_cb.grid(row=10, column=1, sticky="w", pady=6)
lbl(f3, "Estado Actual:",        11); ca_est = tk.StringVar(value="Abierto")
cmb(f3, ca_est,
    ["Abierto", "En proceso", "Suspendido", "Cerrado", "Ganado", "Perdido"], 11)
lbl(f3, "Fecha Est. Conclusion:", 12)
ca_con2 = DateEntry(f3, width=26, date_pattern="yyyy-mm-dd", font=("Calibri", 11))
ca_con2.grid(row=12, column=1, sticky="w", pady=6)

f3_est = tk.StringVar(); f3_ram = tk.StringVar()
f3_des = [None];          f3_has = [None]


def refresh_combos3():
    cli = get_clientes_combo(); abo = get_abogados_combo()
    ca_cli_cb["values"] = list(cli.keys()); ca_cli_cb._map = cli
    ca_abo_cb["values"] = list(abo.keys()); ca_abo_cb._map = abo


def get_d3():
    cli = getattr(ca_cli_cb, "_map", {})
    abo = getattr(ca_abo_cb, "_map", {})
    return {
        "numero_caso":          ca_num.get().strip(),
        "titulo":               ca_tit.get().strip(),
        "tipo_caso":            ca_tip.get().strip(),
        "rama_derecho":         ca_ram.get(),
        "fecha_apertura":       ca_fec.get(),
        "id_cliente":           cli.get(ca_cli_v.get()),
        "contraparte":          ca_con.get().strip(),
        "juzgado":              ca_juz.get().strip(),
        "num_expediente":       ca_exp.get().strip(),
        "id_abogado_principal": abo.get(ca_abo_v.get()),
        "estado":               ca_est.get(),
        "fecha_conclusion":     ca_con2.get(),
    }


def get_filtro3():
    return {
        "estado":       f3_est.get() or None,
        "rama_derecho": f3_ram.get() or None,
        "fecha_desde":  f3_des[0].get() if f3_des[0] else None,
        "fecha_hasta":  f3_has[0].get() if f3_has[0] else None,
    }


def refresh3():
    tree3.delete(*tree3.get_children())
    for r in sp_obtener_casos(get_filtro3()):
        tree3.insert("", "end", values=(
            r["numero_caso"], r["titulo"][:30], r["rama_derecho"] or "",
            r["cliente"] or "", r["abogado_principal"] or "",
            r["estado"], r["fecha_apertura"] or ""
        ))


def on_sel3(e):
    s = tree3.selection()
    if not s:
        return
    r = sp_obtener_caso(str(tree3.item(s[0])["values"][0]))
    if not r:
        return
    for w, k in [(ca_num, "numero_caso"), (ca_tit, "titulo"),
                 (ca_tip, "tipo_caso"),   (ca_con, "contraparte"),
                 (ca_juz, "juzgado"),     (ca_exp, "num_expediente")]:
        w.delete(0, tk.END); w.insert(0, r[k] or "")
    ca_ram.set(r["rama_derecho"] or "")
    ca_est.set(r["estado"])


def save3():
    d = get_d3()
    if mostrar_errores(validar_caso(d)):
        return
    try:
        sp_insertar_caso(d)
        messagebox.showinfo("Guardado", "Caso legal guardado correctamente.")
        clear3(); refresh3(); refresh_combos3()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def update3():
    if not messagebox.askyesno("Confirmar", "Actualizar este caso legal?"):
        return
    d = get_d3()
    if mostrar_errores(validar_caso(d)):
        return
    try:
        sp_actualizar_caso(d)
        messagebox.showinfo("Actualizado", "Caso actualizado correctamente.")
        refresh3()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def delete3():
    num = ca_num.get().strip()
    if not num:
        messagebox.showwarning("Aviso", "Selecciona un caso del listado.")
        return
    if not messagebox.askyesno("Eliminar",
            f"Eliminar el caso '{num}'?\nEsta accion es irreversible."):
        return
    try:
        sp_eliminar_caso(num)
        messagebox.showinfo("Eliminado", "Caso eliminado correctamente.")
        clear3(); refresh3()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def clear3():
    for w in [ca_num, ca_tit, ca_tip, ca_con, ca_juz, ca_exp]:
        w.delete(0, tk.END)
    ca_ram.set(""); ca_est.set("Abierto")
    ca_cli_v.set(""); ca_abo_v.set("")


def excel3():
    rows = sp_obtener_casos(get_filtro3())
    exportar_excel(
        "Casos Legales",
        ["N Caso", "Titulo", "Rama", "Cliente",
         "Abogado", "Estado", "Apertura", "Conclusion"],
        [(r["numero_caso"], r["titulo"], r["rama_derecho"] or "",
          r["cliente"] or "", r["abogado_principal"] or "",
          r["estado"], r["fecha_apertura"] or "",
          r["fecha_conclusion"] or "") for r in rows],
        f"Estado:{f3_est.get() or 'Todos'}"
    )


def pdf3():
    rows = sp_obtener_casos(get_filtro3())
    exportar_pdf(
        "Casos Legales",
        ["N Caso", "Titulo", "Rama", "Estado", "Cliente"],
        [(r["numero_caso"], r["titulo"][:35], r["rama_derecho"] or "",
          r["estado"], r["cliente"] or "") for r in rows],
        f"Estado:{f3_est.get() or 'Todos'}"
    )


def build_filtros3(f):
    tk.Label(f, text="Estado:", font=("Calibri", 10)).grid(
        row=0, column=0, padx=5)
    ttk.Combobox(f, textvariable=f3_est,
        values=["", "Abierto", "En proceso", "Suspendido",
                "Cerrado", "Ganado", "Perdido"],
        width=12, state="readonly").grid(row=0, column=1, padx=5)
    tk.Label(f, text="Rama:", font=("Calibri", 10)).grid(
        row=0, column=2, padx=5)
    ttk.Combobox(f, textvariable=f3_ram,
        values=["", "Civil", "Penal", "Laboral",
                "Tributario", "Mercantil", "Administrativo"],
        width=12, state="readonly").grid(row=0, column=3, padx=5)
    tk.Label(f, text="Desde:", font=("Calibri", 10)).grid(
        row=0, column=4, padx=5)
    f3_des[0] = DateEntry(f, width=12, date_pattern="yyyy-mm-dd")
    f3_des[0].grid(row=0, column=5, padx=5)
    tk.Label(f, text="Hasta:", font=("Calibri", 10)).grid(
        row=0, column=6, padx=5)
    f3_has[0] = DateEntry(f, width=12, date_pattern="yyyy-mm-dd")
    f3_has[0].grid(row=0, column=7, padx=5)
    tk.Button(f, text="Filtrar", font=("Calibri", 9, "bold"),
              bg=NAVY, fg="white",
              command=refresh3).grid(row=0, column=8, padx=10)


make_filtro(inner3, build_filtros3)
tree3 = make_tree(inner3,
    ("N Caso", "Titulo", "Rama", "Cliente", "Abogado", "Estado", "Apertura"))
tree3.bind("<<TreeviewSelect>>", on_sel3)
make_btns(inner3, {
    "Guardar": save3, "Actualizar": update3,
    "Eliminar": delete3, "Limpiar": clear3,
    "Excel": excel3, "PDF": pdf3
})
refresh_combos3()
refresh3()


# ════════════════════════════════════════════════════════════════
#  MÓDULO 4 — AUDIENCIAS Y CITAS
# ════════════════════════════════════════════════════════════════

inner4 = make_scroll(tab4)
tk.Label(inner4, text="GESTION DE AUDIENCIAS Y CITAS",
         font=("Georgia", 15, "bold"), fg=NAVY).pack(pady=(15, 5))

f4 = tk.Frame(inner4); f4.pack(fill="x", padx=60, pady=5)

lbl(f4, "Codigo: *",               1); au_cod = ent(f4, 1)
lbl(f4, "Tipo:",                   2); au_tip = tk.StringVar()
cmb(f4, au_tip,
    ["Audiencia Oral", "Audiencia Preliminar", "Cita con Cliente",
     "Reunion Interna", "Conciliacion"], 2)
lbl(f4, "Caso Relacionado:",       3); au_cas_v  = tk.StringVar()
au_cas_cb = ttk.Combobox(f4, textvariable=au_cas_v, width=26, state="readonly")
au_cas_cb.grid(row=3, column=1, sticky="w", pady=6)
lbl(f4, "Fecha y Hora:",           4)
au_fec = DateEntry(f4, width=26, date_pattern="yyyy-mm-dd", font=("Calibri", 11))
au_fec.grid(row=4, column=1, sticky="w", pady=6)
lbl(f4, "Duracion Estimada:",      5); au_dur = ent(f4, 5)
lbl(f4, "Lugar: *",                6); au_lug = ent(f4, 6)
lbl(f4, "Participantes Internos:", 7); au_pin = ent(f4, 7)
lbl(f4, "Participantes Externos:", 8); au_pex = ent(f4, 8)
lbl(f4, "Proposito:",              9)
au_pro = tk.Text(f4, width=30, height=3, font=("Calibri", 11),
                 relief="solid", bd=1, bg=WHITE)
au_pro.grid(row=9, column=1, sticky="w", pady=6)
lbl(f4, "Resultado Esperado:",    10); au_res = ent(f4, 10)
lbl(f4, "Resultado Real:",        11); au_rea = ent(f4, 11)

f4_tip = tk.StringVar()
f4_des = [None]; f4_has = [None]


def refresh_combos4():
    cas = get_casos_combo()
    au_cas_cb["values"] = list(cas.keys())
    au_cas_cb._map = cas


def get_d4():
    cas = getattr(au_cas_cb, "_map", {})
    return {
        "codigo":            au_cod.get().strip(),
        "tipo":              au_tip.get(),
        "id_caso":           cas.get(au_cas_v.get()),
        "fecha_hora":        au_fec.get(),
        "duracion_estimada": au_dur.get().strip(),
        "lugar":             au_lug.get().strip(),
        "participantes_int": au_pin.get().strip(),
        "participantes_ext": au_pex.get().strip(),
        "proposito":         au_pro.get("1.0", tk.END).strip(),
        "resultado_esperado":au_res.get().strip(),
        "resultado_real":    au_rea.get().strip(),
    }


def get_filtro4():
    return {
        "tipo":        f4_tip.get() or None,
        "fecha_desde": f4_des[0].get() if f4_des[0] else None,
        "fecha_hasta": f4_has[0].get() if f4_has[0] else None,
    }


def refresh4():
    tree4.delete(*tree4.get_children())
    for r in sp_obtener_audiencias(get_filtro4()):
        tree4.insert("", "end", values=(
            r["codigo"], r["tipo"] or "", r["numero_caso"] or "",
            r["fecha_hora"] or "", r["lugar"] or "",
            r["resultado_esperado"] or ""
        ))


def on_sel4(e):
    s = tree4.selection()
    if not s:
        return
    r = sp_obtener_audiencia(str(tree4.item(s[0])["values"][0]))
    if not r:
        return
    for w, k in [(au_cod, "codigo"), (au_dur, "duracion_estimada"),
                 (au_lug, "lugar"),  (au_pin, "participantes_int"),
                 (au_pex, "participantes_ext"),
                 (au_res, "resultado_esperado"),
                 (au_rea, "resultado_real")]:
        w.delete(0, tk.END); w.insert(0, r[k] or "")
    au_tip.set(r["tipo"] or "")
    au_pro.delete("1.0", tk.END)
    au_pro.insert("1.0", r["proposito"] or "")


def save4():
    d = get_d4()
    if mostrar_errores(validar_audiencia(d)):
        return
    try:
        sp_insertar_audiencia(d)
        messagebox.showinfo("Guardado", "Audiencia guardada correctamente.")
        clear4(); refresh4()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def update4():
    if not messagebox.askyesno("Confirmar", "Actualizar esta audiencia?"):
        return
    d = get_d4()
    if mostrar_errores(validar_audiencia(d)):
        return
    try:
        sp_actualizar_audiencia(d)
        messagebox.showinfo("Actualizado", "Audiencia actualizada correctamente.")
        refresh4()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def delete4():
    cod = au_cod.get().strip()
    if not cod:
        messagebox.showwarning("Aviso", "Selecciona una audiencia del listado.")
        return
    if not messagebox.askyesno("Eliminar", f"Eliminar la audiencia '{cod}'?"):
        return
    try:
        sp_eliminar_audiencia(cod)
        messagebox.showinfo("Eliminado", "Audiencia eliminada correctamente.")
        clear4(); refresh4()
    except Exception as ex:
        messagebox.showerror("Error", str(ex))


def clear4():
    for w in [au_cod, au_dur, au_lug, au_pin, au_pex, au_res, au_rea]:
        w.delete(0, tk.END)
    au_tip.set(""); au_cas_v.set("")
    au_pro.delete("1.0", tk.END)


def excel4():
    rows = sp_obtener_audiencias(get_filtro4())
    exportar_excel(
        "Audiencias y Citas",
        ["Codigo", "Tipo", "N Caso", "Fecha/Hora",
         "Lugar", "Res. Esperado", "Res. Real"],
        [(r["codigo"], r["tipo"] or "", r["numero_caso"] or "",
          r["fecha_hora"] or "", r["lugar"] or "",
          r["resultado_esperado"] or "", r["resultado_real"] or "")
         for r in rows],
        f"Tipo:{f4_tip.get() or 'Todos'}"
    )


def pdf4():
    rows = sp_obtener_audiencias(get_filtro4())
    exportar_pdf(
        "Audiencias y Citas",
        ["Codigo", "Tipo", "N Caso", "Fecha/Hora", "Lugar"],
        [(r["codigo"], r["tipo"] or "", r["numero_caso"] or "",
          r["fecha_hora"] or "", r["lugar"] or "")
         for r in rows],
        f"Tipo:{f4_tip.get() or 'Todos'}"
    )


def build_filtros4(f):
    tk.Label(f, text="Tipo:", font=("Calibri", 10)).grid(
        row=0, column=0, padx=5)
    ttk.Combobox(f, textvariable=f4_tip,
        values=["", "Audiencia Oral", "Audiencia Preliminar",
                "Cita con Cliente", "Reunion Interna", "Conciliacion"],
        width=18, state="readonly").grid(row=0, column=1, padx=5)
    tk.Label(f, text="Desde:", font=("Calibri", 10)).grid(
        row=0, column=2, padx=5)
    f4_des[0] = DateEntry(f, width=12, date_pattern="yyyy-mm-dd")
    f4_des[0].grid(row=0, column=3, padx=5)
    tk.Label(f, text="Hasta:", font=("Calibri", 10)).grid(
        row=0, column=4, padx=5)
    f4_has[0] = DateEntry(f, width=12, date_pattern="yyyy-mm-dd")
    f4_has[0].grid(row=0, column=5, padx=5)
    tk.Button(f, text="Filtrar", font=("Calibri", 9, "bold"),
              bg=NAVY, fg="white",
              command=refresh4).grid(row=0, column=6, padx=10)


make_filtro(inner4, build_filtros4)
tree4 = make_tree(inner4,
    ("Codigo", "Tipo", "N Caso", "Fecha/Hora", "Lugar", "Res. Esperado"))
tree4.bind("<<TreeviewSelect>>", on_sel4)
make_btns(inner4, {
    "Guardar": save4, "Actualizar": update4,
    "Eliminar": delete4, "Limpiar": clear4,
    "Excel": excel4, "PDF": pdf4
})
refresh_combos4()
refresh4()

# ════════════════════════════════════════════════════════════════
root.mainloop()
