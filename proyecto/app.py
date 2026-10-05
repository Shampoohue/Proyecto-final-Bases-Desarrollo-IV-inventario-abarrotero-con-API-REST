# app.py
# Importamos librerias para manejar la base de datos
import sqlite3
# Importamos librerias necesarias para manejar las APIs
from flask import Flask, render_template, request, jsonify

# Definimos la aplicación Flask
app = Flask(__name__)
app.json.sort_keys = False

# Función para inicializar la base de datos
def init_db():
    # Inicializa la base de datos con las tablas necesarias
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()

    # Creamos tabla de categorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            descripcion TEXT
        )
    ''')

    # Crea la tabla de artículos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articulos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            categoria_id INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    conn.close()

# Funcion para obtener una conexión a la base de datos
def get_db():
    return sqlite3.connect("inventario.db")

# Forzamos la inicialización de la base de datos al iniciar la aplicación
init_db()
    
# Ruta para obtener la lista de categorías
@app.route("/api/categorias", methods=["GET"])
def get_categorias():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categorias ORDER BY id")
    datos = cursor.fetchall()
    conn.close()

    categorias = []
    # Almacenamos en el diccionario de categorias los datos obtenidos de la base de datos
    for fila in datos:
        categorias.append({
            "id": fila[0],
            "nombre": fila[1],
            "descripcion": fila[2]
        })
    # Devolvemos la lista de categorías en formato JSON con un código de estado 200 (OK)
    return jsonify(categorias), 200

# Ruta para obtener una categoría por su ID
@app.route("/api/categorias/<int:id>", methods=["GET"])
def get_categoria(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categorias WHERE id = ?", (id,))
    fila = cursor.fetchone()
    conn.close()

    # Si no se encuentra la categoría, devolvemos un error 404 (No encontrado)
    if not fila:
        return jsonify({"error": "Categoría no encontrada"}), 404

    # Si se encuentra la categoría, almacenamos sus datos en un diccionario y lo devolvemos en formato JSON con un código de estado 200 (OK)
    categoria = {
        "id": fila[0],
        "nombre": fila[1],
        "descripcion": fila[2]
    }

    # Devolvemos la categoría encontrada en formato JSON con un código de estado 200 (OK)
    return jsonify(categoria), 200

# Ruta para crear una nueva categoría
@app.route("/api/categorias", methods=["POST"])
def create_categoria():
    # Validamos que se haya enviado un JSON con el campo "nombre" y que no esté vacío
    try:
        data = request.json

        # Validamos que se haya enviado un JSON con el campo "nombre" y que no esté vacío
        if not data or "nombre" not in data or not data["nombre"].strip():
            return jsonify({"error": "El nombre de la categoría es obligatorio"}), 400

        nombre = data["nombre"].strip()
        descripcion = data.get("descripcion", "").strip()

        conn = get_db()
        existing = conn.execute("SELECT id FROM categorias WHERE nombre = ?", (nombre,)).fetchone()

        # Validamos que no exista otra categoría con el mismo nombre para evitar duplicados
        if existing:
            conn.close()
            return jsonify({"error": "Ya existe una categoría con ese nombre"}), 400

        # Insertamos la nueva categoría en la base de datos y devolvemos un mensaje de éxito con un código de estado 201 (Creado)
        conn.execute("INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
        conn.commit()
        conn.close()

        # Devolvemos un mensaje de éxito en formato JSON con un código de estado 201 (Creado)
        return jsonify({"mensaje": "Categoría creada exitosamente"}), 201
    
    # Si ocurre cualquier error durante el proceso, devolvemos un mensaje de error con un código de estado 500 (Error Interno del Servidor)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para actualizar una categoría existente por su ID
@app.route("/api/categorias/<int:id>", methods=["PUT"])
def update_categoria(id):

    # Validamos que se haya enviado un JSON con el campo "nombre" y que no esté vacío,
    # luego actualizamos la categoría en la base de datos y devolvemos un mensaje de éxito con un código de estado 200 (OK)
    try:
        data = request.json

        # Validamos que se haya enviado un JSON con el campo "nombre" y que no esté vacío
        if not data or "nombre" not in data or not data["nombre"].strip():
            return jsonify({"error": "El nombre de la categoría es obligatorio"}), 400

        nombre = data["nombre"].strip()
        descripcion = data.get("descripcion", "").strip()

        # Validamos que la categoría a actualizar exista en la base de datos
        conn = get_db()
        categoria = conn.execute("SELECT * FROM categorias WHERE id = ?", (id,)).fetchone()

        # Validamos que la categoría a actualizar exista en la base de datos, si no existe devolvemos un error 404 (No encontrado)
        if not categoria:
            conn.close()
            return jsonify({"error": "Categoría no encontrada"}), 404

        # Validamos que no exista otra categoría con el mismo nombre para evitar duplicados, excluyendo la categoría que estamos actualizando
        duplicate = conn.execute("SELECT id FROM categorias WHERE nombre = ? AND id != ?", (nombre, id)).fetchone()
        if duplicate:
            conn.close()
            return jsonify({"error": "Ya existe otra categoría con ese nombre"}), 400

        # Actualizamos la categoría en la base de datos y devolvemos un mensaje de éxito con un código de estado 200 (OK)
        conn.execute("UPDATE categorias SET nombre = ?, descripcion = ? WHERE id = ?", (nombre, descripcion, id))
        conn.commit()
        conn.close()
        # Devolvemos un mensaje de éxito en formato JSON con un código de estado 200 (OK)
        return jsonify({"mensaje": "Categoría actualizada exitosamente"}), 200
    
    # Si ocurre cualquier error durante el proceso, devolvemos un mensaje de error con un código de estado 500 (Error Interno del Servidor)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para eliminar una categoría por su ID
@app.route("/api/categorias/<int:id>", methods=["DELETE"])
def delete_categoria(id):

    # Obtiene la categoría de la base de datos para validar que exista antes de intentar eliminarla
    conn = get_db()
    categoria = conn.execute("SELECT * FROM categorias WHERE id = ?", (id,)).fetchone()

    # Validamos que la categoría a eliminar exista en la base de datos, si no existe devolvemos un error 404 (No encontrado),
    # luego eliminamos la categoría de la base de datos y devolvemos un mensaje de éxito con un código de estado 200 (OK)
    if not categoria:
        conn.close()
        return jsonify({"error": "Categoría no encontrada"}), 404

    # Eliminamos la categoría de la base de datos y devolvemos un mensaje de éxito con un código de estado 200 (OK)
    conn.execute("DELETE FROM categorias WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Categoría eliminada exitosamente"}), 200

# Rutas para manejar los artículos, incluyendo validaciones para asegurar que los datos sean correctos y que las categorías asociadas existan en la base de datos
@app.route("/api/articulos", methods=["GET"])
def get_articulos():

    # Obtenemos la lista de artículos de la base de datos, incluyendo el nombre de la categoría asociada a cada artículo,
    # y devolvemos los datos en formato JSON con un código de estado 200 (OK)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, a.nombre, a.precio, a.stock, a.categoria_id, c.nombre as categoria_nombre
        FROM articulos a
        LEFT JOIN categorias c ON a.categoria_id = c.id
        ORDER BY a.id
    ''')
    datos = cursor.fetchall()
    conn.close()

    # Almacenamos en el diccionario de artículos los datos obtenidos de la base de datos, incluyendo el nombre de la categoría asociada a cada artículo,
    # y devolvemos la lista de artículos en formato JSON con un código de estado 200 (OK)
    articulos = []
    for fila in datos:
        articulos.append({
            "id": fila[0],
            "nombre": fila[1],
            "precio": fila[2],
            "stock": fila[3],
            "categoria_id": fila[4],
            "categoria_nombre": fila[5]
        })
    return jsonify(articulos), 200

