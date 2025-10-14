# Especificaciones de Implementación - Sistema Salud Vital Ltda.

## 1. Configuración del Entorno de Desarrollo

### 1.1 Entorno Virtual Python

```bash
# Crear entorno virtual
python -m venv eva2

# Activar entorno virtual (Windows)
eva2\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source eva2/bin/activate
```

### 1.2 Dependencias del Proyecto

**requirements.txt**
```txt
Django==4.2.7
djangorestframework==3.14.0
psycopg2-binary==2.9.7
django-cors-headers==4.3.1
drf-spectacular==0.26.5
django-filter==23.3
Pillow==10.0.1
python-decouple==3.8
```

### 1.3 Configuración de PostgreSQL

**Configuración de Base de Datos:**
- Host: localhost
- Puerto: 5432
- Base de datos: salud_vital_db
- Usuario: postgres
- Contraseña: 1983

## 2. Estructura del Proyecto Django

```
salud_vital_project/
├── manage.py
├── requirements.txt
├── .env
├── salud_vital_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── especialidades/
│   ├── medicos/
│   ├── pacientes/
│   ├── consultas/
│   ├── tratamientos/
│   ├── medicamentos/
│   └── recetas/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
└── templates/
    ├── base.html
    ├── dashboard.html
    └── apps/
```

## 3. Configuración de Django Settings

**settings.py**
```python
import os
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
]

LOCAL_APPS = [
    'apps.especialidades',
    'apps.medicos',
    'apps.pacientes',
    'apps.consultas',
    'apps.tratamientos',
    'apps.medicamentos',
    'apps.recetas',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'salud_vital_project.urls'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='salud_vital_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='1983'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# Spectacular settings for OpenAPI
SPECTACULAR_SETTINGS = {
    'TITLE': 'Sistema Salud Vital API',
    'DESCRIPTION': 'API para el sistema de administración médica de Salud Vital Ltda.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Internationalization
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

## 4. Modelos Django Detallados

### 4.1 Modelo Especialidad

```python
# apps/especialidades/models.py
from django.db import models

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'especialidades'
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
```

### 4.2 Modelo Médico

```python
# apps/medicos/models.py
from django.db import models
from apps.especialidades.models import Especialidad

