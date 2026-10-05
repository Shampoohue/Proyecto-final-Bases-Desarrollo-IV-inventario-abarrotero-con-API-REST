// Variables globales para controlar el estado de edición
let editingArticleId = null;
let editingCategoryId = null;

// Mensaje de depuración para confirmar que el script se ha cargado correctamente
console.log("=== script.js cargado correctamente ===");

// Función para cargar las categorías en el dropdown del formulario de artículos
function loadCategoryDropdown() {
    console.log("Cargando dropdown de categorías...");
    // Hacemos una solicitud a la API para obtener las categorías disponibles
    fetch('/api/categorias')
        .then(response => {
            console.log("Respuesta API categorías:", response.status);
            return response.json();
        })
        // Si la respuesta es exitosa, actualizamos el dropdown con las categorías recibidas
        .then(categories => {
            console.log("Categorías recibidas:", categories);
            const select = document.getElementById('articleCategoria');
            if (!select) {
                console.error("No se encontró el elemento select");
                return;
            }
            // Limpiamos el dropdown y agregamos una opción por defecto para "Sin Categoria"
            select.innerHTML = '<option value="">-- Sin Categoria --</option>';
            categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.nombre;
                select.appendChild(option);
            });
            console.log("Dropdown actualizado con", categories.length, "categorías");
        })

        // Si ocurre un error durante la solicitud, lo capturamos y mostramos un mensaje de error
        .catch(error => {
            console.error("Error al cargar categorías:", error);
            alert("Error al cargar categorías: " + error.message);
        });
}

// Función para cargar los artículos desde la API y mostrarlos en la tabla
function loadArticles() {
    console.log("Cargando artículos...");

    // Hacemos una solicitud a la API para obtener los artículos registrados
    fetch('/api/articulos')
        .then(response => response.json())
        .then(articles => {
            console.log("Artículos recibidos:", articles);
            const tbody = document.getElementById('articlesTableBody');
            // Verificamos que el elemento tbody exista antes de intentar manipularlo
            if (!tbody) {
                console.error("No se encontró el tbody");
                return;
            }
            // Si no hay artículos registrados, mostramos un mensaje indicando que la tabla está vacía
            if (articles.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6">No hay artículos registrados</td></tr>';
                return;
            }
            // Si hay artículos, limpiamos la tabla y la llenamos con los datos recibidos de la API
            tbody.innerHTML = '';
            articles.forEach(art => {
                const row = tbody.insertRow();
                row.insertCell(0).textContent = art.id;
                row.insertCell(1).textContent = art.nombre;
                row.insertCell(2).textContent = `$${art.precio.toFixed(2)}`;
                row.insertCell(3).textContent = art.stock;
                row.insertCell(4).textContent = art.categoria_nombre || 'Sin Categoria';
                const actionsCell = row.insertCell(5);
                const editBtn = document.createElement('button');
                editBtn.textContent = 'Editar';
                editBtn.className = 'edit-btn';
                editBtn.onclick = () => populateArticleForm(art);
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Eliminar';
                deleteBtn.className = 'delete-btn';
                deleteBtn.onclick = () => deleteArticle(art.id);
                actionsCell.appendChild(editBtn);
                actionsCell.appendChild(deleteBtn);
            });
        })
        // Si ocurre un error durante la solicitud, lo capturamos y mostramos un mensaje de error
        .catch(error => console.error("Error al cargar artículos:", error));
}

// Función para cargar las categorías desde la API y mostrarlas en la tabla
function loadCategories() {
    console.log("Cargando tabla de categorías...");

    // Hacemos una solicitud a la API para obtener las categorías registradas
    fetch('/api/categorias')
        .then(response => response.json())
        .then(categories => {
            console.log("Categorías recibidas:", categories);
            const tbody = document.getElementById('categoriesTableBody');

            // Verificamos que el elemento tbody exista antes de intentar manipularlo
            if (!tbody) {
                console.error("No se encontró el tbody de categorías");
                return;
            }
            // Si no hay categorías registradas, mostramos un mensaje indicando que la tabla está vacía
            if (categories.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4">No hay categorias registradas</td></tr>';
                return;
            }
            // Si hay categorías, limpiamos la tabla y la llenamos con los datos recibidos de la API
            tbody.innerHTML = '';
            categories.forEach(cat => {
                const row = tbody.insertRow();
                row.insertCell(0).textContent = cat.id;
                row.insertCell(1).textContent = cat.nombre;
                row.insertCell(2).textContent = cat.descripcion || '—';
                const actionsCell = row.insertCell(3);
                const editBtn = document.createElement('button');
                editBtn.textContent = 'Editar';
                editBtn.className = 'edit-btn';
                editBtn.onclick = () => populateCategoryForm(cat);
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = 'Eliminar';
                deleteBtn.className = 'delete-btn';
                deleteBtn.onclick = () => deleteCategory(cat.id);
                actionsCell.appendChild(editBtn);
                actionsCell.appendChild(deleteBtn);
            });
        })
        // Si ocurre un error durante la solicitud, lo capturamos y mostramos un mensaje de error
        .catch(error => console.error("Error al cargar categorías:", error));
}

