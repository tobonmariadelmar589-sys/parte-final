# ⚖️ Justicia & Asociados — LawFirm Management System

Sistema de gestión de escritorio para el bufete de abogados **"Justicia & Asociados"**.

---

## 📁 Estructura del proyecto

```
lawfirm/
├── main.py              ← Parte principal: interfaz gráfica y control del sistema
├── models/
│   └── database.py      ← Conexión a la base de datos y todas las consultas (CRUD)
├── utils/
│   ├── validators.py    ← Valida los datos que ingresa el usuario
│   ├── exportar.py      ← Exporta información a Excel y PDF
│   ├── temas.py         ← Controla el modo claro y oscuro
│   └── favicon.py       ← Ícono de la aplicación y gestión de imágenes
├── assets/              ← Recursos estáticos (imágenes, íconos)
├── init.sql             ← Base de datos: tablas, vistas, triggers y datos de ejemplo
├── Dockerfile           ← Configura cómo se ejecuta la app en un entorno
├── docker-compose.yml   ← Levanta la aplicación junto con sus dependencias
├── requirements.txt     ← Librerías necesarias para que funcione el proyecto
└── README.md            ← Este archivo
```

---

## 🗂️ Módulos del sistema

| # | Pestaña | Descripción |
|---|---------|-------------|
| 1 | **Clientes** | Registro de personas naturales y empresas con foto |
| 2 | **Abogados** | Datos profesionales, especialidades y foto |
| 3 | **Casos Legales** | Apertura y seguimiento de casos con relaciones |
| 4 | **Audiencias y Citas** | Agenda de audiencias y reuniones |

---

## ⚙️ Requisitos

- Python **3.8** o superior
- Las librerías del archivo `requirements.txt`

---

## 🚀 Instalación y ejecución

### Opción 1 — Ejecución directa con Python

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/lawfirm.git
cd lawfirm

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python main.py
```

> La base de datos `lawfirm.db` se crea automáticamente al ejecutar por primera vez.

### Opción 2 — Con Docker

```bash
# Construir y ejecutar el contenedor
docker-compose up --build
```

---

## 🖥️ Uso

1. Al abrir verás **4 pestañas** en la parte superior, una por módulo.
2. Haz clic en un registro del listado para cargarlo en el formulario.
3. Usa los botones de acción:

| Botón | Función |
|-------|---------|
| **Guardar** | Valida y guarda el registro en la base de datos |
| **Actualizar** | Modifica el registro cargado (pide confirmación) |
| **Eliminar** | Elimina el registro seleccionado (pide confirmación) |
| **Limpiar** | Vacía todos los campos del formulario |
| **Exportar Excel** | Genera reporte .xlsx con filtros aplicados |
| **Exportar PDF** | Genera reporte .pdf con filtros aplicados |

4. Usa el menú **Tema** para cambiar entre modo claro y oscuro.
5. En Clientes y Abogados puedes cargar una foto (JPG, PNG o GIF, máx. 5 MB).

---

## 🗄️ Base de datos

El archivo `init.sql` contiene:
- **4 tablas**: `clientes`, `abogados`, `casos`, `audiencias`
- **2 vistas**: `v_casos`, `v_audiencias` (stored procedures)
- **2 triggers**: registro automático de eliminaciones en `log_eliminados`
- **Datos de ejemplo** para probar el sistema desde el primer momento

---

## 🛠️ Tecnologías

| Tecnología | Uso |
|------------|-----|
| Python 3 | Lenguaje principal |
| Tkinter + ttk | Interfaz gráfica de usuario |
| tkcalendar | Selector de fechas con calendario flotante |
| SQLite3 | Base de datos local |
| openpyxl | Exportación a Excel |
| reportlab | Exportación a PDF |
| Pillow | Imágenes y favicon |

---

## 👤 Autor

Proyecto universitario — Programación con Python  
Bufete: **Justicia & Asociados**
