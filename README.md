# Sistema de Administración Médica - Salud Vital Ltda.

## Descripción
Sistema completo de administración médica desarrollado con Django y Django REST Framework para la gestión integral de consultas médicas, pacientes, médicos, tratamientos y medicamentos.

## Características Principales

### 🏥 Gestión Médica Completa
- **Especialidades Médicas**: Registro y administración de especialidades
- **Médicos**: Gestión completa de profesionales médicos
- **Pacientes**: Registro y seguimiento de pacientes
- **Consultas Médicas**: Programación y registro de consultas
- **Tratamientos**: Seguimiento de tratamientos médicos
- **Medicamentos**: Control de inventario y prescripciones
- **Recetas Médicas**: Gestión de prescripciones y dosificaciones

### 🔧 Tecnologías Utilizadas
- **Backend**: Django 4.2.7
- **API REST**: Django REST Framework
- **Base de Datos**: PostgreSQL
- **Documentación**: OpenAPI/Swagger (drf-spectacular)
- **Filtros**: django-filter
- **CORS**: django-cors-headers

## Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- PostgreSQL
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd EVA2BD
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv eva2
   eva2\Scripts\activate  # Windows
   # source eva2/bin/activate  # Linux/Mac
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar PostgreSQL**
   - Crear base de datos: `salud_vital_db`
   - Usuario: `postgres`
   - Contraseña: `1983`
   - Host: `localhost`
   - Puerto: `5432`

5. **Ejecutar migraciones**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Cargar datos iniciales**
   ```bash
   python manage.py load_initial_data
   ```

7. **Iniciar servidor**
   ```bash
   python manage.py runserver
   ```

## Acceso al Sistema

### Panel de Administración
- **URL**: http://127.0.0.1:8000/admin/
- **Usuario**: admin
- **Contraseña**: admin123

### API REST
- **Base URL**: http://127.0.0.1:8000/api/
- **Documentación Swagger**: http://127.0.0.1:8000/api/docs/
- **Documentación ReDoc**: http://127.0.0.1:8000/api/redoc/

## Endpoints de la API

### Especialidades
- `GET /api/especialidades/` - Listar especialidades
- `POST /api/especialidades/` - Crear especialidad
- `GET /api/especialidades/{id}/` - Detalle de especialidad
- `PUT /api/especialidades/{id}/` - Actualizar especialidad
- `DELETE /api/especialidades/{id}/` - Eliminar especialidad

### Médicos
- `GET /api/medicos/` - Listar médicos
- `POST /api/medicos/` - Crear médico
- `GET /api/medicos/{id}/` - Detalle de médico
- `PUT /api/medicos/{id}/` - Actualizar médico
- `DELETE /api/medicos/{id}/` - Eliminar médico
- `GET /api/medicos/{id}/consultas/` - Consultas del médico

### Pacientes
- `GET /api/pacientes/` - Listar pacientes
- `POST /api/pacientes/` - Crear paciente
- `GET /api/pacientes/{id}/` - Detalle de paciente
- `PUT /api/pacientes/{id}/` - Actualizar paciente
- `DELETE /api/pacientes/{id}/` - Eliminar paciente
- `GET /api/pacientes/{id}/consultas/` - Consultas del paciente

### Consultas Médicas
- `GET /api/consultas/` - Listar consultas
- `POST /api/consultas/` - Crear consulta
- `GET /api/consultas/{id}/` - Detalle de consulta
- `PUT /api/consultas/{id}/` - Actualizar consulta
- `DELETE /api/consultas/{id}/` - Eliminar consulta

### Tratamientos
- `GET /api/tratamientos/` - Listar tratamientos
- `POST /api/tratamientos/` - Crear tratamiento
- `GET /api/tratamientos/{id}/` - Detalle de tratamiento
- `PUT /api/tratamientos/{id}/` - Actualizar tratamiento
- `DELETE /api/tratamientos/{id}/` - Eliminar tratamiento
- `GET /api/tratamientos/activos/` - Tratamientos activos

### Medicamentos
- `GET /api/medicamentos/` - Listar medicamentos
- `POST /api/medicamentos/` - Crear medicamento
- `GET /api/medicamentos/{id}/` - Detalle de medicamento
- `PUT /api/medicamentos/{id}/` - Actualizar medicamento
- `DELETE /api/medicamentos/{id}/` - Eliminar medicamento
- `GET /api/medicamentos/stock-bajo/` - Medicamentos con stock bajo
- `GET /api/medicamentos/proximos-vencer/` - Medicamentos próximos a vencer

### Recetas Médicas
- `GET /api/recetas/` - Listar recetas
- `POST /api/recetas/` - Crear receta
- `GET /api/recetas/{id}/` - Detalle de receta
- `PUT /api/recetas/{id}/` - Actualizar receta
- `DELETE /api/recetas/{id}/` - Eliminar receta

## Filtros y Búsquedas

### Médicos
- Filtrar por especialidad
- Buscar por nombre, apellido o RUT

### Pacientes
- Filtrar por rango de edad
- Buscar por nombre, apellido o RUT

### Consultas
- Filtrar por médico, paciente o rango de fechas
- Buscar por motivo

### Medicamentos
- Filtrar por stock bajo o próximos a vencer
- Buscar por nombre

## Estructura del Proyecto

```
EVA2BD/
├── salud_vital_project/          # Configuración principal del proyecto
│   ├── settings.py               # Configuraciones Django
│   ├── urls.py                   # URLs principales
│   └── wsgi.py                   # Configuración WSGI
├── salud_vital/                  # Aplicación principal
│   ├── models.py                 # Modelos de datos
│   ├── serializers.py            # Serializers para API
│   ├── views.py                  # ViewSets y vistas
│   ├── admin.py                  # Configuración del admin
│   ├── urls.py                   # URLs de la aplicación
│   └── management/               # Comandos personalizados
│       └── commands/
│           └── load_initial_data.py
├── requirements.txt              # Dependencias del proyecto
├── manage.py                     # Script de gestión Django
└── README.md                     # Este archivo
```

## Datos de Prueba

El sistema incluye datos iniciales de prueba:

### Especialidades
- Cardiología
- Neurología
- Pediatría
- Ginecología
- Traumatología

### Médicos
- Dr. Juan Carlos González Pérez (Cardiología)
- Dr. María Elena Rodríguez Silva (Neurología)
- Dr. Pedro Antonio Martínez López (Pediatría)

### Pacientes
- Ana María Fernández Castro
- Carlos Eduardo Morales Vega
- Sofía Isabel Herrera Muñoz

### Medicamentos
- Paracetamol
- Ibuprofeno
- Amoxicilina

## Comandos Útiles

### Cargar datos iniciales
```bash
python manage.py load_initial_data
```

### Crear superusuario
```bash
python manage.py createsuperuser
```

### Ejecutar tests
```bash
python manage.py test
```

### Recopilar archivos estáticos
```bash
python manage.py collectstatic
```

## Configuración de Producción

Para despliegue en producción, considerar:

1. **Variables de entorno**: Usar archivo `.env` para configuraciones sensibles
2. **DEBUG**: Establecer `DEBUG = False`
3. **ALLOWED_HOSTS**: Configurar hosts permitidos
4. **Base de datos**: Configurar PostgreSQL en servidor de producción
5. **Archivos estáticos**: Configurar servidor web para servir archivos estáticos
6. **HTTPS**: Implementar certificados SSL

## Soporte y Contacto

Para soporte técnico o consultas sobre el sistema, contactar al equipo de desarrollo.

---

**Salud Vital Ltda.** - Sistema de Administración Médica
Desarrollado con Django y Django REST Framework