import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox

# Función para conectar a la base de datos
def conectar_bd():
    try:
        conn = psycopg2.connect(
            dbname="gestion_inventario",  # Cambia estos valores según tu configuración
            user="postgres",
            password="0000",
            host="localhost"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")
        return None

# Función para obtener los nombres de los salones
def obtener_nombres_salones():
    conn = conectar_bd()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_salon, nombre FROM Salon")
            salones = cursor.fetchall()
            return salones
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener los nombres de los salones: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

# Función para obtener los nombres de los bancos
def obtener_nombres_bancos(id_salon):
    conn = conectar_bd()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_banco, nombre FROM Banco WHERE id_salon = %s", (id_salon,))
            bancos = cursor.fetchall()
            return bancos
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener los nombres de los bancos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

# Función para agregar un elemento
def agregar_elemento(nombre, cantidad, descripcion, id_banco):
    conn = conectar_bd()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO Elemento (nombre, cantidad, descripcion, id_banco)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (nombre, cantidad, descripcion, id_banco))
            conn.commit()
            messagebox.showinfo("Éxito", "Elemento agregado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el elemento: {e}")
        finally:
            cursor.close()
            conn.close()

# Función para modificar un elemento
def modificar_elemento(id_elemento, nombre, cantidad, descripcion):
    conn = conectar_bd()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE Elemento
            SET nombre = %s, cantidad = %s, descripcion = %s
            WHERE id_elemento = %s
            """
            cursor.execute(query, (nombre, cantidad, descripcion, id_elemento))
            conn.commit()
            messagebox.showinfo("Éxito", "Elemento modificado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar el elemento: {e}")
        finally:
            cursor.close()
            conn.close()

# Función para eliminar un elemento
def eliminar_elemento(id_elemento):
    conn = conectar_bd()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Elemento WHERE id_elemento = %s"
            cursor.execute(query, (id_elemento,))
            conn.commit()
            messagebox.showinfo("Éxito", "Elemento eliminado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el elemento: {e}")
        finally:
            cursor.close()
            conn.close()

# Función para visualizar elementos
def visualizar_elementos(id_banco):
    conn = conectar_bd()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT id_elemento, nombre, cantidad, descripcion FROM Elemento WHERE id_banco = %s"
            cursor.execute(query, (id_banco,))
            elementos = cursor.fetchall()
            return elementos
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener los elementos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

# Función para crear subventanas dependiendo de la acción seleccionada
def abrir_ventana_accion(accion):
    ventana_accion = tk.Toplevel()
    ventana_accion.title(f"{accion} Elemento")

    tk.Label(ventana_accion, text="Salón").grid(row=0, column=0)
    tk.Label(ventana_accion, text="Banco").grid(row=1, column=0)

    # Obtener los salones desde la base de datos
    salones = obtener_nombres_salones()
    salon_nombres = [salon[1] for salon in salones]
    salon_combobox = ttk.Combobox(ventana_accion, values=salon_nombres, state="readonly")
    salon_combobox.grid(row=0, column=1)

    banco_combobox = ttk.Combobox(ventana_accion, state="readonly")
    banco_combobox.grid(row=1, column=1)

    # Declaramos la variable bancos para que esté accesible en todo el bloque de la función
    bancos = []

    # Función para actualizar los bancos según el salón seleccionado
    def actualizar_bancos(event):
        nonlocal bancos  # Usamos nonlocal para modificar la variable bancos dentro de la función interna
        salon_seleccionado = salon_combobox.get()
        for salon in salones:
            if salon[1] == salon_seleccionado:
                bancos = obtener_nombres_bancos(salon[0])
                banco_nombres = [banco[1] for banco in bancos]
                banco_combobox['values'] = banco_nombres
                break

    salon_combobox.bind("<<ComboboxSelected>>", actualizar_bancos)

    if accion == "Agregar":
        tk.Label(ventana_accion, text="Nombre del elemento").grid(row=2, column=0)
        tk.Label(ventana_accion, text="Cantidad").grid(row=3, column=0)
        tk.Label(ventana_accion, text="Descripción").grid(row=4, column=0)

        entry_nombre = tk.Entry(ventana_accion)
        entry_cantidad = tk.Entry(ventana_accion)
        entry_descripcion = tk.Entry(ventana_accion)

        entry_nombre.grid(row=2, column=1)
        entry_cantidad.grid(row=3, column=1)
        entry_descripcion.grid(row=4, column=1)

        def agregar_ui():
            nombre = entry_nombre.get()
            cantidad = entry_cantidad.get()
            descripcion = entry_descripcion.get()
            banco_seleccionado = banco_combobox.get()

            for banco in bancos:
                if banco[1] == banco_seleccionado:
                    id_banco = banco[0]
                    break
            agregar_elemento(nombre, int(cantidad), descripcion, id_banco)

        tk.Button(ventana_accion, text="Agregar", command=agregar_ui).grid(row=5, column=1)

    elif accion == "Modificar":
        tk.Label(ventana_accion, text="Elemento").grid(row=2, column=0)

        # Combobox para seleccionar el elemento a modificar
        elemento_combobox = ttk.Combobox(ventana_accion, state="readonly")
        elemento_combobox.grid(row=2, column=1)

        # Variable para almacenar los elementos
        elementos = []

        # Función para actualizar los elementos según el banco seleccionado
        def actualizar_elementos(event):
            nonlocal elementos
            banco_seleccionado = banco_combobox.get()

            for banco in bancos:
                if banco[1] == banco_seleccionado:
                    elementos = visualizar_elementos(banco[0])
                    elemento_nombres = [elemento[1] for elemento in elementos]  # Obtener los nombres de los elementos
                    elemento_combobox['values'] = elemento_nombres
                    break

        banco_combobox.bind("<<ComboboxSelected>>", actualizar_elementos)

        def abrir_ventana_modificar():
            elemento_seleccionado = elemento_combobox.get()

            # Obtener los datos del elemento seleccionado
            for elemento in elementos:
                if elemento[1] == elemento_seleccionado:
                    id_elemento = elemento[0]
                    nombre_actual = elemento[1]
                    cantidad_actual = elemento[2]
                    descripcion_actual = elemento[3]
                    break

            # Crear ventana para modificar los datos
            ventana_modificar = tk.Toplevel()
            ventana_modificar.title(f"Modificar {elemento_seleccionado}")

            tk.Label(ventana_modificar, text="Nombre del elemento").grid(row=0, column=0)
            tk.Label(ventana_modificar, text="Cantidad").grid(row=1, column=0)
            tk.Label(ventana_modificar, text="Descripción").grid(row=2, column=0)

            entry_nombre = tk.Entry(ventana_modificar)
            entry_nombre.insert(0, nombre_actual)
            entry_cantidad = tk.Entry(ventana_modificar)
            entry_cantidad.insert(0, cantidad_actual)
            entry_descripcion = tk.Entry(ventana_modificar)
            entry_descripcion.insert(0, descripcion_actual)

            entry_nombre.grid(row=0, column=1)
            entry_cantidad.grid(row=1, column=1)
            entry_descripcion.grid(row=2, column=1)

            def modificar_ui():
                nuevo_nombre = entry_nombre.get()
                nueva_cantidad = entry_cantidad.get()
                nueva_descripcion = entry_descripcion.get()
                modificar_elemento(id_elemento, nuevo_nombre, int(nueva_cantidad), nueva_descripcion)

            tk.Button(ventana_modificar, text="Guardar Cambios", command=modificar_ui).grid(row=3, column=1)

        tk.Button(ventana_accion, text="Modificar", command=abrir_ventana_modificar).grid(row=3, column=1)

    elif accion == "Eliminar":
        tk.Label(ventana_accion, text="Elemento").grid(row=2, column=0)

        # Combobox para seleccionar el elemento a eliminar
        elemento_combobox = ttk.Combobox(ventana_accion, state="readonly")
        elemento_combobox.grid(row=2, column=1)

        # Variable para almacenar los elementos
        elementos = []

        # Función para actualizar los elementos según el banco seleccionado
        def actualizar_elementos(event):
            nonlocal elementos
            banco_seleccionado = banco_combobox.get()

            for banco in bancos:
                if banco[1] == banco_seleccionado:
                    elementos = visualizar_elementos(banco[0])
                    elemento_nombres = [elemento[1] for elemento in elementos]  # Obtener los nombres de los elementos
                    elemento_combobox['values'] = elemento_nombres
                    break

        banco_combobox.bind("<<ComboboxSelected>>", actualizar_elementos)

        def eliminar_ui():
            elemento_seleccionado = elemento_combobox.get()

            # Obtener el ID del elemento seleccionado
            for elemento in elementos:
                if elemento[1] == elemento_seleccionado:
                    id_elemento = elemento[0]
                    break

            eliminar_elemento(id_elemento)

        tk.Button(ventana_accion, text="Eliminar", command=eliminar_ui).grid(row=3, column=1)

    elif accion == "Visualizar":
        def visualizar_ui():
            banco_seleccionado = banco_combobox.get()

            for banco in bancos:
                if banco[1] == banco_seleccionado:
                    id_banco = banco[0]
                    break

            elementos = visualizar_elementos(id_banco)
            
            if elementos:
                # Crear una nueva ventana para mostrar los elementos
                ventana_elementos = tk.Toplevel()
                ventana_elementos.title("Elementos en el Banco")

                # Encabezados de la tabla
                tk.Label(ventana_elementos, text="Nombre", font=("Arial", 10, "bold")).grid(row=0, column=0)
                tk.Label(ventana_elementos, text="Cantidad", font=("Arial", 10, "bold")).grid(row=0, column=1)
                tk.Label(ventana_elementos, text="Descripción", font=("Arial", 10, "bold")).grid(row=0, column=2)

                # Mostrar cada elemento en una fila de la ventana
                for i, elemento in enumerate(elementos):
                    tk.Label(ventana_elementos, text=elemento[1]).grid(row=i+1, column=0)
                    tk.Label(ventana_elementos, text=elemento[2]).grid(row=i+1, column=1)
                    tk.Label(ventana_elementos, text=elemento[3]).grid(row=i+1, column=2)
            else:
                messagebox.showinfo("Información", "No hay elementos en este banco.")

        tk.Button(ventana_accion, text="Visualizar", command=visualizar_ui).grid(row=3, column=1)

# Ventana principal con opciones
root = tk.Tk()
root.title("Gestión de Inventario")

tk.Button(root, text="Agregar Elemento", command=lambda: abrir_ventana_accion("Agregar")).pack(pady=10)
tk.Button(root, text="Modificar Elemento", command=lambda: abrir_ventana_accion("Modificar")).pack(pady=10)
tk.Button(root, text="Eliminar Elemento", command=lambda: abrir_ventana_accion("Eliminar")).pack(pady=10)
tk.Button(root, text="Visualizar Elementos", command=lambda: abrir_ventana_accion("Visualizar")).pack(pady=10)

root.mainloop()
