# 🚀 Taskify API

Una API REST desarrollada con FastAPI para administrar tareas (TODOs) con autenticación JWT y base de datos PostgreSQL.

## � Instrucciones para correr el proyecto

### Opción 1: Con Docker (Recomendado)

#### Prerrequisitos
- Docker Desktop instalado y en ejecución
- Docker Compose (incluido en Docker Desktop)

#### Pasos para levantar el proyecto

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd Taskify
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   ```
   
   Edita el archivo `.env` si necesitas cambiar alguna configuración (opcional para desarrollo).

3. **Levantar los servicios**
   ```bash
   docker-compose up -d
   ```

4. **Verificar que los servicios estén funcionando**
   ```bash
   docker-compose ps
   ```

5. **Acceder a la aplicación**
   - **API**: http://localhost:8000
   - **Documentación**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

#### Comandos útiles de Docker

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs solo de la API
docker-compose logs -f api

# Parar los servicios
docker-compose down

# Parar y eliminar volúmenes (elimina datos de la BD)
docker-compose down -v

# Reconstruir la imagen de la API
docker-compose build api

# Reiniciar solo un servicio
docker-compose restart api
```

### Opción 2: Instalación Local

#### Prerrequisitos
- Python 3.12+
- PostgreSQL instalado y configurado

#### Pasos

1. **Crear entorno virtual**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   ```
   
   Edita `.env` y cambia la URL de la base de datos:
   ```
   DATABASE_URL=postgresql://postgres:1234@localhost:5432/taskify_db
   ```

4. **Ejecutar migraciones (si las hay)**
   ```bash
   alembic upgrade head
   ```

5. **Ejecutar la aplicación**
   ```bash
   uvicorn main:app --reload
   ```

## 🔧 Ejemplos de uso de los endpoints

### 1. Health Check

```bash
# Con curl
curl http://localhost:8000/health

# Con httpie
http GET localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": 1757276266.9576468,
  "version": "1.0.0"
}
```

### 2. Registro de Usuario

```bash
# Con curl
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "usuario_ejemplo",
       "email": "usuario@ejemplo.com",
       "password": "mi_password_seguro"
     }'

# Con httpie
http POST localhost:8000/auth/register \
     username=usuario_ejemplo \
     email=usuario@ejemplo.com \
     password=mi_password_seguro
```

**Respuesta esperada:**
```json
{
  "id": 1,
  "username": "usuario_ejemplo",
  "email": "usuario@ejemplo.com",
  "is_active": true
}
```

### 3. Login (Obtener Token)

```bash
# Con curl
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=usuario_ejemplo&password=mi_password_seguro"

# Con httpie
http --form POST localhost:8000/auth/login \
     username=usuario_ejemplo \
     password=mi_password_seguro
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 4. Obtener Perfil de Usuario (Requiere Autenticación)

```bash
# Con curl
curl -X GET "http://localhost:8000/auth/me" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Con httpie
http GET localhost:8000/auth/me \
     "Authorization:Bearer YOUR_TOKEN_HERE"
```

### 5. Crear Tarea

```bash
# Con curl
curl -X POST "http://localhost:8000/tasks/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -d '{
       "title": "Mi primera tarea",
       "description": "Descripción de la tarea",
       "completed": false
     }'

# Con httpie
http POST localhost:8000/tasks/ \
     "Authorization:Bearer YOUR_TOKEN_HERE" \
     title="Mi primera tarea" \
     description="Descripción de la tarea" \
     completed:=false
```

### 6. Obtener Todas las Tareas

```bash
# Con curl
curl -X GET "http://localhost:8000/tasks/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Con httpie
http GET localhost:8000/tasks/ \
     "Authorization:Bearer YOUR_TOKEN_HERE"
```

### 7. Obtener Tarea por ID

```bash
# Con curl
curl -X GET "http://localhost:8000/tasks/1" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Con httpie
http GET localhost:8000/tasks/1 \
     "Authorization:Bearer YOUR_TOKEN_HERE"
```

### 8. Actualizar Tarea

```bash
# Con curl
curl -X PUT "http://localhost:8000/tasks/1" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -d '{
       "title": "Tarea actualizada",
       "description": "Nueva descripción",
       "completed": true
     }'

# Con httpie
http PUT localhost:8000/tasks/1 \
     "Authorization:Bearer YOUR_TOKEN_HERE" \
     title="Tarea actualizada" \
     description="Nueva descripción" \
     completed:=true
```

### 9. Eliminar Tarea

```bash
# Con curl
curl -X DELETE "http://localhost:8000/tasks/1" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Con httpie
http DELETE localhost:8000/tasks/1 \
     "Authorization:Bearer YOUR_TOKEN_HERE"
```

## � Documentación Adicional

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛡️ Seguridad

- La API utiliza JWT para autenticación
- Las contraseñas se almacenan hasheadas con bcrypt
- Configurar `SECRET_KEY` en producción con un valor seguro

## 🗄️ Base de Datos

- **PostgreSQL** en Docker: `localhost:5432`
- **Usuario**: `postgres`
- **Contraseña**: `1234`
- **Base de datos**: `taskify_db`

## 🔍 Troubleshooting

### Problemas comunes

1. **Puerto 8000 ocupado**
   ```bash
   # Cambiar puerto en docker-compose.yml
   ports:
     - "8001:8000"  # Usar puerto 8001 en lugar de 8000
   ```

2. **Problemas de conexión a la base de datos**
   ```bash
   # Verificar que PostgreSQL esté funcionando
   docker-compose logs postgres
   ```

3. **Regenerar contenedores**
   ```bash
   docker-compose down -v
   docker-compose up -d --build
   ```