// Función para eliminar un artículo por su ID, con confirmación previa
function deleteArticle(id) {
    // Antes de eliminar, preguntamos al usuario si está seguro de que desea eliminar el artículo
    if (!confirm('¿Estás seguro?')) return;
    fetch(`/api/articulos/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            alert(data.mensaje || data.error);
            if (!data.error) loadArticles();
        })
        // Si ocurre un error durante la solicitud, lo capturamos y mostramos un mensaje de error
        .catch(error => alert('Error: ' + error.message));
}

// Función para llenar el formulario de edición de artículos con los datos del artículo seleccionado
function populateArticleForm(article) {
    editingArticleId = article.id;
    document.getElementById('articleId').value = article.id;
    document.getElementById('articleNombre').value = article.nombre;
    document.getElementById('articlePrecio').value = article.precio;
    document.getElementById('articleStock').value = article.stock;
    document.getElementById('articleCategoria').value = article.categoria_id || '';
    document.getElementById('articleFormTitle').textContent = 'Editar Articulo';
    document.getElementById('articleSubmitBtn').textContent = 'Actualizar Articulo';
    document.getElementById('cancelArticleBtn').style.display = 'inline-block';
}

// Función para resetear el formulario de artículos a su estado inicial, limpiando los campos y restableciendo los textos de los botones
function resetArticleForm() {
    editingArticleId = null;
    document.getElementById('articleId').value = '';
    document.getElementById('articleForm').reset();
    document.getElementById('articleFormTitle').textContent = 'Agregar Nuevo Articulo';
    document.getElementById('articleSubmitBtn').textContent = 'Crear Articulo';
    document.getElementById('cancelArticleBtn').style.display = 'none';
}

// Función para manejar el envío del formulario de artículos, validando los datos ingresados y enviando
// la solicitud correspondiente a la API para crear o actualizar un artículo
function handleArticleSubmit(event) {
    // Evitamos que el formulario se envíe de forma tradicional para manejarlo con JavaScript
    event.preventDefault();
    const nombre = document.getElementById('articleNombre').value.trim();
    const precio = parseFloat(document.getElementById('articlePrecio').value);
    const stock = parseInt(document.getElementById('articleStock').value);
    let categoria_id = document.getElementById('articleCategoria').value;
    categoria_id = categoria_id === '' ? null : parseInt(categoria_id);

    // Validamos que el nombre no esté vacío, que el precio sea un número válido y no negativo, y que el stock sea un número entero válido y no negativo
    if (!nombre) { alert('El nombre es obligatorio'); return; }
    // Validamos que el precio sea un número válido y no negativo, y que el stock sea un número entero válido y no negativo
    if (isNaN(precio) || precio < 0) { alert('Precio inválido'); return; }
    // Validamos que el stock sea un número entero válido y no negativo
    if (isNaN(stock) || stock < 0) { alert('Stock inválido'); return; }

    // Preparamos los datos a enviar a la API, determinamos el método HTTP y la URL según si estamos editando o creando un nuevo artículo
    const data = { nombre, precio, stock, categoria_id };
    const method = editingArticleId ? 'PUT' : 'POST';
    const url = editingArticleId ? `/api/articulos/${editingArticleId}` : '/api/articulos';

    // Enviamos la solicitud a la API con los datos del artículo, y manejamos la respuesta para
    // mostrar un mensaje de éxito o error, y actualizar la lista de artículos y categorías si es necesario
    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.mensaje || data.error);
        if (!data.error) {
            resetArticleForm();
            loadArticles();
            loadCategoryDropdown();
        }
    })
    // Si ocurre un error durante la solicitud, lo capturamos y mostramos un mensaje de error
    .catch(error => alert('Error: ' + error.message));
}

// Función para eliminar una categoría por su ID, con confirmación previa
function deleteCategory(id) {
    // Antes de eliminar, preguntamos al usuario si está seguro de que desea eliminar la categoría
    if (!confirm('¿Eliminar esta categoria?')) return;
    fetch(`/api/categorias/${id}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            alert(data.mensaje || data.error);
            if (!data.error) {
                loadCategories();
                loadCategoryDropdown();
                loadArticles();
            }
        })
        // Si ocurre un error durante la solicitud, lo capturamos y mostramos un mensaje de error
        .catch(error => alert('Error: ' + error.message));
}

