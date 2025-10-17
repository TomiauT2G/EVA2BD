# ============================================================================
# CONFIGURACIÓN DE URLs - APLICACIÓN SALUD VITAL
# ============================================================================
# Este archivo define todas las rutas URL para la aplicación Salud Vital,
# incluyendo endpoints de API REST y vistas basadas en plantillas HTML

# ============================================================================
# IMPORTACIONES NECESARIAS
# ============================================================================
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ============================================================================
# CONFIGURACIÓN DEL ROUTER PARA API REST
# ============================================================================
# Router automático que genera endpoints CRUD para cada ViewSet registrado
# Proporciona endpoints estándar: GET, POST, PUT, PATCH, DELETE
router = DefaultRouter()
router.register(r'especialidades', views.EspecialidadViewSet)
router.register(r'medicos', views.MedicoViewSet)
router.register(r'pacientes', views.PacienteViewSet)
router.register(r'consultas', views.ConsultaMedicaViewSet)
router.register(r'tratamientos', views.TratamientoViewSet)
router.register(r'medicamentos', views.MedicamentoViewSet)
router.register(r'recetas', views.RecetaMedicaViewSet)

# ============================================================================
# PATRONES DE URL PRINCIPALES
# ============================================================================
# Definición de todas las rutas de la aplicación organizadas por funcionalidad

urlpatterns = [
    # ========================================================================
    # ENDPOINTS DE API REST
    # ========================================================================
    # Incluye todas las rutas generadas automáticamente por el router
    path('api/', include(router.urls)),
    
    # ========================================================================
    # DASHBOARD PRINCIPAL
    # ========================================================================
    # Página principal con resumen estadístico del sistema
    path('', views.dashboard, name='dashboard'),
    
    # ========================================================================
    # GESTIÓN DE ESPECIALIDADES MÉDICAS
    # ========================================================================
    # CRUD completo para especialidades: listar, crear, ver, editar, eliminar
    path('especialidades/', views.especialidades_list, name='especialidades_list'),
    path('especialidades/crear/', views.especialidades_create, name='especialidades_create'),
    path('especialidades/<int:pk>/', views.especialidades_detail, name='especialidades_detail'),
    path('especialidades/<int:pk>/editar/', views.especialidades_edit, name='especialidades_edit'),
    path('especialidades/<int:pk>/eliminar/', views.especialidades_delete, name='especialidades_delete'),
    
    # ========================================================================
    # GESTIÓN DE PACIENTES
    # ========================================================================
    # CRUD completo para pacientes con filtros por datos personales
    path('pacientes/', views.pacientes_list, name='pacientes_list'),
    path('pacientes/crear/', views.pacientes_create, name='pacientes_create'),
    path('pacientes/<int:pk>/', views.pacientes_detail, name='pacientes_detail'),
    path('pacientes/<int:pk>/editar/', views.pacientes_edit, name='pacientes_edit'),
    path('pacientes/<int:pk>/eliminar/', views.pacientes_delete, name='pacientes_delete'),
    
    # ========================================================================
    # GESTIÓN DE MÉDICOS
    # ========================================================================
    # CRUD completo para médicos con filtros por especialidad
    path('medicos/', views.medicos_list, name='medicos_list'),
    path('medicos/crear/', views.medicos_create, name='medicos_create'),
    path('medicos/<int:pk>/', views.medicos_detail, name='medicos_detail'),
    path('medicos/<int:pk>/editar/', views.medicos_edit, name='medicos_edit'),
    path('medicos/<int:pk>/eliminar/', views.medicos_delete, name='medicos_delete'),
    
    # ========================================================================
    # GESTIÓN DE CONSULTAS MÉDICAS
    # ========================================================================
    # CRUD para consultas con filtros por fecha, médico y paciente
    path('consultas/', views.consultas_list, name='consultas_list'),
    path('consultas/crear/', views.consultas_create, name='consultas_create'),
    path('consultas/<int:pk>/', views.consultas_detail, name='consultas_detail'),
    path('consultas/<int:pk>/editar/', views.consultas_edit, name='consultas_edit'),
    path('consultas/<int:pk>/eliminar/', views.consultas_delete, name='consultas_delete'),
    
    # ========================================================================
    # GESTIÓN DE TRATAMIENTOS
    # ========================================================================
    # CRUD para tratamientos con seguimiento de fechas y estado
    path('tratamientos/', views.tratamientos_list, name='tratamientos_list'),
    path('tratamientos/crear/', views.tratamientos_create, name='tratamientos_create'),
    path('tratamientos/<int:pk>/', views.tratamientos_detail, name='tratamientos_detail'),
    path('tratamientos/<int:pk>/editar/', views.tratamientos_edit, name='tratamientos_edit'),
    path('tratamientos/<int:pk>/eliminar/', views.tratamientos_delete, name='tratamientos_delete'),
    
    # ========================================================================
    # GESTIÓN DE MEDICAMENTOS
    # ========================================================================
    # CRUD para inventario de medicamentos con alertas de stock y vencimiento
    path('medicamentos/', views.medicamentos_list, name='medicamentos_list'),
    path('medicamentos/crear/', views.medicamentos_create, name='medicamentos_create'),
    path('medicamentos/<int:pk>/', views.medicamentos_detail, name='medicamentos_detail'),
    path('medicamentos/<int:pk>/editar/', views.medicamentos_edit, name='medicamentos_edit'),
    path('medicamentos/<int:pk>/eliminar/', views.medicamentos_delete, name='medicamentos_delete'),
    
    # ========================================================================
    # GESTIÓN DE RECETAS MÉDICAS
    # ========================================================================
    # CRUD para recetas con relación médico-paciente-medicamentos
    path('recetas/', views.recetas_list, name='recetas_list'),
    path('recetas/crear/', views.recetas_create, name='recetas_create'),
    path('recetas/<int:pk>/', views.recetas_detail, name='recetas_detail'),
    path('recetas/<int:pk>/editar/', views.recetas_edit, name='recetas_edit'),
    path('recetas/<int:pk>/eliminar/', views.recetas_delete, name='recetas_delete'),
    
    # ========================================================================
    # GESTIÓN DE CITAS MÉDICAS
    # ========================================================================
    # CRUD para programación y seguimiento de citas médicas
    path('citas/', views.citas_list, name='citas_list'),
    path('citas/crear/', views.citas_create, name='citas_create'),
    path('citas/<int:pk>/', views.citas_detail, name='citas_detail'),
    path('citas/<int:pk>/editar/', views.citas_edit, name='citas_edit'),
    path('citas/<int:pk>/eliminar/', views.citas_delete, name='citas_delete'),
    
    # ========================================================================
    # GESTIÓN DE HISTORIALES CLÍNICOS
    # ========================================================================
    # CRUD para historiales médicos completos de pacientes
    path('historiales/', views.historiales_list, name='historiales_list'),
    path('historiales/crear/', views.historiales_create, name='historiales_create'),
    path('historiales/<int:pk>/', views.historiales_detail, name='historiales_detail'),
    path('historiales/<int:pk>/editar/', views.historiales_edit, name='historiales_edit'),
    path('historiales/<int:pk>/eliminar/', views.historiales_delete, name='historiales_delete'),
]