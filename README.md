# 🚀 Taskify API

Una API REST desarrollada con FastAPI para administrar tareas (TODOs).

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos relacional
- **SQLAlchemy** - ORM para Python
- **JWT** - Autenticación con tokens

## 🚀 Instalación y configuración

### 1. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Copia el archivo `.env` y ajusta las configuraciones según tu entorno.

### 4. Ejecutar la aplicación
```bash
uvicorn main:app --reload
```

La API estará disponible en: http://localhost:8000

## 📖 Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Próximos pasos

- [ ] Configurar base de datos
- [ ] Crear modelos de datos
- [ ] Implementar autenticación
- [ ] Crear endpoints CRUD
- [ ] Agregar tests