// Función para llenar el formulario de edición de categorías con los datos de la categoría seleccionada
function populateCategoryForm(category) {
    editingCategoryId = category.id;
    document.getElementById('categoryId').value = category.id;
    document.getElementById('categoryNombre').value = category.nombre;
    document.getElementById('categoryDescripcion').value = category.descripcion || '';
    document.getElementById('categoryFormTitle').textContent = 'Editar Categoría';
    document.getElementById('categorySubmitBtn').textContent = 'Actualizar Categoría';
    document.getElementById('cancelCategoryBtn').style.display = 'inline-block';
}

// Función para resetear el formulario de categorías a su estado inicial, limpiando los campos y restableciendo los textos de los botones
function resetCategoryForm() {
    editingCategoryId = null;
    document.getElementById('categoryId').value = '';
    document.getElementById('categoryForm').reset();
    document.getElementById('categoryFormTitle').textContent = 'Agregar Nueva Categoría';
    document.getElementById('categorySubmitBtn').textContent = 'Crear Categoría';
    document.getElementById('cancelCategoryBtn').style.display = 'none';
}

// Función para manejar el envío del formulario de categorías, validando los datos ingresados y enviando
function handleCategorySubmit(event) {
    // Evitamos que el formulario se envíe de forma tradicional para manejarlo con JavaScript
    event.preventDefault();
    const nombre = document.getElementById('categoryNombre').value.trim();
    const descripcion = document.getElementById('categoryDescripcion').value.trim();

    // Validamos que el nombre no esté vacío, ya que es un campo obligatorio para crear o actualizar una categoría
    if (!nombre) { alert('El nombre es obligatorio'); return; }

    // Preparamos los datos a enviar a la API, determinamos el método HTTP y la URL según si estamos editando o creando una nueva categoría
    const data = { nombre, descripcion };
    const method = editingCategoryId ? 'PUT' : 'POST';
    const url = editingCategoryId ? `/api/categorias/${editingCategoryId}` : '/api/categorias';

    // Enviamos la solicitud a la API con los datos de la categoría, y manejamos la respuesta para
    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.mensaje || data.error);
        if (!data.error) {
            resetCategoryForm();
            loadCategories();
            loadCategoryDropdown();
            loadArticles();
        }
    })
    // Si ocurre un error durante la solicitud, lo capturamos y mostramos un mensaje de error
    .catch(error => alert('Error: ' + error.message));
}

// INICIALIZACIÓN - Esta es la parte más importante
console.log("Configurando inicialización...");

// Función principal de inicio
function iniciarApp() {
    console.log("Iniciando aplicación...");

    // Verificar que los elementos existen
    if (!document.getElementById('articleForm')) {
        console.error("ERROR: No se encuentra el formulario de artículos");
        return;
    }

    // Configurar eventos
    document.getElementById('articleForm').addEventListener('submit', handleArticleSubmit);
    document.getElementById('cancelArticleBtn').addEventListener('click', resetArticleForm);
    document.getElementById('categoryForm').addEventListener('submit', handleCategorySubmit);
    document.getElementById('cancelCategoryBtn').addEventListener('click', resetCategoryForm);

    // Resetear formularios
    resetArticleForm();
    resetCategoryForm();

    // Cargar datos
    loadCategoryDropdown();
    loadArticles();
    loadCategories();

    console.log("Aplicación iniciada correctamente");
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciarApp);
} else {
    iniciarApp();
}