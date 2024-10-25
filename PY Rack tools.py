import sqlite3
from tkinter import *
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Conectar a la base de datos (o crearla si no existe)
conexion = sqlite3.connect('inspecciones.db')
cursor = conexion.cursor()

# Crear la tabla si no existe
def crear_tabla():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inspecciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora TEXT,
        temperatura REAL,
        humedad REAL,
        nivel_agua TEXT,
        cantidad_lamparas INTEGER,
        cantidad_extintores INTEGER,
        responsable TEXT
    )
    ''')
    conexion.commit()

crear_tabla()

# Crear la ventana principal
ventana = Tk()
ventana.title("Registro de Inspecciones")

# Crear los elementos de la interfaz
labels = ["Temperatura (°C):", "Humedad (%):", "Nivel de Agua (m):", 
          "Cantidad de Lámparas:", "Cantidad de Extintores:", 
          "Responsable de la Revisión:"]
entries = []

for label in labels:
    Label(ventana, text=label).pack()
    entry = Entry(ventana)
    entry.pack()
    entries.append(entry)

label_error = Label(ventana, text="", fg="red")
label_error.pack()

# Función para validar el tipo de dato
def validar_dato(entry, tipo):
    entry = entry.strip()  # Eliminar espacios en blanco
    if tipo == 'float':
        try:
            return float(entry)
        except ValueError:
            return None
    elif tipo == 'int':
        try:
            return int(entry)
        except ValueError:
            return None
    elif tipo == 'str':
        return entry if entry else None  # Retornar None si la cadena está vacía
    return None

# Función para registrar nuevos datos
def registrar_datos():
    label_error.config(text="")  # Limpiar mensajes de error
    datos = [
        validar_dato(entry.get(), tipo) for entry, tipo in zip(entries, ['float', 'float', 'str', 'int', 'int', 'str'])
    ]
    
    # Validar si hay errores en los datos
    if datos[0] is None:
        label_error.config(text="Error: Temperatura debe ser un número.")
        return
    if datos[1] is None:
        label_error.config(text="Error: Humedad debe ser un número.")
        return
    if datos[2] is None:
        label_error.config(text="Error: Nivel de Agua debe ser un texto válido.")
        return
    if datos[3] is None:
        label_error.config(text="Error: Cantidad de Lámparas debe ser un número entero.")
        return
    if datos[4] is None:
        label_error.config(text="Error: Cantidad de Extintores debe ser un número entero.")
        return
    if datos[5] is None:
        label_error.config(text="Error: Responsable de la Revisión no puede estar vacío.")
        return

    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    INSERT INTO inspecciones (fecha_hora, temperatura, humedad, nivel_agua, cantidad_lamparas, cantidad_extintores, responsable) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (fecha_hora, *datos))
    conexion.commit()

    for entry in entries:
        entry.delete(0, END)

# Función para mostrar todos los registros
def mostrar_registros():
    cursor.execute('SELECT * FROM inspecciones')
    registros = cursor.fetchall()

    ventana_registros = Toplevel(ventana)
    ventana_registros.title("Registros de Inspecciones")

    texto = Text(ventana_registros)
    texto.pack()
    for registro in registros:
        texto.insert(END, f"ID: {registro[0]}\n Fecha y Hora: {registro[1]}\n Temperatura: {registro[2]}\n Humedad: {registro[3]}\n Nivel de Agua: {registro[4]}\n Lámparas: {registro[5]}\n Extintores: {registro[6]}\n Responsable: {registro[7]}\n")

# Función para graficar temperatura y humedad
def graficar_datos():
    cursor.execute('SELECT fecha_hora, temperatura, humedad FROM inspecciones')
    registros = cursor.fetchall()
    
    if registros:
        fechas = [registro[0] for registro in registros]
        temperaturas = [registro[1] for registro in registros]
        humedades = [registro[2] for registro in registros]

        plt.figure(figsize=(10, 5))
        plt.plot(fechas, temperaturas, label='Temperatura (°C)', color='red', marker='o')
        plt.plot(fechas, humedades, label='Humedad (%)', color='blue', marker='o')
        plt.xlabel('Fecha y Hora')
        plt.ylabel('Valores')
        plt.title('Gráfico de Temperatura y Humedad')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()
    else:
        label_error.config(text="No hay datos para graficar.")

# Función para exportar datos a Excel
def exportar_a_excel():
    cursor.execute('SELECT * FROM inspecciones')
    registros = cursor.fetchall()
    
    if registros:
        df = pd.DataFrame(registros, columns=['ID', 'Fecha y Hora', 'Temperatura', 'Humedad', 'Nivel de Agua', 'Cantidad de Lámparas', 'Cantidad de Extintores', 'Responsable'])
        df.to_excel('inspecciones.xlsx', index=False)
        label_error.config(text="Datos exportados a inspeciones.xlsx exitosamente.")
    else:
        label_error.config(text="No hay datos para exportar.")

# Función para limpiar la base de datos
def limpiar_base_datos():
    def verificar_credenciales():
        if entry_usuario.get() == "admin" and entry_contrasena.get() == "conver":
            cursor.execute('DROP TABLE IF EXISTS inspecciones')  # Eliminar la tabla
            crear_tabla()  # Volver a crear la tabla
            label_error.config(text="Base de datos limpiada exitosamente.")
            ventana_credenciales.destroy()
        else:
            label_error.config(text="Credenciales incorrectas. Intente de nuevo.")

    ventana_credenciales = Toplevel(ventana)
    ventana_credenciales.title("Credenciales de Administrador")

    Label(ventana_credenciales, text="Usuario:").pack()
    entry_usuario = Entry(ventana_credenciales)
    entry_usuario.pack()

    Label(ventana_credenciales, text="Contraseña:").pack()
    entry_contrasena = Entry(ventana_credenciales, show="*")
    entry_contrasena.pack()

    Button(ventana_credenciales, text="Verificar", command=verificar_credenciales).pack()

# Crear los botones y asociarlos a las funciones
Button(ventana, text="Registrar", command=registrar_datos).pack()
Button(ventana, text="Mostrar Registros", command=mostrar_registros).pack()
Button(ventana, text="Graficar Datos", command=graficar_datos).pack()
Button(ventana, text="Exportar a Excel", command=exportar_a_excel).pack()
Button(ventana, text="Limpiar Base de Datos", command=limpiar_base_datos).pack()

# Empaquetar los elementos en la ventana
ventana.mainloop()

# Cerrar la conexión a la base de datos al finalizar
conexion.close()