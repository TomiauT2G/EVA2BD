from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para las APIs REST
router = DefaultRouter()
router.register(r'especialidades', views.EspecialidadViewSet)
router.register(r'medicos', views.MedicoViewSet)
router.register(r'pacientes', views.PacienteViewSet)
router.register(r'consultas', views.ConsultaMedicaViewSet)
router.register(r'tratamientos', views.TratamientoViewSet)
router.register(r'medicamentos', views.MedicamentoViewSet)
router.register(r'recetas', views.RecetaMedicaViewSet)

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Especialidades
    path('especialidades/', views.especialidades_list, name='especialidades_list'),
    path('especialidades/crear/', views.especialidades_create, name='especialidades_create'),
    path('especialidades/<int:pk>/', views.especialidades_detail, name='especialidades_detail'),
    path('especialidades/<int:pk>/editar/', views.especialidades_edit, name='especialidades_edit'),
    path('especialidades/<int:pk>/eliminar/', views.especialidades_delete, name='especialidades_delete'),
    
    # Pacientes
    path('pacientes/', views.pacientes_list, name='pacientes_list'),
    path('pacientes/crear/', views.pacientes_create, name='pacientes_create'),
    path('pacientes/<int:pk>/', views.pacientes_detail, name='pacientes_detail'),
    path('pacientes/<int:pk>/editar/', views.pacientes_edit, name='pacientes_edit'),
    path('pacientes/<int:pk>/eliminar/', views.pacientes_delete, name='pacientes_delete'),
    
    # Médicos
    path('medicos/', views.medicos_list, name='medicos_list'),
    path('medicos/crear/', views.medicos_create, name='medicos_create'),
    path('medicos/<int:pk>/', views.medicos_detail, name='medicos_detail'),
    path('medicos/<int:pk>/editar/', views.medicos_edit, name='medicos_edit'),
    path('medicos/<int:pk>/eliminar/', views.medicos_delete, name='medicos_delete'),
    
    # Consultas Médicas
    path('consultas/', views.consultas_list, name='consultas_list'),
    path('consultas/crear/', views.consultas_create, name='consultas_create'),
    path('consultas/<int:pk>/', views.consultas_detail, name='consultas_detail'),
    path('consultas/<int:pk>/editar/', views.consultas_edit, name='consultas_edit'),
    path('consultas/<int:pk>/eliminar/', views.consultas_delete, name='consultas_delete'),
    
    # Tratamientos
    path('tratamientos/', views.tratamientos_list, name='tratamientos_list'),
    path('tratamientos/crear/', views.tratamientos_create, name='tratamientos_create'),
    path('tratamientos/<int:pk>/', views.tratamientos_detail, name='tratamientos_detail'),
    path('tratamientos/<int:pk>/editar/', views.tratamientos_edit, name='tratamientos_edit'),
    path('tratamientos/<int:pk>/eliminar/', views.tratamientos_delete, name='tratamientos_delete'),
    
    # Medicamentos
    path('medicamentos/', views.medicamentos_list, name='medicamentos_list'),
    path('medicamentos/crear/', views.medicamentos_create, name='medicamentos_create'),
    path('medicamentos/<int:pk>/', views.medicamentos_detail, name='medicamentos_detail'),
    path('medicamentos/<int:pk>/editar/', views.medicamentos_edit, name='medicamentos_edit'),
    path('medicamentos/<int:pk>/eliminar/', views.medicamentos_delete, name='medicamentos_delete'),
    
    # Recetas Médicas
    path('recetas/', views.recetas_list, name='recetas_list'),
    path('recetas/crear/', views.recetas_create, name='recetas_create'),
    path('recetas/<int:pk>/', views.recetas_detail, name='recetas_detail'),
    path('recetas/<int:pk>/editar/', views.recetas_edit, name='recetas_edit'),
    path('recetas/<int:pk>/eliminar/', views.recetas_delete, name='recetas_delete'),
    
    # Citas Médicas
    path('citas/', views.citas_list, name='citas_list'),
    path('citas/crear/', views.citas_create, name='citas_create'),
    path('citas/<int:pk>/', views.citas_detail, name='citas_detail'),
    path('citas/<int:pk>/editar/', views.citas_edit, name='citas_edit'),
    path('citas/<int:pk>/eliminar/', views.citas_delete, name='citas_delete'),
    
    # Historiales Clínicos
    path('historiales/', views.historiales_list, name='historiales_list'),
    path('historiales/crear/', views.historiales_create, name='historiales_create'),
    path('historiales/<int:pk>/', views.historiales_detail, name='historiales_detail'),
    path('historiales/<int:pk>/editar/', views.historiales_edit, name='historiales_edit'),
    path('historiales/<int:pk>/eliminar/', views.historiales_delete, name='historiales_delete'),
]