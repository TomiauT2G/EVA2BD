"""
URL configuration for salud_vital_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# ============================================================================
# IMPORTACIONES NECESARIAS
# ============================================================================
# Importación del módulo de administración de Django
from django.contrib import admin
# Importación de funciones para definir rutas URL
from django.urls import path, include
# Importación de configuraciones del proyecto
from django.conf import settings
# Importación para servir archivos estáticos en desarrollo
from django.conf.urls.static import static
# Importaciones para la documentación automática de la API REST
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# ============================================================================
# CONFIGURACIÓN DE RUTAS URL PRINCIPALES
# ============================================================================
urlpatterns = [
    # Ruta para el panel de administración de Django
    path('admin/', admin.site.urls),
    
    # Inclusión de todas las rutas de la aplicación principal 'salud_vital'
    # Esto incluye todas las rutas para pacientes, médicos, medicamentos, etc.
    path('', include('salud_vital.urls')),
    
    # ========================================================================
    # RUTAS PARA DOCUMENTACIÓN DE LA API REST
    # ========================================================================
    # Ruta para generar el esquema OpenAPI de la API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Ruta para la interfaz Swagger UI (documentación interactiva de la API)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Ruta para la interfaz ReDoc (documentación alternativa de la API)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# ============================================================================
# CONFIGURACIÓN PARA SERVIR ARCHIVOS MEDIA EN DESARROLLO
# ============================================================================
# Solo en modo DEBUG (desarrollo), se configuran las rutas para servir
# archivos media (imágenes, documentos subidos por usuarios, etc.)
# En producción, esto debe ser manejado por el servidor web (nginx, apache)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