class Medico(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medicos'
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"Dr. {self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
```

### 4.3 Modelo Paciente

```python
# apps/pacientes/models.py
from django.db import models

class Paciente(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pacientes'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def edad(self):
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
```

### 4.4 Modelo Consulta Médica

```python
# apps/consultas/models.py
from django.db import models
from apps.pacientes.models import Paciente
from apps.medicos.models import Medico

class ConsultaMedica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT)
    fecha_consulta = models.DateTimeField()
    motivo = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultas_medicas'
        verbose_name = 'Consulta Médica'
        verbose_name_plural = 'Consultas Médicas'
        ordering = ['-fecha_consulta']

    def __str__(self):
        return f"Consulta {self.paciente.nombre_completo} - {self.fecha_consulta.strftime('%d/%m/%Y')}"
```

### 4.5 Modelo Tratamiento

```python
# apps/tratamientos/models.py
from django.db import models
from apps.consultas.models import ConsultaMedica

class Tratamiento(models.Model):
    consulta = models.ForeignKey(ConsultaMedica, on_delete=models.CASCADE)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tratamientos'
        verbose_name = 'Tratamiento'
        verbose_name_plural = 'Tratamientos'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Tratamiento {self.consulta.paciente.nombre_completo} - {self.fecha_inicio}"

    @property
    def esta_activo(self):
        from datetime import date
        if not self.fecha_fin:
            return True
        return date.today() <= self.fecha_fin
```

### 4.6 Modelo Medicamento

```python
# apps/medicamentos/models.py
from django.db import models

class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medicamentos'
        verbose_name = 'Medicamento'
        verbose_name_plural = 'Medicamentos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def stock_bajo(self):
        return self.stock <= 10

    @property
    def proximo_vencimiento(self):
        from datetime import date, timedelta
        return self.fecha_vencimiento <= date.today() + timedelta(days=30)
```

### 4.7 Modelo Receta Médica

```python
# apps/recetas/models.py
from django.db import models
from apps.tratamientos.models import Tratamiento
from apps.medicamentos.models import Medicamento

class RecetaMedica(models.Model):
    FRECUENCIA_CHOICES = [
        ('cada_8_horas', 'Cada 8 horas'),
        ('cada_12_horas', 'Cada 12 horas'),
        ('cada_24_horas', 'Cada 24 horas'),
        ('segun_necesidad', 'Según necesidad'),
    ]

    tratamiento = models.ForeignKey(Tratamiento, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    frecuencia = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES)
    duracion = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recetas_medicas'
        verbose_name = 'Receta Médica'
        verbose_name_plural = 'Recetas Médicas'
        ordering = ['-created_at']

    def __str__(self):
        return f"Receta {self.medicamento.nombre} - {self.tratamiento.consulta.paciente.nombre_completo}"

    @property
    def costo_total(self):
        return self.cantidad * self.medicamento.precio_unitario
```

## 5. Serializers Django REST Framework

### 5.1 Serializer Base

```python
# apps/core/serializers.py
from rest_framework import serializers

class BaseModelSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
```

### 5.2 Serializers Específicos

```python
# apps/especialidades/serializers.py
from rest_framework import serializers
from .models import Especialidad

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'

# apps/medicos/serializers.py
from rest_framework import serializers
from .models import Medico
from apps.especialidades.serializers import EspecialidadSerializer

class MedicoSerializer(serializers.ModelSerializer):
    especialidad_nombre = serializers.CharField(source='especialidad.nombre', read_only=True)
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Medico
        fields = '__all__'

class MedicoDetailSerializer(MedicoSerializer):
    especialidad = EspecialidadSerializer(read_only=True)
```

## 6. ViewSets y Filtros

### 6.1 ViewSet Base

```python
# apps/core/viewsets.py
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

class BaseModelViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = '__all__'
    ordering = ['-created_at']
```

### 6.2 ViewSets Específicos

```python
# apps/medicos/views.py
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Medico
from .serializers import MedicoSerializer, MedicoDetailSerializer
from .filters import MedicoFilter

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.select_related('especialidad')
    serializer_class = MedicoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MedicoFilter
    search_fields = ['nombre', 'apellido', 'rut']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MedicoDetailSerializer
        return MedicoSerializer
```

## 7. Configuración de URLs

### 7.1 URLs Principales

```python
# salud_vital_project/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.core.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('', include('apps.dashboard.urls')),
]
```

### 7.2 URLs de API

```python
# apps/core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.especialidades.views import EspecialidadViewSet
from apps.medicos.views import MedicoViewSet
from apps.pacientes.views import PacienteViewSet
from apps.consultas.views import ConsultaMedicaViewSet
from apps.tratamientos.views import TratamientoViewSet
from apps.medicamentos.views import MedicamentoViewSet
from apps.recetas.views import RecetaMedicaViewSet

router = DefaultRouter()
router.register(r'especialidades', EspecialidadViewSet)
router.register(r'medicos', MedicoViewSet)
router.register(r'pacientes', PacienteViewSet)
router.register(r'consultas', ConsultaMedicaViewSet)
router.register(r'tratamientos', TratamientoViewSet)
router.register(r'medicamentos', MedicamentoViewSet)
router.register(r'recetas', RecetaMedicaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## 8. Comandos de Inicialización

### 8.1 Script de Configuración Inicial

```bash
# Crear proyecto
django-admin startproject salud_vital_project
cd salud_vital_project

# Crear aplicaciones
python manage.py startapp apps.especialidades
python manage.py startapp apps.medicos
python manage.py startapp apps.pacientes
python manage.py startapp apps.consultas
python manage.py startapp apps.tratamientos
python manage.py startapp apps.medicamentos
python manage.py startapp apps.recetas
python manage.py startapp apps.dashboard

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos iniciales
python manage.py loaddata initial_data.json

# Ejecutar servidor
python manage.py runserver
```

### 8.2 Archivo .env

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=salud_vital_db
DB_USER=postgres
DB_PASSWORD=1983
DB_HOST=localhost
DB_PORT=5432
```

Este documento proporciona todas las especificaciones técnicas necesarias para implementar el sistema completo de administración médica con Django REST Framework, PostgreSQL y documentación OpenAPI.