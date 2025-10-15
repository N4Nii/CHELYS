import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Clase de conexión a la base de datos
class ConexionBD:
    def __init__(self):
        try:
            self.conexion = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="toor",  # Cambia si hace falta
                database="biblioteca"
            )
            self.cursor = self.conexion.cursor(dictionary=True)
            print(" Conectado a la base de datos.")
        except Error as e:
            print(f" Error al conectar: {e}")
            self.conexion = None
            self.cursor = None

    def ejecutar_consulta(self, sql, params=None):
        try:
            if not self.conexion or not self.cursor:
                print(" No hay conexión a la base de datos.")
                return False
            self.cursor.execute(sql, params or ())
            self.conexion.commit()
            return True
        except Error as e:
            print(f" Error en consulta: {e}")
            return False

    def ejecutar_lectura(self, sql, params=None):
        try:
            if not self.conexion or not self.cursor:
                print(" No hay conexión a la base de datos.")
                return []
            self.cursor.execute(sql, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f" Error en lectura: {e}")
            return []

    def cerrar(self):
        if self.conexion and hasattr(self.conexion, "is_connected") and self.conexion.is_connected():
            self.cursor.close()
            self.conexion.close()
            print(" Conexión cerrada.")

# Clases del sistema
class Libro:
    def __init__(self, titulo, autor, anio, disponible=1):
        self.__titulo = titulo
        self.__autor = autor
        self.__anio = anio
        self.__disponible = disponible

    def get_datos(self):
        return (self.__titulo, self.__autor, self.__anio, self.__disponible)

class Usuario:
    def __init__(self, nombre, tipo):
        self.__nombre = nombre
        self.__tipo = tipo

    def get_datos(self):
        return (self.__nombre, self.__tipo)

# Funciones del sistema
def registrar_libro(conexion):
    print("\n Registrar nuevo libro")
    titulo = input("Título: ")
    autor = input("Autor: ")
    anio_input = input("Año (ej. 2023): ")
    try:
        anio = int(anio_input)
    except ValueError:
        print(" Año inválido. Usa un número entero.")
        return

    libro = Libro(titulo, autor, anio, 1)
    sql = """
    INSERT INTO libros (titulo, autor, anio, disponible)
    VALUES (%s, %s, %s, %s)
    """
    if conexion.ejecutar_consulta(sql, libro.get_datos()):
        print(" Libro registrado.")

def registrar_usuario(conexion):
    print("\n Registrar nuevo usuario")
    nombre = input("Nombre: ")
    tipo = input("Tipo (ej. alumno, profesor, externo): ")

    usuario = Usuario(nombre, tipo)
    sql = "INSERT INTO usuarios (nombre, tipo) VALUES (%s, %s)"
    if conexion.ejecutar_consulta(sql, usuario.get_datos()):
        print(" Usuario registrado.")

def registrar_prestamo(conexion):
    print("\n Registrar nuevo préstamo")
    id_usuario = input("ID Usuario: ")
    id_libro = input("ID Libro: ")

    libro = conexion.ejecutar_lectura("SELECT * FROM libros WHERE id = %s AND disponible = 1", (id_libro,))
    if not libro:
        print(" Libro no disponible o no existe.")
        return

    usuario = conexion.ejecutar_lectura("SELECT * FROM usuarios WHERE id = %s", (id_usuario,))
    if not usuario:
        print(" Usuario no existe.")
        return

    sql = "INSERT INTO prestamos (id_usuario, id_libro, fecha_prestamo) VALUES (%s, %s, NOW())"
    if conexion.ejecutar_consulta(sql, (id_usuario, id_libro)):
        conexion.ejecutar_consulta("UPDATE libros SET disponible = 0 WHERE id = %s", (id_libro,))
        print(" Préstamo registrado.")

def devolver_libro(conexion):
    print("\n Devolver libro")
    id_prestamo = input("ID del préstamo: ")

    prestamo = conexion.ejecutar_lectura("SELECT * FROM prestamos WHERE id = %s AND fecha_devolucion IS NULL", (id_prestamo,))
    if not prestamo:
        print(" Préstamo no válido o ya devuelto.")
        return

    id_libro = prestamo[0]['id_libro']

    sql = "UPDATE prestamos SET fecha_devolucion = NOW() WHERE id = %s"
    if conexion.ejecutar_consulta(sql, (id_prestamo,)):
        conexion.ejecutar_consulta("UPDATE libros SET disponible = 1 WHERE id = %s", (id_libro,))
        print(" Libro devuelto correctamente.")

def listar_libros(conexion):
    print("\n Lista de libros:")
    libros = conexion.ejecutar_lectura("SELECT * FROM libros")
    for libro in libros:
        estado = "Disponible" if libro.get("disponible") else "Prestado"
        print(f"{libro['id']}: {libro['titulo']} - {libro['autor']} ({libro['anio']}) — {estado}")

def listar_prestamos(conexion):
    print("\n Lista de préstamos:")
    prestamos = conexion.ejecutar_lectura("""
        SELECT p.id, u.nombre, l.titulo, p.fecha_prestamo, p.fecha_devolucion
        FROM prestamos p
        JOIN usuarios u ON p.id_usuario = u.id
        JOIN libros l ON p.id_libro = l.id
    """)
    for p in prestamos:
        devuelto = p['fecha_devolucion'] or "Pendiente"
        print(f"{p['id']}: {p['nombre']} prestó '{p['titulo']}' el {p['fecha_prestamo']} - Devolución: {devuelto}")

# Menú principal
def menu():
    conexion = ConexionBD()
    if conexion.conexion is None:
        print("No se puede continuar sin conexión a la base de datos.")
        return

    while True:
        print("\n===== BIBLIOTECA - Menú Principal =====")
        print("1. Registrar libro")
        print("2. Registrar usuario")
        print("3. Registrar préstamo")
        print("4. Devolver libro")
        print("5. Listar libros")
        print("6. Listar préstamos")
        print("0. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            registrar_libro(conexion)
        elif opcion == "2":
            registrar_usuario(conexion)
        elif opcion == "3":
            registrar_prestamo(conexion)
        elif opcion == "4":
            devolver_libro(conexion)
        elif opcion == "5":
            listar_libros(conexion)
        elif opcion == "6":
            listar_prestamos(conexion)
        elif opcion == "0":
            conexion.cerrar()
            print(" ¡Hasta luego!")
            break
        else:
            print(" Opción inválida.")

if __name__ == "__main__":
    menu()