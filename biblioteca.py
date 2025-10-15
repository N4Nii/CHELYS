import mysql.connector
import datetime
import os  # Para limpiar la pantalla


# ==========================
# CLASE CONEXIÓN A BASE DE DATOS
# ==========================
class ConexionBD:
    def __init__(self):
        try:
            self.conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="toor",
                database="biblioteca",
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.conexion.cursor(dictionary=True)
        except mysql.connector.Error as e:
            print(f"❌ Error de conexión a MySQL: {e}")

    def ejecutar(self, query, valores=None):
        try:
            self.cursor.execute(query, valores or ())
            if query.strip().lower().startswith("select"):
                resultados = self.cursor.fetchall()
                return resultados
            self.conexion.commit()
            return True
        except mysql.connector.Error as e:
            print(f"⚠️ Error al ejecutar la consulta: {e}")
            self.conexion.rollback()
            return None

    def cerrar(self):
        self.cursor.close()
        self.conexion.close()


# ==========================
# CLASE LIBRO
# ==========================
class Libro:
    def __init__(self, titulo, autor, anio, disponible=True):
        self.__titulo = titulo
        self.__autor = autor
        self.__anio = anio
        self.__disponible = disponible

    def get_titulo(self): return self.__titulo
    def get_autor(self): return self.__autor
    def get_anio(self): return self.__anio
    def get_disponible(self): return self.__disponible
    def set_disponible(self, valor): self.__disponible = valor

    def guardar(self):
        conexion = ConexionBD()
        conexion.ejecutar(
            "INSERT INTO libros (titulo, autor, anio, disponible) VALUES (%s, %s, %s, %s)",
            (self.__titulo, self.__autor, self.__anio, self.__disponible)
        )
        conexion.cerrar()

    @staticmethod
    def listar():
        conexion = ConexionBD()
        libros = conexion.ejecutar("SELECT * FROM libros")
        if libros:
            print("\n📚 LISTA DE LIBROS")
            print("-" * 50)
            for libro in libros:
                estado = "Disponible" if libro["disponible"] else "Prestado"
                print(f"{libro['id']} - {libro['titulo']} ({libro['autor']}, {libro['anio']}) - {estado}")
        else:
            print("⚠️ No se pudieron obtener los libros.")
        conexion.cerrar()

    @staticmethod
    def actualizar_disponibilidad(id_libro, disponible):
        conexion = ConexionBD()
        conexion.ejecutar("UPDATE libros SET disponible = %s WHERE id = %s", (disponible, id_libro))
        conexion.cerrar()

    @staticmethod
    def actualizar_titulo(id_libro, nuevo_titulo):
        conexion = ConexionBD()
        conexion.ejecutar("UPDATE libros SET titulo = %s WHERE id = %s", (nuevo_titulo, id_libro))
        conexion.cerrar()
        print("✅ Título actualizado correctamente.")


# ==========================
# CLASE USUARIO
# ==========================
class Usuario:
    def __init__(self, nombre, tipo):
        self.__nombre = nombre
        self.__tipo = tipo

    def guardar(self):
        conexion = ConexionBD()
        conexion.ejecutar(
            "INSERT INTO usuarios (nombre, tipo) VALUES (%s, %s)",
            (self.__nombre, self.__tipo)
        )
        conexion.cerrar()

    @staticmethod
    def listar():
        conexion = ConexionBD()
        usuarios = conexion.ejecutar("SELECT * FROM usuarios")
        if usuarios:
            print("\n👤 LISTA DE USUARIOS")
            print("-" * 50)
            for usuario in usuarios:
                print(f"{usuario['id']} - {usuario['nombre']} ({usuario['tipo']})")
        else:
            print("⚠️ No se pudieron obtener los usuarios.")
        conexion.cerrar()