# Ruta para obtener un artículo por su ID, incluyendo el nombre de la categoría asociada al artículo
@app.route("/api/articulos/<int:id>", methods=["GET"])
def get_articulo(id):

    # Obtenemos el artículo de la base de datos por su ID, incluyendo el nombre de la categoría asociada al artículo
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.id, a.nombre, a.precio, a.stock, a.categoria_id, c.nombre as categoria_nombre
        FROM articulos a
        LEFT JOIN categorias c ON a.categoria_id = c.id
        WHERE a.id = ?
    ''', (id,))
    fila = cursor.fetchone()
    conn.close()
    
    # Validamos que el artículo exista en la base de datos, si no existe devolvemos un error 404 (No encontrado),
    if not fila:
        return jsonify({"error": "Artículo no encontrado"}), 404
    
    # Si se encuentra el artículo, almacenamos sus datos en un diccionario, incluyendo el nombre de la categoría asociada al artículo,
    # y lo devolvemos en formato JSON con un código de estado 200 (OK)
    articulo = {
        "id": fila[0],
        "nombre": fila[1],
        "precio": fila[2],
        "stock": fila[3],
        "categoria_id": fila[4],
        "categoria_nombre": fila[5]
    }
    return jsonify(articulo), 200

# Ruta para crear un nuevo artículo, incluyendo validaciones para asegurar que los datos sean correctos y que las categorías asociadas existan en la base de datos
@app.route("/api/articulos", methods=["POST"])
def create_articulo():

    # Validamos que se haya enviado un JSON con los campos obligatorios "nombre", "precio" y "stock", y que los datos sean correctos
    try:
        data = request.json
        required = ["nombre", "precio", "stock"]

        # Validamos que se hayan enviado los campos obligatorios "nombre", "precio" y "stock", y que los datos sean correctos,
        # incluyendo validaciones para asegurar que el precio sea un número positivo, el stock sea un entero no negativo, y que la categoría asociada exista en la base de datos si se especifica una categoría_id
        for field in required:
            if field not in data:
                return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

        # Validamos que el nombre del artículo no esté vacío, que el precio sea un número positivo, que el stock sea un entero no negativo,
        # y que la categoría asociada exista en la base de datos si se especifica una categoría_id
        nombre = data["nombre"].strip()
        if not nombre:
            return jsonify({"error": "El nombre del artículo no puede estar vacío"}), 400

        # Validamos que el precio sea un número positivo, que el stock sea un entero no negativo,
        # y que la categoría asociada exista en la base de datos si se especifica una categoría_id
        try:
            precio = float(data["precio"])
            if precio < 0:
                raise ValueError
            
        # Validamos que el precio sea un número positivo, que el stock sea un entero no negativo,
        except:
            return jsonify({"error": "El precio debe ser un número positivo"}), 400

        # Validamos que el precio sea un número positivo, que el stock sea un entero no negativo,
        # y que la categoría asociada exista en la base de datos si se especifica una categoría_id
        try:
            stock = int(data["stock"])
            if stock < 0:
                raise ValueError
            
        # Validamos que el precio sea un número positivo, que el stock sea un entero no negativo,
        # y que la categoría asociada exista en la base de datos si se especifica una categoría_id
        except:
            return jsonify({"error": "El stock debe ser un entero no negativo"}), 400

        # Validamos que la categoría asociada exista en la base de datos si se especifica una categoría_id,
        # y que la categoría_id sea un número entero positivo, si no es así, consideramos que no se ha especificado una categoría para el artículo
        categoria_id = data.get("categoria_id")
        if categoria_id is not None:
            try:
                categoria_id = int(categoria_id)
                if categoria_id <= 0:
                    categoria_id = None
            except:
                categoria_id = None

        # Validamos que la categoría asociada exista en la base de datos si se especifica una categoría_id, y que la categoría_id sea un número entero positivo,
        # si no es así, consideramos que no se ha especificado una categoría para el artículo
        conn = get_db()
        if categoria_id:
            cat_exists = conn.execute("SELECT id FROM categorias WHERE id = ?", (categoria_id,)).fetchone()
            if not cat_exists:
                conn.close()
                return jsonify({"error": "La categoría especificada no existe"}), 400

        # Insertamos el nuevo artículo en la base de datos y devolvemos un mensaje de éxito con un código de estado 201 (Creado)
        conn.execute(
            "INSERT INTO articulos (nombre, precio, stock, categoria_id) VALUES (?, ?, ?, ?)",
            (nombre, precio, stock, categoria_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Artículo creado exitosamente"}), 201
    
    # Si ocurre cualquier error durante el proceso, devolvemos un mensaje de error con un código de estado 500 (Error Interno del Servidor)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para actualizar un artículo existente por su ID
@app.route("/api/articulos/<int:id>", methods=["PUT"])
def update_articulo(id):
    # Validamos que se haya enviado un JSON con los campos obligatorios "nombre", "precio" y "stock", y que los datos sean correctos
    try:
        data = request.json
        required = ["nombre", "precio", "stock"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

        # Validamos que el nombre del artículo no esté vacío, que el precio sea un número positivo, que el stock sea un entero no negativo,
        nombre = data["nombre"].strip()
        if not nombre:
            return jsonify({"error": "El nombre del artículo no puede estar vacío"}), 400
        
        # Validamos que el precio sea un número positivo, que el stock sea un entero no negativo
        try:
            precio = float(data["precio"])
            if precio < 0:
                raise ValueError
            
        # Validamos que el precio sea un número positivo, que el stock sea un entero no negativo
        except:
            return jsonify({"error": "El precio debe ser un número positivo"}), 400

        # Validamos que el precio sea un número positivo, que el stock sea un entero no negativo
        try:
            stock = int(data["stock"])
            if stock < 0:
                raise ValueError
            
        # Validamos que el precio sea un número positivo, que el stock sea un entero no negativo
        except:
            return jsonify({"error": "El stock debe ser un entero no negativo"}), 400

        # Validamos que la categoría asociada exista en la base de datos si se especifica una categoría_id, y que la categoría_id sea un número entero positivo
        categoria_id = data.get("categoria_id")
        if categoria_id is not None:
            try:
                categoria_id = int(categoria_id)
                if categoria_id <= 0:
                    categoria_id = None
            except:
                categoria_id = None

        # Validamos que la categoría asociada exista en la base de datos si se especifica una categoría_id, y que la categoría_id sea un número entero positivo
        conn = get_db()
        articulo = conn.execute("SELECT * FROM articulos WHERE id = ?", (id,)).fetchone()
        if not articulo:
            conn.close()
            return jsonify({"error": "Artículo no encontrado"}), 404

        # Validamos que la categoría asociada exista en la base de datos si se especifica una categoría_id, y que la categoría_id sea un número entero positivo
        if categoria_id:
            cat_exists = conn.execute("SELECT id FROM categorias WHERE id = ?", (categoria_id,)).fetchone()
            if not cat_exists:
                conn.close()
                return jsonify({"error": "La categoría especificada no existe"}), 400

        # Actualizamos el artículo en la base de datos y devolvemos un mensaje de éxito con un código de estado 200 (OK)
        conn.execute(
            "UPDATE articulos SET nombre = ?, precio = ?, stock = ?, categoria_id = ? WHERE id = ?",
            (nombre, precio, stock, categoria_id, id)
        )
        conn.commit()
        conn.close()
        return jsonify({"mensaje": "Artículo actualizado exitosamente"}), 200
    
    # Si ocurre cualquier error durante el proceso, devolvemos un mensaje de error con un código de estado 500 (Error Interno del Servidor)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para eliminar un artículo por su ID
@app.route("/api/articulos/<int:id>", methods=["DELETE"])
def delete_articulo(id):
    conn = get_db()
    articulo = conn.execute("SELECT * FROM articulos WHERE id = ?", (id,)).fetchone()

    # Validamos que el artículo a eliminar exista en la base de datos, si no existe devolvemos un error 404 (No encontrado)
    if not articulo:
        conn.close()
        return jsonify({"error": "Artículo no encontrado"}), 404

    # Eliminamos el artículo de la base de datos y devolvemos un mensaje de éxito con un código de estado 200 (OK)
    conn.execute("DELETE FROM articulos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Artículo eliminado exitosamente"}), 200

# Ruta para renderizar la página principal de la aplicación
@app.route("/")
def index():
    return render_template("index.html")

# Iniciamos la aplicación Flask en modo de depuración para facilitar el desarrollo y la detección de errores
if __name__ == "__main__":
    app.run(debug=True)