# ==========================
# CLASE PRÉSTAMO
# ==========================
class Prestamo:
    def __init__(self, id_usuario, id_libro, fecha_prestamo, fecha_devolucion=None):
        self.__id_usuario = id_usuario
        self.__id_libro = id_libro
        self.__fecha_prestamo = fecha_prestamo
        self.__fecha_devolucion = fecha_devolucion

    def registrar(self):
        conexion = ConexionBD()
        libro = conexion.ejecutar("SELECT disponible FROM libros WHERE id = %s", (self.__id_libro,))
        libro = libro[0] if libro else None
        if not libro:
            print("❌ El libro no existe.")
        elif not libro["disponible"]:
            print("⚠️ El libro no está disponible.")
        else:
            conexion.ejecutar(
                "INSERT INTO prestamos (id_usuario, id_libro, fecha_prestamo, fecha_devolucion) VALUES (%s, %s, %s, %s)",
                (self.__id_usuario, self.__id_libro, self.__fecha_prestamo, self.__fecha_devolucion)
            )
            Libro.actualizar_disponibilidad(self.__id_libro, False)
            print("✅ Préstamo registrado correctamente.")
        conexion.cerrar()

    @staticmethod
    def devolver(id_prestamo, fecha_devolucion):
        conexion = ConexionBD()
        prestamo = conexion.ejecutar("SELECT id_libro FROM prestamos WHERE id = %s", (id_prestamo,))
        prestamo = prestamo[0] if prestamo else None
        if prestamo:
            id_libro = prestamo["id_libro"]
            conexion.ejecutar(
                "UPDATE prestamos SET fecha_devolucion = %s WHERE id = %s",
                (fecha_devolucion, id_prestamo)
            )
            Libro.actualizar_disponibilidad(id_libro, True)
            print("📘 Libro devuelto con éxito.")
        else:
            print("❌ No se encontró el préstamo.")
        conexion.cerrar()

    @staticmethod
    def listar():
        conexion = ConexionBD()
        prestamos = conexion.ejecutar("""
            SELECT p.id, u.nombre, l.titulo, p.fecha_prestamo, p.fecha_devolucion
            FROM prestamos p
            JOIN usuarios u ON p.id_usuario = u.id
            JOIN libros l ON p.id_libro = l.id
        """)
        if prestamos:
            print("\n📖 LISTA DE PRÉSTAMOS")
            print("-" * 60)
            for p in prestamos:
                estado = "Activo" if p["fecha_devolucion"] is None else "Devuelto"
                print(f"{p['id']} - {p['nombre']} tiene '{p['titulo']}' desde {p['fecha_prestamo']} ({estado})")
        else:
            print("⚠️ No se pudieron obtener los préstamos.")
        conexion.cerrar()


# ==========================
# INTERFAZ POR TERMINAL
# ==========================
def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def menu():
    while True:
        limpiar_pantalla()
        print("===== SISTEMA DE BIBLIOTECA =====")
        print("1. Registrar Libro")
        print("2. Registrar Usuario")
        print("3. Registrar Préstamo")
        print("4. Devolver Libro")
        print("5. Listar Libros")
        print("6. Listar Usuarios")
        print("7. Listar Préstamos")
        print("8. Actualizar título de un libro")
        print("0. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            titulo = input("Título (o 0 para cancelar): ")
            if titulo == "0":
                continue
            autor = input("Autor (o 0 para cancelar): ")
            if autor == "0":
                continue
            try:
                anio = input("Año (o 0 para cancelar): ")
                if anio == "0":
                    continue
                anio = int(anio)
                libro = Libro(titulo, autor, anio)
                libro.guardar()
                print("✅ Libro registrado correctamente.")
            except ValueError:
                print("⚠️ Año inválido.")
            input("\nPresione Enter para continuar...")

        elif opcion == "2":
            nombre = input("Nombre (o 0 para cancelar): ")
            if nombre == "0":
                continue
            tipo = input("Tipo de usuario (Alumno/Profesor, o 0 para cancelar): ")
            if tipo == "0":
                continue
            usuario = Usuario(nombre, tipo)
            usuario.guardar()
            print("✅ Usuario registrado.")
            input("\nPresione Enter para continuar...")

        elif opcion == "3":
            try:
                id_usuario = input("ID Usuario (o 0 para cancelar): ")
                if id_usuario == "0":
                    continue
                id_usuario = int(id_usuario)

                id_libro = input("ID Libro (o 0 para cancelar): ")
                if id_libro == "0":
                    continue
                id_libro = int(id_libro)

                fecha = datetime.date.today()
                prestamo = Prestamo(id_usuario, id_libro, fecha)
                prestamo.registrar()
            except ValueError:
                print("⚠️ Debes ingresar IDs válidos.")
            input("\nPresione Enter para continuar...")

        elif opcion == "4":
            try:
                id_prestamo = input("ID del préstamo (o 0 para cancelar): ")
                if id_prestamo == "0":
                    continue
                id_prestamo = int(id_prestamo)

                fecha_dev = datetime.date.today()
                Prestamo.devolver(id_prestamo, fecha_dev)
            except ValueError:
                print("⚠️ ID inválido.")
            input("\nPresione Enter para continuar...")

        elif opcion == "5":
            Libro.listar()
            input("\nPresione Enter para continuar...")

        elif opcion == "6":
            Usuario.listar()
            input("\nPresione Enter para continuar...")

        elif opcion == "7":
            Prestamo.listar()
            input("\nPresione Enter para continuar...")

        elif opcion == "8":
            Libro.listar()
            try:
                id_libro = input("Ingrese el ID del libro a actualizar (o 0 para cancelar): ")
                if id_libro == "0":
                    continue
                id_libro = int(id_libro)
                nuevo_titulo = input("Ingrese el nuevo título: ")
                Libro.actualizar_titulo(id_libro, nuevo_titulo)
            except ValueError:
                print("⚠️ ID inválido.")
            input("\nPresione Enter para continuar...")

        elif opcion == "0":
            print("👋 Saliendo del sistema... ¡Hasta pronto!")
            break
        else:
            print("❌ Opción inválida, intente de nuevo.")
            input("\nPresione Enter para continuar...")


# ==========================
# PROGRAMA PRINCIPAL
# ==========================
if __name__ == "__main__":
    menu()